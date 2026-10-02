# CLAUDE.md — Mapa de contexto

> Leia SÓ o que a tarefa exige. Este arquivo é o índice; os detalhes estão nos specs.

## Projeto
Analisador e Gerador de Dados — trabalho de Estatística. Backend **FastAPI** + núcleo **Python puro** (pandas/numpy/scipy/plotly); frontend **React + Vite + TypeScript** (react-plotly.js). Uso local, 1 usuário. Entrega final **08/12/2026**.

## Regras fixas
- Não adicionar autoria/coautoria de IA em commits, PRs, código ou docs. Não incluir seção "uso de IA" no relatório.
- Código, docs e textos de interface em **português**.
- **Antes de escrever qualquer código, leia `docs/padroes-codigo.md`** (limites: arquivo ≤ 500 linhas, ciclomática ≤ 10, cognitiva ≤ 15, aninhamento ≤ 3, zero duplicação; camadas e padrões de projeto).
- Monólito em camadas por domínio: `router → servico → domínio/repositório`. Domínios só conversam via `servico.py`. Código de domínio não importa FastAPI/Pydantic.
- Textos para o usuário seguem `docs/specs/16-ux-writing.md` (tom neutro, linguagem simples).
- Toda decisão nova → 1 linha em `docs/decisions.md`; decisão estrutural → ADR em `docs/adr/`.
- Toda mudança entregue → `CHANGELOG.md` (seção *Não lançado*).
- Commits: Conventional Commits (`feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`).

## Qual arquivo ler para cada tarefa
| Tarefa | Ler |
|---|---|
| Visão geral, escopo, premissas | `docs/specs/00-visao-geral.md` |
| Enunciado original do professor | `docs/requisitos-professor.md` |
| Cronograma / marcos | `docs/roadmap.md` |
| Leitura de arquivos (TXT/CSV/TSV/XLSX/JSON) | `docs/specs/01-leitura.md` |
| Classificação de tipos de variável | `docs/specs/02-tipos.md` |
| Limpeza de dados | `docs/specs/03-limpeza.md` |
| Tabelas de frequência | `docs/specs/04-frequencias.md` |
| Média, mediana, moda | `docs/specs/05-tendencia-central.md` |
| Quartis, decis, percentis, "onde está meu valor" | `docs/specs/06-separatrizes.md` |
| Amplitude, variância, DP, IQR, CV | `docs/specs/07-dispersao.md` |
| Escolha de gráficos por tipo | `docs/specs/08-graficos.md` |
| Normal/Binomial, assimetria, curtose | `docs/specs/09-distribuicoes-forma.md` |
| Correlação e regressão | `docs/specs/10-correlacao-regressao.md` |
| Gerador univariado/bivariado | `docs/specs/11-gerador.md` |
| Detector de dados artificiais | `docs/specs/12-detector.md` |
| Relatório HTML | `docs/specs/13-relatorio.md` |
| Endpoints e contratos da API | `docs/specs/14-api.md` |
| Telas e fluxo do frontend | `docs/specs/15-frontend.md` |
| Redação de textos/avisos | `docs/specs/16-ux-writing.md` |
| Tratamento de erros e testes | `docs/specs/17-erros-testes.md` |
| Design das telas (Claude Design) | `docs/design/` |
| Padrões de código, camadas, lint | `docs/padroes-codigo.md` |

## Estrutura
```
backend/app/core/          config, erros, handlers, logging
backend/app/compartilhado/ utils sem regra de negócio
backend/app/dominios/      datasets · analise · graficos · gerador · detector · relatorio
                           (cada um: router.py, schemas.py, servico.py, módulos de domínio)
backend/tests/             espelha app/
frontend/src/              app/ · features/<etapa>/ · shared/
dados-exemplo/             datasets de demonstração
docs/                      specs, adr, decisions, design
```

## Comandos (quando o código existir)
- Backend: `cd backend && uvicorn app.main:app --reload` · testes: `pytest` · lint: `ruff check . && complexipy app`
- Frontend: `cd frontend && npm run dev` · build: `npm run build`
