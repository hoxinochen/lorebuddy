import { PROFILE_ID, PROFILE_REVISION, DAMAGE_LIMIT, DAMAGE_TYPES, RULES } from './profile.mjs';
import { captureInputSnapshot } from './snapshot.mjs';

const BINDING_KEYS = ['environment', 'ability', 'target', 'event'];
const FIELDS = new Set([...BINDING_KEYS, 'raw_damage', 'damage_basis', 'save_outcome',
  'eligibility', 'defense_coverage', 'other_adjustments']);
const UNSUPPORTED = Object.freeze({ components: 'mixed_damage_not_supported',
  conditional_resistance: 'conditional_defense_not_supported', temporary_hp: 'temporary_hp_not_supported' });
const FIXED_FIELDS = new Set(['on_success_override', 'defenses', 'damage_type', 'linked_reduction', 'operation_order']);
const isRecord = value => value !== null && typeof value === 'object' && !Array.isArray(value);

// context is assembled by the caller from selected definitions / confirmed scene facts.
// Never populate it by blindly trusting the model's tool arguments.
export function calculate(request, context) {
  const issues = [];
  const add = (status, code, field) => issues.push({ status, code, field });
  const finishFailure = () => ({
    status: issues.some(x => x.status === 'invalid') ? 'invalid'
      : issues.some(x => x.status === 'unsupported') ? 'unsupported' : 'needs_input',
    issues,
  });
  if (!isRecord(request) || !isRecord(context)) {
    add('invalid', 'invalid_envelope', 'request/context');
    return finishFailure();
  }
  for (const key of Object.keys(request)) {
    if (Object.hasOwn(UNSUPPORTED, key)) add('unsupported', UNSUPPORTED[key], key);
    else if (FIXED_FIELDS.has(key)) add('invalid', 'fixed_rule_override', key);
    else if (!FIELDS.has(key)) add('invalid', 'unknown_field', key);
  }
  if (request.environment !== PROFILE_ID || context.environment !== PROFILE_ID) {
    add('unsupported', 'unsupported_profile', 'environment');
  }
  if (context.profile_revision !== PROFILE_REVISION) add('invalid', 'profile_revision_mismatch', 'profile_revision');
  for (const key of ['definition_revision', 'defense_snapshot']) {
    if (typeof context[key] !== 'string' || !context[key].trim()) add('invalid', 'missing_context_revision', key);
  }
  const definition = isRecord(context.definitions) && Object.hasOwn(context.definitions, request.ability)
    ? context.definitions[request.ability] : null;
  if (!definition) add('invalid', 'unresolved_ability', 'ability');
  for (const key of BINDING_KEYS) {
    if (typeof request[key] !== 'string' || !request[key].trim()) add('invalid', 'missing_binding', key);
    else if (request[key] !== context[key]) add('invalid', 'context_mismatch', key);
  }
  if (!Number.isSafeInteger(request.raw_damage)) add('invalid', 'damage_not_integer', 'raw_damage');
  else if (request.raw_damage < 0 || request.raw_damage > DAMAGE_LIMIT) add('invalid', 'damage_out_of_range', 'raw_damage');
  if (request.damage_basis !== 'before_save_and_defenses') add('invalid', 'wrong_damage_basis', 'damage_basis');
  for (const key of ['eligibility', 'defense_coverage']) {
    const allowed = key === 'eligibility' ? ['confirmed', 'unknown', 'rejected'] : ['confirmed', 'unknown'];
    if (request[key] == null || request[key] === 'unknown') add('needs_input', `${key}_unknown`, key);
    else if (!allowed.includes(request[key])) add('invalid', 'invalid_enum', key);
  }
  if (request.eligibility === 'rejected') add('invalid', 'target_ineligible', 'eligibility');
  if (context.defense_coverage !== 'confirmed') add('needs_input', 'defense_coverage_unknown', 'context.defense_coverage');
  if (request.other_adjustments == null) add('needs_input', 'adjustment_coverage_unknown', 'other_adjustments');
  else if (request.other_adjustments !== 'none') add('unsupported', 'unsupported_adjustment', 'other_adjustments');
  if (definition) {
    if (typeof definition.save !== 'boolean' || !['half', 'zero', 'unchanged'].includes(definition.on_success)
      || typeof definition.linked_reduction !== 'boolean' || !DAMAGE_TYPES.includes(definition.damage_type)
      || typeof definition.id !== 'string' || definition.id !== request.ability) {
      add('invalid', 'invalid_definition', 'context.definitions');
    }
    if (definition.save && request.save_outcome == null) add('needs_input', 'missing_save_outcome', 'save_outcome');
    else if (definition.save && !['success', 'failure'].includes(request.save_outcome)) add('invalid', 'invalid_save_outcome', 'save_outcome');
    else if (!definition.save && request.save_outcome !== 'not_applicable') add('invalid', 'save_not_applicable', 'save_outcome');
  }
  const defenses = context.target_defenses;
  if (!isRecord(defenses) || Object.keys(defenses).some(k => !['resistance', 'vulnerability', 'immunity'].includes(k))) {
    add('invalid', 'invalid_defenses', 'context.target_defenses');
  } else {
    for (const key of ['resistance', 'vulnerability', 'immunity']) {
      if (!Array.isArray(defenses[key]) || defenses[key].some(t => !DAMAGE_TYPES.includes(t))) {
        add('invalid', 'invalid_defenses', `context.target_defenses.${key}`);
      }
    }
  }
  if (context.verified_facts != null) {
    if (!isRecord(context.verified_facts)) add('invalid', 'invalid_verified_facts', 'context.verified_facts');
    else for (const [key, value] of Object.entries(context.verified_facts)) {
      if (!FIELDS.has(key) || request[key] !== value) add('invalid', 'context_mismatch', `verified_facts.${key}`);
    }
  }
  if (issues.length) return finishFailure();

  const binding = Object.fromEntries(BINDING_KEYS.map(k => [k, request[k]]));
  binding.profile_revision = context.profile_revision;
  binding.definition_revision = context.definition_revision;
  binding.defense_snapshot = context.defense_snapshot;
  const damageType = definition.damage_type;
  let amount = request.raw_damage;
  const trace = [];
  const step = (stage, operation, after) => {
    trace.push({ stage, operation, before: amount, after, rule_ref: RULES[stage] });
    amount = after;
    return after;
  };
  const success = definition.save && request.save_outcome === 'success';
  const afterAbility = step('ability', success ? definition.on_success : 'unchanged',
    success && definition.on_success === 'half' ? Math.floor(amount / 2)
      : success && definition.on_success === 'zero' ? 0 : amount);
  const resistance = defenses.resistance.includes(damageType);
  const afterResistance = step('resistance', resistance ? 'halve_once_floor' : 'not_applicable',
    resistance ? Math.floor(amount / 2) : amount);
  const vulnerability = defenses.vulnerability.includes(damageType);
  const afterVulnerability = step('vulnerability', vulnerability ? 'double_once' : 'not_applicable',
    vulnerability ? amount * 2 : amount);
  const immune = defenses.immunity.includes(damageType);
  // Numeric immunity gate only; no claims about ordering of other triggered effects.
  const damageTaken = step('immunity', immune ? 'zero_damage' : 'not_applicable', immune ? 0 : amount);
  return {
    status: 'calculated', binding, input_snapshot: captureInputSnapshot(request, context),
    stages: { after_ability: afterAbility, after_resistance: afterResistance, after_vulnerability: afterVulnerability },
    damage_taken: damageTaken,
    linked_reduction: definition.linked_reduction ? damageTaken : null,
    trace,
    resolved_facts: { raw_damage: request.raw_damage, save_outcome: request.save_outcome,
      damage_type: damageType, on_success: definition.on_success,
      resistance, vulnerability, immunity: immune, definition_status: definition.status },
    coverage: 'single event/target/type; numeric damage only; no HP mutation, recovery or triggers',
    issues: [],
  };
}
