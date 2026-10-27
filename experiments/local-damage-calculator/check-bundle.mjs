// Static build proof only. This deliberately does not claim real-browser validation.
import { readFileSync, writeFileSync } from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import { calculate } from './engine.mjs';
import { PROFILE_ID, PROFILE_REVISION } from './profile.mjs';
const path = new URL('../../build/local-damage-calculator-research-2026-10-22/', import.meta.url);
const html = readFileSync(new URL('index.html', path), 'utf8');
const bundle = html.match(/<script>([\s\S]*?)<\/script>/)[1];
new vm.Script(bundle); // Compilation only; no DOM emulation or browser interaction.
const fixtureText = html.match(/<script id="fixture-data" type="application\/json">([\s\S]*?)<\/script>/)[1];
const fixtures = JSON.parse(fixtureText);
assert.equal(Object.keys(fixtures).length, 4);
assert.ok(html.includes("connect-src 'none'"));
assert.ok(!/<(?:script|link|img|iframe)\b[^>]*\b(?:src|href)=/i.test(html));
assert.ok(!/\b(?:fetch|XMLHttpRequest|WebSocket|EventSource|importScripts|eval)\s*\(/.test(bundle));
assert.ok(!/^import\s/m.test(bundle));
assert.ok(!/^export\s/m.test(bundle));
assert.ok(!/\/\*(?:FIXTURES|BUNDLE)\*\//.test(html));
const definition = fixtures['half-drain'];
const request = { environment: PROFILE_ID, ability: definition.id, target: 'fixture-target-A', event: 'fixture-event-A',
  raw_damage: 13, damage_basis: 'before_save_and_defenses', save_outcome: 'success', eligibility: 'confirmed',
  defense_coverage: 'confirmed', other_adjustments: 'none' };
const context = { environment: PROFILE_ID, ability: definition.id, target: request.target, event: request.event,
  profile_revision: PROFILE_REVISION, definition_revision: 'synthetic-fixture-1', defense_snapshot: 'fixed-benchmark-snapshot',
  defense_coverage: 'confirmed', definitions: { [definition.id]: definition },
  target_defenses: { resistance: ['psychic'], vulnerability: [], immunity: [] } };
for (let i = 0; i < 2000; i++) calculate(request, context);
const batchTimes = [];
for (let batch = 0; batch < 100; batch++) {
  const start = performance.now();
  for (let i = 0; i < 100; i++) assert.equal(calculate(request, context).damage_taken, 3);
  batchTimes.push((performance.now() - start) / 100);
}
batchTimes.sort((a, b) => a - b);
const report = { html_bytes: Buffer.byteLength(html), inline_script_bytes: Buffer.byteLength(bundle),
  build_syntax: 'pass', fixture_parse: 'pass', runtime_network_apis: 'none detected in static scan',
  external_resource_tags: 'none', csp_connect_src: 'none',
  benchmark: { runtime: process.version, scope: 'Node calculation + validation + assertion; not browser or AI latency',
    warmup: 2000, runs: 10000, batch_size: 100,
    median_batch_mean_ms_per_calculation: batchTimes[49], p95_batch_mean_ms_per_calculation: batchTimes[94] },
  browser_interaction: 'not_run: browser policy blocks file://; no workaround attempted',
  actual_ai_calls: 0, terminal_changes: false };
writeFileSync(new URL('build-check.json', path), JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify(report, null, 2));
