"""New scenes and evaluator-only Gold after complete corpus source validation."""
from pathlib import Path
import copy
import json
import hashlib
from validate import validate_corpus, validate_questions
from produce import ROOT,OUT,EXT,SCOPES,save,load

c=load(OUT/'input/knowledge.json');validate_corpus(c)
reg=load(OUT/'input/regression-questions.json')
by={k:next(x for x in c['cards'] if x['id']==c['alias_registry'][k]) for k in ['SU','IN','G25','F','S','A','E','G']}
roster=copy.deepcopy(reg['questions'][8]['scene']['roster'])
for instance,k in [('air-A','A'),('earth-A','E'),('guardian-A','G')]:
 card=by[k];roster.append({'instance_id':instance,'prototype_id':card['id'],'current_hp':card['header']['hp'],'max_hp':card['header']['hp'],'position_plane':'material','can_see_and_be_seen':True,'can_speak_and_gesture':k!='G','resources':'all_printed_uses_available','sourced_effects':[]})
for r in roster:r['entity_kind']='creature'
questions=[];gold=[]

def val(a,r,v,d,linked=None):return {'semantic_status':'numeric_result','stages':{'after_ability':a,'after_resistance':r,'after_vulnerability':v},'damage_taken':d,'linked_reduction':linked}
def add(n,text,actor,action,target,expected,*,dice=None,facts=None,scope='damage_and_linked',inside=True,pending=()):
 scene={'roster':copy.deepcopy(roster),'event':{'actor_instance_id':actor,'declared_action_name':action,'target_instance_ids':[target],'amount_mode':'recorded_roll' if dice is not None else 'printed_fixed','attack_outcome':'hit','save_outcome':None,'distance_ft':5,'same_plane':True,'actor_can_see_target':True,'target_can_see_actor':True,'other_damage_adjustments':'none','defense_effect_inventory':'complete_unless_explicitly_unknown'}}
 if dice is not None:scene['event']['recorded_dice']=dice
 if facts:scene['event'].update(facts)
 q={'id':f'N{n:02}','question':text,'request_scope':scope,'scene':scene,'delivery':'input/knowledge.json in full'}
 questions.append(q)
 actorcard=next(card for card in c['cards'] if card['id']==next(r['prototype_id'] for r in scene['roster'] if r['instance_id']==actor))
 a=next((a for a in actorcard['abilities'] if a['title']==action),None)
 source_ids=[actorcard['source_evidence_id']]+([a['source_evidence_id']] if a else [])
 if action=='火球术':source_ids.append(next(s['source_evidence_id'] for s in c['spells'] if s['alias']=='P.FIREBALL'))
 gold.append({'id':q['id'],'category':'within_numeric_core_if_data_binding_succeeds' if inside else 'outside_core_or_missing_input','expected':expected,'pending_non_numeric_effects':list(pending),'source_evidence_ids':source_ids,'review':'root_AI_source_checked; not_independent_human_approval'})
 return scene

# Literal expected numbers below were checked against source damage, defenses and rounding;
# no consumer implementation or core output is consulted to prepare these values.
add(1,'气元素以雷鸣猛击命中土元素，使用卡载固定值，双方没有额外修正。只求该次伤害。','air-A','雷鸣猛击','earth-A',val(14,14,28,28))
add(2,'气元素的雷鸣猛击命中土元素；2d8已记录1、2，使用能力自己的加值。只求该次伤害。','air-A','雷鸣猛击','earth-A',val(8,8,16,16),dice=[1,2])
add(3,'气元素以雷鸣猛击命中另一气元素，采用固定值，无额外修正。只求伤害。','air-A','雷鸣猛击','air-A',val(14,14,14,0))
# Distinct source/target identity, not a self-attack disguised as another creature.
questions[-1]['scene']['roster'].append({**copy.deepcopy(next(r for r in roster if r['instance_id']=='air-A')),'instance_id':'air-B'})
questions[-1]['scene']['event']['target_instance_ids']=['air-B']
add(4,'气元素以雷鸣猛击命中2025幽魂，采用固定值，只求该次伤害。','air-A','雷鸣猛击','ghost-A',val(14,7,7,7))
add(5,'气元素以雷鸣猛击命中盾卫，采用固定值；盾卫没有额外防御。只求伤害，不结算后续回合。','air-A','雷鸣猛击','guardian-A',val(14,14,14,14))
add(6,'土元素以猛击命中火元素，采用固定值。目标是元素生物，非物件或建筑。只求该次伤害。','earth-A','猛击','fire-A',val(14,7,7,7))
add(7,'土元素以猛击命中气元素，采用固定值，双方无额外修正。只求该次伤害。','earth-A','猛击','air-A',val(14,7,7,7))
add(8,'土元素以猛击命中盾卫；本题盾卫明确为构装生物而非物件。采用固定值，只求该次伤害。','earth-A','猛击','guardian-A',val(14,14,14,14))
add(9,'土元素以猛击命中2025幽魂；2d8已记录8、7，使用能力自己的加值，求伤害。','earth-A','猛击','ghost-A',val(20,10,10,10),dice=[8,7])
add(10,'土元素以岩石射击命中火元素，采用固定值。只求命中伤害，不应用倒地或其他状态。','earth-A','岩石射击','fire-A',val(8,4,4,4),pending=['条件性倒地条款及目标状态免疫仍保留，不声称状态已应用'])
add(11,'土元素以岩石射击命中盾卫，1d6已记录5，使用能力自己的加值。只求伤害，不应用倒地。','earth-A','岩石射击','guardian-A',val(10,10,10,10),dice=[5],pending=['条件性倒地未应用'])
add(12,'2025幽魂以凋零之触命中盾卫；采用固定值，只求本次伤害。','ghost-A','凋零之触','guardian-A',val(19,19,19,19))
add(13,'火元素以燃烧攻击命中盾卫，采用固定值。只求这次命中的伤害，不推进燃烧危害。','fire-A','燃烧','guardian-A',val(10,10,10,10),pending=['点燃与后续燃烧危害未应用'])
add(14,'魅魔以魔性之触命中盾卫，采用固定值，无其他修正。只求伤害。','succubus-A','魔性之触','guardian-A',val(16,16,16,16))
add(15,'梦魔以毁梦之触命中盾卫，采用固定值。只求命中伤害，不处理诅咒或短休。','incubus-A','毁梦之触','guardian-A',val(15,15,15,15),pending=['本梦魔来源的诅咒未应用'])
add(16,'史拉绿蟾以混沌法杖命中盾卫，采用固定值。状态骰另已记录为1，只求伤害，不应用状态。','slaad-A','混沌法杖','guardian-A',val(8,8,8,8),facts={'condition_die_d4':1},pending=['随机状态条款及目标免疫仍保留，未应用'])
s=add(17,'土元素以猛击命中冒险者，目标是类人生物；目标两个独立来源的钝击抗性及钝击易伤均确认适用。采用固定值，只求伤害。','earth-A','猛击','adventurer-A',val(14,7,14,14))
pc=next(r for r in s['roster'] if r['instance_id']=='adventurer-A')
pc['sourced_effects']=[{'effect_instance_id':f'bludgeon-{i}','source_instance_id':f'source-{i}','kind':kind,'damage_type':'bludgeoning','applicability':'confirmed_for_this_event','active':True} for i,kind in enumerate(['damage_resistance','damage_resistance','damage_vulnerability'])]
add(18,'史拉绿蟾合法使用三环火球术，盾卫确认在区域内且敏捷豁免失败。8d6已记录6、6、5、4、4、3、2、1；只求盾卫伤害，不结算其他对象。','slaad-A','火球术','guardian-A',val(31,31,31,31),dice=[6,6,5,4,4,3,2,1],facts={'attack_outcome':None,'save_outcome':'failure','spell_level':3,'spell_target_in_area':True,'verbal_somatic_available':True,'daily_use_available':True},pending=['区域内其他对象及点燃未执行'])
add(19,'盾卫以拳击命中火元素，采用卡载固定值。要求结算本次命中的全部伤害分量，不允许只取其中一种。','guardian-A','拳击','fire-A',{'semantic_status':'outside_core','reason':'mixed_damage','rule_answer':{'bludgeoning_after_resistance':5,'force':7,'total_damage':12},'require':'明确保留两分量并说明当前单类型核心未完成整体请求'},inside=False)
s=add(20,'土元素以猛击命中一段建筑墙体，采用固定值；墙体防御已完整确认，无抗性、易伤或免疫。要求结算包括攻城怪物在内的伤害。','earth-A','猛击','adventurer-A',{'semantic_status':'outside_core','reason':'conditional_owner_damage_modifier','rule_answer':{'damage_taken':28},'require':'识别物件/建筑双倍条款；不得按普通生物14返回成功'},inside=False)
s['roster'].append({'instance_id':'wall-A','prototype_id':None,'entity_kind':'structure','current_hp':100,'max_hp':100,'intrinsic_defenses':{'damage_resistance':[],'damage_vulnerability':[],'damage_immunity':[],'condition_immunity':[]},'sourced_effects':[],'defense_inventory_complete':True})
s['event']['target_instance_ids']=['wall-A']
s=add(21,'冒险者佩戴本盾卫绑定的命令护符，双方距离30尺；本次转移前伤害已确认13，所有防御已处理且无其他修正，双方尚未扣HP。要求完整应用连接转伤并更新双方HP。','guardian-A','连接','adventurer-A',{'semantic_status':'outside_core','reason':'damage_transfer_and_hp_write','rule_answer':{'wearer_damage':6,'guardian_transferred_damage':7},'require':'识别本护符、本盾卫与向上取整；不声称HP已写入'},facts={'distance_ft':30,'incoming_damage_before_transfer_after_defenses':13,'wearer_amulet_instance_id':'amulet-A','guardian_bound_amulet_instance_id':'amulet-A'},scope='full_ability',inside=False)
next(r for r in s['roster'] if r['instance_id']=='guardian-A')['bound_amulet_instance_id']='amulet-A'
s=add(22,'盾卫已合法储存原施法者的三环火球术；其释放机会与目标合法性均已确认。要求用原施法者DC17释放，并在释放后清空储法槽。目标冒险者敏捷豁免成功，无额外防御。8d6已记录6、6、5、4、4、3、2、1。','guardian-A','法术储存','adventurer-A',{'semantic_status':'outside_core','reason':'stored_spell_call_and_resource_state','rule_answer':{'damage_taken':15,'save_dc':17,'slot_empty_after_release':True},'require':'调用必须来自储存实例而非盾卫固有施法；保留原施法者参数且不声称资源已更新'},dice=[6,6,5,4,4,3,2,1],facts={'attack_outcome':None,'save_outcome':'success','release_opportunity_confirmed':True,'spell_target_in_area':True,'stored_spell_instance':{'id':'stored-A','spell_id':c['alias_registry']['P.FIREBALL'],'cast_level':3,'original_caster_instance_id':'original-caster-X','save_dc':17,'spell_attack_bonus':9,'components_waived':['V','S','M']}},scope='full_ability',inside=False)
# A stored instance refers to an external original caster receipt; it is not a new monster card.
s=add(23,'有人要求气元素用雷鸣猛击结算一次命中，但现场目标距其11尺，没有延长触及的效果。请按本卡触及与现场信息判断能否继续结算。','air-A','雷鸣猛击','adventurer-A',{'semantic_status':'invalid','reason':'target_out_of_range','required_issue_codes':['target_out_of_range'],'forbid_numeric_result':True},facts={'distance_ft':11},inside=False)
s=add(24,'土元素猛击已命中盾卫，采用固定值；盾卫现场新增防御清单尚未核对完整。要求结算最终伤害，不能把未确认清单当没有修正。','earth-A','猛击','guardian-A',{'semantic_status':'needs_input','reason':'defense_coverage_unknown','required_issue_codes':['defense_coverage_unknown'],'forbid_numeric_result':True},facts={'defense_effect_inventory':'unknown'},inside=False)
next(r for r in s['roster'] if r['instance_id']=='guardian-A')['defense_inventory_complete']=False
new={'corpus_delivery_id':c['delivery_id'],'format_revision':'lorebuddy.dnd2024.scene-request-1','instructions':'Load full knowledge.json; request_scope is the only explicit request intent. Resolve owners, facts and formulas from corpus and scene. Do not read evaluator or prepare_questions.py. Preserve unexecuted effects.','questions':questions}
validate_questions(new,c);save('input/new-questions.json',new)
# Gold saved only after corpus validation and complete question construction.
oldgold=load(ROOT/'experiments/full-cluster-calculator-pilot/evaluator/gold.json')
save('evaluator/regression-gold.json',oldgold)
save('evaluator/new-gold.json',{'review':'root_AI_against_frozen_sources; not_independent_human_approval','fixed_before_consumer_execution':True,'cases':gold})
save('evaluator/results-template.json',{'status':'Not Run','consumer_acceptance':'Pending','regression_count':24,'new_count':24,'cases':[{'id':q['id'],'actual':None,'read_binding_score':None,'numeric_score':None,'scope_score':None,'elapsed_ms':None} for q in reg['questions']+questions]})
text='# 合同v1首批：24题回归与24道新题\n\n所有题共用完整knowledge.json。现场完整事实见对应JSON；此文件不含评分答案。\n'
for title,qs in [('回归24题',reg['questions']),('新增24题',questions)]:
 text+='\n## '+title+'\n'
 for q in qs:text+=f"\n### {q['id']}\n\n请求范围：`{q['request_scope']}`\n\n{q['question']}\n"
(OUT/'input/测试题.md').write_text(text)
save('reports/question-production.json',{'corpus_prevalidated_before_questions':True,'new_questions':24,'new_numeric_compatible':18,'new_boundary':6,'regression_questions':24,'old_gold_sha256':hashlib.sha256((ROOT/'experiments/full-cluster-calculator-pilot/evaluator/gold.json').read_bytes()).hexdigest(),'calculator_called_to_prepare_gold':False,'llm_calls':False,'consumer_execution':'Not Run'})
print('Prepared 24 new questions (18 numeric/6 boundary), preserved 24 regression questions and original Gold.')
