import { validInputSnapshot, sameInputSnapshot } from './snapshot.mjs';

const BINDINGS = ['environment', 'ability', 'target', 'event', 'profile_revision', 'definition_revision', 'defense_snapshot'];
const STAGES = ['after_ability', 'after_resistance', 'after_vulnerability'];
const record = x => x !== null && typeof x === 'object' && !Array.isArray(x);
const nonnegativeInteger = x => Number.isSafeInteger(x) && x >= 0;
const completeBinding = x => record(x) && BINDINGS.every(k => Object.hasOwn(x, k) && typeof x[k] === 'string' && x[k].trim());
const completeStages = x => record(x) && STAGES.every(k => Object.hasOwn(x, k) && nonnegativeInteger(x[k]));
const completeFinals = x => Object.hasOwn(x, 'damage_taken') && nonnegativeInteger(x.damage_taken)
  && Object.hasOwn(x, 'linked_reduction') && (x.input_snapshot.context.definition.linked_reduction
    ? nonnegativeInteger(x.linked_reduction) : x.linked_reduction === null);
const snapshotBindingMatches = x => BINDINGS.every(k =>
  x.binding[k] === (Object.hasOwn(x.input_snapshot.request, k) ? x.input_snapshot.request[k] : x.input_snapshot.context[k]));

// Returns a routing recommendation only. It never calls a model or accesses credentials.
export function compareDraft(draft, result, { higherModelConfigured = false } = {}) {
  const conflict = (status, differences) => ({ status, differences,
    action: higherModelConfigured ? 'request_higher_model_review' : 'conflict_without_model_call' });
  const invalidTool = fields => ({ status: 'invalid_tool_result', differences: fields, action: 'repair_tool_result_without_model_call' });
  if (!record(result) || !['calculated', 'invalid', 'needs_input', 'unsupported'].includes(result.status)) {
    return invalidTool(['status']);
  }
  if (result.status !== 'calculated') {
    if (!Array.isArray(result.issues) || !result.issues.length || result.issues.some(x => !record(x)
      || !['invalid', 'unsupported', 'needs_input'].includes(x.status) || typeof x.code !== 'string' || !x.code.trim()
      || typeof x.field !== 'string')) return invalidTool(['issues']);
    if (result.status === 'needs_input') return { status: 'needs_input', action: 'request_input_without_model_call', issues: result.issues };
    if (result.status === 'unsupported') return { status: 'unsupported', action: 'report_unsupported', issues: result.issues };
    return { status: 'invalid', action: 'repair_request_without_model_call', issues: result.issues };
  }
  if (!completeBinding(result.binding)) return invalidTool(['binding']);
  if (!validInputSnapshot(result.input_snapshot)) return invalidTool(['input_snapshot']);
  if (!snapshotBindingMatches(result)) return invalidTool(['binding/input_snapshot']);
  if (!completeStages(result.stages)) return invalidTool(['stages']);
  if (!completeFinals(result)) return invalidTool(['damage_taken/linked_reduction']);
  if (!record(draft) || !completeBinding(draft.binding)) return conflict('missing_draft_binding', ['binding']);
  if (!validInputSnapshot(draft.input_snapshot)) return conflict('invalid_draft', ['input_snapshot']);
  if (!completeStages(draft.stages)) return conflict('missing_draft_stage', ['stages']);
  if (!completeFinals(draft)) return conflict('invalid_draft', ['damage_taken/linked_reduction']);
  const bindingDiffs = BINDINGS.filter(k => draft.binding[k] !== result.binding[k]);
  if (bindingDiffs.length) return conflict('context_mismatch', bindingDiffs);
  if (!snapshotBindingMatches(draft)) return conflict('context_mismatch', ['binding/input_snapshot']);
  if (!sameInputSnapshot(draft.input_snapshot, result.input_snapshot)) return conflict('input_mismatch', ['input_snapshot']);
  const numeric = ['damage_taken', 'linked_reduction'].filter(k => draft[k] !== result[k]);
  if (numeric.length) return conflict('numeric_mismatch', numeric);
  const stageDiffs = STAGES.filter(k => draft.stages[k] !== result.stages[k]);
  if (stageDiffs.length) return conflict('stage_mismatch', stageDiffs);
  return { status: 'matched', action: 'present_supported_calculation',
    limitation: '一致不能发现两路共享的错误现场事实；不核验整段自然语言。' };
}
