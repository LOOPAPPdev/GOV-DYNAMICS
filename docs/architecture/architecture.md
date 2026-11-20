# Architecture

Design: documentation mirror for modular TypeScript + Python monorepo, one React frontend, FastAPI modular backend, Python core/harness/knowledge/dynamics. Runtime persistence is external. Cloudflare Pages is a proposed frontend deployment target and R2 object storage is proposed. OIDC/RBAC/ACL, SSE, CI/CD and HITL are crosscutting concerns.

## Dependency order

A. Registry + contracts → B. Core + Knowledge → C. Agent Harness + Dynamics → D. API + Web → E. Verify + Deploy.

**Note:** implementation, integration, deployment and normative compliance are unverified.
