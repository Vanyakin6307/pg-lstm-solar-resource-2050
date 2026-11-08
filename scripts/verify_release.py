"""Verify repository artifacts against the canonical manifest and frozen SHA-256 list.

Standard library only. This does not train the LSTM or execute SAM.
"""
from pathlib import Path
import hashlib
import json
import csv
import sys

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = json.loads((ROOT / 'metadata' / 'RELEASE_FILES_SHA256.json').read_text(encoding='utf-8'))
errors = []
for item in EXPECTED['files']:
    rel = item['repository_path']
    p = ROOT / rel
    if not p.is_file():
        errors.append(f'MISSING: {rel}')
        continue
    sha = hashlib.sha256(p.read_bytes()).hexdigest()
    if sha != item['sha256']:
        errors.append(f'INVALID_SHA256: {rel} expected={item["sha256"]} got={sha}')
    else:
        print(f'OK SHA256 {rel}')

# Semantic checks of the key data product. SAM CSV contains 2 metadata rows plus 17520 observations.
final_file = ROOT / 'data/final/PI_LSTM_V24V1_2050_FINAL_RESOURCE.csv'
if final_file.is_file():
    with final_file.open(newline='', encoding='utf-8-sig') as f:
        rows = sum(1 for _ in csv.reader(f)) - 1
    if rows != 17520:
        errors.append(f'FINAL records: expected 17520, got {rows}')
    else:
        print('OK FINAL 2050: 17520 records')
sam_file = ROOT / 'data/final/Tumbabiro_PI_LSTM_V24V1_2050_SAM.csv'
if sam_file.is_file():
    with sam_file.open(newline='',encoding='utf-8-sig') as f:
        rows = sum(1 for _ in csv.reader(f))
    if rows != 17523:
        errors.append(f'SAM CSV physical lines: expected 17523, got {rows}')
    else:
        print('OK SAM CSV: 2 metadata rows, 1 header, 17520 records')
print(f'Checked {len(EXPECTED["files"])} SHA-256 records')
if errors:
    for e in errors: print('ERROR',e,file=sys.stderr)
    raise SystemExit(1)
print('PASS: archive integrity checks; computational replication still pending.')
