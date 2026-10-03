# Design — índice

Design das telas feito no Claude Design. Fonte visual: `telas/*.dc.html` (abrir `telas/Telas.dc.html` servindo a pasta por HTTP). Tokens: `frontend/src/shared/ui/tokens.css`.

| Arquivo | Ler quando |
|---|---|
| `handoff.md` | For começar a implementar o design (ordem por marco, interações, assets) |
| `tokens.md` | For usar cor, tipografia, espaço, raio ou sombra |
| `componentes.md` | For criar ou alterar algo em `shared/ui` |
| `telas.md` | For implementar uma etapa em `features/<etapa>` |
| `graficos-plotly.md` | For mexer em gráficos (frontend ou `dominios/graficos`) |
| `prompt-claude-design.md` | Quiser ver o pedido original |

## Princípios (do prompt e da spec 16)
1. Fluxo guiado em 8 etapas; simples primeiro, técnico recolhido ("Ver fórmula", "Detalhes técnicos").
2. O sistema explica o que fez: tipo, cálculo e alerta sempre com motivo.
3. Não aplicável aparece **esmaecido com motivo**, nunca some.
4. Tipo de variável e severidade: sempre **ícone + palavra + cor**.
5. Toda tela: carregando (skeleton), vazio (com próximo passo), erro (mensagem + ação), sucesso (toast).
6. Um número-chave por card, rótulo curto, interpretação em uma frase.

## Layout geral
```
┌──────────┬───────────────────────────────────────────────┐
│ Barra    │ Cabeçalho 64px                                 │
│ lateral  ├───────────────────────────────────────────────┤
│ 264px    │ main: padding 32px, max-width 1176px, gap 20–24│
│ (fixa)   │  "Etapa N de 8" 13/500 texto-2                 │
│          │  h1 28/700 −0,015em                            │
│          │  ajuda 15/400 texto-2                          │
│          │  conteúdo                                       │
└──────────┴───────────────────────────────────────────────┘
```
- Grid raiz: `grid-template-columns: 264px minmax(0,1fr)`; fundo `--cor-fundo`.
- Ações principais ficam no fim da tela, alinhadas à direita (primário por último).

## Responsivo
| Largura | Comportamento |
|---|---|
| ≥ 1280 px | Barra lateral expandida (264 px) |
| 768–1279 px | Barra recolhida em 72 px (só número/ícone de estado; nome em tooltip). Botão "Recolher barra"/hambúrguer abre sobreposta com `--sombra-3` e overlay. Grids de 3–4 cards viram 2 colunas; layouts lado a lado (tabela + gráfico) empilham |
| < 768 px | Leitura básica, 1 coluna (não é foco) |

## Acessibilidade (obrigatório)
- Contraste: texto ≥ 4,5:1; bordas de campo, ícones e séries de gráfico ≥ 3:1 nos dois temas (tokens já calibrados).
- Foco: `:focus-visible { outline: 2px solid var(--cor-foco); outline-offset: 2px }`. Nunca remover outline sem substituto.
- Alvos ≥ 24×24 px; botões e itens de etapa com 40–44 px de altura.
- Tabelas com `<th scope>`; gráficos com título descritivo ("Distribuição de peso_kg (n = 227)") + resumo textual ao lado + `aria-label`.
- Barra lateral: `<nav aria-label="Etapas da análise">`, `<ol>`, `aria-current="step"` na atual, `aria-disabled` nas bloqueadas.
- Abas: `role="tablist"/"tab"`, setas ←/→. Segmented: `role="radiogroup"`. Drawer: `role="dialog" aria-modal`, foco preso, Esc fecha e devolve foco.
- Editor de ordem (ordinais): arrastar **e** teclado (↑/↓ e botões Subir/Descer).
