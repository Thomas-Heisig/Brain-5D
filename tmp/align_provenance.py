import json
import subprocess
from pathlib import Path

root = Path('f:/Brain-5D')
head = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True, cwd=root).stdout.strip()

files = [
    'research/generated/verification/determinism_infrastructure.json',
    'research/generated/verification/restore_determinism.json',
    'research/generated/verification/single_listener.json',
    'research/generated/verification/structural_e2e.json',
    'research/generated/verification/structural_live_loop.json',
    'tests/test_baseline.json',
]

for rel in files:
    p = root / rel
    data = json.loads(p.read_text(encoding='utf-8'))
    if 'test_run_head' in data:
        data['test_run_head'] = head
    if 'tested_commit' in data:
        data['tested_commit'] = head
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(f'Updated {rel} -> {head[:8]}')
