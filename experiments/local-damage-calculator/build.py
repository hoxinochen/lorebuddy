"""Deterministically inline our modules and synthetic fixtures; no network or dependencies."""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT.parents[1] / 'build/local-damage-calculator-research-2026-10-22/index.html'
modules = []
for name in ['profile.mjs', 'snapshot.mjs', 'engine.mjs', 'compare.mjs', 'demo.mjs']:
    source = (ROOT / name).read_text()
    source = re.sub(r'^import .*?;\n', '', source, flags=re.M)
    source = re.sub(r'^export (?=(?:const|function) )', '', source, flags=re.M)
    modules.append('{\n' + source + '\n}' if name == 'demo.mjs' else source)
# Modules other than demo have a very small, explicit top-level vocabulary.
# Compare module's private BINDINGS/STAGES names do not collide with engine names.
bundle = '\n'.join(modules)
assert '</script' not in bundle.lower()
data = json.dumps(json.loads((ROOT / 'synthetic-fixtures.json').read_text()), ensure_ascii=False).replace('<', '\\u003c')
page = (ROOT / 'index.template.html').read_text().replace('/*FIXTURES*/', data).replace('/*BUNDLE*/', bundle)
assert '/*FIXTURES*/' not in page and '/*BUNDLE*/' not in page
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text(page, encoding='utf-8')
print(json.dumps({'output': str(OUTPUT), 'bytes': OUTPUT.stat().st_size}, ensure_ascii=False))
