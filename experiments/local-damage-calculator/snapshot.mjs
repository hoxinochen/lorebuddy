import { DAMAGE_LIMIT, DAMAGE_TYPES } from './profile.mjs';

const SNAPSHOT_REQUEST_FIELDS = ['environment', 'ability', 'target', 'event', 'raw_damage',
  'damage_basis', 'save_outcome', 'eligibility', 'defense_coverage', 'other_adjustments'];
const SNAPSHOT_CONTEXT_FIELDS = ['environment', 'ability', 'target', 'event', 'profile_revision',
  'definition_revision', 'defense_snapshot', 'target_defenses', 'defense_coverage', 'definition', 'verified_facts'];
const snapshotRecord = x => x !== null && typeof x === 'object' && !Array.isArray(x);
const ownFields = (x, keys) => snapshotRecord(x) && keys.every(k => Object.hasOwn(x, k));
const snapshotText = x => typeof x === 'string' && x.trim().length > 0;

function freezeSnapshot(value, seen = new WeakSet()) {
  if (value && typeof value === 'object' && !seen.has(value)) {
    seen.add(value);
    Object.values(value).forEach(child => freezeSnapshot(child, seen));
    Object.freeze(value);
  }
  return value;
}

// Capture at draft creation / tool execution, never inside the comparison function.
// Full supported request + selected effective context; unrelated definitions are excluded.
export function captureInputSnapshot(request, context) {
  return freezeSnapshot(structuredClone({
    snapshot_revision: 'input-snapshot-1', request,
    context: {
      ...Object.fromEntries(SNAPSHOT_CONTEXT_FIELDS.filter(k => !['definition', 'verified_facts'].includes(k))
        .map(k => [k, context[k]])),
      definition: context.definitions?.[request.ability] ?? null,
      verified_facts: context.verified_facts ?? null,
    },
  }));
}

// Canonical JSON preserves value/type and array order, but ignores object-key order.
// Reject unsupported values/cycles instead of converting undefined/NaN into matching nulls.
function canonicalSnapshot(value, ancestors = new Set()) {
  if (value === null || typeof value === 'string' || typeof value === 'boolean') return JSON.stringify(value);
  if (typeof value === 'number' && Number.isFinite(value)) return JSON.stringify(value);
  if (!value || typeof value !== 'object' || ancestors.has(value)) throw new TypeError('Non-JSON snapshot');
  ancestors.add(value);
  let result;
  if (Array.isArray(value)) {
    if (Object.keys(value).length !== value.length) throw new TypeError('Sparse snapshot array');
    result = '[' + value.map(x => canonicalSnapshot(x, ancestors)).join(',') + ']';
  } else {
    if (![Object.prototype, null].includes(Object.getPrototypeOf(value))) throw new TypeError('Non-JSON snapshot record');
    result = '{' + Object.keys(value).sort().map(k => JSON.stringify(k) + ':' + canonicalSnapshot(value[k], ancestors)).join(',') + '}';
  }
  ancestors.delete(value);
  return result;
}

export function validInputSnapshot(snapshot) {
  if (!ownFields(snapshot, ['snapshot_revision', 'request', 'context']) || snapshot.snapshot_revision !== 'input-snapshot-1') return false;
  const q = snapshot.request, c = snapshot.context;
  if (!ownFields(q, SNAPSHOT_REQUEST_FIELDS) || Object.keys(q).some(k => !SNAPSHOT_REQUEST_FIELDS.includes(k))
    || !ownFields(c, SNAPSHOT_CONTEXT_FIELDS) || Object.keys(c).some(k => !SNAPSHOT_CONTEXT_FIELDS.includes(k))) return false;
  if (!['environment', 'ability', 'target', 'event'].every(k => snapshotText(q[k]) && c[k] === q[k])
    || !['profile_revision', 'definition_revision', 'defense_snapshot'].every(k => snapshotText(c[k]))) return false;
  if (!Number.isSafeInteger(q.raw_damage) || q.raw_damage < 0 || q.raw_damage > DAMAGE_LIMIT
    || q.damage_basis !== 'before_save_and_defenses' || q.eligibility !== 'confirmed'
    || q.defense_coverage !== 'confirmed' || c.defense_coverage !== 'confirmed' || q.other_adjustments !== 'none') return false;
  const d = c.definition;
  if (!ownFields(d, ['id', 'save', 'on_success', 'linked_reduction', 'damage_type']) || d.id !== q.ability
    || typeof d.save !== 'boolean' || !['half', 'zero', 'unchanged'].includes(d.on_success)
    || typeof d.linked_reduction !== 'boolean' || !DAMAGE_TYPES.includes(d.damage_type)
    || !(d.save ? ['success', 'failure'].includes(q.save_outcome) : q.save_outcome === 'not_applicable')) return false;
  if (!ownFields(c.target_defenses, ['resistance', 'vulnerability', 'immunity'])
    || Object.keys(c.target_defenses).some(k => !['resistance', 'vulnerability', 'immunity'].includes(k))
    || Object.values(c.target_defenses).some(a => !Array.isArray(a) || a.some(t => !DAMAGE_TYPES.includes(t)))) return false;
  if (c.verified_facts !== null && (!snapshotRecord(c.verified_facts)
    || Object.entries(c.verified_facts).some(([k, v]) => !SNAPSHOT_REQUEST_FIELDS.includes(k) || q[k] !== v))) return false;
  try { canonicalSnapshot(snapshot); return true; } catch { return false; }
}

export function sameInputSnapshot(left, right) {
  return validInputSnapshot(left) && validInputSnapshot(right) && canonicalSnapshot(left) === canonicalSnapshot(right);
}
