#!/usr/bin/env python3
"""Validate governance registry, agent specs and workflow references."""
from __future__ import annotations
import csv
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CSV_SCHEMAS = {
    "registry/tags.csv": ["tag_id", "xml_tag", "category", "original_label", "status"],
    "registry/crosswalk.csv": ["mapping_id", "source_id", "target_id", "relation", "approval_status"],
    "registry/aliases.csv": ["alias_id", "legacy_name", "canonical_name", "status", "approved_by"],
    "registry/directory-index.csv": ["directory_id", "path", "purpose", "status"],
    "registry/master-index.csv": [
        "document_id", "path", "title", "category", "version", "status",
        "source_url", "owner", "last_reviewed", "related_requirement"
    ],
}

def validate(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    for rel in ("registry/manifest.json", "registry/aliases.json"):
        try:
            value = json.loads((root / rel).read_text(encoding="utf-8"))
            if not isinstance(value, dict):
                errors.append(f"{rel}: expected a JSON object")
        except (OSError, ValueError) as exc:
            errors.append(f"{rel}: {exc}")

    for rel, expected in CSV_SCHEMAS.items():
        try:
            with (root / rel).open(newline="", encoding="utf-8-sig") as handle:
                reader = csv.DictReader(handle, strict=True)
                if reader.fieldnames != expected:
                    errors.append(f"{rel}: unexpected header: {reader.fieldnames!r}")
                for row_number, row in enumerate(reader, 2):
                    if None in row:
                        errors.append(f"{rel}:{row_number}: extra columns")
        except (OSError, UnicodeError, csv.Error) as exc:
            errors.append(f"{rel}: {exc}")

    def read_yaml(path: Path):
        try:
            obj = yaml.safe_load(path.read_text(encoding="utf-8"))
            if not isinstance(obj, dict):
                errors.append(f"{path.relative_to(root)}: expected a YAML mapping")
                return {}
            return obj
        except (OSError, UnicodeError, yaml.YAMLError) as exc:
            errors.append(f"{path.relative_to(root)}: {exc}")
            return {}

    agents = {}
    for path in sorted((root / "agents").glob("*.yaml")):
        spec = read_yaml(path)
        agent_id = spec.get("id")
        if not isinstance(agent_id, str) or agent_id != path.stem:
            errors.append(f"{path.relative_to(root)}: id must match filename")
        elif agent_id in agents:
            errors.append(f"duplicate agent ID: {agent_id}")
        else:
            agents[agent_id] = spec
        if not spec.get("status"):
            errors.append(f"{path.relative_to(root)}: missing status")

    registry = read_yaml(root / "registry/agents.yaml")
    entries = registry.get("agents", [])
    registered = []
    if not isinstance(entries, list):
        errors.append("registry/agents.yaml: agents must be a list")
        entries = []
    for item in entries:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str):
            errors.append("registry/agents.yaml: invalid agent entry")
        else:
            registered.append(item["id"])
    if len(registered) != len(set(registered)):
        errors.append("registry/agents.yaml: duplicate registered agent ID")
    if set(registered) != set(agents):
        errors.append(
            f"registry/agents.yaml out of sync: missing={sorted(set(agents)-set(registered))}; "
            f"orphan={sorted(set(registered)-set(agents))}"
        )

    workflows = set()
    for path in sorted((root / "workflows").glob("*.yaml")):
        spec = read_yaml(path)
        workflow_id = spec.get("id")
        if not isinstance(workflow_id, str) or workflow_id != path.stem:
            errors.append(f"{path.relative_to(root)}: id must match filename")
        elif workflow_id in workflows:
            errors.append(f"duplicate workflow ID: {workflow_id}")
        else:
            workflows.add(workflow_id)
        if not spec.get("status"):
            errors.append(f"{path.relative_to(root)}: missing status")
        if spec.get("agent") and spec["agent"] not in agents:
            errors.append(f"{path.relative_to(root)}: unknown agent {spec['agent']}")

    if not agents:
        errors.append("agents/: no YAML agent specifications")
    if not workflows:
        errors.append("workflows/: no YAML workflow specifications")
    return errors


if __name__ == "__main__":
    issues = validate()
    if issues:
        for issue in issues:
            print("FAIL:", issue, file=sys.stderr)
        sys.exit(1)
    print("PASS: JSON, CSV headers, YAML syntax, dynamic agent registry and workflow references")
