# 0008 — Design system com variáveis CSS e tema por atributo
- **Status:** Aceito
- **Data:** 02/10/2026

## Contexto
O design (Claude Design, `docs/design/`) define temas claro e escuro, cores semânticas para 6 tipos de variável e 3 severidades, e uma paleta de gráficos que precisa valer na tela (Plotly) e no relatório. As telas serão impressas em relatório e precisam de consistência.

## Opções consideradas
1. Variáveis CSS em `tokens.css` + atributo `data-tema` no `<html>`.
2. Tema em objeto TS (CSS-in-JS / styled-components).
3. Tailwind com tokens no config.

## Decisão
Opção 1. `frontend/src/shared/ui/tokens.css` é a fonte única; componentes usam `var(--token)` (CSS Modules por componente). Tema escolhido em `data-tema`, padrão por `prefers-color-scheme`, salvo em `localStorage`. O wrapper Plotly lê os tokens via `getComputedStyle` e mescla o `layout` do tema na figura vinda do backend (ADR 0003 continua valendo para dados e tipo de gráfico). O relatório usa os valores do tema claro, espelhados em `dominios/graficos/tema.py`.

## Consequências
- (+) Troca de tema sem re-render de React; tokens legíveis no DevTools e no handoff.
- (+) Sem dependência de biblioteca de estilos.
- (−) Valores do tema claro duplicados em Python para o relatório. Mitigação: teste que compara `tema.py` com `tokens.css`.
