"""Bounded formalization preparation. Never approves rules or mutates prior inputs."""
from pathlib import Path
import argparse
import copy
import hashlib
import json
import platform
import sys
import uuid

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
PREVIOUS = ROOT / 'experiments/rule-cluster-contract-v1-batch-1'
NS = uuid.UUID('5f54005b-08fb-4de5-9d21-11bd71ce3883')
EXT = 'lorebuddy-dnd2024-review'

def uid(key):
    return 'urn:uuid:' + str(uuid.uuid5(NS, key))

def load(path):
    return json.loads(path.read_text())

def sha(data):
    return 'sha256:' + hashlib.sha256(data).hexdigest()

def encoded(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode()

def build(out):
    files = {}
    def save(path, value):
        files[path] = encoded(value)
    k = load(PREVIOUS / 'input/knowledge.json')
    acceptance = load(PREVIOUS / 'reports/batch-acceptance.json')
    assert acceptance['status'] == 'accepted_internal_candidate_batch'
    assert sha((PREVIOUS / 'input/knowledge.json').read_bytes())[7:] == acceptance['knowledge_sha256']
    sources = {s['entry_id']: s for s in k['sources']}
    ev = {e['id']: e for e in k['evidence']}
    acquisition = ROOT / 'build/acquisition-run-1/f1824e5ebdc3584ba98398335dbf1408'
    inventory_path = acquisition / 'inventory/entries.jsonl'
    inventory = {e['id']: e for e in map(json.loads, inventory_path.read_text().splitlines())}
    artifact_path = acquisition / 'inventory/artifact.json'
    artifact = load(artifact_path)
    container_path = acquisition / artifact['extensions']['m1b-acquisition']['preserved_path']
    assert sha(container_path.read_bytes()) == artifact['digest']
    assert container_path.stat().st_size == artifact['size']
    work_claims = {}
    mappings = {}
    fragments = {}
    entries = []
    for sid, s in sources.items():
        raw, note = Path(s['raw_path']).read_bytes(), Path(s['note_path']).read_bytes()
        assert sha(raw)[7:] == s['raw_sha256'] and sha(note)[7:] == s['note_sha256']
        entry = inventory[sid]
        assert entry['artifact_id'] == s['artifact_id'] == artifact['id']
        assert entry['digest'] == sha(raw) and entry['size'] == len(raw)
        assert (acquisition / 'extracted' / entry['storage_path']).resolve() == Path(s['raw_path']).resolve()
        claim = s['reviewed_mapping_candidate']
        key = claim['book_id']
        if key not in work_claims:
            work_claims[key] = {'work_id': uid('work-claim:' + key), 'edition_id': uid('edition-claim:' + key)}
            pair = work_claims[key]
            save('sources/catalog/works/' + pair['work_id'][9:] + '.json', {
                'schema': 'm2.publication-claim@0.1.0', 'id': pair['work_id'], 'kind': 'work',
                'title_claim': claim['book_name'], 'identity_status': 'claimed',
                'basis': 'previous accepted candidate catalog classification; not bibliographic verification',
                'review_status': 'in_review', 'rights': 'unknown'})
            save('sources/catalog/editions/' + pair['edition_id'][9:] + '.json', {
                'schema': 'm2.publication-claim@0.1.0', 'id': pair['edition_id'], 'kind': 'edition',
                'work_id': pair['work_id'], 'title_claim': claim['book_name'], 'language': 'zh-Hans',
                'translation_authority': 'unknown', 'identity_status': 'claimed', 'rights': 'unknown',
                'basis': 'local Chinese expression claim; not an official Chinese edition assertion', 'review_status': 'in_review'})
        pair = work_claims[key]
        mid, fid, bid = uid('mapping:' + sid), uid('raw-entry-fragment:' + sid), uid('boundary:' + sid)
        mapping = {'schema': 'core.source-mapping@0.1.0', 'id': mid,
                   'source': {'kind': 'entry', 'id': sid}, 'target': pair,
                   'mapping_status': 'claimed', 'review_status': 'pending',
                   'lifecycle': {'status': 'draft', 'revision': 1},
                   'extensions': {EXT: {'previous_mapping': claim, 'decision_scope': 'accept claimed association or reject; never auto-verify'}}}
        mappings[sid] = mapping
        save('metadata/source-mappings/' + mid[9:] + '.json', mapping)
        fragment = {'schema': 'core.source-fragment@0.1.0', 'id': fid, 'entry_id': sid,
                    'entry_digest': sha(raw), 'locator': {'kind': 'byte-range', 'start': 0, 'end': len(raw), 'parser': 'raw-bytes-no-parser@1'},
                    'fragment_digest': sha(raw), 'source_mapping_ids': [mid], 'boundary_record_id': bid,
                    'lifecycle': {'status': 'draft', 'revision': 1},
                    'extensions': {EXT: {'selection': 'whole raw entry audit envelope; not a fine-grained rule boundary',
                                        'digest_semantics': 'raw selected bytes under executable core.source-fragment@0.1.0 schema; not source-fragment-events protocol',
                                        'full_fidelity_claim': False}}}
        fragments[sid] = fragment
        save('metadata/fragments/' + fid[9:] + '.json', fragment)
        save('metadata/boundaries/' + bid[9:] + '.json', {
            'schema': 'core.boundary-record@0.1.0', 'id': bid, 'artifact_id': artifact['id'], 'entry_id': sid,
            'candidate_key': sha((sid + ':whole-entry-audit').encode()),
            'locator': {'kind': 'byte-range', 'start': 0, 'end': len(raw)}, 'proposed_title': claim['title'],
            'status': 'proposed', 'node_id': None,
            'decision': {'review_status': 'pending', 'reviewer_id': None, 'reason': 'Audit envelope only; per-subject derived ranges remain separate.'},
            'lifecycle': {'status': 'draft', 'revision': 1}})
        entries.append({'entry_id': sid, 'inventory_record': entry, 'fragment_id': fid,
                        'source_mapping_id': mid, 'raw_path': s['raw_path'], 'note_path': s['note_path'],
                        'note_sha256': sha(note), 'encoding': s['encoding']})
    save('metadata/evidence/source-lock.json', {
        'artifact_record': artifact, 'artifact_record_path': str(artifact_path),
        'preserved_container_path': str(container_path),
        'inventory_path': str(inventory_path), 'inventory_sha256': sha(inventory_path.read_bytes()),
        'selected_entries': entries, 'ownership': 'Original Artifact and full Inventory remain in frozen acquisition; selected records here are locked references, not a new Inventory.'})
    for e in ev.values():
        source = sources[e['source_entry_id']]
        start, end = e['range']['start'], e['range']['end']
        assert Path(source['note_path']).read_bytes()[start:end] == e['text'].encode()
        save('metadata/evidence/records/' + e['id'][9:] + '.json', {
            'schema': 'm2.derived-text-evidence@0.1.0', 'id': e['id'], 'original_record': e,
            'raw_fragment_id': fragments[e['source_entry_id']]['id'],
            'derived_artifact_path': source['note_path'], 'derived_artifact_digest': 'sha256:' + source['note_sha256'],
            'coordinate_basis': 'derived_note_utf8_not_raw_entry',
            'raw_to_derived_fidelity': 'not_proven_by_this_record'})
    objects = []
    for c in k['cards']:
        objects.append(('creature', c, c['source_evidence_id'], c['verbatim_text']))
        objects.extend(('ability', a, a['source_evidence_id'], a['verbatim_text']) for a in c['abilities'])
    objects.extend(('spell', s, s['source_evidence_id'], s['verbatim_text']) for s in k['spells'])
    for s in k['shared_rules']:
        source = sources[s['source_entry_id']]
        # Shared rule bodies deliberately retain complete original Note, including front matter.
        objects.append(('shared_reference', s, None, s['content']['text']))
    subjects, review_queue = [], []
    for kind, obj, eid, text in objects:
        sid = ev[eid]['source_entry_id'] if eid else obj['source_entry_id']
        source = sources[sid]
        if eid:
            body_range = {x: ev[eid]['range'][x] for x in ['start', 'end']}
        else:
            body_range = {'start': 0, 'end': len(text.encode())}
        assert Path(source['note_path']).read_bytes()[body_range['start']:body_range['end']] == text.encode()
        oid, rid = obj['id'], uid('review:' + obj['id'])
        module = 'creatures' if kind in ['creature', 'ability'] else ('spells' if kind == 'spell' else 'common')
        body_path = 'library/review-bodies/' + oid[9:] + '.md'
        files[body_path] = text.encode()  # Exact bytes, no added newline or formatting.
        subject = {
            'schema': 'm2.rule-review-subject@0.1.0', 'id': oid, 'subject_kind': kind,
            'title': obj['title'], 'language': obj.get('language', 'zh-Hans'), 'module': module,
            'rules_context_id': k['rules_context']['id'], 'review_status': 'in_review',
            'body': {'path': body_path, 'digest': sha(text.encode()), 'encoding': 'utf-8'},
            'source_binding': {'entry_id': sid, 'artifact_id': source['artifact_id'],
                               'fragment_id': fragments[sid]['id'], 'mapping_id': mappings[sid]['id'],
                               'derived_evidence_id': eid, 'derived_note_utf8_range': body_range},
            'full_fidelity': 'not_claimed', 'candidate_snapshot': copy.deepcopy(obj),
            'review_record_id': rid,
            'dependency_ids': sorted({r['to_id'] for r in k['relations'] if r['from_id'] == oid} |
                                     set(obj.get('mechanics', {}).get('dependencies', []))),
            'uncompiled_semantics_retained': True}
        subjects.append(subject)
        save('metadata/review-subjects/' + oid[9:] + '.json', subject)
        record = {'schema': 'm2.rule-review-record@0.1.0', 'id': rid, 'subject_id': oid,
                  'subject_digest': sha(encoded(subject)), 'status': 'awaiting_review',
                  'ai_precheck': 'source_note_bytes_and_input_identity_verified; not_human_approval',
                  'human_decision': None, 'reviewer': None,
                  'checks': ['content_and_exceptions', 'applicability_and_claimed_source',
                             'structured_fields_and_call_overrides', 'dependencies_and_uncompiled_scope'],
                  'source_fidelity_gate': 'pending_normative_raw_to_library_coverage'}
        save('metadata/reviews/' + rid[9:] + '.json', record)
        review_queue.append({'subject_id': oid, 'review_record_id': rid, 'kind': kind,
                             'title': obj['title'], 'owner_id': obj.get('owner_id'), 'body': body_path})
    for category, dirname in [('structured_extractions', 'structured-extractions'), ('editorial_decisions', 'adoptions'),
                              ('mapping_rules', 'extraction-rules'), ('relations', 'relationships'), ('expressions', 'expressions')]:
        for record in k[category]:
            save('metadata/' + dirname + '/' + record['id'][9:] + '.json', record)
    save('metadata/evidence/research-receipts.json', k['research_receipts'])
    save('metadata/clusters.json', k['clusters'])
    plan = {'schema': 'm2.package-boundary-plan@0.1.0', 'status': 'proposed_for_review',
            'access_domain': {'id': uid('access:local-owner'), 'principal': 'local project owner; no public distribution', 'status': 'proposed'},
            'language': 'zh-Hans', 'rules_context': k['rules_context'], 'rights': 'unknown',
            'packages': [{'id': uid('package:' + name), 'name': name, 'package_revision': '0.1.0-draft.1',
                          'content_dependencies': deps, 'build_dependencies': [] if name == 'audit' else ['audit'],
                          'payload_scope': scope}
                         for name, deps, scope in [('audit', [], 'locked original Artifact/Entry references, mappings, evidence and reviews'),
                                                   ('common', [], 'six complete shared references; no consumer-specific truncation'),
                                                   ('spells', ['common'], 'eleven complete spells; spell bodies own base casting facts'),
                                                   ('creatures', ['common', 'spells'], 'eight creatures and forty-five owned abilities')]],
            'source_authority': 'claimed and unknown preserved separately from local rule adoption',
            'release': 'not_requested; Rights unknown never grants redistribution',
            'schemas': ['existing finite D&D production profile retained', 'review-subject schema is a staging envelope, not new Core'],
            'migration': 'Original 70 semantic IDs retained; new review/mapping/fragment IDs separate. Original consumed corpus remains immutable.',
            'note': 'Boundary plan only; no Package publication or source relocation in this run.'}
    save('metadata/package-plan.json', plan)
    save('metadata/review-queue.json', review_queue)
    lines = ['# 本批正式化审核入口', '',
             '状态：待审；0项规则正式批准。70个审核对象不等于70个已批准知识节点。', '',
             '八张整卡作为完整性视图，45能力、11法术分别维护拥有者事实；六份共享材料保持完整来源参考，不将整个术语页伪装为单条原子规则。', '',
             '正文链接为原字节副本；逐字段值、法术覆盖及依赖见同ID的review-subject记录。', '',
             '| 类别 | 标题 | 拥有者 | 原文 | 结构与审核绑定 |', '|---|---|---|---|---|']
    titles = {o['id']: o['title'] for _, o, _, _ in objects}
    for item in review_queue:
        oid = item['subject_id']
        label = item['title'].replace('|', '／')
        owner = titles.get(item['owner_id'], '—')
        lines.append(f"| {item['kind']} | {label} | {owner} | [全文]({item['body']}) | [记录](metadata/review-subjects/{oid[9:]}.json) |")
    lines += ['', '## 本批采用决定（原文和采用分开）', '']
    for decision in k['editorial_decisions']:
        lines.append(f"- `{decision['alias']}`：{json.dumps(decision['adopted'], ensure_ascii=False)}；[依据与适用范围](metadata/adoptions/{decision['id'][9:]}.json)。")
    lines += ['', '## 审核范围与当前阻断', '',
              '1. 70对象的正文、归属、适用环境和254字段抽取；3项既有采用决定，均未因P6接纳而提升为正式批准。',
              '2. 20条Entry到出版身份的claimed映射；接受这一关联声明不等于核验为verified。',
              '3. 私有包边界与同一local-owner访问域；不授予公开再分发许可。',
              '4. 正式忠实转写节点激活前，仍须完成原始事件流、Library事件流及逐Unit保真覆盖；当前whole-entry审计Fragment不能代替该证明。', '',
              '以上审核决定分别记录；当前human_decision为空，未伪造用户终审或审核人。']
    files['REVIEW.md'] = ('\n'.join(lines) + '\n').encode()

    issues = [
        {'id': uid('issue:human-review'), 'code': 'HUMAN_RULE_REVIEW_PENDING', 'scope': [s['id'] for s in subjects],
         'blocks': ['approved_rule_status'], 'resolution': 'Review exact 70 subjects, 254 extractions and 3 adoption decisions; record scoped user decisions.'},
        {'id': uid('issue:mapping-review'), 'code': 'CLAIMED_MAPPING_REVIEW_PENDING', 'scope': [m['id'] for m in mappings.values()],
         'blocks': ['formal_traceability_approval'], 'resolution': 'Review claimed associations as claims; verification not implied and unknown translation/Rights remain.'},
        {'id': uid('issue:fidelity'), 'code': 'NORMATIVE_FIDELITY_COVERAGE_NOT_IMPLEMENTED', 'scope': [s['id'] for s in subjects],
         'blocks': ['formal_transcription_node_activation', 'full_fidelity_claim'],
         'resolution': 'Raw whole-entry Fragments and exact Note ranges are different coordinate systems. Source/Library events, per-unit Coverage Map and all reference/visibility decisions must pass the normative protocols before formal transcription nodes activate.'},
        {'id': uid('issue:package-policy'), 'code': 'PACKAGE_PLAN_PENDING', 'scope': [p['id'] for p in plan['packages']],
         'blocks': ['package_assembly'], 'resolution': 'Confirm private access/principal and package dependency boundaries before assembly; this is not a public rights decision.'}]
    save('metadata/issues/open.json', issues)
    manifest = {'schema': 'm2.formalization-intake@0.1.0', 'status': 'review_preparation_complete_formal_approval_blocked',
                'input_delivery_id': k['delivery_id'], 'input_digest': sha((PREVIOUS / 'input/knowledge.json').read_bytes()),
                'p6_decision': str(PREVIOUS / 'reports/batch-acceptance.json'), 'p6_decision_digest': sha((PREVIOUS / 'reports/batch-acceptance.json').read_bytes()),
                'counts': {'subjects': len(subjects), 'creatures': 8, 'abilities': 45, 'spells': 11, 'shared_references': 6,
                           'raw_fragments': len(fragments), 'mappings': len(mappings), 'evidence_records': len(ev),
                           'extractions': len(k['structured_extractions']), 'adoptions': len(k['editorial_decisions'])},
                'toolchain': {'python': platform.python_version(), 'generator_digest': sha(Path(__file__).read_bytes()),
                              'validator_digest': sha((HERE / 'validate.py').read_bytes()),
                              'normative_inputs': {str(p.relative_to(ROOT)): sha(p.read_bytes()) for p in [
                                  ROOT/'schemas/fragment.schema.json', ROOT/'schemas/source-mapping.schema.json',
                                  ROOT/'schemas/boundary-record.schema.json',
                                  ROOT/'docs/milestone-0/integrity-protocols.md', ROOT/'AGENTS.md']}},
                'file_digests': {p: sha(data) for p, data in sorted(files.items())}}
    files['intake.json'] = encoded(manifest)
    for path, data in files.items():
        dest = out / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
    return manifest

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=HERE / 'review-bundle')
    args = parser.parse_args()
    print(json.dumps(build(args.output)['counts'], ensure_ascii=False))
