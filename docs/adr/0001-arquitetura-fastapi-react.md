# 0001 — Arquitetura FastAPI + React
- **Status:** Aceito
- **Data:** 02/10/2026

## Contexto
O sistema precisa de interface rica (tabelas, gráficos interativos, formulários de geração, lista de avisos) e de cálculos estatísticos em Python. O design das telas será feito no Claude Design, que produz HTML/React.

## Opções consideradas
1. **Streamlit** — muito rápido, mas personalização visual limitada; o design não seria reproduzível fielmente.
2. **Script único** — rápido no início, insustentável com 2–4 pessoas.
3. **FastAPI + React/Vite/TS** — duas aplicações, mas separação clara e liberdade total de UI.
4. FastAPI + Jinja2/HTMX — tudo em Python, interatividade limitada.

## Decisão
Opção 3. Backend FastAPI expõe o núcleo estatístico via JSON; frontend React + Vite + TypeScript consome a API e renderiza gráficos com `react-plotly.js`.

## Consequências
- (+) Design implementável fielmente; trabalho paralelo backend × frontend.
- (+) Contratos JSON explícitos (`docs/specs/14-api.md`) servem de documentação.
- (−) Dois processos para rodar (uvicorn + vite). Mitigação: README com comandos e proxy do Vite para `/api`.
- (−) CORS e tipagem duplicada. Mitigação: proxy do Vite em dev; tipos TS gerados do OpenAPI com `openapi-typescript` (D34).
