# Componentes (`frontend/src/shared/ui`)

Referência visual: `telas/Design System.dc.html` §Componentes. Medidas em px. Todos os interativos: `:focus-visible` com anel 2 px `--cor-foco`, offset 2. Transição 120 ms em cores e sombra.

## Botao
Props: `variante: 'primario'|'secundario'|'fantasma'|'perigo'`, `carregando?`, `icone?`, `tamanho?: 'md'|'lg'`. Altura 40 (md) / 44 (lg); padding 0 16 (fantasma 0 12); raio 8; texto 14–15; ícone 18–20 com gap 8.
| Variante | Padrão | Hover | Ativo | Desabilitado |
|---|---|---|---|---|
| primario | bg primaria, texto sobre-primaria, 600 | bg primaria-hover | bg primaria-ativa | bg superficie-2, texto desab |
| secundario | bg superficie, borda 1 borda-forte, texto, 500 | bg superficie-2 | bg borda, borda texto-2 | borda borda, texto desab |
| fantasma | texto primaria, 500 | bg primaria-suave | bg mix 18% primaria | texto desab |
| perigo | borda 1 erro, texto erro, bg superficie, 600 | bg erro-suave | bg erro, texto superficie | borda borda, texto desab |
Carregando: spinner 14 (borda 2 currentColor, lado direito transparente, rotação 0,8 s linear) + verbo no gerúndio ("Calculando…"); `aria-busy`, botão desabilitado.

## CampoTexto / CampoNumero
Rótulo acima 13/500, gap 6. Campo 40 alto, padding 0 12, raio 8, borda 1 borda-forte, bg superficie, valor em mono 14–15. Hover: borda texto-2. Foco: borda foco + outline 2 foco offset 1. Desabilitado: bg superficie-2, borda borda, texto desab. Erro: borda 2 erro + linha abaixo com ícone `error` 16 e mensagem 13 erro no formato "{o que}. {como resolver}." (`aria-invalid`, `aria-describedby`). Números aceitam vírgula decimal.

## Select
Igual ao campo + ícone `expand_more` 20 texto-2 à direita. Lista: bg superficie-elevada, borda, raio 8, sombra-2, padding 4; item 36 alto, raio 6; selecionado bg primaria-suave, texto primaria 500 + `check`; item inválido em texto desab com motivo ("Binária · precisa de 2 valores"). Usar listbox acessível (ex.: Radix/Headless UI ou nativo `<select>`).

## Segmented
Container: padding 3, raio 8, bg superficie-2, borda 1 borda, gap 2. Segmento 32 alto, padding 0 14, raio 6, 14. Selecionado: bg superficie, sombra-1, 600, texto; demais texto-2. `role="radiogroup"`.

## Abas
Barra com borda inferior 1 borda, gap 4. Aba 44 alto, padding 0 14, 14. Ativa: texto primaria 600 + `box-shadow: inset 0 -2px 0 var(--cor-primaria)`. Hover: texto. Não aplicável: texto desab + ícone `block` 16, `aria-disabled`, tooltip com motivo.

## ChipTipo
`<ChipTipo tipo="continua" curto />`. Altura 26, padding 0 10 0 8, raio 999, gap 6, 13/600; bg `--tipo-X-suave`, texto `--tipo-X`, borda 1 `color-mix(in oklab, var(--tipo-X) 35%, transparent)`; ícone 17. Identificador: borda tracejada. Variante "corrigido": selo 11/500 bg superficie texto-2. Tooltip com o nome completo.

## BadgeSeveridade
Altura 26 (24 no drawer), padding 0 10 0 8, raio 6, 13/600, bg `--sev-X-suave`, texto `--sev-X`, ícone preenchido 18 (`font-variation-settings:'FILL' 1`).

## CardMetrica
- `tamanhoValor="menor"` (26 px) para valores longos, como a equação da reta (tela 5a).
Props: `rotulo, valor, unidade?, interpretacao, selo?, formula?: {expressao, calculo}`, `naoAplicavel?: {motivo}`. bg superficie, borda 1 borda, raio 12, sombra-1, padding 18 20, gap 6. Rótulo 13/500 texto-2; valor mono 32–34/600 com unidade 16/500 texto-2 (margem 4–6); selo opcional 12,5/600 bg primaria-suave texto primaria raio 6 padding 2 8 ("Variação moderada"); interpretação 14/1,5; botão fantasma "Ver fórmula"/"Ocultar fórmula" com `expand_more/less`. Fórmula aberta: bloco bg superficie-2 raio 8 padding 12 14, expressão mono 16/500 centralizada + cálculo mono 12,5 texto-2.
**Não aplicável:** borda 1 tracejada borda-forte, bg superficie-2, sem sombra; rótulo + selo "Não se aplica" (11,5/600, borda 1 borda-forte, raio 4); valor "—" em texto desab; motivo 14 texto-2 no formato "{medida} não se aplica a {tipo}: {motivo}."

## Tabela
Container borda 1 borda raio 10–12 overflow hidden. Cabeçalho fixo (`position: sticky; top: 0`) bg superficie-2, 12,5/600, borda inferior 1 borda-forte; nomes de coluna em mono. Células padding 8–10 × 16–20, 13,5–14, números à direita com tabular-nums. Zebra: linhas pares `--cor-zebra`. Destacada: bg `--cor-destaque-linha` + `box-shadow: inset 3px 0 0 var(--sev-atencao)` (ou cor da severidade) + valor em 600. Faltante: "—" ou "vazio" itálico texto-2. Rodapé: "Linhas 119–123 de 230", contagem de destacadas com ícone, paginação com botões 32×32 (`chevron_left/right`, `aria-label`). Mais de 200 linhas → virtualizar.

## AreaUpload
Borda 2 tracejada borda-forte, raio 16, bg superficie, min-height 400, conteúdo centralizado gap 16: círculo 72 bg primaria-suave com `upload_file` 36; "Arraste e solte seu arquivo aqui" 20/600; "ou escolha no computador. Tamanho máximo: 50 MB." 15 texto-2; Botao primário lg "Escolher arquivo" (`folder_open`); formatos como etiquetas mono 13 (padding 4 10, raio 6, bg superficie-2, borda). Arrastando: borda primaria, bg primaria-suave, texto "Solte para enviar". Enviando: barra de progresso 6 px. Erro: borda erro, bg erro-suave. Também acessível por teclado (é um `<button>`/`<label>` do input file).

## BarraEtapas (stepper lateral)
Ver `telas/Barra Lateral.dc.html`. Largura 264, bg superficie, borda direita. Topo 64 alto com marca (quadrado 28 raio 8 primaria com "x̄" mono 13/600) + "Analisador e Gerador" 14/600 / "de Dados" 12 texto-2. Lista padding 12 gap 2; item 44 alto, padding 0 12, raio 8, gap 12, 14.
| Estado | Marcador 26×26 | Item |
|---|---|---|
| Concluída | círculo bg sucesso-suave, `check` 18/600 sucesso | texto; à direita "Concluída" 12/500 sucesso; hover superficie-2 |
| Atual | círculo bg primaria, número mono 12/600 sobre-primaria | bg primaria-suave, texto primaria 600, `aria-current="step"` |
| Disponível | círculo borda 1,5 borda-forte, número texto-2 | texto; hover superficie-2 |
| Bloqueada | círculo borda 1,5 tracejada borda, número | texto desab + `lock` 18 (`aria-label="Bloqueada"`) |
Com etapas bloqueadas, frase 12 texto-2: "As etapas 2 a 8 ficam disponíveis depois que você importar um arquivo." Rodapé: botão "Recolher barra" (`left_panel_close`).

## Cabecalho
64 alto, padding 0 32, bg superficie, borda inferior. Esquerda: `description` 22 + nome do arquivo mono 14/600 + "230 linhas × 8 colunas" 13 texto-2. Direita: Botao secundário 36 "Trocar arquivo" (`swap_horiz`) + alternância de tema (pílula com 2 botões 30×30, `light_mode`/`dark_mode`, selecionado bg superficie + sombra-1; `role="radiogroup" aria-label="Tema"`). Sem arquivo: "Nenhum arquivo importado".

## Toast
Canto superior direito abaixo do cabeçalho (top 80, right 32), largura 380, bg superficie-elevada, borda, raio 10, sombra-2, padding 14 16, gap 12. Ícone 22 preenchido (`check_circle` sucesso / `error` erro), título 14/600 no formato "verbo no passado + quantidade" ("Limpeza aplicada: 12 linhas removidas."), apoio 13 texto-2, fechar `close`. Sucesso `role="status"`; erro `role="alert"` com ação fantasma ("Tentar de novo").

## Drawer
Lateral direita, largura 600, altura total, bg superficie-elevada, sombra-3, overlay `--cor-overlay`. Cabeçalho padding 20 24 com badge, título 18/600, subtítulo 14 texto-2, fechar 40×40. Corpo rolável (tabela). Rodapé padding 14 24 com contagem e ação secundária.

## Accordion "Detalhes técnicos"
Gatilho 44 alto, 14/500 texto-2, `chevron_right` (fechado) / `expand_more` (aberto), `aria-expanded`. Conteúdo: `<dl>` em grid 120px/1fr gap 8 16, 13,5; valores em mono; fórmula em bloco superficie-2 raio 6 padding 8 12. Começa recolhido.

## Tooltip
bg `--cor-texto`, texto `--cor-superficie`, 13/1,45, padding 8 12, raio 6, max 260, seta 6. Abre em hover e foco, fecha com Esc.

## EstadoVazio
Borda 1 tracejada borda-forte (ou card normal na tela inteira), padding 24–56, centralizado: círculo 44–64 com ícone, título 15–20/600, frase 13–15 texto-2 com o próximo passo, ação opcional.

## Skeleton
Blocos bg superficie-2 (barras de gráfico em `--cor-borda`), raio 4–6, alturas iguais às do conteúdo final. Pulso de opacidade 1 → 0,55, 1,2 s (desligar com reduced-motion). Container `aria-busy="true"` + texto `role="status"` ("Calculando as estatísticas de peso_kg…").

## Banner (Aviso)
Padding 12 14–16, raio 10, gap 10, ícone 20 preenchido. Atenção: bg sev-atencao-suave, borda 1 sev-atencao-borda, `warning`. Info: bg sev-info-suave, `info`. Erro de tela: bg erro-suave, borda 1 erro, `error` 24, título 15/600 + texto 14 + links de ação. Texto começa com o fato em 600 ("Fora da faixa observada.").

## BlocoFormula
bg superficie-2, raio 10, padding 16, gap 8: sobrelinha (12/600 maiúsculas texto-2), expressão mono 18/500 centralizada, substituição numérica mono 13 texto-2. Pode usar KaTeX se preferirem renderização matemática; manter fonte mono no texto de apoio.

## ReguaSeparatrizes
Ver tela 4a. Altura 60 + rótulos 34. Trilho 10 alto raio 5 bg superficie-2 borda 1 borda-forte. Faixa da separatriz que contém o valor: `color-mix(in oklab, var(--cor-primaria) 32%, var(--cor-superficie))`. Marcas: 2×22 texto-2 em cada Q (ou D/P conforme o segmented). Marcador: círculo 16 primaria com borda 2 superficie + anel 1 primaria, e acima o valor mono 13/600 em etiqueta primaria-suave. Rótulos mono 12,5 em duas linhas ("Q1" / "62,1"); mín à esquerda, máx à direita. Posição = (v − mín)/(máx − mín). Abaixo, frase `aria-live` em bloco primaria-suave: "O valor 75 está no 3º quartil (entre Q2 = 69,8 e Q3 = 77,9). Cerca de 66% dos dados são menores que ele." `role="img"` com `aria-label` equivalente.

## CartaoAlerta
Ver `telas/Cartao Alerta.dc.html`. Card padding 20 24, gap 14. Ordem fixa (spec 16):
1. Linha de topo: BadgeSeveridade · "R4 · Valores redondos" 13 texto-2 · (espaço) · coluna mono 13 texto-2.
2. Título h3 17/600. 3. Resumo 15/1,55.
4–5. Grid 2 colunas gap 16 28: "POR QUE CHAMA ATENÇÃO" e "PODE SER NORMAL SE…" (sobrelinha + 14/1,55; o segundo começa com "…").
6. Exemplo: bloco superficie-2 raio 8 padding 12 14 com sobrelinha "EXEMPLO", valores mono 13,5 e Botao secundário 36 "Ver na tabela" (`table_view`) → abre Drawer com as linhas destacadas.
7. "O que fazer:" (600) + texto 14, ícone `arrow_forward` primaria.
8. Accordion "Detalhes técnicos" colado ao rodapé (borda superior), com Medida, Valor, Limiar, Teste, p-valor (+ tradução: "chance de acontecer por acaso: menos de 1 em 1.000"), Fórmula.
Modo **recolhido** (lista longa): só 1–3 + botão fantasma "Ver explicação" (`expand_more`).

## Ícones (Material Symbols Rounded)
check, lock, left_panel_close, description, swap_horiz, light_mode, dark_mode, upload_file, folder_open, file_download, error, check_circle, close, expand_more, expand_less, chevron_right, chevron_left, drag_indicator, arrow_upward, arrow_downward, arrow_forward, help_center, content_copy, straighten, spellcheck, history, undo, cleaning_services, block, remove, add, lightbulb, info, warning, report, table_view, refresh, verified, download, playlist_add, dataset, auto_awesome, menu_book, code, print, scatter_plot, help, sell, stairs, pin, toggle_on, fingerprint.
