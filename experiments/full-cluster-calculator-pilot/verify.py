"""Material verification and assembly fault injection only; never execute a calculator."""
from pathlib import Path
import copy
import hashlib
import json
import re

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
def load(p):return json.loads(p.read_text())
def check(c):
    cards=c['cards']; evidence={e['alias']:e for e in c['evidence']}
    sources={s['entry_id']:s for s in c['sources']}
    assert len(cards)==5 and sum(len(x['abilities']) for x in cards)==30,'card/ability coverage'
    ids=[x['id'] for key in ['cards','spells','shared_rules','expressions','clusters'] for x in c[key]]+[a['id'] for x in cards for a in x['abilities']]
    assert len(ids)==len(set(ids)),'duplicate identity'
    ids=set(ids)
    for e in evidence.values():
        s=sources[e['source_entry_id']]; b=Path(s['note_path']).read_bytes()
        assert b[e['range']['start']:e['range']['end']].decode()==e['text'],'evidence text range'
        assert hashlib.sha256(e['text'].encode()).hexdigest()==e['text_sha256'],'evidence digest'
    for card in cards:
        assert card['verbatim_text']==evidence[card['card_evidence']]['text'],'full card text'
        assert card['header']['source_evidence'] in evidence
        assert card['review_status']=='candidate'
        for a in card['abilities']:
            assert a['owner_id']==card['id'],'ability owner'
            assert a['verbatim_text']==evidence[a['verbatim_evidence']]['text'],'full ability text'
            assert a['verbatim_text'] in card['verbatim_text'],'ability in original card'
            assert set(a.get('required_evidence',[])) <= set(evidence),'evidence closure'
            for dep in a['mechanics']['dependencies']:assert dep in ids,'semantic dependency closure'
            for call in a['mechanics'].get('spell_calls',[]):assert call['target_id'] in ids,'spell dependency closure'
    for cluster in c['clusters']:
        assert cluster['root_object_id'] in ids
        assert set(cluster['content_dependencies'])<=ids,'cluster closure'
    for rel in c['relations']:
        assert rel['from_id'] in ids and rel['to_id'] in ids,'relationship closure'
    for p in c['shared_rules']:
        b=Path(sources[p['source_entry_id']]['note_path']).read_bytes()
        assert p['content']['text'].encode()==b,'complete public entry'
        assert p['coverage']['start']==0 and p['coverage']['end']==len(b)
    for s in c['spells']:
        assert s['verbatim_text']==evidence[s['alias']]['text'],'complete spell text'
    assert len(c['spells'])==11 and len(c['shared_rules'])==6,'module scope'
    # Retained legacy aliases must resolve; they are not the identities themselves.
    for value in c['alias_registry'].values():
        for x in value if isinstance(value,list) else [value]:assert x in ids,'alias resolution'

corpus=load(HERE/'input/knowledge.json'); check(corpus)
for s in corpus['sources']:
    for p,h in [('note_path','note_sha256'),('raw_path','raw_sha256')]:
        assert hashlib.sha256(Path(s[p]).read_bytes()).hexdigest()==s[h]
# Full inherited card/ability fields were not silently removed in the new projection.
oldcards={}
for b,keys in [('build/m2-cross-relations-6cards-2026-10-22',['SU','IN','G25']),('build/m2-seven-card-optimization-2026-10-22/current',['F','S'])]:
    old=load(ROOT/b/'cards.json');oldcards.update({old[k]['id']:old[k] for k in keys})
for card in corpus['cards']:
    old=oldcards[card['id']]
    assert [a['id'] for a in card['abilities']]==[a['id'] for a in old['abilities']]
    for a,b in zip(card['abilities'],old['abilities']):
        for key,value in b.items():assert a[key]==value,(a['id'],key)
q=load(HERE/'input/questions.json')['questions'];g=load(HERE/'evaluator/gold.json')['cases']
assert len(q)==len(g)==24 and len({x['id'] for x in q})==24
assert [x['id'] for x in q]==[x['id'] for x in g]
assert sum(x['category']=='within_numeric_core_if_data_binding_succeeds' for x in g)==18
for x in q:
    assert len(x['scene']['roster'])==7
    assert set(x['scene']['event']['target_instance_ids']) <= {a['instance_id'] for a in x['scene']['roster']}
    def keys(o):
        if isinstance(o,dict):
            for k,v in o.items():yield k;yield from keys(v)
        elif isinstance(o,list):
            for v in o:yield from keys(v)
    assert not {'request','context','expected','gold','stages','damage_taken','expression_id','selected_ability_id'} & set(keys(x)),'per-case prebinding or answer leak'
    actor=next(r for r in x['scene']['roster'] if r['instance_id']==x['scene']['event']['actor_instance_id'])
    card=next(c for c in corpus['cards'] if c['id']==actor['prototype_id'])
    declared=x['scene']['event']['declared_action_name']
    if declared=='火球术':assert card['id']==corpus['alias_registry']['S']
    else:assert declared in [a['title'] for a in card['abilities']]

faults=[]
for name,mutate in [
    ('drop_unused_ability',lambda c:c['cards'][0]['abilities'].pop()),
    ('truncate_verbatim_card',lambda c:c['cards'][0].update(verbatim_text=c['cards'][0]['verbatim_text'][:-10])),
    ('remove_shared_spell',lambda c:c['spells'].pop(0)),
    ('wrong_ability_owner',lambda c:c['cards'][0]['abilities'][0].update(owner_id=c['cards'][1]['id'])),
    ('truncate_unused_public_rule',lambda c:c['shared_rules'][0]['content'].update(text=c['shared_rules'][0]['content']['text'][:-1])),
]:
    broken=copy.deepcopy(corpus);mutate(broken)
    try:check(broken)
    except AssertionError as e:faults.append({'fault':name,'blocked':True,'reason':str(e)})
    else:raise AssertionError('fault escaped: '+name)
report={'status':'material_checks_passed_not_calculator_execution','cards':5,'abilities':30,'spells':11,'full_shared_entries':6,'evidence':len(corpus['evidence']),'source_entries':len(corpus['sources']),
        'questions':24,'numeric_mechanism_within_core':18,'outside_or_missing':6,'same_full_corpus_for_all_questions':True,'per_case_request_context_or_expected_values':False,
        'original_card_ability_fields_preserved':True,'source_raw_and_note_bytes_match':True,'fault_injections':faults,'calculator_execution':'Not Run','llm_execution':'Not Run','human_final_approval':'Pending'}
(HERE/'reports').mkdir(exist_ok=True)
(HERE/'reports/material-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
