"""Read-only recheck of supplied Terminal evidence against the fixed input/Gold.

This scores existing output; it does not execute the consumer or approve rules.
"""
import hashlib
import json
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parent
TERMINAL = Path('/Users/chenzehao/Projects/DND Terminal')
EVIDENCE = Path('/Users/chenzehao/Vaults/obsidian/obisidian/理工学习相关/DND Terminal/version-work/c0.1.0/evidence/contract-v1-batch-1-consumer-2026-10-26')


def read(path):
    return json.loads(path.read_text())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


knowledge = read(BASE / 'input/knowledge.json')
cards = {c['id']: c for c in knowledge['cards']}
abilities = {a['id']: a for c in cards.values() for a in c['abilities']}
spells = {s['id']: s for s in knowledge['spells']}
evidence = {e['id']: e for e in knowledge['evidence']}
questions, gold = {}, {}
question_files = ['regression-questions.json', 'new-questions.json']
for filename in question_files:
    questions[filename] = {q['id']: q for q in read(BASE / 'input' / filename)['questions']}
    gold[filename] = {g['id']: g for g in read(BASE / 'evaluator' / filename.replace('questions', 'gold'))['cases']}

outside_codes = dict(zip(
    ['C19', 'C20', 'C21', 'C22', 'C23', 'N19', 'N20', 'N21', 'N22'],
    ['hp_branch_and_unconsciousness_not_supported', 'hp_and_temporary_hp_settlement_not_supported',
     'multi_target_and_effect_application_not_supported', 'source_scoped_effect_removal_not_supported',
     'instance_migration_not_supported', 'mixed_damage_not_supported',
     'conditional_owner_damage_modifier_not_supported', 'damage_transfer_and_hp_not_supported',
     'stored_spell_release_and_resource_not_supported']))
summaries = {}
pending_kinds = {
    'C10': ['sourced_curse'], 'C13': ['ignite'], 'C14': ['ignite'],
    'C17': ['unrequested_area_targets', 'ignite'], 'C18': ['sourced_condition'],
    'N10': ['condition'], 'N11': ['condition'], 'N13': ['ignite'],
    'N15': ['sourced_curse'], 'N16': ['sourced_condition'],
    'N18': ['unrequested_area_targets', 'ignite']
}  # Explicit review mapping from natural-language Gold requirements.
for phase in ['first', 'verified']:
    raw_path = EVIDENCE / phase / 'raw.json'
    raw, score = read(raw_path), read(EVIDENCE / phase / 'score.json')
    assert score['raw_sha256'] == digest(raw_path)
    assert raw['input_sha256']['knowledge'] == digest(BASE / 'input/knowledge.json')
    for filename in question_files:
        assert raw['input_sha256']['question_sets'][filename] == digest(BASE / 'input' / filename)
        gf = filename.replace('questions', 'gold')
        assert score['gold_sha256'][gf] == digest(BASE / 'evaluator' / gf)
    expected_keys = {(f, qid) for f, qs in questions.items() for qid in qs}
    actual_keys = [(r['question_set'], r['id']) for r in raw['results']]
    assert len(actual_keys) == len(set(actual_keys)) == 48 and set(actual_keys) == expected_keys
    counts = Counter()
    for row in raw['results']:
        filename, qid = row['question_set'], row['id']
        q, g, result = questions[filename][qid], gold[filename][qid], row['result']
        binding = result['binding']
        roster = {e['instance_id']: e for e in q['scene']['roster']}
        event = q['scene']['event']
        assert binding['scene_snapshot'] == q['scene']
        assert binding['delivery_id'] == knowledge['delivery_id']
        for field in ['contract_id', 'contract_revision', 'schema_revision']:
            assert binding[field] == knowledge[field]
        assert row['scope_source'] == 'question.request_scope'
        assert result['request_scope'] == q['request_scope'] and result['applied'] is False
        assert binding['actor_instance_id'] == event['actor_instance_id']
        assert binding['actor_prototype_id'] == roster[event['actor_instance_id']]['prototype_id']
        assert binding['target_instance_ids'] == event['target_instance_ids']
        ability = abilities[binding['ability_id']]
        assert ability['owner_id'] == binding['actor_prototype_id']
        for source in binding['source_evidence']:
            assert source == evidence[source['id']]
        if binding['spell_id']:
            assert binding['spell_id'] in spells
        else:
            assert ability['title'] == event['declared_action_name']
        expected = g['expected']
        numeric = result.get('numeric')
        if expected['semantic_status'] == 'numeric_result':
            assert result['status'] == 'calculated'
            for field in ['stages', 'damage_taken', 'linked_reduction']:
                assert numeric[field] == expected[field], (qid, field)
            assert numeric['input_snapshot']['request'] == result['core_request']
            # The core snapshots only the selected definition, not its lookup map.
            context = dict(result['core_context'])
            context['definition'] = context.pop('definitions')[result['core_request']['ability']]
            context.setdefault('verified_facts', None)
            assert numeric['input_snapshot']['context'] == context
            assert json.loads(result['core_request']['event']) == event
            pending = {e['kind'] for e in result['pending_effects']}
            if g.get('pending_non_numeric_effects'):
                assert qid in pending_kinds
            assert set(pending_kinds.get(qid, [])) <= pending
            counts['numeric'] += 1
        else:
            status = 'unsupported' if expected['semantic_status'] == 'outside_core' else expected['semantic_status']
            assert result['status'] == status and numeric is None
            codes = {i['code'] for i in result['issues']}
            required = expected.get('required_issue_codes', [])
            if qid in outside_codes:
                required = [outside_codes[qid]]
            if qid == 'C24':
                required = ['missing_save_outcome']
            assert set(required) <= codes
            counts['boundary'] += 1
        counts[result['status']] += 1
    summaries[phase] = {'raw_sha256': digest(raw_path), 'counts': dict(counts), 'checks': 'passed'}

manifest = read(EVIDENCE / 'verified/source-manifest.json')
for relative, sha in manifest.items():
    assert digest(EVIDENCE / 'verified/source' / relative) == sha
    assert digest(TERMINAL / relative) == sha

receipt = {
    'recorded_on': '2026-10-26', 'status': 'P5_verified',
    'delivery_id': knowledge['delivery_id'], 'knowledge_sha256': digest(BASE / 'input/knowledge.json'),
    'upstream_evidence': str(EVIDENCE), 'method': 'verify_consumer_receipt.py; existing output rechecked, no consumer rerun',
    'phases': summaries, 'source_snapshot_and_current_files_match': len(manifest),
    'checked': ['exact case sets and fixed input/Gold digests', '36 numeric results and all stages',
                '12 boundary statuses and reason codes', 'full scene snapshots and direct request scopes',
                'ability ownership, source evidence records, numeric input snapshots', 'all applied=false',
                'Gold required pending effects retained'],
    'p6': {'recommendation': 'accept_internal_candidate_batch', 'user_decision': 'pending'},
    'resolves_preparation_issue': 'urn:uuid:f1dc4170-db2d-5bb5-8d01-0659ee9153d9',
    'remaining_boundary': 'Full casting legality/effects, mixed damage, structure multiplier, transfer, HP/state/resource writes and migration remain unsupported.',
    'authority': 'AI recheck of supplied evidence; not independent human source approval or formal Package release'
}
(BASE / 'reports/consumer-receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(receipt, ensure_ascii=False, indent=2))
