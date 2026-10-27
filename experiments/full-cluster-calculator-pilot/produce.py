"""Produce a bounded, full-content candidate corpus BEFORE constructing questions.
No calculator import, execution, per-question request/context, or LLM invocation.
"""
from pathlib import Path
import copy
import hashlib
import json
import re
import uuid

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
CROSS = ROOT/'build/m2-cross-relations-6cards-2026-10-22'
SEVEN = ROOT/'build/m2-seven-card-optimization-2026-10-22/current'
NS = uuid.UUID('26eb0c66-b1e5-488b-9ddf-28350128ffbd')
uid = lambda name: 'urn:uuid:'+str(uuid.uuid5(NS,name))
sha = lambda data: hashlib.sha256(data).hexdigest()
def load(p): return json.loads(p.read_text())
def save(rel,data):
    p=OUT/rel; p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')

def prepare_corpus():
    cards={}; evidence={}; sources={}; receipts={}; decisions=[]; issues=[]
    for base, selected in [(CROSS,['SU','IN','G25']),(SEVEN,['F','S'])]:
        old=load(base/'cards.json')
        cards.update({k:copy.deepcopy(old[k]) for k in selected})
        for e in load(base/'evidence.json'):
            if e['alias'].startswith(('P.','M.')) or e['alias'].split('.')[0] in selected:
                if e['alias'] in evidence: assert evidence[e['alias']]==e
                evidence[e['alias']]=e
        for s in load(base/'sources.json'):
            if s['entry_id'] in {e['source_entry_id'] for e in evidence.values()}:
                if s['entry_id'] in sources: assert sources[s['entry_id']]==s
                sources[s['entry_id']]=s
        decisions += [d for d in load(base/'metadata/editorial-decisions.json') if d.get('object') in selected]
        for d in load(base/'metadata/research-receipts.json'): receipts[d['alias']]=d
        for d in load(base/'metadata/issues.json'):
            subjects=d.get('subject',d.get('object',[])); subjects=[subjects] if isinstance(subjects,str) else subjects
            if any(x in selected for x in subjects): issues.append(d)
    # Keep only receipts used by retained editorial decisions or source issues.
    used_receipts={r for d in decisions+issues for r in d.get('basis',[]) if r.startswith('R.')}
    receipts={k:v for k,v in receipts.items() if k in used_receipts}
    source_checks=[]
    for s in sources.values():
        for path,digest in [('note_path','note_sha256'),('raw_path','raw_sha256')]:
            assert sha(Path(s[path]).read_bytes())==s[digest],s[path]
        source_checks.append({'entry_id':s['entry_id'],'note_and_raw_match_existing_receipt':True})
    for e in evidence.values():
        s=sources[e['source_entry_id']]; raw=Path(s['note_path']).read_bytes()
        assert raw[e['range']['start']:e['range']['end']].decode()==e['text'],e['alias']
        assert sha(e['text'].encode())==e['text_sha256']

    spell_aliases=['P.DOMINATE','P.DREAM','P.DISGUISE','P.HYPNOTIC','P.ETHEREAL','P.DETECT','P.THOUGHTS','P.HAND','P.FIREBALL','P.INVISIBILITY']
    # All non-spell shared source Entries are retained in full, independently of questions.
    shared_sources={e['source_entry_id'] for a,e in evidence.items() if a.startswith(('P.','M.')) and a not in spell_aliases+['P.RAYS']}
    public=[]
    for sid in sorted(shared_sources):
        s=sources[sid]; b=Path(s['note_path']).read_bytes()
        public.append({'id':uid('public-module:'+sid),'kind':'shared_rule_entry','title':Path(s['note_path']).stem,
                       'source_entry_id':sid,'content':{'format':'m1_published_markdown_utf8','text':b.decode()},
                       'coverage':{'start':0,'end':len(b),'basis':'whole_note_utf8','complete_entry':True},
                       'evidence_ids':[e['id'] for e in evidence.values() if e['source_entry_id']==sid]})
    # P.RAYS is not a call from these five cards; retain its full spell as unused contextual material.
    # It was part of the inherited common corpus, and is never selected per question.
    spell_aliases += ['P.RAYS']
    spells=[]
    for a in spell_aliases:
        e=evidence[a]
        spells.append({'id':uid('spell:'+e['id']),'kind':'spell','alias':a,'title':next((line.strip('# ') for line in e['text'].splitlines() if line.startswith('#### ')),a),
                       'source_evidence_id':e['id'],'verbatim_text':e['text'],'review_status':'candidate',
                       'rule_context':'PHB2024','structured_mechanics_status':'verbatim_complete_structured_facets_below_are_partial_not_silent_defaults'})
    shared_id={e['alias']:p['id'] for p in public for e in evidence.values() if e['source_entry_id']==p['source_entry_id']}
    spell_id={s['alias']:s['id'] for s in spells}
    by_title={(k,a['title']):a['id'] for k,c in cards.items() for a in c['abilities']}
    aliases={k:c['id'] for k,c in cards.items()} | shared_id | spell_id
    aliases.update({'G25.WitheringTouch':by_title['G25','凋零之触'], 'F.Burn':by_title['F','燃烧'], 'S.ChaosStaff':by_title['S','混沌法杖'],
                    'FiendishTouch':by_title['SU','魔性之触'], 'Charm_or_DrainingKiss':[by_title['SU','魅惑'],by_title['SU','汲命之吻']], 'RestlessTouch':by_title['IN','毁梦之触']})

    # This is a proposed data expression, not executable engine code or an accepted Schema.
    expressions=[{'id':uid('expression:single-damage'),'name':'dnd2024.single_damage',
                  'inputs':['raw_damage_from_selected_amount','save_outcome_if_rule_requires','confirmed_target_defenses','confirmed_eligibility','other_adjustment_coverage'],
                  'ordered_operations':[{'op':'ability_success_branch','rounding':'floor_if_halved'}, {'op':'matching_resistance_once','rounding':'floor'}, {'op':'matching_vulnerability_once','multiplier':2}, {'op':'matching_immunity_numeric_gate','value':0}],
                  'outputs':['damage_taken','linked_reduction_if_declared'],
                  'not_equivalent_to':['hit_point_loss','action_legality','condition_application','full_action_completion'],
                  'source_evidence_ids':[evidence[x]['id'] for x in ['P.ROUND','P.RESISTANCE','P.IMMUNITY']]}]
    numeric={
      ('SU','魔性之触'):(16,'2d10+5','psychic','hit',None),
      ('SU','汲命之吻'):(13,'3d8','psychic','constitution_save','half'),
      ('IN','毁梦之触'):(15,'3d6+5','psychic','hit',None),
      ('G25','虚体移动'):(5,None,'force','own_turn_end_inside_object',None),
      ('G25','凋零之触'):(19,'3d10+3','necrotic','hit',None),
      ('G25','恐惧面容'):(10,'2d6+3','psychic','wisdom_save','zero'),
      ('F','火焰灵光'):(5,'1d10','fire','source_turn_end',None),
      ('F','火焰形态'):(5,'1d10','fire','first_entry_per_target_per_turn',None),
      ('F','水体易感'):(3,'1d6','cold','water_exposure_each_unit',None),
      ('F','燃烧'):(10,'2d6+3','fire','hit',None),
      ('S','混沌法杖'):(8,'1d8+4','force','hit',None),
    }
    effect_extras={('SU','汲命之吻'):[{'kind':'maximum_hp_reduction','amount_from':'damage_taken','recovery_dependency':shared_id['P.LONG_REST']}],
      ('IN','毁梦之触'):[{'kind':'sourced_curse','duration_hours':24,'ends_early':'this_source_dies','prevents':'benefit_from_short_rest'}],
      ('G25','恐惧面容'):[{'kind':'condition','name':'frightened','when':'failed_save','ends':'this_source_next_turn_start'},{'kind':'source_specific_immunity','when':'successful_save','duration_hours':24}],
      ('F','火焰灵光'):[{'kind':'ignite','targets':['creatures','flammable_objects'],'dependency':shared_id['P.BURNING']}],
      ('F','燃烧'):[{'kind':'ignite','targets':['creatures','flammable_objects'],'dependency':shared_id['P.BURNING']}],
      ('S','混沌法杖'):[{'kind':'sourced_condition','choose_by_d4':{'1':'charmed','2':'frightened','3':'poisoned','4':'incapacitated'},'ends':'this_source_next_turn_start'}]}
    for k,c in cards.items():
        c['previous_candidate_revision']=c.get('candidate_revision',1)
        c['candidate_revision']=c['previous_candidate_revision']+1
        c['rule_edition']='2024'; c['rule_context_id']=uid('ruleset:dnd2024-mm2025-phb2024')
        c['prototype_role']='printed_template_not_live_instance'
        c['verbatim_text']=evidence[c['card_evidence']]['text']
        c['source_evidence_id']=evidence[c['card_evidence']]['id']
        for a in c['abilities']:
            a['owner_id']=c['id']; a['verbatim_text']=evidence[a['verbatim_evidence']]['text'];a['source_evidence_id']=evidence[a['verbatim_evidence']]['id']
            a['mechanics']={'kind':'source_bound_candidate','clauses':copy.deepcopy(a['critical_fields']),
                            'dependencies':[aliases[x] for x in a.get('required_evidence',[])],
                            'structured_coverage':'critical_clauses_plus_complete_verbatim; not_every_semantic_clause_compiled'}
            if (k,a['title']) in numeric:
                fixed,dice,dtype,trigger,on_success=numeric[k,a['title']]
                a['mechanics']['damage']={'expression_id':expressions[0]['id'],'amount':{'printed_fixed':fixed,'dice':dice,'selection':'use_scene_amount_mode; recorded_dice_must_not_be_rerolled'},
                    'damage_type':dtype,'trigger':trigger,'save_success':on_success,'linked_reduction_from_damage_taken':k=='SU' and a['title']=='汲命之吻',
                    'other_effects':effect_extras.get((k,a['title']),[])}
            if (k,a['title'])==('IN','噩梦'):
                a['mechanics']['branches']=[{'when':{'save':'failure','target_current_hp_lte':20},'effect':{'kind':'unconscious','hours':1,'early_end':['damage','another_creature_within_5ft_uses_action_to_wake']}},
                    {'when':{'save':'failure','target_current_hp_gt':20},'effect':{'kind':'damage','amount':{'printed_fixed':18,'dice':'4d8'},'damage_type':'psychic'}},
                    {'when':{'save':'success'},'effect':{'kind':'none_stated'}}]
                a['mechanics']['branch_selection_time']='before_applying_this_effect; no_reentry_after_damage'
    # Direct spell callers always point to independent spell owners; overrides stay on the caller.
    calls=[('SU','魅惑',['P.DOMINATE']),('IN','施法',['P.DISGUISE','P.ETHEREAL','P.DREAM','P.HYPNOTIC']),('G25','以太化',['P.ETHEREAL']),('S','施法',['P.DETECT','P.THOUGHTS','P.HAND','P.FIREBALL','P.INVISIBILITY'])]
    relations=[]
    for k,title,targets in calls:
        ability=next(a for a in cards[k]['abilities'] if a['title']==title)
        ability['mechanics']['spell_calls']=[{'target_id':spell_id[t],'caller_overrides_from':'/critical_fields','source_evidence_id':ability['source_evidence_id']} for t in targets]
        for t in targets:relations.append({'id':uid('calls:'+ability['id']+spell_id[t]),'kind':'calls_spell','from_id':ability['id'],'to_id':spell_id[t]})
    for k,t in [('SU','IN'),('IN','SU')]:
        relations.append({'id':uid('replace:'+k),'kind':'replaces_game_statistics_on_long_rest','from_id':cards[k]['abilities'][0]['id'],'to_id':cards[t]['id'],'runtime_migration_algorithm':'unknown_not_defined'})
    fireball=next(s for s in spells if s['alias']=='P.FIREBALL')
    fireball['numeric_facets']={'expression_id':expressions[0]['id'],'base_dice':'8d6','damage_type':'fire','save':'dexterity','on_success':'half','upcast':{'base_level':3,'dice_added_per_level':'1d6'},'area':{'shape':'sphere','radius_ft':20},'ignites':'unworn_uncarried_flammable_objects'}
    dream=next(s for s in spells if s['alias']=='P.DREAM')
    dream['numeric_facets']={'damage_dice':'3d6','damage_type':'psychic','trigger':'target_wakes_after_failed_wisdom_save_in_nightmare_branch','not_immediate_damage':True}
    eth=next(s for s in spells if s['alias']=='P.ETHEREAL')
    eth['numeric_facets']={'displacement_damage':{'kind':'multiply','factor':2,'input':'displacement_distance_ft','damage_type':'force','trigger':'spell_end_in_occupied_space'},'duration_hours':8,'upcast_target_limits':{'8':3,'9':6}}
    rays=next(s for s in spells if s['alias']=='P.RAYS')
    rays['numeric_facets']={'rays_at_base_level':3,'damage_each_ray':'2d6','damage_type':'fire','each_ray_separate_attack':True,'upcast_extra_rays_per_level':1}
    # Full-corpus delivery is common to every question. Clusters describe ownership/dependencies,
    # not per-question retrieval recipes or answer keys.
    clusters=[]
    all_shared=[p['id'] for p in public]
    for k,c in cards.items():
        included=[k]+(['IN'] if k=='SU' else ['SU'] if k=='IN' else [])
        called={t['to_id'] for t in relations if t['kind']=='calls_spell' and any(t['from_id']==a['id'] for ck in included for a in cards[ck]['abilities'])}
        clusters.append({'id':uid('cluster:'+c['id']),'title':c['title']+'完整规则簇','root_object_id':c['id'],
            'content_dependencies':[cards[x]['id'] for x in included]+sorted(called)+all_shared,
            'coverage':'all_card_text_all_card_abilities_all_direct_spell_calls_full_shared_rule_entries; no_question_filter',
            'review_status':'candidate','uncompiled_semantics':'original complete text remains available; unsupported consumer must report limit'})
    corpus={'delivery_id':uid('delivery:full-clusters-1'),'format_revision':'research-full-cluster-1','status':'candidate_not_formal_schema_or_release',
        'rules_context':{'id':uid('ruleset:dnd2024-mm2025-phb2024'),'system':'D&D','rules_edition':'2024','content_claims':['MM2025','PHB2024'],'publication_identity':'claimed','translation_authority':'unknown','rights':'unknown'},
        'scope':{'cards':list(cards),'complete_for':'selected five cards, all their abilities, all direct spell calls and six entire shared rule Entries; not entire rulebook',
                 'incidental_reference_policy':'literal in source; not claimed as full world/class/item simulation','same_corpus_for_every_case':True},
        'cards':list(cards.values()),'spells':spells,'shared_rules':public,'expressions':expressions,'relations':relations,'clusters':clusters,
        'alias_registry':aliases,'evidence':list(evidence.values()),'sources':list(sources.values()),'editorial_decisions':decisions,'research_receipts':list(receipts.values()),'known_issues':issues}
    save('input/knowledge.json',corpus)
    text='# 五对象完整规则簇候选\n\n本阅读视图由knowledge.json生成，不含题目或答案。仅候选，非正式接纳。所有题共用整个材料。\n'
    for c in corpus['cards']:
        text+=f"\n## {c['title']}\n\nID：{c['id']}\n\n### 原卡全文\n\n{c['verbatim_text']}\n\n### 全部能力的结构化候选\n\n"
        for a in c['abilities']:text+=f"#### {a['title']}\n\n```json\n{json.dumps({'id':a['id'],'owner_id':a['owner_id'],'critical_fields':a['critical_fields'],'mechanics':a['mechanics']},ensure_ascii=False,indent=2)}\n```\n\n{a['editorial_explanation']}\n"
    for s in spells:text+=f"\n## 共享法术：{s['title']}\n\n{s['verbatim_text']}\n"
    for p in public:text+=f"\n## 公共规则完整Entry：{p['title']}\n\n{p['content']['text']}\n"
    text+='\n## 采用决定与已知边界\n\n```json\n'+json.dumps({'editorial_decisions':decisions,'known_issues':issues},ensure_ascii=False,indent=2)+'\n```\n'
    (OUT/'input/完整规则簇.md').write_text(text)
    save('production-receipt.json',{'phase':'corpus_produced_before_questions','card_count':len(cards),'ability_count':sum(len(c['abilities']) for c in cards.values()),'spell_count':len(spells),'shared_complete_entries':len(public),'evidence_count':len(evidence),'source_count':len(sources),'source_checks':source_checks,'calculation_run':False})
    return corpus


def prepare_questions(corpus):
    by_key={k:next(c for c in corpus['cards'] if c['id']==corpus['alias_registry'][k]) for k in ['SU','IN','G25','F','S']}
    # Full scene roster stays present for every case. Target defenses are NOT flattened into requests.
    roster=[{'instance_id':i,'prototype_id':by_key[k]['id'],'current_hp':hp,'max_hp':hp,'position_plane':'material','can_see_and_be_seen':True,'can_speak_and_gesture':True,'resources':'all_printed_uses_available','sourced_effects':[]} for i,k,hp in [('succubus-A','SU',71),('incubus-A','IN',66),('ghost-A','G25',45),('ghost-B','G25',45),('fire-A','F',93),('slaad-A','S',144)]]
    roster.append({'instance_id':'adventurer-A','prototype_id':None,'creature_type':'humanoid','current_hp':40,'max_hp':60,'position_plane':'material','can_see_and_be_seen':True,
                   'intrinsic_defenses':{'damage_resistance':[],'damage_vulnerability':[],'damage_immunity':[],'condition_immunity':[]},'sourced_effects':[],
                   'defense_inventory_complete':True})
    questions=[]; gold=[]
    def case(n,text,actor,action,target='adventurer-A',*,save_outcome=None,grants=(),amount='printed_fixed',dice=None,facts=None,expected=None,inside=True,pending=()):
        scene=copy.deepcopy(roster)
        pc=next(x for x in scene if x['instance_id']=='adventurer-A')
        pc['sourced_effects']=[{'effect_instance_id':f'grant-{j}','source_instance_id':f'confirmed-source-{j}','kind':kind,'damage_type':'psychic','applicability':'confirmed_for_this_event'} for j,kind in enumerate(grants)]
        if action=='汲命之吻':pc['sourced_effects'].append({'effect_instance_id':'charm-by-A','source_instance_id':'succubus-A','kind':'charmed','active':True})
        event={'actor_instance_id':actor,'declared_action_name':action,'target_instance_ids':[target],'amount_mode':amount,
               'attack_outcome':'hit' if action in ['魔性之触','毁梦之触','凋零之触','燃烧','混沌法杖'] else None,'save_outcome':save_outcome,
               'distance_ft':5,'actor_can_see_target':True,'target_can_see_actor':True,'same_plane':True,
               'other_damage_adjustments':'none','defense_effect_inventory':'complete_unless_explicitly_unknown'}
        if dice is not None:event['recorded_dice']=dice
        if facts:event.update(facts)
        question={'id':f'C{n:02}','question':text,'scene':{'roster':scene,'event':event},'delivery':'input/knowledge.json in full; no per-case retrieval subset'}
        questions.append(question)
        gold.append({'id':question['id'],'category':'within_numeric_core_if_data_binding_succeeds' if inside else 'outside_core_or_missing_input',
                     'expected':expected,'pending_non_numeric_effects':list(pending),'scoring':'root_AI_source_checked_not_independent_human_approval'})
    def result(a,r,v,d,linked=None):return {'semantic_status':'numeric_result','stages':{'after_ability':a,'after_resistance':r,'after_vulnerability':v},'damage_taken':d,'linked_reduction':linked}
    case(1,'魅魔A对已被它魅惑的冒险者使用汲命之吻。目标体质豁免成功，另有已确认心灵抗性。采用卡载固定伤害，只问本次伤害及对应上限减损数值。','succubus-A','汲命之吻',save_outcome='success',grants=['damage_resistance'],expected=result(6,3,3,3,3))
    case(2,'同样合法的汲命之吻，目标体质豁免失败且有心灵抗性。采用卡载固定值，求本次伤害和对应上限减损。','succubus-A','汲命之吻',save_outcome='failure',grants=['damage_resistance'],expected=result(13,6,6,6,6))
    case(3,'汲命之吻体质豁免成功，目标有心灵抗性。本次3d8已记录为8、8、1，求伤害和对应上限减损，不重新掷骰。','succubus-A','汲命之吻',save_outcome='success',grants=['damage_resistance'],amount='recorded_roll',dice=[8,8,1],expected=result(8,4,4,4,4))
    case(4,'汲命之吻体质豁免成功且目标有心灵抗性。3d8已记录为1、1、1，求本次数值，不把0伤害当作缺结果。','succubus-A','汲命之吻',save_outcome='success',grants=['damage_resistance'],amount='recorded_roll',dice=[1,1,1],expected=result(1,0,0,0,0))
    case(5,'合法汲命之吻，冒险者豁免成功，没有心灵抗性、易伤或免疫。采用卡载固定值，求本次伤害及对应上限减损。','succubus-A','汲命之吻',save_outcome='success',expected=result(6,6,6,6,6))
    case(6,'合法汲命之吻，豁免成功；目标仅获已确认的心灵易伤。采用卡载固定值，求伤害及对应上限减损。','succubus-A','汲命之吻',save_outcome='success',grants=['damage_vulnerability'],expected=result(6,6,12,12,12))
    case(7,'合法汲命之吻，豁免成功。目标有两个独立来源的心灵抗性及一项心灵易伤，均确认适用。采用卡载固定值，求伤害及减损。','succubus-A','汲命之吻',save_outcome='success',grants=['damage_resistance','damage_resistance','damage_vulnerability'],expected=result(6,3,6,6,6))
    case(8,'合法汲命之吻，豁免成功。目标同时有心灵抗性和心灵伤害免疫，采用卡载固定值，求伤害及对应上限减损。','succubus-A','汲命之吻',save_outcome='success',grants=['damage_resistance','damage_immunity'],expected=result(6,3,3,0,0))
    case(9,'魅魔A以魔性之触命中梦魔A。双方均使用本批卡，采用固定伤害，无额外修正。只求本次伤害。','succubus-A','魔性之触','incubus-A',expected=result(16,8,8,8))
    case(10,'梦魔A以毁梦之触命中魅魔A，采用固定伤害，无额外修正。只求伤害；不要求计算器写入或删除诅咒。','incubus-A','毁梦之触','succubus-A',expected=result(15,7,7,7),pending=['来源诅咒仍是能力的一部分，不得声称已完成诅咒状态处理'])
    case(11,'幽魂A以凋零之触命中幽魂B；两者都是本批2025卡。采用固定伤害，只求伤害。','ghost-A','凋零之触','ghost-B',expected=result(19,19,19,0))
    case(12,'幽魂A以凋零之触命中无额外防御的冒险者。3d10已记录4、8、9，按能力自己的固定加值计算最终伤害。','ghost-A','凋零之触',amount='recorded_roll',dice=[4,8,9],expected=result(24,24,24,24))
    case(13,'火元素的燃烧攻击命中史拉绿蟾，采用卡载固定值，无额外修正。只求这次命中的伤害，不推进后续回合。','fire-A','燃烧','slaad-A',expected=result(10,5,5,5),pending=['点燃及其后续每回合危害未应用'])
    case(14,'火元素回合结束，史拉绿蟾处于其8尺处，确认在灵光内。只结算该目标当时的固定伤害，不推进燃烧危害。','fire-A','火焰灵光','slaad-A',facts={'timing':'source_turn_end','distance_ft':8},expected=result(5,2,2,2),pending=['点燃及后续危害未应用；不能宣称已结算区域内所有对象'])
    case(15,'火元素本回合首次进入史拉绿蟾的空间，触发已确认。采用固定值，只求这一次火焰形态伤害。','fire-A','火焰形态','slaad-A',facts={'first_entry_into_this_target_space_this_turn':True},expected=result(5,2,2,2))
    case(16,'幽魂A在自己的回合结束时仍位于物件内部，无额外修正。按虚体移动条款求它本次受到的固定伤害。','ghost-A','虚体移动','ghost-A',facts={'timing':'own_turn_end','inside_object':True},expected=result(5,5,5,5))
    case(17,'史拉绿蟾合法使用本卡火球术，目标冒险者敏捷豁免成功且具有已确认火焰抗性。8d6已记录6、5、4、4、4、3、3、2。仅结算这名目标的伤害。','slaad-A','火球术',save_outcome='success',amount='recorded_roll',dice=[6,5,4,4,4,3,3,2],facts={'spell_level':3,'spell_target_in_area':True,'verbal_somatic_available':True,'daily_use_available':True},expected=result(15,7,7,7),pending=['未结算区域内其他对象及可燃物件'])
    # Fire resistance is a runtime effect here, not the psychic grants used above.
    questions[-1]['scene']['roster'][-1]['sourced_effects']=[{'effect_instance_id':'fire-resistance-A','source_instance_id':'confirmed-source-0','kind':'damage_resistance','damage_type':'fire','applicability':'confirmed_for_this_event'}]
    case(18,'史拉绿蟾的混沌法杖命中幽魂A，采用卡载固定值，只求伤害。附带状态骰已经记录为4；不要把它当伤害骰或把状态写入也说成已完成。','slaad-A','混沌法杖','ghost-A',facts={'condition_die_d4':4},expected=result(8,8,8,8),pending=['失能效果需独立状态处理；本次数值成功不代表整个能力已执行'])
    case(19,'梦魔A对当前HP21的冒险者使用噩梦，目标感知豁免失败且有心灵抗性。要求完整选择HP分支，给出伤害及是否昏迷。','incubus-A','噩梦',save_outcome='failure',grants=['damage_resistance'],facts={'target_current_hp_before_effect':21},expected={'semantic_status':'outside_core','reason':'conditional_hp_branch_and_condition','rule_answer':{'damage_taken':9,'unconscious':False},'acceptable_consumer_response':'明确说明不支持分支/状态处理；不得给出自称完整核验的单纯伤害成功'},inside=False)
    questions[-1]['scene']['roster'][-1]['current_hp']=21
    case(20,'汲命之吻豁免成功，目标有心灵抗性、当前HP40、临时HP10。要求计算最终HP、剩余临时HP及对应上限减损。','succubus-A','汲命之吻',save_outcome='success',grants=['damage_resistance'],facts={'target_temporary_hp':10},expected={'semantic_status':'outside_core','reason':'temporary_hp_and_hp_mutation','rule_answer':{'damage_taken':3,'hp_lost':0,'hp_after':40,'temporary_hp_after':7,'linked_reduction':3},'acceptable_consumer_response':'可分离显示伤害3，但须声明未完成所求HP结算，整体不能记完成'},inside=False)
    questions[-1]['scene']['roster'][-1]['temporary_hp']=10
    case(21,'火元素回合结束，魅魔、史拉绿蟾、冒险者均确认在灵光内，冒险者没有额外防御。要求一次性结算三名目标的固定伤害并应用燃烧。','fire-A','火焰灵光',facts={'timing':'source_turn_end','all_listed_targets_in_aura':True},expected={'semantic_status':'outside_core','reason':'multi_target_and_ignite_state','rule_answer':{'succubus-A':2,'slaad-A':2,'adventurer-A':5},'acceptable_consumer_response':'声明多目标/状态未支持，不把某一目标数值冒充完整结果'},inside=False)
    questions[-1]['scene']['event']['target_instance_ids']=['succubus-A','slaad-A','adventurer-A']
    case(22,'冒险者同时有梦魔A毁梦之触的诅咒和另一独立X造成的同类短休受限。梦魔A死亡。要求删除该结束的效果，同时保留仍有效的效果。','incubus-A','毁梦之触',facts={'source_has_died':True,'sourced_curses':[{'id':'curse-A','source':'incubus-A'},{'id':'curse-X','source':'other-X','independent_effect_confirmed_active':True}]},expected={'semantic_status':'outside_core','reason':'source_specific_state_removal','rule_answer':{'remove':['curse-A'],'retain':['curse-X']},'acceptable_consumer_response':'明确不支持状态写入；不得清除所有同名状态'},inside=False)
    next(x for x in questions[-1]['scene']['roster'] if x['instance_id']=='incubus-A').update(current_hp=0,dead=True)
    case(23,'梦魔A完成长休并选择化身魅魔；变形前当前HP23、最大HP66，托梦术已用一次、催眠图纹未用。要求给出休息及替换后的当前HP和各资源剩余值，而不是只给印刷默认卡。','incubus-A','化身魅魔','incubus-A',facts={'current_hp_before_change':23,'max_hp_before_change':66,'spent_resource_record':{'托梦术':1,'催眠图纹':0},'other_hp_recovery_blockers':'none'},expected={'semantic_status':'outside_core','reason':'runtime_statistics_migration_undefined','rule_answer':None,'acceptable_consumer_response':'可以指出改用魅魔卡及长休通则；跨数据卡实例HP/资源迁移没有已制定算法，不能直接把默认71当结果'},inside=False)
    next(x for x in questions[-1]['scene']['roster'] if x['instance_id']=='incubus-A').update(current_hp=23,resources={'托梦术':{'used':1},'催眠图纹':{'used':0}})
    case(24,'合法汲命之吻，目标有心灵抗性及心灵免疫，但体质豁免结果没有提供。要求完整核验并结算；不能自行补成成功或失败。','succubus-A','汲命之吻',save_outcome=None,grants=['damage_resistance','damage_immunity'],expected={'semantic_status':'needs_input','missing':['save_outcome'],'forbid_completed_numeric_result':True,'note':'沿用本批完整输入契约；免疫不能绕过必需输入校验'},inside=False)
    save('input/questions.json',{'corpus_delivery_id':corpus['delivery_id'],'instructions':'先读取完整knowledge.json，不读evaluator，不按题裁剪材料。解析现场与能力引用；缺读取能力、机制或输入须分别报告。不得把本题转交LLM或临时实现读取器后冒充现有能力。','questions':questions})
    human='# 完整规则簇消费测试题\n\n全部24题共用完整knowledge.json和完整规则簇.md。此文件不含答案；现场完整结构见questions.json。\n'
    for q in questions:human+=f"\n## {q['id']}\n\n{q['question']}\n"
    (OUT/'input/测试题.md').write_text(human)
    # Gold is prepared after the full corpus. It is never part of the delivery input.
    save('evaluator/gold.json',{'review':'root_AI_against_source_and_declared_contract; not independent human approval','cases':gold})
    save('evaluator/results-template.json',{'status':'not_run','implementation':None,'data_reader_implemented':None,'results':[{'id':q['id'],'data_read_status':None,'binding_status':None,'actual':None,'numeric_score':None,'scope_score':None,'total_elapsed_ms':None,'reader_binding_ms':None,'core_ms':None} for q in questions]})
    print('Prepared corpus first, then 24 questions (18 numeric-core-compatible, 6 outside/missing). No execution.')

if __name__=='__main__':
    corpus=prepare_corpus()
    prepare_questions(corpus)
