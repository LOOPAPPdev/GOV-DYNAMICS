# Dynamic governance master index

The root AGENTS.md is an instruction document, not an executable process.

On push to a repository branch, .github/workflows/master-index-autosync.yml scans committed documentation with scripts/sync_master_index.py. New records are appended to registry/master-index.csv and the workflow commits the index on the same branch. It runs validations and regression tests first.

## Commands

python scripts/sync_master_index.py --check
python scripts/sync_master_index.py --write
python scripts/validate_master_index.py

The script preserves the exact ten CSV columns, all existing IDs and curated metadata. New IDs use a deterministic hash of the repository path. Unknown metadata is left blank and new status is pending_review. Existing deleted or renamed paths cause failure; they are not removed without review.

Generated folder README placeholders are excluded. Agent and workflow YAML files, authored documents, Skills and deliverables are eligible. Files not committed to this repository are not discovered.

Workflow permissions must allow contents: write and the branch must allow the GitHub Actions bot to push. If these permissions are blocked, the workflow reports a failure rather than pretending to have persisted anything.

An update on a feature branch or an open PR is not visible in main until the PR is merged. Files in this public repository are already public when uploaded. The indexing script is not a secret scanner; review source material before committing.
