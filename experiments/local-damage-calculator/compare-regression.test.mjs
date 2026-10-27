import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { calculate } from './engine.mjs';
import { compareDraft } from './compare.mjs';
import { captureInputSnapshot, sameInputSnapshot } from './snapshot.mjs';
import { PROFILE_ID, PROFILE_REVISION } from './profile.mjs';

const fixtures = JSON.parse(readFileSync(new URL('./synthetic-fixtures.json', import.meta.url)));
function scene() {
  const d = fixtures['half-drain'];
  const request = { environment: PROFILE_ID, ability: d.id, target: 'same-target', event: 'same-event', raw_damage: 13,
    damage_basis: 'before_save_and_defenses', save_outcome: 'success', eligibility: 'confirmed',
    defense_coverage: 'confirmed', other_adjustments: 'none' };
  const context = { environment: PROFILE_ID, ability: d.id, target: request.target, event: request.event,
    profile_revision: PROFILE_REVISION, definition_revision: 'synthetic-fixture-1', defense_snapshot: 'same-defense-label',
    definitions: { [d.id]: structuredClone(d) }, defense_coverage: 'confirmed',
    target_defenses: { resistance: ['psychic'], vulnerability: [], immunity: [] } };
  return { request, context };
}
function pair() {
  const s = scene(), result = calculate(s.request, s.context);
  return { draft: structuredClone(result), result: structuredClone(result) };
}
const mustReject = (draft, result, expected) => {
  let actual;
  assert.doesNotThrow(() => { actual = compareDraft(draft, result); });
  assert.equal(actual.status, expected);
  assert.notEqual(actual.status, 'matched');
};

test('REG01 same event, raw12 and raw13 both round to3 but inputs mismatch', () => {
  const s = scene(); s.request.raw_damage = 12;
  const draft = calculate(s.request, s.context);
  s.request.raw_damage = 13;
  const result = calculate(s.request, s.context);
  assert.deepEqual(draft.stages, result.stages);
  assert.equal(draft.damage_taken, 3); assert.equal(result.damage_taken, 3);
  mustReject(draft, result, 'input_mismatch');
});
test('REG02 equal zero results still bind different save outcomes', () => {
  const s = scene(); s.request.raw_damage = 0;
  const draft = calculate(s.request, s.context);
  s.request.save_outcome = 'failure';
  const result = calculate(s.request, s.context);
  assert.deepEqual(draft.stages, result.stages);
  mustReject(draft, result, 'input_mismatch');
});
test('REG03 snapshots are detached, deeply frozen and never rebound to current input', () => {
  const s = scene(), snapshot = captureInputSnapshot(s.request, s.context);
  s.request.raw_damage = 12;
  s.context.target_defenses.resistance.push('cold');
  assert.equal(snapshot.request.raw_damage, 13);
  assert.deepEqual(snapshot.context.target_defenses.resistance, ['psychic']);
  assert.ok(Object.isFrozen(snapshot.context.definition));
  assert.throws(() => { snapshot.request.raw_damage = 12; }, TypeError);
  assert.throws(() => snapshot.context.target_defenses.resistance.push('fire'), TypeError);
});
test('REG04 changed effective defenses cannot hide behind same defense snapshot label', () => {
  const s = scene(); s.request.raw_damage = 0;
  const draft = calculate(s.request, s.context);
  s.context.target_defenses.resistance = [];
  const result = calculate(s.request, s.context);
  assert.deepEqual(draft.stages, result.stages);
  mustReject(draft, result, 'input_mismatch');
});
test('REG05 changed selected definition cannot hide behind same revision', () => {
  const s = scene(); s.request.raw_damage = 0;
  const draft = calculate(s.request, s.context);
  s.context.definitions[s.request.ability].on_success = 'zero';
  const result = calculate(s.request, s.context);
  mustReject(draft, result, 'input_mismatch');
});
test('REG06 captured snapshots survive JSON transport and object key reordering', () => {
  const { draft, result } = pair();
  draft.input_snapshot.request = Object.fromEntries(Object.entries(draft.input_snapshot.request).reverse());
  assert.ok(sameInputSnapshot(draft.input_snapshot, result.input_snapshot));
  assert.equal(compareDraft(JSON.parse(JSON.stringify(draft)), result).status, 'matched');
});
test('REG07 both missing final fields cannot compare as undefined equals undefined', () => {
  const { draft, result } = pair();
  for (const obj of [draft, result]) for (const key of ['damage_taken', 'linked_reduction']) delete obj[key];
  mustReject(draft, result, 'invalid_tool_result');
});
test('REG08 each missing final field on either side is rejected', () => {
  for (const side of ['draft', 'result']) for (const key of ['damage_taken', 'linked_reduction']) {
    const p = pair(); delete p[side][key];
    mustReject(p.draft, p.result, side === 'result' ? 'invalid_tool_result' : 'invalid_draft');
  }
});
test('REG09 strings, booleans, null, undefined, fractions and nonfinite finals are rejected', () => {
  for (const side of ['draft', 'result']) for (const key of ['damage_taken', 'linked_reduction']) {
    for (const value of ['3', true, null, undefined, -1, 1.5, NaN, Infinity, 2 ** 53]) {
      const p = pair(); p[side][key] = value;
      mustReject(p.draft, p.result, side === 'result' ? 'invalid_tool_result' : 'invalid_draft');
    }
  }
});
test('REG10 null linked_reduction is valid only for a definition with no reduction', () => {
  const s = scene(), d = fixtures.half;
  s.request.ability = d.id; s.context.ability = d.id; s.context.definitions = { [d.id]: d };
  const result = calculate(s.request, s.context);
  assert.equal(result.linked_reduction, null);
  assert.equal(compareDraft(result, result).status, 'matched');
  const broken = structuredClone(result); broken.linked_reduction = 0;
  mustReject(broken, result, 'invalid_draft');
});
test('REG11 missing or malformed tool binding returns explicit error without throwing', () => {
  for (const value of [undefined, null, [], {}, { event: 'same-event' }]) {
    const { draft, result } = pair(); result.binding = value;
    mustReject(draft, result, 'invalid_tool_result');
  }
});
test('REG12 missing or malformed tool stages never throw or match', () => {
  for (const value of [undefined, null, [], {}, { after_ability: 6 }]) {
    const { draft, result } = pair(); result.stages = value;
    mustReject(draft, result, 'invalid_tool_result');
  }
});
test('REG13 absent or incomplete input snapshots never match, even on both sides', () => {
  for (const side of ['draft', 'result']) for (const value of [undefined, null, {}, { snapshot_revision: 'input-snapshot-1' }]) {
    const p = pair(); p[side].input_snapshot = value;
    mustReject(p.draft, p.result, side === 'result' ? 'invalid_tool_result' : 'invalid_draft');
  }
  const p = pair(); delete p.draft.input_snapshot; delete p.result.input_snapshot;
  mustReject(p.draft, p.result, 'invalid_tool_result');
});
test('REG14 partial or incorrectly typed snapshots cannot be blessed by equal payloads', () => {
  for (const mutate of [x => { delete x.request.save_outcome; }, x => { x.request.raw_damage = '13'; },
    x => { delete x.context.target_defenses.immunity; }, x => { x.request.raw_damage = NaN; },
    x => { x.request.save_outcome = 'unknown'; }, x => { x.request.damage_basis = 'after_save'; }]) {
    const p = pair(); mutate(p.result.input_snapshot); p.draft.input_snapshot = structuredClone(p.result.input_snapshot);
    mustReject(p.draft, p.result, 'invalid_tool_result');
  }
});
test('REG15 tool binding must agree with its own captured snapshot', () => {
  const p = pair(); p.result.binding.event = 'another-event'; p.draft.binding.event = 'another-event';
  mustReject(p.draft, p.result, 'invalid_tool_result');
});
test('REG16 malformed failure envelopes also return explicit error without model calls', () => {
  for (const bad of [null, {}, { status: 'calculated' }, { status: 'needs_input' },
    { status: 'invalid', issues: [] }, { status: 'unsupported', issues: [null] }]) {
    const result = compareDraft({}, bad, { higherModelConfigured: true });
    assert.equal(result.status, 'invalid_tool_result');
    assert.equal(result.action, 'repair_tool_result_without_model_call');
  }
});
test('REG17 scope/eligibility and captured verified facts are mandatory', () => {
  for (const mutate of [x => { delete x.request.eligibility; }, x => { delete x.request.other_adjustments; },
    x => { delete x.request.defense_coverage; }, x => { delete x.context.verified_facts; }]) {
    const p = pair(); mutate(p.result.input_snapshot);
    mustReject(p.draft, p.result, 'invalid_tool_result');
  }
});
test('REG18 snapshots reject non-JSON/cyclic values instead of throwing during comparison', () => {
  const p = pair(); p.result.input_snapshot.context.definition.loop = p.result.input_snapshot;
  mustReject(p.draft, p.result, 'invalid_tool_result');
});
