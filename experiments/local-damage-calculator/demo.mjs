import { calculate } from './engine.mjs';
import { compareDraft } from './compare.mjs';
import { PROFILE_ID, PROFILE_REVISION } from './profile.mjs';
import { captureInputSnapshot } from './snapshot.mjs';

const fixtures = JSON.parse(document.getElementById('fixture-data').textContent);
const definitions = Object.fromEntries(Object.values(fixtures).map(d => [d.id, d]));
const $ = id => document.getElementById(id);
const number = id => $(id).value.trim() === '' ? NaN : Number($(id).value);
const labels = { ability: '能力分支', resistance: '抗性', vulnerability: '易伤', immunity: '免疫' };
const descriptions = { half: '成功半伤，向下取整', zero: '成功不受伤害', unchanged: '保留伤害',
  halve_once_floor: '减半一次，向下取整', double_once: '加倍一次', not_applicable: '不适用，保持数值', zero_damage: '免疫，伤害为零' };
const issueLabels = {
  missing_save_outcome: '请补充豁免是成功还是失败。', defense_coverage_unknown: '请确认目标的防御信息完整。',
  eligibility_unknown: '请确认目标已满足这项能力的资格条件。', target_ineligible: '目标不满足资格条件，本次不能结算。',
  unsupported_adjustment: '此样机暂不支持额外减伤，请交还人工判断。', damage_not_integer: '原始伤害必须是整数。',
  damage_out_of_range: '请输入0到1,000,000之间的原始伤害。', save_not_applicable: '此模板没有豁免，请选择“不适用”。',
  invalid_save_outcome: '此模板需要豁免，请选择成功或失败。',
};
const stageKeys = ['after_ability', 'after_resistance', 'after_vulnerability'];
let eventCounter = 0;
let frozenDraft = null;

function collect() {
  const defenses = { resistance: $('resistance').checked ? ['psychic'] : [],
    vulnerability: $('vulnerability').checked ? ['psychic'] : [], immunity: $('immunity').checked ? ['psychic'] : [] };
  const request = { environment: PROFILE_ID, ability: fixtures[$('ability').value].id,
    target: 'synthetic-target-A', event: `local-event-${eventCounter}`,
    raw_damage: number('raw'), damage_basis: 'before_save_and_defenses',
    save_outcome: $('save').value === 'unknown' ? null : $('save').value,
    eligibility: $('eligibility').value, defense_coverage: $('coverage').checked ? 'confirmed' : 'unknown',
    other_adjustments: $('other').checked ? [{ kind: 'subtract', amount: 5 }] : 'none' };
  const context = { environment: PROFILE_ID, ability: request.ability, target: request.target, event: request.event,
    profile_revision: PROFILE_REVISION, definition_revision: 'synthetic-fixture-1',
    defense_snapshot: JSON.stringify(defenses), definitions, target_defenses: defenses,
    defense_coverage: request.defense_coverage };
  return { request, context };
}
function captureDraft(request, context) {
  // Captured before calculate runs; never auto-filled from the tool's result.
  const binding = { environment: request.environment, ability: request.ability, target: request.target,
    event: request.event, profile_revision: context.profile_revision,
    definition_revision: context.definition_revision, defense_snapshot: context.defense_snapshot };
  return Object.freeze({ binding: Object.freeze(binding), input_snapshot: captureInputSnapshot(request, context),
    stages: Object.freeze(Object.fromEntries(stageKeys.map((k, i) => [k, number(`draft-${i}`)]))),
    damage_taken: number('draft-damage'),
    linked_reduction: fixtures[$('ability').value].linked_reduction ? number('draft-reduction') : null });
}
function resetOutput() {
  $('result').hidden = true;
  $('status').textContent = '输入就绪，点击计算查看结果。';
  $('status').className = 'status';
}
function render() {
  const { request, context } = collect();
  // Reuse the previously captured draft. Never rebind current inputs here.
  const draft = $('compare').checked ? frozenDraft : null;
  const result = calculate(request, context);
  const comparison = draft ? compareDraft(draft, result) : null;
  $('result').hidden = false;
  $('trace').replaceChildren();
  $('numbers').hidden = result.status !== 'calculated';
  $('machine-output').textContent = JSON.stringify({ result, comparison, simulated_draft: draft }, null, 2);
  if (result.status !== 'calculated') {
    $('status').className = 'status attention';
    $('status').textContent = result.issues.map(x => issueLabels[x.code] ?? '本次输入暂不能处理，请查看详细记录。').join(' ');
    $('comparison').textContent = '未生成数值，不与草案比较，也不调用模型。';
    return;
  }
  $('status').className = 'status';
  $('status').textContent = '本地结算完成；结果仅覆盖下方计算阶段。';
  $('damage-result').textContent = result.damage_taken;
  $('reduction-result').textContent = result.linked_reduction === null ? '不适用' : result.linked_reduction;
  for (const [index, entry] of result.trace.entries()) {
    const tr = document.createElement('tr');
    const draftValue = !draft ? '未提供' : index < 3 ? draft.stages[stageKeys[index]] : draft.damage_taken;
    for (const value of [labels[entry.stage], `${entry.before} → ${entry.after}`, descriptions[entry.operation],
      Number.isNaN(draftValue) ? '未提供' : draftValue]) {
      const td = document.createElement('td'); td.textContent = value; tr.append(td);
    }
    $('trace').append(tr);
  }
  if (!comparison) $('comparison').textContent = '尚未固定模拟草案，仅展示本地结果；可先固定草案，再比较。';
  else if (comparison.status === 'matched') $('comparison').textContent = '计算一致。双方仍可能共享错误输入；这不代表整道规则问题已经核验。';
  else {
    $('comparison').textContent = comparison.status === 'input_mismatch'
      ? '现场输入不同：固定草案与本次计算使用了不同输入，即使最后数字相同也不能认定一致。'
      : ['invalid_tool_result', 'invalid_draft', 'missing_draft_stage', 'missing_draft_binding'].includes(comparison.status)
        ? '无法比较：草案或工具结果存在缺项或格式错误，请补齐后重试。'
        : '发现分歧：草案与本地结果不一致。此样机只标记冲突，不调用模型。';
    $('status').className = 'status attention';
  }
}
function preset(name) {
  eventCounter += 1;
  frozenDraft = null;
  $('draft-state').textContent = '草案尚未固定。';
  $('ability').value = name === 'opposites' ? 'direct' : 'half-drain';
  $('raw').value = 13;
  $('save').value = name === 'opposites' ? 'not_applicable' : name === 'missing' ? 'unknown' : 'success';
  $('resistance').checked = true;
  $('vulnerability').checked = name === 'opposites';
  $('immunity').checked = false;
  $('eligibility').value = 'confirmed';
  $('coverage').checked = true;
  $('other').checked = false;
  $('compare').checked = name === 'omission';
  [13, 6, 6].forEach((value, index) => { $(`draft-${index}`).value = value; });
  $('draft-damage').value = 6;
  $('draft-reduction').value = 6;
  $('draft-fields').hidden = !$('compare').checked;
  $('draft-reduction').disabled = !fixtures[$('ability').value].linked_reduction;
  resetOutput();
}
$('capture-draft').addEventListener('click', () => {
  const { request, context } = collect();
  frozenDraft = captureDraft(request, context);
  $('draft-state').textContent = `已固定草案：原始伤害${request.raw_damage}，豁免${$('save').selectedOptions[0].textContent}。修改现场输入不会改写这份快照。`;
  resetOutput();
});
$('form').addEventListener('submit', event => { event.preventDefault(); render(); });
$('form').addEventListener('input', () => {
  $('draft-fields').hidden = !$('compare').checked;
  $('draft-reduction').disabled = !fixtures[$('ability').value].linked_reduction;
  resetOutput();
});
document.querySelectorAll('[data-preset]').forEach(button => {
  button.addEventListener('click', () => preset(button.dataset.preset));
});
preset('omission');
