import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, writeFileSync, mkdtempSync, copyFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { pathToFileURL } from 'node:url';
import { calculate } from './engine.mjs';
import { compareDraft } from './compare.mjs';
import { PROFILE_REVISION } from './profile.mjs';

const gold = JSON.parse(readFileSync(new URL('../../docs/milestone-2/local-damage-calculator-cases-2026-10-22.json', import.meta.url)));
const byId = Object.fromEntries(gold.cases.map(c => [c.case_id, c]));
const definitions = Object.fromEntries(Object.values(gold.fixtures).map(d => [d.id, d]));
function prepare(flat) {
  const request = structuredClone(flat);
  const defenses = request.defenses;
  delete request.defenses; // Legacy research fixture -> trusted context, never production AI arguments.
  request.ability = gold.fixtures[request.ability]?.id ?? request.ability;
  const context = { environment: request.environment, ability: request.ability, target: request.target,
    event: request.event, profile_revision: PROFILE_REVISION, definition_revision: 'synthetic-fixture-1',
    defense_snapshot: JSON.stringify(defenses), target_defenses: defenses,
    defense_coverage: 'confirmed', definitions };
  return { request, context };
}
const run = (flat, fn = calculate) => { const p = prepare(flat); return fn(p.request, p.context); };
function matches(result, expected) {
  assert.equal(result.status, expected.status);
  if (expected.issue) assert.ok(result.issues.some(x => x.code === expected.issue), JSON.stringify(result));
  else {
    assert.deepEqual(result.stages, expected.stages);
    assert.equal(result.damage_taken, expected.damage_taken);
    assert.equal(result.linked_reduction, expected.linked_reduction);
    assert.equal(result.trace.length, 4);
  }
  if (result.status !== 'calculated') {
    assert.ok(!Object.hasOwn(result, 'damage_taken'), 'Failure must not masquerade as zero damage');
  }
}
for (const c of gold.cases) test(`${c.case_id} ${c.purpose}`, () => matches(run(c.request), c.expected));

for (const c of gold.comparison_cases) test(`${c.case_id} ${c.qualification}`, () => {
  const flat = structuredClone(byId[c.basis].request);
  const p = prepare(flat);
  const initial = calculate(p.request, p.context);
  if (c.trusted_context) p.context.verified_facts = c.trusted_context;
  if (c.changed_request) Object.assign(p.request, c.changed_request);
  const result = calculate(p.request, p.context);
  // Older identity-only fixtures omitted numeric fields; supply their frozen Gold,
  // not current tool output, to satisfy the stricter draft contract.
  const draft = { binding: structuredClone(initial.binding), input_snapshot: initial.input_snapshot,
    ...structuredClone(c.ai_draft ?? byId[c.basis].expected) };
  if (c.changed_binding) Object.assign(draft.binding, c.changed_binding);
  const compared = compareDraft(draft, result, { higherModelConfigured: c.higher_model_configured ?? true });
  if (c.expected === 'matched_but_semantically_wrong_not_detected') {
    assert.equal(compared.status, 'matched'); // A deliberate blind spot, not a successful error detector.
    assert.equal(result.damage_taken, 6);
    assert.notEqual(result.damage_taken, 3);
  } else if (c.trusted_context) {
    assert.ok(result.issues.some(x => x.code === 'context_mismatch'));
    assert.equal(compared.action, 'repair_request_without_model_call');
  } else if (['conflict_without_model_call', 'request_input_without_model_call', 'report_unsupported'].includes(c.expected)) {
    assert.equal(compared.action, c.expected);
  } else assert.equal(compared.status, c.expected);
});

test('inputs unchanged, deterministic output, no ambient time/random dependency', () => {
  const p = prepare(byId.C01.request);
  const original = structuredClone(p);
  const first = calculate(p.request, p.context);
  assert.deepEqual(calculate(p.request, p.context), first);
  assert.deepEqual(p, original);
});
test('request cannot replace selected target defenses', () => {
  const p = prepare(byId.C01.request);
  p.request.defenses = { resistance: [], vulnerability: [], immunity: [] };
  assert.ok(calculate(p.request, p.context).issues.some(x => x.code === 'fixed_rule_override'));
});
test('multiple issues are preserved, even for immune target', () => {
  const p = prepare(byId.C33.request);
  p.request.eligibility = 'unknown';
  const result = calculate(p.request, p.context);
  assert.ok(result.issues.some(x => x.code === 'missing_save_outcome'));
  assert.ok(result.issues.some(x => x.code === 'eligibility_unknown'));
  assert.equal(result.status, 'needs_input');
});
test('malformed context, defense values and non-finite numbers fail closed', () => {
  assert.equal(calculate(null, {}).status, 'invalid');
  for (const raw of [NaN, Infinity, -Infinity, true]) {
    const p = prepare(byId.C01.request); p.request.raw_damage = raw;
    assert.equal(calculate(p.request, p.context).status, 'invalid');
  }
  const p = prepare(byId.C01.request);
  delete p.context.target_defenses.immunity;
  assert.equal(calculate(p.request, p.context).status, 'invalid');
});
test('stale profile, definition revision and defense snapshot cannot compare as matched', () => {
  const p = prepare(byId.C01.request);
  const result = calculate(p.request, p.context);
  for (const key of ['profile_revision', 'definition_revision', 'defense_snapshot']) {
    const draft = structuredClone(result); draft.binding[key] = 'stale';
    assert.equal(compareDraft(draft, result).status, 'context_mismatch');
  }
});

const mutations = [
  ['skip_success_half', "success && definition.on_success === 'half' ? Math.floor(amount / 2)",
    "success && definition.on_success === 'half' ? amount"],
  ['stack_resistance', 'resistance ? Math.floor(amount / 2) : amount',
    'resistance ? Math.floor(amount / (2 ** defenses.resistance.filter(t => t === damageType).length)) : amount'],
  ['cancel_resistance_vulnerability', 'const resistance = defenses.resistance.includes(damageType);',
    'const cancelBoth = defenses.resistance.includes(damageType) && defenses.vulnerability.includes(damageType); const resistance = defenses.resistance.includes(damageType) && !cancelBoth;'],
  ['derive_reduction_from_raw', 'definition.linked_reduction ? damageTaken : null',
    'definition.linked_reduction ? request.raw_damage : null'],
];
for (const [fault, before, after] of mutations) test(`fault injection detects ${fault}`, async () => {
  const source = readFileSync(new URL('./engine.mjs', import.meta.url), 'utf8');
  assert.ok(source.includes(before), 'Mutation seam moved; do not silently skip');
  const folder = mkdtempSync(join(tmpdir(), 'lorebuddy-calculator-mutation-'));
  try {
    copyFileSync(new URL('./profile.mjs', import.meta.url), join(folder, 'profile.mjs'));
    copyFileSync(new URL('./snapshot.mjs', import.meta.url), join(folder, 'snapshot.mjs'));
    let mutated = source.replace(before, after);
    if (fault === 'cancel_resistance_vulnerability') {
      mutated = mutated.replace('const vulnerability = defenses.vulnerability.includes(damageType);',
        'const vulnerability = defenses.vulnerability.includes(damageType) && !cancelBoth;');
    }
    writeFileSync(join(folder, 'engine.mjs'), mutated);
    const mutant = await import(pathToFileURL(join(folder, 'engine.mjs')).href);
    const required = gold.planned_mutations.find(m => m.fault === fault).must_be_caught_by;
    for (const id of required) assert.throws(() => matches(run(byId[id].request, mutant.calculate), byId[id].expected));
  } finally { rmSync(folder, { recursive: true, force: true }); }
});
