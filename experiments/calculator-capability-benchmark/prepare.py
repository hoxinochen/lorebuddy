"""Prepare research-only benchmark material. Does not import/run a calculator or LLM."""
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
CROSS = 'build/m2-cross-relations-6cards-2026-10-22'
HIGH = 'build/m2-facts-first-high-2026-10-22'
SEVEN = 'build/m2-finite-production-7cards-2026-10-22'
PROFILE = 'research.dnd2024-srd521'

def read(path):
    return json.loads((ROOT / path).read_text())

def write(path, value):
    (OUT / path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

# Facts below are manually mapped from the selected evidence, not copied from answers.
g25 = {'resistance': ['acid', 'bludgeoning', 'cold', 'fire', 'lightning', 'piercing', 'slashing', 'thunder'], 'vulnerability': [], 'immunity': ['necrotic', 'poison']}
fire = {'resistance': ['bludgeoning', 'piercing', 'slashing'], 'vulnerability': [], 'immunity': ['fire', 'poison']}
slaad = {'resistance': ['acid', 'cold', 'fire', 'lightning', 'thunder'], 'vulnerability': [], 'immunity': []}
psychic = {'resistance': ['psychic'], 'vulnerability': [], 'immunity': []}
empty = {'resistance': [], 'vulnerability': [], 'immunity': []}
cases, gold = [], []

# Expected values are literal, source-checked evaluation assertions, never engine output.
def add(cid, question, raw, dtype, defenses, origin, evidence, expected, *, save=False, linked=False, outcome='not_applicable', cohort='numeric', environment=PROFILE):
    ability = 'benchmark:' + cid
    definition = {'id': ability, 'save': save, 'on_success': 'half' if save else 'unchanged', 'damage_type': dtype, 'linked_reduction': linked, 'status': 'candidate_research_only'}
    request = {'environment': environment, 'ability': ability, 'target': 'benchmark-target:' + cid, 'event': 'benchmark-event:' + cid,
               'raw_damage': raw, 'damage_basis': 'before_save_and_defenses', 'save_outcome': outcome,
               'eligibility': 'confirmed', 'defense_coverage': 'confirmed', 'other_adjustments': 'none'}
    context = {k: request[k] for k in ['environment', 'ability', 'target', 'event']}
    context.update(profile_revision='draft-1', definition_revision='benchmark-mapping-1', defense_snapshot='benchmark-defense:' + cid,
                   target_defenses=copy.deepcopy(defenses), defense_coverage='confirmed', definitions={ability: definition})
    cases.append({'id': cid, 'question': question, 'evidence_refs': evidence, 'request': request, 'context': context})
    gold.append({'id': cid, 'cohort': cohort, 'origin': origin, 'expected': expected, 'review': 'root_AI_source_checked_not_independent_human_approval'})

# Eight numeric projections from five historical questions. No new model tests.
def numeric(n, question, raw, dtype, defenses, qid, refs, stages, damage, *, batch=CROSS, linked=False, save=False):
    expected = {'status': 'calculated', 'stages': dict(zip(['after_ability','after_resistance','after_vulnerability'], stages)), 'damage_taken': damage, 'linked_reduction': damage if linked else None}
    add(f'N{n:02}', question, raw, dtype, defenses, {'kind':'historical_numeric_projection','batch':batch,'question_id':qid}, refs, expected, linked=linked, save=save, outcome='success' if save else 'not_applicable')

numeric(1, '2025幽魂未附身，受到20点寒冷伤害，无其他修正。计算该次最终伤害。', 20,'cold',g25,'V01',['cross:G25.HEADER','cross:P.RESISTANCE','cross:P.ROUND'],[20,10,10],10)
numeric(2, '2025幽魂未附身，受到魔法武器造成的20点挥砍伤害，无其他修正。计算最终伤害。',20,'slashing',g25,'V01',['cross:G25.HEADER','cross:P.RESISTANCE','cross:P.ROUND'],[20,10,10],10)
numeric(3, '2025幽魂未附身，受到非魔法攻击造成的20点挥砍伤害，无其他修正。计算最终伤害。',20,'slashing',g25,'V01',['cross:G25.HEADER','cross:P.RESISTANCE','cross:P.ROUND'],[20,10,10],10)
numeric(4, '本批2025火元素受到魔法武器造成的11点挥砍伤害，无其他修正。计算最终伤害。',11,'slashing',fire,'E06',['seven:F.CARD','seven:P.RESISTANCE','seven:P.ROUND'],[11,5,5],5,batch=HIGH)
numeric(5, '史拉绿蟾对法术的豁免已判失败，随后受到28点火焰伤害，无其他修正。计算最终伤害；不重新判定豁免。',28,'fire',slaad,'G14',['seven:S.CARD','seven:P.RESISTANCE'],[28,14,14],14)
numeric(6, '史拉绿蟾对法术的豁免已判失败，原始闪电伤害31，只有本卡防御且无其他修正。计算最终伤害。',31,'lightning',slaad,'R02',['seven:S.CARD','seven:P.RESISTANCE','seven:P.ROUND'],[31,15,15],15)
numeric(7, '史拉绿蟾对法术的豁免已判失败，原始力场伤害31，只有本卡防御且无其他修正。计算最终伤害。',31,'force',slaad,'R02',['seven:S.CARD','seven:P.RESISTANCE'],[31,31,31],31)
numeric(8, '汲命之吻的目标满足来源与距离条件，体质豁免成功；原始固定13点心灵伤害，目标有心灵抗性，无其他修正。计算最终伤害及该次对应的生命值上限减损数值，不执行写入或恢复。',13,'psychic',psychic,'D09',['cross:SU.ABILITY.5','cross:P.RESISTANCE','cross:P.ROUND'],[6,3,3],3,linked=True,save=True)

# Three edition boundaries retain historical rule identity, even if some arithmetic looks reusable.
for n, label, dtype, defense, semantic in [(1,'寒冷','cold',{'resistance':[],'vulnerability':[],'immunity':['cold']},0), (2,'魔法武器挥砍','slashing',empty,20), (3,'非魔法攻击挥砍','slashing',{'resistance':['slashing'],'vulnerability':[],'immunity':[]},10)]:
    add(f'B{n:02}',f'选择2014幽魂，未附身，受到20点{label}伤害，无其他修正。当前只提供2024研究Profile；检查能否执行，不得替换为2025幽魂。',20,dtype,defense,
        {'kind':'historical_edition_boundary','batch':CROSS,'question_id':'V01'},['cross:G14.HEADER'],{'status':'unsupported','required_issue_codes':['unsupported_profile'],'forbid_numeric_result':True},cohort='boundary',environment='benchmark.dnd2014-unimplemented')
    gold[-1]['historical_rule_answer_outside_current_profile'] = semantic
    gold[-1]['exclusion'] = 'Not in numeric accuracy; inability to execute is a capability limit, not equality with historical LLM coverage.'

# Five new boundary probes, not historical matched questions and not new monster facts.
for n, description, status, code in [
    (4,'汲命之吻原始13点心灵伤害，目标有心灵抗性、资格已确认，但豁免结果未提供。检查能否结算。','needs_input','missing_save_outcome'),
    (5,'汲命之吻原始13点心灵伤害、豁免成功，但目标防御是否完整尚未确认。检查能否结算。','needs_input','defense_coverage_unknown'),
    (6,'汲命之吻原始13点心灵伤害、豁免成功、心灵抗性已确认；另有额外固定减伤，当前计算流程未支持。检查能否结算。','unsupported','unsupported_adjustment'),
    (7,'合成接口边界请求：同一次事件有7点心灵及6点火焰两种伤害分量。检查当前单类型核心能否接收；这不是对汲命之吻正文的修改。','unsupported','mixed_damage_not_supported'),
    (8,'汲命之吻输入的13被标记为豁免与防御处理后的数值，仍要求执行完整减伤流程。检查输入口径是否合法。','invalid','wrong_damage_basis')]:
    add(f'B{n:02}',description,13,'psychic',psychic,{'kind':'new_boundary_probe','derived_from':'N08','historical_llm_comparison':False},['cross:SU.ABILITY.5'],{'status':status,'required_issue_codes':[code],'forbid_numeric_result':True},save=True,linked=True,outcome='success',cohort='boundary')
    req, ctx = cases[-1]['request'], cases[-1]['context']
    if n == 4: req['save_outcome'] = None
    if n == 5:
        req['defense_coverage'] = 'unknown'; ctx['defense_coverage'] = 'unknown'; ctx['target_defenses'] = copy.deepcopy(empty)
    if n == 6: req['other_adjustments'] = 'additional_fixed_reduction'
    if n == 7: req['components'] = [{'type':'psychic','amount':7},{'type':'fire','amount':6}]
    if n == 8: req['damage_basis'] = 'after_save_and_defenses'

selected = []
for namespace,path,aliases in [('cross',CROSS+'/evidence.json',{'G14.HEADER','G25.HEADER','SU.ABILITY.5','P.RESISTANCE','P.ROUND'}),('seven',SEVEN+'/evidence.json',{'F.CARD','S.CARD','P.RESISTANCE','P.ROUND'})]:
    for e in read(path):
        if e['alias'] in aliases:
            selected.append({'ref':namespace+':'+e['alias'],'origin_file':path,**e})

# Save calculator inputs BEFORE reading any historical answer/Gold file.
write('input/cases.json',{'benchmark_id':'damage-capability-2026-10-23','status':'prepared_not_run','cases':cases})
write('input/evidence.json',selected)
questions = '# 计算器能力测试题（不含答案）\n\n共16项。每项独立；固定原始伤害，不掷骰、不应用HP、不调用LLM。计算器接收cases.json中每项request/context；文本和evidence供人核对映射。\n'
for c in cases:
    questions += f"\n## {c['id']}\n\n{c['question']}\n\n规则证据：{', '.join(c['evidence_refs'])}。\n"
(OUT/'input/questions.md').write_text(questions)

# Evaluation-only area. Historical answers are observations, not automatically correct Gold.
write('evaluator/gold.json',{'status':'source_checked_expected_not_calculator_output','cases':gold})
history = []
for batch,qid,answer_path in [(CROSS,'V01',CROSS+'/answers/V.json'),(HIGH,'E06',HIGH+'/answers/facts_E.json'),(CROSS,'G14',CROSS+'/answers/R.json'),(CROSS,'R02',CROSS+'/answers/R.json'),(CROSS,'D09',CROSS+'/answers/D.json')]:
    q = next(q for q in read(batch+'/private/gold.json')['questions'] if q['id']==qid)
    answers = read(answer_path)
    answer = next(a for a in answers['answers'] if a['id']==qid)
    ids = [g['id'] for g in gold if g['origin'].get('batch')==batch and g['origin'].get('question_id')==qid]
    history.append({'batch':batch,'question_id':qid,'case_ids':ids,'original_question_and_gold':q,'answer_file':answer_path,'model':answers['model'],'effort':answers['effort'],'original_answer':answer,
                    'numeric_projection_review':'fail' if qid=='D09' else 'pass',
                    'review_note':'D09 original answer says 6/6; source and original Gold require 3/3. Preserve failure.' if qid=='D09' else 'Only selected numeric subitems reviewed; not entire original question or new prompt.',
                    'per_question_latency_ms':None,'latency_status':'not_recorded; historical batch wall time cannot be divided by question count'})
write('evaluator/historical-baseline.json',history)
write('evaluator/results-template.json',{'status':'not_run','implementation':None,'environment':None,'timing_method':None,
 'cases':[{'id':c['id'],'actual_result':None,'score':None,'cold_first_call_ms':None,'warm_samples_ms':[],'warm_p50_ms':None,'warm_p95_ms':None} for c in cases]})
print('Prepared 16 cases, 9 evidence records, 5 historical question records. No calculator/model executed.')
