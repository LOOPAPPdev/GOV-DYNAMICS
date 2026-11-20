# AGENTS.md — GOV-DYNAMICS

This repository is documentation-only. This instruction file is not a daemon and never stores data by itself.

## Dynamic master index

WHEN files are committed on a branch, THEN the workflow in .github/workflows/master-index-autosync.yml runs scripts/sync_master_index.py --write. The workflow records missing files in registry/master-index.csv and commits the changes on the same branch. It does not import external documents from other apps.

MUST retain the existing ten CSV columns. MUST preserve existing IDs, titles, owners, versions, status, source links, review dates and requirement references. MUST NOT invent missing metadata. MUST NOT delete or overwrite indexed records. MUST fail closed if an indexed file is removed or renamed.

New IDs are deterministic path hashes and new records receive status pending_review. Run python scripts/sync_master_index.py --check to test completeness without changes. Run python scripts/validate_master_index.py to test integrity.

A pending PR branch is separate from main. An updated index on the PR branch appears in main only after merge.

DOC-09 is specified in agents/DOC-09.yaml and workflows/document-intake.yaml. It is not a running autonomous service. This public repository MUST NOT store secrets or personal records.

Follow Spec → Plan → TDD → Verify and obtain human approval for consequential changes. Preserve registry/manifest.json, aliases and crosswalk when semantics or IDs change. Do not claim tests or compliance without evidence.
