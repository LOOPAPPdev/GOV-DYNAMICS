# DOC-09 — Documentation intake

**Objetivo:** receber documentação existente, classificá-la e atualizar o Master Index sem perder proveniência.

## Operação
1. Fornecer os documentos e respetivos links de origem ao agente DOC-09.
2. O agente lê o conteúdo real de cada ficheiro e verifica a presença de segredos e dados sensíveis.
3. O agente escolhe o diretório existente de acordo com a responsabilidade principal; casos ambíguos ficam pendentes.
4. O agente verifica duplicados, nomes e IDs antes de preparar a alteração numa branch.
5. O agente adiciona uma linha por documento em `registry/master-index.csv`, mantendo o cabeçalho e as dez colunas existentes.
6. Executar `python scripts/validate_master_index.py` e solicitar revisão por pull request.
7. Integrar somente após aprovação.

## Estado
A especificação do agente e a validação do índice estão disponíveis. A importação automática de ficheiros externos, análise de conteúdo por LLM e criação automática de pull requests **não estão implementadas**. O índice começa vazio e não se deve inventar registos.
