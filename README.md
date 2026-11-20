# GOV-DYNAMICS

Documentação de governança da arquitetura **Manus LEGO / LOOP Dynamics**. Esta estrutura espelha estritamente os diretórios e os nomes de ficheiros solicitados, mas não implementa um produto executável. A persistência operacional é externa ao repositório.

## Arquitetura

- `apps/web`: React + TypeScript + Vite + React Flow + Mermaid (proposto).
- `services/api`: FastAPI + SSE + OIDC + RBAC + Pydantic (proposto).
- `packages/python`: Core, Harness, Knowledge/RAG e Dynamics.
- `agents/`, `workflows/`: especificações declarativas.
- `registry/`, `packages/contracts/`: IDs, schemas, aliases, compatibilidade.
- `infrastructure/`, `tests/`, `.github/`: documentação de deploy e verificação.

## Ordem de dependências

A. Registry + Contracts → B. Core + Knowledge → C. Agent Harness + Dynamics → D. API + Web → E. Verify + Deploy.

## Estado

A estrutura física existe para receber documentação. Os módulos de aplicação, segurança, testes de integração, build e deploy não foram implementados. `pnpm-lock.yaml` e `uv.lock` só devem ser adicionados após geração pelos gestores de dependências; nunca se devem fabricar lockfiles. Os diretórios vazios têm `.gitkeep` para preservação no Git. Não submeter credenciais nem bases de dados operacionais.
