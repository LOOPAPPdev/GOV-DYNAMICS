---
name: systemic-analysis
description: Analisar qualquer sistema delimitado mediante o pensamento sistémico; produzir iceberg, relações causais, loops, arquétipos, comportamento temporal, alavancagem, roadmap e verificação, distinguindo hipótese de evidência. Usar sempre que o utilizador pedir para analisar um sistema ou problema complexo, compreender causas recorrentes, mapear feedback loops ou diagramas causais (CLD), identificar arquétipos sistémicos, pontos de alavancagem ou roadmap de intervenção, mesmo que não diga "pensamento sistémico" nem "system dynamics".
---

# Systemic Analysis — LOOP Dynamics

Converte um problema complexo num `case.json` validado, com diagrama e relatório, onde cada afirmação aponta para evidência ou fica etiquetada como hipótese. Essa separação é o valor da skill: um diagrama causal sem ela parece conclusão quando é conjetura.

## Trigger

Usar quando o utilizador pedir para analisar um sistema, compreender um problema complexo, identificar causas recorrentes, mapear feedback loops, selecionar pontos de intervenção ou construir um roadmap sistémico.

## Pré-condições

1. Se estiver no repositório do agente, ler `AGENTS.md`, `docs/source-extraction.md`, `docs/workflow.md` e `schemas/case.schema.json`, e usar os `scripts/` do repositório. Fora dele, usar os equivalentes desta skill: `references/agent-rules.md`, `references/source-extraction.md`, `references/workflow.md`, `schemas/case.schema.json` e `scripts/` (cópias do pacote v1.0.0).
2. Confirmar nome e problema ou objetivo. Se faltarem dados, criar um caso `draft` sem valores inventados:
   `python scripts/new_case.py --id CASE-001 --name "…" --problem "…" --objective "…" --output case.json`
3. Determinar `system.method_fit` (`high|medium|low|unknown`) antes de modelar. Com `low`, dizer ao utilizador que outra abordagem é mais proporcional e não forçar loops ou arquétipos.

## Contrato de dados (`case.json` é a única fonte)

Usar exatamente estes nomes; o schema tem `additionalProperties: false`.

- Raiz: `workflow_version` ("1.0.0"), `case_id`, `status` (`draft|review_ready|externally_validated`), `system`, `evidence`, `iceberg`, `variables`, `links`, `loops`, `archetypes`, `behavior_hypotheses`, `leverage_points`, `roadmap`, `simulation`, `review`.
- `evidence[]`: `id` (`EV-…`), `kind` (`observation|measurement|document|interview|assumption`), `statement`, `status` (`verified|unverified`), `source`. Só marcar `verified` com fonte; uma `assumption` nunca é `verified`.
- `variables[]`: `id` `V1…`, `kind` (`stock|flow|auxiliary|exogenous|unknown`), `unit`, `evidence_ids`.
- `links[]`: `id` `L1…`, `source`, `target`, `polarity` (`+|-|unknown`), `delay` (`none|possible|confirmed|unknown`), `status` (`hypothesis|supported`), `evidence_ids`, `disconfirmation_test`. `supported` exige evidência `verified`.
- `loops[]`: `id` `R1…`/`B1…`/`U1…`, `link_ids` (ordem do ciclo, mínimo 2), `classification` (`reinforcing|balancing|undetermined`), `status`.
- `archetypes[]`, `behavior_hypotheses[]`, `leverage_points[]`, `roadmap[]`: ver `schemas/case.schema.json` para os campos; todos exigem condição de refutação ou critério de paragem.

## Execução (G0–G7, por ordem; detalhe em `references/workflow.md`)

- **G0** Definir sistema, fronteiras (`boundary_included/excluded`), `horizon`, stakeholders e a decisão que a análise informa.
- **G1** Iceberg: eventos → padrões → estruturas → modelos mentais. Ligar cada afirmação a `evidence_ids` ou tratá-la como hipótese. Sem observações longitudinais, não alegar padrões.
- **G2** `variables` e `links` com IDs únicos, sinal e atraso. Relação desconhecida: `polarity: "unknown"`. Sem evidência: `status: "hypothesis"` mais `disconfirmation_test`.
- **G3** Loops fechados e arquétipos. Calcular o tipo pelo produto dos sinais: número par de `-` = `reinforcing`, ímpar = `balancing`, qualquer `unknown` = `undetermined`. Arquétipo só com estrutura e teste de refutação; a aparência do diagrama não basta.
- **G4** Hipóteses temporais condicionais (`behavior_hypotheses`) com `time_horizon` e `disconfirmation_test`. Distinguir comportamento observado de explicação causal hipotética.
- **G4S** (opcional) Só com modelo formal, unidades, calibração e dados verificados; caso contrário `simulation.status = "not_performed"` com `results` vazio.
- **G5** Pontos de alavancagem por mecanismo, evidência, risco e viabilidade. Não prometer impacto não medido.
- **G6** Roadmap com `owner`, `indicator`, `checkpoint`, `stop_condition` e `approval_required`. Apresentar, não executar. Qualquer ação com efeito externo precisa de aprovação humana explícita.
- **G7** Verificar e entregar:
  1. `python scripts/validate_case.py case.json --strict`; corrigir erros e repetir.
  2. `python scripts/render_mermaid.py case.json --output diagram.mmd`.
  3. Escrever análise e handoff. Os avisos (`WARN`) medem incerteza, não falsidade, e não bloqueiam. `--strict` exige completude estrutural, não verdade empírica. A revisão externa fica pendente (`review.external_reviewer: null`) até ser realmente executada; nunca declarar `externally_validated` sem revisor e evidência.

## Entregas

- `case.json` validado estruturalmente.
- `diagram.mmd` gerado do caso (o diagrama é qualitativo, não um modelo calibrado).
- Relatório com `01_CONTEXT`, `02_ICEBERG`, `03_CAUSAL_MAP`, `04_LOOPS_ARCHETYPES`, `05_BEHAVIOR`, `06_LEVERAGE`, `07_ROADMAP`, `08_VALIDATION_AND_HANDOFF`.
- Em `08`: resultado do validador (colar a saída real), limitações, próximo gate e classificação VERIFIED, PARTIALLY VERIFIED, PROPOSED ou BLOCKED. O validador não verifica factos, por isso análise sem fontes verificadas é no máximo PROPOSED.

## Sem dados

Não alegar previsão, causalidade confirmada ou efeito quantitativo. Produzir a melhor análise qualitativa possível, etiquetar incertezas e listar as evidências mínimas para avançar (que medição, de que fonte, para que link ou hipótese). Um caso `draft` com poucos links e vários `unknown` é preferível a um caso completo com relações inventadas. Valores ilustrativos são demonstração, não evidência.

Atribuição: a ordem G0–G7, os campos JSON, gates e G4S são extensões de engenharia do pacote LOOP, não conteúdo do curso do Insper (ver `references/source-extraction.md`). Não os apresentar como metodologia oficial do Insper.

Responder no idioma do utilizador (pt-BR por defeito no repositório); manter IDs e chaves JSON como no schema.
