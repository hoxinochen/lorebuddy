"""Approved bounded producer. Corpus first; no calculator or Gold dependency."""
from pathlib import Path
import copy
import hashlib
import json
import re
import sys
import uuid

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
OUT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else HERE
OLD=ROOT/'experiments/full-cluster-calculator-pilot'
BASE=ROOT/'build/m2-seven-card-optimization-2026-10-22/current'
NS=uuid.UUID('ea16c745-5c2b-4f79-a258-2c8796ac0c5f')
EXT='lorebuddy.dnd2024'
FORMAT='lorebuddy.dnd2024.rule-cluster-contract-1'
SCOPES=['damage_and_linked','full_ability','hp_settlement','source_state_change','instance_migration']
def uid(s):return 'urn:uuid:'+str(uuid.uuid5(NS,s))
def load(p):return json.loads(p.read_text())
def sha(b):return hashlib.sha256(b).hexdigest()
def save(rel,value):
 p=OUT/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')


def produce():
 old=load(OLD/'input/knowledge.json');c=copy.deepcopy(old)
 all_old=load(BASE/'cards.json');be={x['alias']:x for x in load(BASE/'evidence.json')}
 ev={e['alias']:e for e in c['evidence']};sources={s['entry_id']:s for s in c['sources']}
 cards={k:next(x for x in c['cards'] if x['id']==c['alias_registry'][k]) for k in ['SU','IN','G25','F','S']}
 for k in ['A','E','G']:
  card=copy.deepcopy(all_old[k]);cards[k]=card
  for a,e in be.items():
   if a.split('.')[0]==k:
    if a in ev:assert ev[a]==e
    ev[a]=e
  for s in load(BASE/'sources.json'):
   if s['entry_id'] in {e['source_entry_id'] for e in ev.values()}:sources[s['entry_id']]=s
 c['delivery_id']=uid('batch-1');c['format_revision']=FORMAT;c['schema_revision']='1.0.0'
 c['contract_id']='m2-rule-cluster-production-consumption-v1';c['contract_revision']='v1-r1';c['delivery_revision']=1
 c['scope'].update(cards=list(cards),complete_for='eight full MM2025 candidate cards; all 45 abilities; 11 full spells; six complete shared Entries',same_corpus_for_every_case=True)
 c['scope']['stored_spell_boundary']='Full storage eligibility retained; concrete selected spells are Fireball/Scorching Ray. Other spell libraries are not silently supplied.'
 c['evidence']=list(ev.values());c['sources']=list(sources.values());c['cards']=list(cards.values())
 # Preserve adopted storage wording and its separate research evidence.
 for d in load(BASE/'metadata/editorial-decisions.json'):
  if d.get('object')=='G':c['editorial_decisions'].append(d)
 needed={a for d in c['editorial_decisions'] for a in d.get('basis',[]) if a.startswith('R.')}
 receipts={r['alias']:r for r in c['research_receipts']}
 for r in load(BASE/'metadata/research-receipts.json'):
  if r['alias'] in needed:receipts[r['alias']]=r
 c['research_receipts']=list(receipts.values())
 c['known_issues'] += [x for x in load(BASE/'metadata/issues.json') if x.get('object')=='G']
 expr=c['expressions'][0];expr['expression_revision']=1
 aliases=c['alias_registry'];by_title={}
 identities={'SU':('medium','fiend'),'IN':('medium','fiend'),'G25':('medium','undead'),'F':('large','elemental'),'S':('large','aberration'),'A':('large','elemental'),'E':('large','elemental'),'G':('large','construct')}
 additions={('A','雷鸣猛击'):(14,'2d8+5','thunder','hit',None),('A','旋风'):(24,'4d10+2','thunder','strength_save','half'),('E','猛击'):(14,'2d8+5','bludgeoning','hit',None),('E','岩石射击'):(8,'1d6+5','bludgeoning','hit',None)}
 for k,card in cards.items():
  aliases[k]=card['id'];card['previous_candidate_revision']=card.get('candidate_revision',1);card['candidate_revision']=card['previous_candidate_revision']+1
  card['rule_edition']='2024';card['rule_context_id']=c['rules_context']['id'];card['prototype_role']='printed_template_not_live_instance'
  card['source_evidence_id']=ev[card['card_evidence']]['id'];card['verbatim_text']=ev[card['card_evidence']]['text']
  size,ctype=identities[k]
  card['extensions']={EXT:{'identity_traits':{'entity_kind':'creature','size':size,'creature_type':ctype,'source_evidence_id':ev[card['header']['source_evidence']]['id']},'content_coverage':{'card_text':'complete','all_abilities':'complete','structured_semantics':'partial_explicit','formal_rule_approval':False}}}
  for a in card['abilities']:
   by_title[k,a['title']]=a['id'];a['owner_id']=card['id'];a['source_evidence_id']=ev[a['verbatim_evidence']]['id'];a['verbatim_text']=ev[a['verbatim_evidence']]['text']
   if 'mechanics' not in a:a['mechanics']={'kind':'source_bound_candidate','clauses':copy.deepcopy(a['critical_fields']),'dependencies':[],'structured_coverage':'critical_clauses_and_complete_verbatim; remaining_semantics_uncompiled'}
   if (k,a['title']) in additions:
    n,dice,t,trigger,success=additions[k,a['title']]
    others=[]
    if a['title']=='旋风':others=[{'kind':'push','distance_ft_max':20,'when':'failed_save'},{'kind':'condition','name':'prone','when':'failed_save'}]
    if a['title']=='岩石射击':others=[{'kind':'condition','name':'prone','when':{'target_max_size':'large'}}]
    a['mechanics']['damage']={'expression_id':expr['id'],'amount':{'printed_fixed':n,'dice':dice,'selection':'use_scene_amount_mode; recorded_dice_must_not_be_rerolled'},'damage_type':t,'trigger':trigger,'save_success':success,'linked_reduction_from_damage_taken':False,'other_effects':others}
   a['extensions']={EXT:{'source_parameter_bindings':[{'json_pointer':'/critical_fields','source_evidence_id':a['source_evidence_id'],'basis':'inherited_reviewed_candidate_clause_projection_not_verbatim','adopted_decisions':a.get('field_binding',{}).get('adopted_decisions',[])}]}}
 for name,k,title in [('A.ThunderousSlam','A','雷鸣猛击'),('E.Slam','E','猛击'),('E.RockLaunch','E','岩石射击'),('G.Fist','G','拳击')]:aliases[name]=by_title[k,title]
 for k,card in cards.items():
  for a in card['abilities']:a['mechanics']['dependencies']=[aliases[x] for x in a.get('required_evidence',[])]
 # Whole-owner rule applies before defenses, even when attacking through another ability.
 siege=next(a for a in cards['E']['abilities'] if a['title']=='攻城怪物')
 cards['E']['extensions'][EXT]['passive_numeric_rules']=[{'owner_ability_id':siege['id'],'when':{'target_entity_kind_in':['object','structure']},'operation':{'kind':'multiply_damage','factor':2,'phase':'before_resistance'},'source_evidence_id':siege['source_evidence_id'],'execution_requirement':'conditional_damage_modifier'}]
 for a in cards['E']['abilities']:
  if 'damage' in a['mechanics']:a['extensions'][EXT]['owner_modifier_dependencies']=[siege['id']]
 whirl=next(a for a in cards['A']['abilities'] if a['title']=='旋风')
 whirl['extensions'][EXT]['qualification_contract']={'target_size_max':'medium','target_inside_source_space':True,'recharge':{'die':'1d6','min':4,'max':6},'source_evidence_id':whirl['source_evidence_id']}
 fist=next(a for a in cards['G']['abilities'] if a['title']=='拳击')
 fist['extensions'][EXT]['damage_components']={'same_hit':True,'components':[{'printed_fixed':11,'dice':'2d6+4','damage_type':'bludgeoning'},{'printed_fixed':7,'dice':'2d6','damage_type':'force'}],'execution_requirement':'mixed_damage','source_evidence_id':fist['source_evidence_id']}
 bound=next(a for a in cards['G']['abilities'] if a['title']=='连接')
 bound['extensions'][EXT]['transfer_contract']={'source_amulet':'this_guardian_bound_amulet','max_distance_ft':60,'fraction':{'numerator':1,'denominator':2,'rounding':'ceil'},'execution_requirement':'damage_transfer','source_evidence_id':bound['source_evidence_id']}
 store=next(a for a in cards['G']['abilities'] if a['title']=='法术储存')
 store['extensions'][EXT]['stored_spell_contract']={'capacity':1,'max_spell_level':4,'selected_spell_and_parameters_from':'runtime_stored_spell_instance','parameter_owner':'original_storing_caster','on_release':'stored_spell_lost','execution_requirement':'stored_spell_call','source_evidence_id':store['source_evidence_id']}
 for al in ['P.FIREBALL','P.RAYS']:
  target=aliases[al]
  c['relations'].append({'id':uid('stores:'+target),'kind':'stores_selected_spell','from_id':store['id'],'to_id':target,'call_mode':'stored_spell_instance_not_intrinsic_spellcasting'})

 # Minimal source-bound spell contract, not a general executable spell engine.
 mapping_names=['literal_header','component_presence','concentration_marker','candidate_clause_projection','whole_source_reference']
 methods={'literal_header':'Copy the exact stated header value; do not infer unstated mechanics.','component_presence':'Read V/S/M markers before the material-detail parentheses.','concentration_marker':'Read the explicit concentration marker in the duration header under the selected PHB2024 convention.','candidate_clause_projection':'Project inherited source-checked clauses or the explicit source-bound target/save table; retain adoption context, never treat as verbatim.','whole_source_reference':'Retain the complete source unit or its explicit reference without claiming all prose executable.'}
 mapping_rules=[{'id':uid('mapping:'+x),'name':EXT+'.'+x,'revision':1,'method':methods[x]} for x in mapping_names]
 mapping_ids={x:uid('mapping:'+x) for x in mapping_names}
 c['mapping_rules']=mapping_rules
 def fact(e,value,state='known',fragment=None,rule='whole_source_reference',decisions=None):
  text=e['text'];loc=text.find(fragment) if fragment else 0
  assert loc>=0,(e['alias'],fragment)
  start=e['range']['start']+len(text[:loc].encode());end=start+len((fragment or text).encode())
  return {'state':state,'value':value,'binding':{'source_evidence_id':e['id'],'source_entry_id':e['source_entry_id'],'source_note_utf8_range':{'start':start,'end':end},'mapping_rule_id':mapping_ids[rule],'adopted_decision_ids':decisions or []}}
 def header(e,label):
  m=re.search(r'\*\*'+re.escape(label)+r'：\*\*([^\n]+)',e['text']);assert m,(e['alias'],label)
  return m.group(1).strip(),m.group(0)
 levels={'零':0,'一':1,'二':2,'三':3,'四':4,'五':5,'六':6,'七':7,'八':8,'九':9}
 spell_targets={
  'P.DOMINATE':({'kind':'one_creature','creature_type':'humanoid','visible':True},{'kind':'saving_throw','ability':'wisdom','repeat_when':'target_takes_damage','ends_on_success':True}),
  'P.DREAM':({'kind':'known_creature','same_plane':True,'messenger':'self_or_touched_willing_creature'},{'kind':'conditional_saving_throw','ability':'wisdom','when':'nightmare_message_branch'}),
  'P.DISGUISE':({'kind':'self'},{'kind':'no_save_or_attack_stated','discovery_check':'intelligence_investigation_against_spell_dc'}),
  'P.HYPNOTIC':({'kind':'area_creatures','shape':'cube','side_ft':30,'must_see_pattern':True},{'kind':'saving_throw','ability':'wisdom','on_failure':['charmed','incapacitated','speed_zero']}),
  'P.ETHEREAL':({'kind':'self','upcast':{'8':{'max_targets':3,'willing':True,'within_ft':10},'9':{'max_targets':6,'willing':True,'within_ft':10}}},{'kind':'no_save_or_attack_stated'}),
  'P.DETECT':({'kind':'self','sensing_radius_ft':30},{'kind':'no_save_or_attack_stated'}),
  'P.THOUGHTS':({'kind':'self','modes':['sense_thoughts','read_thoughts'],'selected_creature_within_ft':30,'information_requires':'knows_language_or_telepathy'},{'kind':'conditional_saving_throw','ability':'wisdom','when':'deeper_probe','on_success':'spell_ends'}),
  'P.HAND':({'kind':'point_within_range','cannot_attack':True,'max_carried_weight_lb':10},{'kind':'no_save_or_attack_stated'}),
  'P.FIREBALL':({'kind':'point_and_all_creatures_in_area','shape':'sphere','radius_ft':20},{'kind':'saving_throw','ability':'dexterity','on_failure':'full_damage','on_success':'half_damage'}),
  'P.INVISIBILITY':({'kind':'touched_creature','base_max_targets':1,'extra_targets_per_slot_level_above_2':1},{'kind':'no_save_or_attack_stated'}),
  'P.RAYS':({'kind':'one_or_more_targets','target_entity_kind':'not_stated_in_local_text','base_rays':3},{'kind':'ranged_spell_attack','separate_attack_per_ray':True,'on_hit':'2d6_fire'})}
 for sp in c['spells']:
  e=ev[sp['alias']];activation,aq=header(e,'施法时间');distance,rq=header(e,'施法距离');components,cq=header(e,'法术成分');duration,dq=header(e,'持续时间')
  level_match=re.search(r'\*([一二三四五六七八九])环 ',e['text']);level=levels[level_match.group(1)] if level_match else 0
  assert level_match or '戏法' in e['text']
  material=re.search(r'[（(](.*)[）)]',components)
  mat=material.group(1) if material else None
  letters=components.split('（')[0].split('(')[0]
  up=re.search(r'\*\*升环施法。\*\*([^\n]+)',e['text'])
  spell_contract={'base_level':fact(e,level,rule='whole_source_reference'),
    'activation':fact(e,activation,fragment=aq,rule='literal_header'),
    'range':fact(e,distance,fragment=rq,rule='literal_header'),
    'targeting':fact(e,spell_targets[sp['alias']][0],rule='candidate_clause_projection'),
    'components':{'verbal':fact(e,'V' in letters,fragment=cq,rule='component_presence'),'somatic':fact(e,'S' in letters,fragment=cq,rule='component_presence'),'material':fact(e,'M' in letters,fragment=cq,rule='component_presence'),
     'material_detail':fact(e,mat,state='known' if mat else 'not_applicable',fragment=cq,rule='literal_header'),
     'material_consumption':fact(e,None,state='not_stated',fragment=cq),'material_value':fact(e,mat if mat and re.search('[铜银金铂].?币',mat) else None,state='known' if mat and re.search('[铜银金铂].?币',mat) else 'not_stated',fragment=cq)},
    'duration':fact(e,duration,fragment=dq,rule='literal_header'),
    'concentration':fact(e,'专注' in duration,fragment=dq,rule='concentration_marker'),
    'save_attack':fact(e,spell_targets[sp['alias']][1],rule='candidate_clause_projection'),
    'upcast':fact(e,up.group(1) if up else None,state='known' if up else 'not_stated',fragment=up.group(0) if up else None,rule='literal_header' if up else 'whole_source_reference'),
    'effects':[fact(e,{'read_from_evidence_id':e['id'],'numeric_facet_pointer':'/numeric_facets' if 'numeric_facets' in sp else None},state='partially_structured' if 'numeric_facets' in sp else 'verbatim_only')],
    'coverage':'headers_targets_saves_and_calls_structured; remaining_effect_prose_retained_uncompiled; not_full_casting_legality'}
  sp['extensions']={EXT:{'casting_contract':spell_contract}};sp['candidate_revision']=2
 # Calls are separate from spell facts and include even unsupported spells.
 for k,card in cards.items():
  for a in card['abilities']:
   calls=a['mechanics'].get('spell_calls',[])
   isstore=k=='G' and a['title']=='法术储存'
   if isstore:calls=[{'target_id':aliases[x]} for x in a['critical_fields']['tested_spells']]
   if not calls:continue
   cl=a['critical_fields'];e=ev[a['verbatim_evidence']];new=[]
   for call in calls:
    sid=call['target_id'];spell=next(s for s in c['spells'] if s['id']==sid);al=spell['alias']
    waived= ['V','S','M'] if cl.get('components_override')=='none' or cl.get('release_components')=='none' else ['M'] if cl.get('components_override')=='no_material_only' else cl.get('components_waived',[])
    perday=al in cl.get('each_once_per_day',cl.get('one_per_day_each',[]))
    unlimited=al in cl.get('at_will',[])
    decision_ids=[d['id'] for d in c['editorial_decisions'] if d.get('object')==k and (d.get('alias')=='ED.HYPNOTIC' and al=='P.HYPNOTIC' or d.get('alias')=='ED.STORE')]
    project=lambda value,state='known':fact(e,value,state=state,rule='candidate_clause_projection')
    new.append({'spell_id':sid,'mode':'stored_spell_instance' if isstore else 'intrinsic_spell_call','mapping_adoption_ids':decision_ids,
      'cast_level':project(cl.get('cast_level'),'known' if cl.get('cast_level') is not None else 'requires_runtime' if isstore else 'not_stated'),
      'parameter_owner':project('original_storing_caster' if isstore else 'this_actor_instance'),
      'casting_ability':project(cl.get('casting_ability',cl.get('ability',cl.get('release_ability_from'))),'known' if any(x in cl for x in ['casting_ability','ability','release_ability_from']) else 'not_stated'),
      'save_dc':project(cl.get('save_dc',cl.get('dc')),'known' if any(x in cl for x in ['save_dc','dc']) else 'requires_runtime' if isstore else 'not_stated'),
      'spell_attack_bonus':project(cl.get('spell_attack_bonus'),'known' if 'spell_attack_bonus' in cl else 'requires_runtime' if isstore else 'not_stated'),
      'components_waived':project(waived),
      'concentration_override':project(None,'not_stated'),
      'target_override':project(cl.get('local_target_override',{}).get(al),'known' if al in cl.get('local_target_override',{}) else 'not_stated'),
      'availability':project({'kind':'stored_instance','capacity':1} if isstore else {'kind':'each_once_per_day','recovery_evidence_id':ev['M.USAGE']['id']} if perday else {'kind':'at_will'} if unlimited else None,'requires_runtime' if isstore else 'known' if perday or unlimited else 'not_stated'),
      'uncompiled_qualifications':project({x:cl[x] for x in ['storage_requires','cast_distance_ft','cast_on_guardian','max_spell_level','on_store','on_new_store','on_release','visible_across_planes','cross_plane_interaction'] if x in cl})})
   a['extensions'][EXT]['casting_calls']=new
 allshared=[x['id'] for x in c['shared_rules']]
 existing={x['root_object_id'] for x in c['clusters']}
 for k in ['A','E','G']:
  card=cards[k];deps=allshared+[card['id']]
  if k=='G':deps += [aliases['P.FIREBALL'],aliases['P.RAYS']]
  c['clusters'].append({'id':uid('cluster:'+card['id']),'cluster_revision':1,'title':card['title']+'完整规则簇','root_object_id':card['id'],'content_dependencies':deps,'coverage':'complete_card_all_abilities_direct_dependencies','review_status':'candidate','uncompiled_semantics':'retained_not_silently_executed'})
 for cluster in c['clusters']:cluster['cluster_revision']=cluster.get('cluster_revision',1)+1 if cluster['root_object_id'] in existing else 1
 c['alias_records']=[{'alias':alias,'language':'zxx','target_ids':value if isinstance(value,list) else [value],'role':'legacy_symbol_not_identity'} for alias,value in aliases.items()]
 c['structured_extractions']=[]
 decision_ids={d['alias']:d['id'] for d in c['editorial_decisions']}
 def leaves(value,path=''):
  if isinstance(value,dict) and value:
   for key,v in value.items():yield from leaves(v,path+'/'+key.replace('~','~0').replace('/','~1'))
  elif isinstance(value,list) and value:
   for idx,v in enumerate(value):yield from leaves(v,path+'/'+str(idx))
  else:yield path,value
 def adoption_for_field(card,ability,pointer,value):
  symbol=next(k for k,v in cards.items() if v['id']==card['id'])
  top=pointer.removeprefix('/critical_fields/').split('/')[0]
  result=[]
  for d in c['editorial_decisions']:
   if d.get('object')!=symbol:continue
   if d['alias']=='ED.HYPNOTIC' and value=='P.HYPNOTIC':result.append(d['id'])
   if d['alias']=='ED.STORE' and ability['title']=='法术储存' and top in d['fields']:result.append(d['id'])
   if d['alias']=='ED.SLAAD' and ability['title']=='施法' and top in ['dc','spell_attack_bonus']:result.append(d['id'])
  return result
 for card in c['cards']:
  for a in card['abilities']:
   bindings=[]
   for pointer,value in leaves(a['critical_fields'],'/critical_fields'):
    record={'id':uid('extraction:'+a['id']+pointer),'revision':1,'subject_id':a['id'],'json_pointer':pointer,'value':value,'review_status':'candidate','binding':fact(ev[a['verbatim_evidence']],value,rule='candidate_clause_projection',decisions=adoption_for_field(card,a,pointer,value))['binding']}
    c['structured_extractions'].append(record);bindings.append({'json_pointer':pointer,'extraction_id':record['id']})
   a['extensions'][EXT]['source_parameter_bindings']=bindings
 c['compatibility']={'previous_format':'research-full-cluster-1','current_format':FORMAT,'old_reader':'calculator-corpus-1','status':'explicit_consumer_adaptation_required','legacy_clauses':'derived_compatibility_projection; must_equal_canonical_fields','request_scope':'top_level_case_field; no_question_id_table_in_production_API'}
 c['delivery_policy']={'kind':'internal_candidate_not_Package_release','access':'existing_authorized_local_research_only','rights':'unknown','formal_rule_approval':False,'consumer_acceptance':'pending'}
 save('input/knowledge.json',c)
 # Text views are generated, never manually maintained as a second source.
 view='# 八对象完整规则簇：合同v1首批\n\n候选内容；原文与结构化采用分开。所有测试共用完整语料。\n'
 for card in c['cards']:
  view+=f"\n## {card['title']}\n\nID：{card['id']}\n\n### 原卡全文\n\n{card['verbatim_text']}\n\n### 全部能力与结构化采用\n\n"
  for a in card['abilities']:
   view+=f"#### {a['title']}\n\n原文：\n\n{a['verbatim_text']}\n\n```json\n{json.dumps({'id':a['id'],'owner_id':a['owner_id'],'critical_fields':a['critical_fields'],'mechanics':a['mechanics'],'extensions':a['extensions']},ensure_ascii=False,indent=2)}\n```\n\n采用说明：{a['editorial_explanation']}\n"
  view+='\n```json\n'+json.dumps(card['extensions'],ensure_ascii=False,indent=2)+'\n```\n'
 for spell in c['spells']:
  view+=f"\n## 法术：{spell['title']}\n\n{spell['verbatim_text']}\n\n```json\n{json.dumps(spell['extensions'],ensure_ascii=False,indent=2)}\n```\n"
 for pub in c['shared_rules']:view+=f"\n## 公共规则完整Entry：{pub['title']}\n\n{pub['content']['text']}\n"
 view+='\n## 采用决定与已知问题\n\n```json\n'+json.dumps({'editorial_decisions':c['editorial_decisions'],'known_issues':c['known_issues']},ensure_ascii=False,indent=2)+'\n```\n'
 (OUT/'input/完整规则簇.md').write_text(view)
 intake={'contract_id':c['contract_id'],'contract_revision':c['contract_revision'],'delivery_id':c['delivery_id'],'format_revision':FORMAT,'objects':[{'alias':k,'id':v['id'],'title':v['title'],'ability_ids':[a['id'] for a in v['abilities']],'source_evidence_id':v['source_evidence_id']} for k,v in cards.items()],
   'sources':[{'entry_id':s['entry_id'],'artifact_id':s['artifact_id'],'raw_path':s['raw_path'],'raw_sha256':s['raw_sha256'],'note_path':s['note_path'],'note_sha256':s['note_sha256']} for s in c['sources']],
   'source_counts':{'cards':len(cards),'abilities':sum(len(x['abilities']) for x in cards.values()),'spells':len(c['spells']),'shared_entries':len(c['shared_rules']),'evidence':len(c['evidence']),'source_entries':len(c['sources'])},
   'inputs':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p.read_bytes())} for p in [OLD/'input/knowledge.json',OLD/'input/questions.json',BASE/'cards.json',BASE/'evidence.json',BASE/'sources.json',BASE/'metadata/editorial-decisions.json',BASE/'metadata/research-receipts.json',BASE/'metadata/issues.json']]}
 intake['toolchain']={'python':sys.version.split()[0],'producers':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p.read_bytes())} for p in [HERE/'produce.py',HERE/'make_schemas.py',HERE/'prepare_questions.py',HERE/'validate.py']]}
 save('intake.json',intake)
 # Regressions: copy questions and scenes exactly; only add the explicit request scope.
 scopepath=HERE/'fixtures/request-scopes-source.json'
 scopebytes=scopepath.read_bytes();scopes=load(scopepath)
 assert scopes['revision']=='explicit-scope-adapter-2'
 qold=load(OLD/'input/questions.json');scopeby={s['question_id']:s for s in scopes['cases']}
 regression={'corpus_delivery_id':c['delivery_id'],'format_revision':'lorebuddy.dnd2024.scene-request-1','instructions':'Use the same full knowledge.json. request_scope is explicit; the producer does not supply bindings or numeric answers.','questions':[]}
 for q in qold['questions']:
  assert scopeby[q['id']]['request_scope'] in SCOPES
  v=copy.deepcopy(q);v['request_scope']=scopeby[q['id']]['request_scope'];v['delivery']='input/knowledge.json in full';regression['questions'].append(v)
 save('input/regression-questions.json',regression)
 save('migration.json',{'source_questions':str((OLD/'input/questions.json').relative_to(ROOT)),'source_questions_sha256':sha((OLD/'input/questions.json').read_bytes()),'scope_source_path':str(scopepath),'scope_source_origin':str(ROOT.parent/'DND Terminal/tests/fixtures/calculator/full-cluster/request-scopes.json'),'scope_source_sha256':sha(scopebytes),'scope_source_revision':scopes['revision'],'changed_fields':['top_level corpus_delivery_id/instructions/format_revision','per_case request_scope','per_case delivery_label'],'preserved_fields':['id','question','scene'],'data_format_requires_new_reader':True,'terminal_code_modified':False})
 save('reports/issues.json',[{'id':uid('issue:consumer-adaptation'),'status':'pending_consumer_action','owner':'Terminal','kind':'format_compatibility','object_id':c['delivery_id'],'finding':'New explicit format, canonical casting fields, owner modifiers and mixed components need consumer adaptation; no 48-case pass is claimed.'},{'id':uid('issue:casting-coverage'),'status':'explicitly_uncompiled','owner':'Buddy/consumer_contract','kind':'coverage','finding':'Spell headers, targets, saves and caller overrides are structured. Remaining effect prose is retained explicitly uncompiled; no full casting legality claim.'}])
 print(json.dumps(intake['source_counts'],ensure_ascii=False))
 return c
if __name__=='__main__':produce()
