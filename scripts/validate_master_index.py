#!/usr/bin/env python3
"""Read-only validation of the governance master index."""
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "registry/master-index.csv"
FIELDS = ["document_id","path","title","category","version","status","source_url","owner","last_reviewed","related_requirement"]
errors = []
with INDEX.open(newline="", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    if reader.fieldnames != FIELDS:
        errors.append("Unexpected CSV header")
    rows = list(reader)
ids, paths = set(), set()
for n, row in enumerate(rows, 2):
    ident, rel = row.get("document_id", ""), row.get("path", "")
    if not ident or ident in ids: errors.append(f"line {n}: missing/duplicate document_id")
    if not rel or rel in paths: errors.append(f"line {n}: missing/duplicate path")
    ids.add(ident); paths.add(rel)
    path = (ROOT / rel).resolve()
    if not path.is_relative_to(ROOT): errors.append(f"line {n}: path traversal")
    elif not path.is_file(): errors.append(f"line {n}: missing file {rel}")
    if rel.startswith("registry/") and rel.endswith("master-index.csv"):
        errors.append(f"line {n}: master index cannot index itself")
if errors:
    print("\n".join(errors), file=sys.stderr)
    sys.exit(1)
print(f"PASS: {len(rows)} indexed documents; unique IDs and paths; all files exist")
