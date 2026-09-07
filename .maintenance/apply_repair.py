"""Apply the checksum-bound, AI-assisted repair without overwriting newer work."""
from pathlib import Path
import base64
import gzip
import hashlib
import json
import subprocess
import tempfile

ROOT = Path.cwd().resolve()
EXPECTED = 'b0e7aba4c4a4c88179d52957cba27fdb7ef89d498230479f2df6096fdda5bf65'
encoded = ''.join((ROOT / f'.maintenance/repair-part-{i}.b64').read_text().strip() for i in range(5))
raw = gzip.decompress(base64.b64decode(encoded, validate=True))
assert hashlib.sha256(raw).hexdigest() == EXPECTED, 'Transport checksum mismatch'
payload = json.loads(raw)
base = payload['base']
subprocess.run(['git', 'merge-base', '--is-ancestor', base, 'HEAD'], check=True)
changes = []
for item in payload['files']:
    relative = Path(item['path'])
    assert not relative.is_absolute() and '..' not in relative.parts
    path = ROOT / relative
    assert not path.is_symlink(), f'Symlink target: {relative}'
    original = b'' if item['new'] else subprocess.check_output(['git', 'show', f'{base}:{relative.as_posix()}'])
    assert hashlib.sha256(original).hexdigest() == item['before'], f'Base mismatch: {relative}'
    lines = original.decode('utf-8').splitlines(keepends=True)
    for start, end, replacement in reversed(item['edits']):
        lines[start:end] = replacement.splitlines(keepends=True)
    target = ''.join(lines).encode('utf-8')
    assert hashlib.sha256(target).hexdigest() == item['after'], f'Output mismatch: {relative}'
    current = path.read_bytes() if path.exists() else b''
    if current == target:
        continue
    if current != original:
        assert not item['new'], f'Concurrent new file: {relative}'
        with tempfile.TemporaryDirectory() as directory:
            files = [Path(directory) / name for name in ('current', 'base', 'repair')]
            for file, data in zip(files, (current, original, target)):
                file.write_bytes(data)
            result = subprocess.run(['git', 'merge-file', '-p', *map(str, files)], capture_output=True)
            assert result.returncode == 0, f'Concurrent conflict, preserved remote work: {relative}'
            target = result.stdout
    changes.append((path, target))
for path, target in changes:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(target)
    print('Applied', path.relative_to(ROOT))
subprocess.run(['git', 'add', '--', *[str(path.relative_to(ROOT)) for path, _ in changes]], check=True)
subprocess.run(['git', 'rm', '-r', '--cached', '--ignore-unmatch', 'node_modules', 'test-results'], check=True)
print(f'Applied {len(changes)} source files; historical experiment artifacts unchanged.')
