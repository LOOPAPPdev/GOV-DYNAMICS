# Procedimento do agente · G0–G7

## Interface

**Input**: `system.name`, `system.problem`, `system.objective`; opcionais `horizon`, fronteiras, stakeholders, fontes e medições. **Output**: `case.json`, `diagram.mmd`, análise e handoff. **Fonte única**: `case.json`.

| Gate | Entrada | Ação do agente | Saída e critério de avanço |
|---|---|---|---|
| **G0 · Delimitar** | Nome, problema, objetivo | Verificar se há interdependência e dinâmica no tempo. Declarar fronteiras, período e stakeholders. | Declaração do sistema e `METHOD_FIT`. `STOP` quando não existe adequação mínima. |
| **G1 · Iceberg** | Problema delimitado, dados | Separar eventos observáveis, padrões, estruturas geradoras e modelos mentais. Ligar cada afirmação à fonte ou rotular hipótese. | Quatro camadas com lacunas visíveis. Sem alegar padrão sem observações longitudinais. |
| **G2 · Causas** | Iceberg, evidências | Identificar variáveis, relações causais, sinais `+/-/unknown`, possíveis atrasos e fronteiras de causalidade. | Grafo com IDs únicos e referência de evidência por relação. Relações hipotéticas identificadas. |
| **G3 · Loops e arquétipos** | Grafo causal | Procurar ciclos fechados, calcular polaridade estrutural e procurar padrões de arquétipos. | Loops fechados e consistentes. Arquétipos só quando há estrutura e hipótese refutável. |
| **G4 · Comportamento** | Loops, histórico disponível | Formular hipóteses de comportamento ao longo do tempo e condições de refutação. | Hipóteses temporais qualitativas. Sem previsão quantitativa automática. |
| **G4S · Simulação opcional** | Modelo formal + dados | Somente se houver equações/regras, unidades, condições iniciais, calibração/validação e análise de sensibilidade adequadas. | Simulação documentada ou `not_performed`. Nunca confundir resultados hipotéticos com medições reais. |
| **G5 · Alavancagem** | Estruturas e loops | Identificar variáveis e regras cuja alteração possa mudar o comportamento. Comparar mecanismo, evidência, riscos e viabilidade. | Candidatos rastreáveis; nenhuma classificação de alto impacto sem justificativa. |
| **G6 · Intervenção** | Pontos de alavancagem | Criar roadmap de ações com responsável, indicador, checkpoint, riscos, reversibilidade e critério de paragem. | Plano executável, sem aplicar mudanças no mundo real. |
| **G7 · Verificação** | Caso completo | Validar integridade JSON, IDs, links, loops, citações e incertezas. Submeter a especialista/decisor para validação externa quando necessário. | `analysis.md` e `handoff.md`, com status `draft`, `review_ready` ou `externally_validated` apenas com evidência real. |

## Regras THEN/IF obrigatórias

- **WHEN** o problema não tiver comportamento temporal ou relações relevantes **THEN** assinalar `METHOD_FIT: LOW` e não inventar um loop.
- **IF** não houver histórico **THEN** descrever os padrões como hipóteses, nunca como fatos estabelecidos.
- **IF** uma relação não estiver documentada **THEN** usar `status: hypothesis` e registrar o que a refutaria.
- **IF** uma ligação tiver polaridade desconhecida **THEN** a classificação automática do loop MUST ser `undetermined`.
- **IF** um loop não fechar **THEN** não tratá-lo como loop; retornar ao G2.
- **IF** não existirem medições/equações suficientes **THEN** a simulação deve manter-se `not_performed`.
- **WHEN** uma ação real afetar pessoas, orçamento ou sistemas externos **THEN** obter aprovação humana explícita antes de agir.
- **IF** um resultado for gerado apenas por valores ilustrativos **THEN** assinalá-lo como demonstração, não evidência empírica.
- **WHEN** o agente mudar de contexto **THEN** preservar `case.json`, gates concluídos, evidências e o próximo passo no handoff.

## Testes de aceitação (Gherkin)

**AT-01 · Dados de entrada**
GIVEN um nome, um problema e um objetivo WHEN o caso é criado THEN os campos existem e o status permanece `draft`.

**AT-02 · Integridade do grafo**
GIVEN uma ligação para variável inexistente WHEN a validação é executada THEN a ligação falha com referência ao ID.

**AT-03 · Feedback correto**
GIVEN um loop fechado com uma ligação negativa WHEN o tipo é calculado THEN o resultado é `balancing`.

**AT-04 · Ausência de evidências**
GIVEN uma alegação causal sem dados WHEN o agente responde THEN a ligação é rotulada `hypothesis` e a confiança não é apresentada como verificada.

**AT-05 · Não simular indevidamente**
GIVEN ausência de dados e equações validadas WHEN o agente chega a G4S THEN o resultado é `not_performed`.

**AT-06 · Segurança de intervenção**
GIVEN uma proposta com impacto externo WHEN o agente termina o roadmap THEN apresenta a proposta sem executá-la.
