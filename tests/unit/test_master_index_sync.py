"""Regression tests for non-destructive automatic master-index updates."""
import tempfile
import unittest
from pathlib import Path
from scripts.sync_master_index import FIELDS, collect, load_rows, render

class AutoIndexTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root/"registry").mkdir()
        (self.root/"docs/cases").mkdir(parents=True)
        (self.root/"catalog/skills").mkdir(parents=True)
        self.index = self.root/"registry/master-index.csv"
        self.index.write_text(",".join(FIELDS)+"\n")

    def test_append_idempotent_and_preserve_unknown_metadata(self):
        (self.root/"docs/cases/example.html").write_text("<html></html>")
        rows, n = collect(self.root,load_rows(self.index))
        self.assertEqual(n,1)
        self.assertEqual(rows[0]["status"],"pending_review")
        self.assertEqual(rows[0]["source_url"],"")
        self.assertEqual(rows[0]["last_reviewed"],"")
        self.index.write_text(render(rows))
        again, n = collect(self.root,load_rows(self.index))
        self.assertEqual(n,0)
        self.assertEqual(rows,again)

    def test_existing_document_metadata_is_immutable(self):
        (self.root/"catalog/skills/original.skill").write_bytes(b"original")
        row = dict.fromkeys(FIELDS,"")
        row.update(document_id="GOV-DOC-001",path="catalog/skills/original.skill",
                   status="specified",version="1.0.0",title="Curated title")
        self.index.write_text(render([row]))
        rows, n = collect(self.root,load_rows(self.index))
        self.assertEqual(n,0)
        self.assertEqual(rows[0],row)

    def test_missing_original_blocks_automatic_removal(self):
        row = dict.fromkeys(FIELDS,"")
        row.update(document_id="GOV-DOC-001",path="docs/missing.pdf")
        self.index.write_text(render([row]))
        with self.assertRaisesRegex(ValueError,"missing or renamed"):
            collect(self.root,load_rows(self.index))

    def test_placeholder_files_are_excluded(self):
        (self.root/"docs/README.md").write_text("# placeholder")
        (self.root/"registry/manifest.json").write_text("{}")
        rows, count = collect(self.root,load_rows(self.index))
        self.assertEqual((rows,count),([],0))

    def test_added_skill_does_not_change_existing_id(self):
        (self.root/"catalog/skills/old.skill").write_bytes(b"old")
        row = dict.fromkeys(FIELDS,"")
        row.update(document_id="GOV-DOC-001",path="catalog/skills/old.skill")
        self.index.write_text(render([row]))
        (self.root/"catalog/skills/new.skill").write_bytes(b"new")
        rows, count = collect(self.root,load_rows(self.index))
        self.assertEqual(count,1)
        self.assertEqual(rows[0]["document_id"],"GOV-DOC-001")

if __name__ == "__main__": unittest.main()
