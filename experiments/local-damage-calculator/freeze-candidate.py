"""Freeze an allowlisted, local-only integration candidate; never a public Package release."""
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
DEST = ROOT / 'build/local-damage-calculator-candidate-2026-10-23-r1'
SOURCE = 'experiments/local-damage-calculator/'
FILES = [SOURCE + name for name in [
    'profile.mjs', 'snapshot.mjs', 'engine.mjs', 'compare.mjs', 'demo.mjs',
    'index.template.html', 'build.py', 'check-bundle.mjs', 'test.mjs',
    'compare-regression.test.mjs', 'synthetic-fixtures.json', 'README.md',
    'candidate-revision.json', 'freeze-candidate.py',
]] + [
    'docs/milestone-2/local-damage-calculator-cases-2026-10-22.json',
    'docs/milestone-2/local-damage-calculator-fix-2026-10-23.md',
    'build/local-damage-calculator-research-2026-10-22/index.html',
    'build/local-damage-calculator-fix-2026-10-23/prepatch-reproduction.json',
    'build/local-damage-calculator-fix-2026-10-23/tests.tap',
    'build/local-damage-calculator-research-2026-10-22/build-check.json',
]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def verify(folder):
    manifest_path = folder / 'candidate-manifest.json'
    manifest = json.loads(manifest_path.read_text())
    expected = {'candidate-manifest.json', 'SHA256SUMS'}
    sums = []
    for row in manifest['files']:
        rel = row['path']
        if Path(rel).is_absolute() or '..' in Path(rel).parts:
            raise ValueError('Invalid candidate path')
        p = folder / rel
        if p.is_symlink() or not p.is_file():
            raise ValueError(f'Missing/unsafe candidate file: {rel}')
        data = p.read_bytes()
        if len(data) != row['bytes'] or digest(data) != row['sha256']:
            raise ValueError(f'Candidate drift: {rel}')
        expected.add(rel)
        sums.append(f"{row['sha256']}  {rel}")
    sums.append(f'{digest(manifest_path.read_bytes())}  candidate-manifest.json')
    if (folder / 'SHA256SUMS').read_text() != '\n'.join(sums) + '\n':
        raise ValueError('Checksum receipt mismatch')
    actual = {str(p.relative_to(folder)) for p in folder.rglob('*') if p.is_file() or p.is_symlink()}
    if actual != expected:
        raise ValueError('Unexpected/missing candidate payload')
    print(json.dumps({'candidate': str(folder), 'payload_files': len(manifest['files']),
                      'sha256_validation': 'pass', 'terminal_acceptance': 'not_run'}, ensure_ascii=False))


if len(sys.argv) > 1:
    if len(sys.argv) != 3 or sys.argv[1] != '--verify':
        raise SystemExit('Usage: freeze-candidate.py [--verify CANDIDATE_DIRECTORY]')
    verify(Path(sys.argv[2]).resolve())
else:
    if DEST.exists():
        raise SystemExit('Candidate already fixed; verify it or use a separately reviewed new revision.')
    contents = {rel: (ROOT / rel).read_bytes() for rel in FILES}
    revision = json.loads(contents[SOURCE + 'candidate-revision.json'])
    rows = []
    for rel, data in sorted(contents.items()):
        output = DEST / 'payload' / rel
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(data)
        rows.append({'path': 'payload/' + rel, 'bytes': len(data), 'sha256': digest(data)})
    manifest = {'artifact_kind': 'local_integration_candidate_not_public_release',
                'candidate_revision': revision, 'prepared_on': '2026-10-23',
                'scope': 'two comparator fixes only; original arithmetic/rule scope retained',
                'tests': {'total': 73, 'passed': 73, 'original': 55, 'new_regression': 18},
                'not_run': ['browser interaction', 'Terminal acceptance', 'real AI', 'automatic escalation', 'battle state writes'],
                'files': rows,
                'checksum_scope': 'payload + manifest; SHA256SUMS excludes itself; checksums are not signatures or rights approval'}
    (DEST / 'candidate-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    sums = [f"{r['sha256']}  {r['path']}" for r in rows]
    sums.append(f"{digest((DEST / 'candidate-manifest.json').read_bytes())}  candidate-manifest.json")
    (DEST / 'SHA256SUMS').write_text('\n'.join(sums) + '\n')
    verify(DEST)
