"""Regression tests: new agents must not break CI because of fixed counts."""
import tempfile
import unittest
from pathlib import Path

from scripts.validate_registry import validate


class RegistryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        for dirname in ("registry", "agents", "workflows"):
            (self.root / dirname).mkdir()
        for name, header in (
            ("tags.csv", "tag_id,xml_tag,category,original_label,status\n"),
            ("crosswalk.csv", "mapping_id,source_id,target_id,relation,approval_status\n"),
            ("aliases.csv", "alias_id,legacy_name,canonical_name,status,approved_by\n"),
            ("directory-index.csv", "directory_id,path,purpose,status\n"),
            ("master-index.csv", "document_id,path,title,category,version,status,source_url,owner,last_reviewed,related_requirement\n"),
        ):
            (self.root / "registry" / name).write_text(header, encoding="utf-8")
        (self.root / "registry/manifest.json").write_text("{}", encoding="utf-8")
        (self.root / "registry/aliases.json").write_text("{}", encoding="utf-8")
        self.add_agent("A-00")
        (self.root / "workflows/example.yaml").write_text(
            "id: example\nagent: A-00\nstatus: documentation_only\n", encoding="utf-8"
        )

    def add_agent(self, ident):
        (self.root / "agents" / f"{ident}.yaml").write_text(
            f"id: {ident}\nstatus: documentation_only\n", encoding="utf-8"
        )
        ids = sorted(path.stem for path in (self.root / "agents").glob("*.yaml"))
        contents = "schema_version: '1.0.0'\nagents:\n" + "".join(
            f"  - id: {item}\n    status: documentation_only\n" for item in ids
        )
        (self.root / "registry/agents.yaml").write_text(contents, encoding="utf-8")

    def test_dynamic_number_of_agents(self):
        self.add_agent("B-01")
        self.assertEqual(validate(self.root), [])

    def test_missing_registry_entry_fails_closed(self):
        self.add_agent("B-01")
        (self.root / "registry/agents.yaml").write_text(
            "agents:\n  - id: A-00\n", encoding="utf-8"
        )
        self.assertTrue(any("out of sync" in e for e in validate(self.root)))

    def test_unknown_workflow_agent_is_rejected(self):
        (self.root / "workflows/example.yaml").write_text(
            "id: example\nagent: UNKNOWN\nstatus: specified\n", encoding="utf-8"
        )
        self.assertTrue(any("unknown agent" in e for e in validate(self.root)))

    def test_invalid_yaml_is_rejected(self):
        (self.root / "agents/A-00.yaml").write_text("id: [\n", encoding="utf-8")
        self.assertNotEqual(validate(self.root), [])


if __name__ == "__main__":
    unittest.main()
