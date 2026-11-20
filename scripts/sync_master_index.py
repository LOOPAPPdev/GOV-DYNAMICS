#!/usr/bin/env python3
"""Discover committed documents and update the canonical master index without data loss."""
import argparse
import csv
import hashlib
import io
import re
import sys
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
FIELDS = ["document_id","path","title","category","version","status","source_url","owner","last_reviewed","related_requirement"]
EXT = {".md",".mdx",".rst",".txt",".pdf",".html",".htm",".json",".jsonl",".yaml",".yml",".csv",".mmd",".svg",".drawio",".png",".jpg",".jpeg",".webp"}
ROOT_DOCS = {"README.md","AGENTS.md","CONTRIBUTING.md","SECURITY.md"}
BLOCKED = {".git","node_modules",".venv","__pycache__","dist","build","secrets","credentials","private"}

def eligible(path):
    parts = path.parts
    if len(parts) == 1:
        return path.as_posix() in ROOT_DOCS
    if any(p in BLOCKED for p in parts) or path.name in {"README.md",".gitkeep",".DS_Store"}:
        return False
    if path.name.startswith(".") or path.suffix.lower() in {".pem",".key",".p12"}:
        return False
    area = parts[0]
    if area in {"docs","agents","workflows","config","infrastructure"}:
        return path.suffix.lower() in EXT
    if area == "catalog":
        return path.suffix.lower() in EXT | {".skill",".py"}
    if area == "packages":
        return parts[:2] == ("packages","contracts") and path.suffix.lower() in EXT
    if area in {"apps","services","tests","data"}:
        return path.suffix.lower() in {".md",".mdx",".rst",".txt",".pdf",".html",".mmd"}
    return False

def category(path):
    parts = path.parts
    if len(parts) == 1: return "governance"
    if parts[:2] == ("catalog","skills"):
        return "skill" if path.suffix.lower() == ".skill" else "skill-source"
    if parts[:2] == ("docs","cases"): return "deliverable"
    if parts[0] == "docs": return "docs-" + (parts[1] if len(parts)>2 else "general")
    return {"agents":"agent","workflows":"workflow","packages":"contract",
            "catalog":"catalog","config":"configuration","infrastructure":"infrastructure",
            "apps":"frontend","services":"backend","data":"data","tests":"verification"}.get(parts[0],"document")

def title(path, full):
    if path.suffix.lower() == ".md":
        try:
            with full.open(encoding="utf-8") as f:
                for _, line in zip(range(32), f):
                    match = re.match(r"^# (.+?)\s*$", line)
                    if match: return match.group(1).strip()
        except UnicodeError:
            pass
    return path.stem.replace("_"," ").strip() or path.name

def load_rows(index):
    with index.open(encoding="utf-8-sig",newline="") as f:
        reader = csv.DictReader(f,strict=True)
        if reader.fieldnames != FIELDS:
            raise ValueError("Master Index CSV header differs from the ten canonical columns")
        rows = list(reader)
    ids, paths = set(), set()
    for row in rows:
        if None in row or any(v is None for v in row.values()):
            raise ValueError("Malformed CSV row")
        ident, rel = row["document_id"], row["path"]
        pure = PurePosixPath(rel)
        if not ident or ident in ids: raise ValueError("Empty or duplicate document ID: "+ident)
        if not rel or rel != pure.as_posix() or pure.is_absolute() or ".." in pure.parts or rel in paths:
            raise ValueError("Unsafe or duplicate path: "+rel)
        ids.add(ident); paths.add(rel)
    return rows

def collect(root, rows):
    known = {r["path"] for r in rows}
    ids = {r["document_id"] for r in rows}
    count = 0
    for full in sorted(root.rglob("*")):
        if not full.is_file() or full.is_symlink(): continue
        path = PurePosixPath(full.relative_to(root).as_posix())
        if not eligible(path) or path.as_posix() in known: continue
        ident = "GOV-DOC-" + hashlib.sha256(path.as_posix().encode()).hexdigest()[:12].upper()
        if ident in ids: raise ValueError("ID collision: "+ident)
        row = dict.fromkeys(FIELDS,"")
        row.update(document_id=ident,path=path.as_posix(),title=title(path,full),
                   category=category(path),status="pending_review")
        rows.append(row); known.add(path.as_posix()); ids.add(ident); count += 1
    for row in rows:
        full = (root / row["path"]).resolve()
        if not full.is_relative_to(root.resolve()) or not full.is_file():
            raise ValueError("Indexed file missing or renamed: "+row["document_id"]+" -> "+row["path"])
    return rows, count

def render(rows):
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output,fieldnames=FIELDS,lineterminator="\n")
    writer.writeheader(); writer.writerows(rows)
    return output.getvalue()

def main():
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write",action="store_true")
    mode.add_argument("--check",action="store_true")
    args = parser.parse_args()
    try:
        path = ROOT / "registry/master-index.csv"
        rows, count = collect(ROOT,load_rows(path))
        if count and args.check:
            print("FAIL: "+str(count)+" documents absent from master index",file=sys.stderr)
            return 1
        if count and args.write: path.write_text(render(rows),encoding="utf-8")
        print(("UPDATED" if count and args.write else "PASS")+": "+str(len(rows))+" indexed, "+str(count)+" new")
        return 0
    except (OSError,UnicodeError,ValueError,csv.Error) as exc:
        print("FAIL: "+str(exc),file=sys.stderr)
        return 1

if __name__ == "__main__": sys.exit(main())
