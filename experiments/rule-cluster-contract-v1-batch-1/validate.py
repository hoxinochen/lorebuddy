"""Finite-schema, provenance, ownership, migration and assembly verification."""
from pathlib import Path
import copy
import hashlib
import json
import re
import sys
import importlib.metadata
from jsonschema import Draft202012Validator

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
EXT='lorebuddy.dnd2024'
def load(p):return json.loads(p.read_text())
def digest(b):return hashlib.sha256(b).hexdigest()
def pointer(value,path):
 for part in path.strip('/').split('/'):
  part=part.replace('~1','/').replace('~0','~');value=value[int(part)] if isinstance(value,list) else value[part]
 return value
SCHEMA=load(HERE/'schemas/lorebuddy.dnd2024.production.json')
SCENE=load(HERE/'schemas/lorebuddy.dnd2024.scene-request.json')
Draft202012Validator.check_schema(SCHEMA);Draft202012Validator.check_schema(SCENE)

def validate_corpus(c,source_check=True):
 Draft202012Validator(SCHEMA).validate(c)
 ids=[];objects={}
 for key in ['cards','spells','shared_rules','expressions','relations','clusters','evidence','mapping_rules','structured_extractions','editorial_decisions','research_receipts']:
  for x in c[key]:
   ids.append(x['id']);objects[x['id']]=x
   if key=='cards':
    for a in x['abilities']:ids.append(a['id']);objects[a['id']]=a
 assert len(ids)==len(set(ids)),'duplicate identities'
 assert sum(len(x['abilities']) for x in c['cards'])==45,'full ability set'
 sources={s['entry_id']:s for s in c['sources']};assert len(sources)==20
 objects.update(sources);objects[c['rules_context']['id']]=c['rules_context']
 ev={e['id']:e for e in c['evidence']};aliases=c['alias_registry']
 baseline_expression=load(ROOT/'experiments/full-cluster-calculator-pilot/input/knowledge.json')['expressions'][0]
 for expression in c['expressions']:
  assert expression['name']==baseline_expression['name'] and expression['ordered_operations']==baseline_expression['ordered_operations'],'unknown execution expression'
 for e in ev.values():
  assert e['source_entry_id'] in sources
  assert digest(e['text'].encode())==e['text_sha256'],'evidence digest'
  if source_check:
   raw=Path(sources[e['source_entry_id']]['note_path']).read_bytes()
   assert raw[e['range']['start']:e['range']['end']].decode()==e['text'],'evidence source range'
 for s in sources.values():
  if source_check:
   for p,h in [('note_path','note_sha256'),('raw_path','raw_sha256')]:assert digest(Path(s[p]).read_bytes())==s[h],'source bytes'
 for card in c['cards']:
  assert card['verbatim_text']==ev[card['source_evidence_id']]['text'],'whole card verbatim'
  assert card['rule_context_id']==c['rules_context']['id'],'rule edition'
  assert card['header']['source_evidence'] in {e['alias'] for e in ev.values()}
  for a in card['abilities']:
   assert a['owner_id']==card['id'],'wrong owner'
   assert a['verbatim_text']==ev[a['source_evidence_id']]['text'] and a['verbatim_text'] in card['verbatim_text'],'whole ability verbatim'
   assert a['critical_fields']==a['mechanics']['clauses'],'legacy/canonical conflict'
   for dep in a['mechanics']['dependencies']:assert dep in objects,'missing direct dependency'
   for b in a['extensions'][EXT]['source_parameter_bindings']:
    x=objects[b['extraction_id']];assert x['subject_id']==a['id']
    assert x['value']==pointer(a,b['json_pointer']),'field extraction mismatch'
   calls=a['extensions'][EXT].get('casting_calls',[])
   old=a['critical_fields']
   declared=[old['spell']] if 'spell' in old else old.get('at_will',[])+old.get('each_once_per_day',old.get('one_per_day_each',[]))
   if 'tested_spells' in old:declared=old['tested_spells']
   assert sorted(x['spell_id'] for x in calls)==sorted(aliases[x] for x in declared),'caller spell closure'
   for call in calls:
    expected=['V','S','M'] if old.get('components_override')=='none' or old.get('release_components')=='none' else ['M'] if old.get('components_override')=='no_material_only' else old.get('components_waived',[])
    assert call['components_waived']['value']==expected,'component override conflict'
    if 'save_dc' in old or 'dc' in old:assert call['save_dc']['value']==old.get('save_dc',old.get('dc')),'DC conflict'
    if 'spell_attack_bonus' in old:assert call['spell_attack_bonus']['value']==old['spell_attack_bonus'],'spell bonus conflict'
    if 'cast_level' in old:assert call['cast_level']['value']==old['cast_level'],'slot conflict'
    if 'release_parameters_from' in old:assert call['parameter_owner']['value']=='original_storing_caster','stored parameter ownership'
 for s in c['spells']:
  assert s['verbatim_text']==ev[s['source_evidence_id']]['text'],'spell verbatim'
  cc=s['extensions'][EXT]['casting_contract'];text=s['verbatim_text']
  for field,label in [('activation','施法时间'),('range','施法距离'),('duration','持续时间')]:
   m=re.search(r'\*\*'+label+r'：\*\*([^\n]+)',text);assert m
   assert cc[field]['value']==m.group(1).strip(),'spell header projection'
  assert cc['concentration']['value']==('专注' in cc['duration']['value']),'concentration projection'
  match=re.search(r'\*\*法术成分：\*\*([^\n]+)',text);letters=match.group(1).split('（')[0].split('(')[0]
  for key,letter in [('verbal','V'),('somatic','S'),('material','M')]:assert cc['components'][key]['value']==(letter in letters),'spell component projection'
 for p in c['shared_rules']:
  if source_check:assert p['content']['text'].encode()==Path(sources[p['source_entry_id']]['note_path']).read_bytes(),'public Entry incomplete'
 for rel in c['relations']:assert rel['from_id'] in objects and rel['to_id'] in objects,'relationship target'
 for cluster in c['clusters']:
  assert cluster['root_object_id'] in objects
  for dep in cluster['content_dependencies']:assert dep in objects,'cluster dependency'
 for value in aliases.values():
  for i in value if isinstance(value,list) else [value]:assert i in objects,'alias target'
 def walk(n):
  if isinstance(n,dict):
   if isinstance(n.get('binding'),dict) and 'source_note_utf8_range' in n['binding']:
    b=n['binding'];e=ev[b['source_evidence_id']]
    assert b['source_entry_id']==e['source_entry_id']
    assert b['mapping_rule_id'] in objects
    for did in b['adopted_decision_ids']:assert did in objects,'adoption target'
    r=b['source_note_utf8_range'];assert e['range']['start']<=r['start']<r['end']<=e['range']['end'],'parameter range'
    if source_check:
     by=Path(sources[b['source_entry_id']]['note_path']).read_bytes();by[r['start']:r['end']].decode()
   if n.get('json_pointer') and n.get('subject_id'):
    assert n['subject_id'] in objects
    assert pointer(objects[n['subject_id']],n['json_pointer'])==n['value']
    b=n['binding'];assert b['source_evidence_id'] in ev and b['mapping_rule_id'] in objects
   for v in n.values():walk(v)
  elif isinstance(n,list):
   for v in n:walk(v)
 walk(c)
 # Whole-owner modifier and complete mixed damage are invariant, not optional export features.
 earth=next(x for x in c['cards'] if x['id']==aliases['E']);guard=next(x for x in c['cards'] if x['id']==aliases['G'])
 assert earth['extensions'][EXT]['passive_numeric_rules'][0]['operation']['factor']==2
 fist=next(a for a in guard['abilities'] if a['title']=='拳击')
 assert fist['extensions'][EXT]['damage_components']['components']==[{'printed_fixed':11,'dice':'2d6+4','damage_type':'bludgeoning'},{'printed_fixed':7,'dice':'2d6','damage_type':'force'}],'mixed damage lost'
 return objects

def validate_questions(doc,corpus):
 Draft202012Validator(SCENE).validate(doc)
 assert len({q['id'] for q in doc['questions']})==24
 assert doc['corpus_delivery_id']==corpus['delivery_id']
 cardids={x['id'] for x in corpus['cards']}
 for q in doc['questions']:
  roster=q['scene']['roster'];events=q['scene']['event'];instanceids={r['instance_id'] for r in roster}
  assert len(instanceids)==len(roster),'duplicate scene identity'
  assert events['actor_instance_id'] in instanceids
  assert set(events['target_instance_ids'])<=instanceids
  assert all(r['prototype_id'] is None or r['prototype_id'] in cardids for r in roster)
  assert not {'expected','stages','damage_taken','core_request','core_context','selected_ability_id','expression_id'} & set(q),'answer leak'
  if events['amount_mode']=='recorded_roll':
   actor=next(r for r in roster if r['instance_id']==events['actor_instance_id'])
   card=next(c for c in corpus['cards'] if c['id']==actor['prototype_id'])
   ability=next((a for a in card['abilities'] if a['title']==events['declared_action_name']),None)
   dice=ability.get('mechanics',{}).get('damage',{}).get('amount',{}).get('dice') if ability else None
   if dice is None:
    sid=events.get('stored_spell_instance',{}).get('spell_id')
    spell=next((s for s in corpus['spells'] if s['id']==sid or events['declared_action_name'] in s['title'].split('｜')),None)
    if spell:dice=spell.get('numeric_facets',{}).get('base_dice')
   if dice:
    m=re.fullmatch(r'(\d+)d(\d+)([+-]\d+)?',dice);assert m,'unsupported fixture dice syntax'
    rolls=events.get('recorded_dice');assert isinstance(rolls,list) and len(rolls)==int(m[1]),'recorded dice count'
    assert all(type(v) is int and 1<=v<=int(m[2]) for v in rolls),'recorded dice range'
 return True

if __name__=='__main__':
 c=load(HERE/'input/knowledge.json');validate_corpus(c)
 old=load(ROOT/'experiments/full-cluster-calculator-pilot/input/knowledge.json')
 added=load(ROOT/'build/m2-seven-card-optimization-2026-10-22/current/cards.json')
 expected={x['id']:x for x in old['cards']};expected.update({added[k]['id']:added[k] for k in ['A','E','G']})
 for card in c['cards']:
  original=expected[card['id']]
  assert [a['id'] for a in card['abilities']]==[a['id'] for a in original['abilities']],'complete identity set'
  for a,b in zip(card['abilities'],original['abilities']):assert a['critical_fields']==b['critical_fields'],'inherited facts changed'
 q=load(HERE/'input/regression-questions.json');validate_questions(q,c)
 oldq=load(ROOT/'experiments/full-cluster-calculator-pilot/input/questions.json')
 for new,original in zip(q['questions'],oldq['questions']):
  for field in ['id','question','scene']:assert new[field]==original[field],'old test semantics changed'
 newpath=HERE/'input/new-questions.json'
 if newpath.exists():validate_questions(load(newpath),c)
 faults=[]
 def bad_owner(d):d['cards'][0]['abilities'][0]['owner_id']=d['cards'][1]['id']
 def bad_call(d):
  a=next(a for card in d['cards'] for a in card['abilities'] if a['extensions'][EXT].get('casting_calls'))
  a['extensions'][EXT]['casting_calls'][0]['components_waived']['value']=['M']
 for name,mut in [('drop_unused_ability',lambda d:d['cards'][0]['abilities'].pop()),('remove_shared_spell',lambda d:d['spells'].pop()),('wrong_owner',bad_owner),('duplicate_id',lambda d:d['cards'][0].update(id=d['cards'][1]['id'])),('mixed_edition',lambda d:d['cards'][0].update(rule_context_id='urn:uuid:00000000-0000-0000-0000-000000000000')),('caller_component_conflict',bad_call),('unknown_expression',lambda d:d['expressions'][0].update(name='unknown.operator')),('extraction_value_conflict',lambda d:d['structured_extractions'][0].update(value='wrong'))]:
  broken=copy.deepcopy(c);mut(broken)
  try:validate_corpus(broken,False)
  except Exception as e:faults.append({'fault':name,'blocked':True,'error':type(e).__name__,'detail':str(e)[:160]})
  else:raise AssertionError('fault escaped: '+name)
 missing=copy.deepcopy(q);del missing['questions'][0]['request_scope']
 try:validate_questions(missing,c)
 except Exception: faults.append({'fault':'missing_request_scope','blocked':True})
 else:raise AssertionError('request scope defaulted')
 for name,mut in [('invalid_recorded_die',lambda d:d['questions'][2]['scene']['event']['recorded_dice'].__setitem__(0,999)),('missing_scene_actor',lambda d:d['questions'][0]['scene']['event'].pop('actor_instance_id'))]:
  broken=copy.deepcopy(q);mut(broken)
  try:validate_questions(broken,c)
  except Exception:faults.append({'fault':name,'blocked':True})
  else:raise AssertionError('scene fault escaped: '+name)
 report={'production_status':'material_validated_candidate_not_formal_rule_approval','contract_revision':'v1-r1','schema_validator':importlib.metadata.version('jsonschema'),'counts':{'cards':8,'abilities':45,'spells':11,'shared_entries':6,'evidence':len(c['evidence']),'source_entries':len(c['sources']),'field_extractions':len(c['structured_extractions']),'regression_cases':24,'new_cases':24 if newpath.exists() else 0},'old_id_text_and_scene_semantics_preserved':True,'source_bytes_ranges_and_parameter_bindings_checked':True,'fault_injections':faults,'consumer_acceptance':'Pending','llm_calls':False,'terminal_changes':False}
 (HERE/'reports/material-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False,indent=2))
