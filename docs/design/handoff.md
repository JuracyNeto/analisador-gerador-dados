# Handoff: Design system e telas — Analisador e Gerador de Dados

> Leia este arquivo primeiro. Ele é o ponto de entrada para implementar o design no repositório `JuracyNeto/analisador-gerador-dados` (branch `develop`).

## Visão geral
Design system (temas claro e escuro) e as 8 telas do fluxo guiado: 1 Importar · 2 Variáveis · 3 Limpeza · 4 Análise univariada · 5 Bivariada · 6 Gerador · 7 Detector · 8 Relatório. Atende WCAG 2.1 AA e as specs 15 (frontend) e 16 (UX writing).

## Sobre os arquivos de design
Os arquivos em `docs/design/telas/*.dc.html` são **referências de design feitas em HTML**: protótipos que mostram aparência e comportamento. **Não são código de produção.** A tarefa é **recriar estas telas no frontend React + Vite + TypeScript** do repositório, seguindo `docs/padroes-codigo.md` (features por etapa, `shared/ui`, react-query, Plotly sob demanda). Para abrir um protótipo, sirva a pasta `docs/design/telas/` por HTTP (ex.: `npx serve docs/design/telas`) e abra `Telas.dc.html` (todas as telas) ou `Design System.dc.html`.

## Fidelidade
**Alta fidelidade (hi-fi).** Cores, tipografia, espaçamentos, raios, estados e textos são finais. Recriar com precisão de pixel. Os gráficos são desenhos de referência do estilo; na implementação use **Plotly** com o tema de `docs/design/graficos-plotly.md`.

## Documentos
| Documento | Conteúdo |
|---|---|
| [README.md](README.md) | Índice, princípios, layout geral, responsivo, acessibilidade |
| [tokens.md](tokens.md) | Todos os tokens (cores claro/escuro, tipo, severidade, gráficos, tipografia, espaço, raio, sombra) |
| [componentes.md](componentes.md) | Componentes de `shared/ui`, medidas e todos os estados |
| [telas.md](telas.md) | Cada tela: layout, componentes, textos exatos, estados, mapeamento para `features/` |
| [graficos-plotly.md](graficos-plotly.md) | Tema Plotly e escolha de gráfico por tipo |

## Ordem sugerida de implementação (por marco do roadmap)
1. **M0:** `tokens.css`, provider de tema, layout (`BarraEtapas`, `Cabecalho`), componentes base de `shared/ui`, wrapper Plotly com tema.
2. **M1:** telas 1, 2, 3, 4 (Frequências, Tendência, Separatrizes, Dispersão, Gráficos), 8.
3. **M2:** tela 4 (Forma e distribuição) e tela 5.
4. **M3:** telas 6 e 7 (`CartaoAlerta`, drawer "Ver na tabela").

## Interações e estado (resumo)
- Estado do servidor só via react-query; estado de tela como união discriminada `{status:'carregando'}|{status:'erro',erro}|{status:'ok',dados}`.
- Etapas 2–8 bloqueadas até existir `datasetId`. Etapa concluída = já visitada com dados válidos.
- Tema: `data-tema` em `<html>`; padrão de `prefers-color-scheme`; escolha salva em `localStorage('tema')`.
- Toasts com `aria-live="polite"`, somem após 6 s (pausam com hover/foco). Erros com `role="alert"` e ação.
- Sem animações além de transições de 120 ms (`background-color`, `border-color`, `box-shadow`) e drawer entrando pela direita em 200 ms `cubic-bezier(.2,.8,.2,1)`. Respeitar `prefers-reduced-motion`.
Detalhes por tela em `telas.md`.

## Assets
- Fontes (Google Fonts): **Inter** 400/500/600/700 e **JetBrains Mono** 400/500/600. Em produção, preferir `@fontsource/inter` e `@fontsource/jetbrains-mono` (uso local, sem depender de rede).
- Ícones: **Material Symbols Rounded** (Google). Em produção, `@material-symbols/font-400` ou SVGs equivalentes. Nomes usados estão em `componentes.md` §Ícones. Ícones decorativos com `aria-hidden`; ícones sozinhos com `aria-label`.
- Nenhuma imagem raster.
