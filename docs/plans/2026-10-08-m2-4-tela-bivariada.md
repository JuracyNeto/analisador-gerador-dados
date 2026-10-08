# M2.4 — Tela 5 Bivariada (frontend) — plano de implementação

> **Para o agente:** execute tarefa por tarefa, em TDD (Vitest + Testing Library). Antes de escrever código, leia `CLAUDE.md`, `docs/padroes-codigo.md` (§5–§7), specs 10, 15 e 16, `docs/design/telas.md` (tela **5 Bivariada**), `docs/design/graficos-plotly.md`, o print `5a-bivariada.png` e os contratos em `docs/plans/2026-10-08-m2-visao-geral.md`.

**Objetivo:** liberar a etapa 5 com a tela do print 5a: seletores X/Y (com "Trocar X e Y"), cards r de Pearson, R² e reta de regressão, dispersão com a reta, painel "Prever Y para X =" com banner de extrapolação, heatmap da matriz de correlação e card largo de resíduos com "Como ler os resíduos"; estado vazio "Escolha duas colunas numéricas".

**Arquitetura:** feature nova `features/bivariada/` (`api.ts`, `parametros.ts`, `cartoes.ts`, `estadoBivariada.ts`, `textos.ts`, `components/`, `hooks/`). Antes, os cartões de métrica genéricos saem de `features/analise` para `shared/metricas/` (D103), porque features não importam umas das outras e copiar seria duplicação. Bivariada e matriz são consultas **independentes** em paralelo (§6: nada em cascata); a previsão é uma terceira consulta, habilitada só depois do clique em "Prever".

**Branch:** `feat/frontend-bivariada` (sai de `develop` depois do merge do M2.3) → PR para `develop`. **Prazo sugerido:** 30/10/2026.

---

## Visão geral das tarefas

| # | Tarefa | Arquivos principais |
|---|---|---|
| 1 | Cartões de métrica em `shared/metricas/` (refatoração, sem mudar comportamento) | `shared/metricas/*`, `features/analise/*` |
| 2 | Etapa 5 liberada, rota, navegação e invalidação | `app/etapas.ts`, `app/rotas.ts`, `shared/navegacao/caminhos.ts`, `shared/api/dataset.ts`, `features/variaveis/api.ts`, textos de Análise e Relatório |
| 3 | Papel `divergente` no tema do Plotly | `shared/graficos/temaPlotly.ts` |
| 4 | Base da feature: tipos, API, parâmetros na URL, fixtures | `features/bivariada/tipos.ts`, `api.ts`, `parametros.ts`, `hooks/useParametrosBivariada.ts`, `testes/fixtures/bivariada.ts`, `shared/api/colunas.ts` |
| 5 | Seletores X/Y e troca | `components/SeletoresPar.tsx` |
| 6 | Cards r, R², reta | `cartoes.ts`, `components/CardsBivariada.tsx` |
| 7 | Painel "Prever Y para X =" | `hooks/usePrevisao.ts`, `components/PainelPrevisao.tsx` |
| 8 | Matriz e resíduos | `components/CardMatriz.tsx`, `components/CardResiduos.tsx` |
| 9 | Página, estados e layout | `estadoBivariada.ts`, `PaginaBivariada.tsx`, `components/CorpoBivariada.tsx`, CSS |
| 10 | Documentação | `docs/**`, `CHANGELOG.md` |
| 11 | Verificação, teste manual no preview, resumo e PR | — |

### Regras que a tela segue
- **Colunas:** só discretas e contínuas (`filtrarNumericas` sobre a consulta de colunas do M1.6, mesma chave). Padrão: as duas primeiras numéricas (X = 1ª, Y = 2ª). `?x=&y=` na URL (D104; mesma ideia da D78); coluna da URL que não é mais numérica cai no padrão.
- **Seletores:** Select "X (explica)" e "Y (é explicada)" (altura 44) com nome mono; a opção escolhida no outro lado aparece desabilitada; botão 44 "Trocar X e Y" (`swap_horiz`, `aria-label`) inverte os dois na URL.
- **Menos de 2 colunas numéricas** → `EstadoVazio` "Escolha duas colunas numéricas" / "Selecione X e Y acima para ver a correlação e a reta de regressão." (texto de `telas.md`; com uma só numérica, a descrição troca para "Este arquivo tem só uma coluna numérica. Confira os tipos na etapa Variáveis." + ação "Ir para Variáveis").
- **Cards** (grid de 3, print 5a), com `GradeCardsMetrica`:
  | Card | Valor | Selo | Interpretação | "Ver fórmula" |
  |---|---|---|---|---|
  | Correlação de Pearson (r) | r (3 casas significativas) | "Correlação positiva forte" (força × sentido) | `pearson.interpretacao` + frase do teste t | fórmula `pearson` + cálculo; apoio com Spearman (ρ) |
  | Coeficiente de determinação (R²) | R² com unidade "%" | — | `r2.interpretacao` | fórmula `r2` + cálculo |
  | Reta de regressão | `regressao.equacao` (mono 26) | — | `reta.interpretacao` | fórmula `regressao` + cálculo (b e a) |
- **Dispersão** (grid `1.5fr 1fr`, esquerda) com `Grafico` (altura 420): figura `dispersao`; título/resumo da figura.
- **Prever Y para X =** (direita, em cima): `CampoNumero` com rótulo = nome de X, botão primário "Prever"; resultado em bloco `superficie-2`: rótulo "{y} previsto" e valor mono 26; `frase` em `aria-live="polite"`; `aviso` em `Banner` atenção com título "Fora da faixa observada." quando `extrapolacao`. Valor inválido → erro no campo ("Digite um número, por exemplo 1,75.") sem consultar. Trocar X ou Y apaga a previsão.
- **Matriz** (direita, embaixo): card "Matriz de correlação (Pearson)" com `Grafico` (altura 320) da `figura` e o `resumo` abaixo; sem figura (< 2 numéricas não acontece aqui, mas a API pode devolver `null`) → só o resumo.
- **Resíduos** (card largo): `Grafico` (altura 300) + bloco "Como ler os resíduos" com o resumo da figura `residuos`.
- **Estados:** carregando colunas (skeleton tabela), calculando (skeleton de 3 cards + gráfico, "Calculando a relação entre {x} e {y}…"), erro da bivariada com `EstadoErro` (sem "Tentar de novo" para `COLUNA_NAO_NUMERICA`, `COLUNAS_IGUAIS`, `POUCOS_PARES`, `SEM_VARIACAO`), sessão expirada pelo `useSessaoExpirada` (D61). A matriz carrega e falha de forma independente (skeleton e `EstadoErro` só no card dela).
- **Barra de ações:** "Voltar para Análise univariada" e "Continuar para Relatório" (D89 atualizada).

---

### Tarefa 1: cartões de métrica em `shared/metricas/` (refatoração)

**Arquivos:**
- Criar: `shared/metricas/cartoes.ts` (`DefinicaoCartao`, `propsDoCartao`, `medidaAusente`, `comInterpretacao`), `shared/metricas/formatacao.ts` (`formatarValorMedida`), `shared/metricas/GradeCardsMetrica.tsx` (+ `.module.css`), testes movidos
- Modificar: `features/analise/cartoes.ts` (fica só com os cartões da análise: tendência, dispersão, resumo categórico, moda), `cartoesForma.ts`, componentes que importavam os itens movidos
- Tipos `Medida`/`Formula` passam a vir de `shared/api/schema` (`components['schemas']`) nos módulos de `shared/`.

O texto de apoio de Czuber (`C.apoioCzuber`) é da análise: `propsDoCartao` ganha `apoio?: { medida: Medida; texto: (calculo: string) => string }` em `DefinicaoCartao`, para `shared/` não conhecer textos da feature.

**Passos:** mover os testes junto (`cartoes.test.ts` → parte para `shared/metricas/cartoes.test.ts`); rodar a suíte inteira **antes** de qualquer mudança de comportamento; `jscpd` 0.

**Commit:** `refactor(frontend): cartões de métrica em shared/metricas para reuso entre etapas`

---

### Tarefa 2: etapa 5 liberada, rota, navegação e invalidação

**Arquivos:** `app/etapas.ts` (+ teste), `app/rotas.ts` (+ teste), `shared/navegacao/caminhos.ts`, `shared/api/dataset.ts` (+ teste), `features/variaveis/api.ts`, `features/analise/textos.ts`, `features/analise/PaginaAnalise.tsx`, `features/relatorio/textos.ts`, `PaginaRelatorio.tsx`

- `CAMINHOS.bivariada = '/bivariada'`; etapa 5 sem `disponivelEm`; `PAGINAS[5] = PaginaBivariada` (lazy).
- `chavesDataset.bivariada(id) = ['datasets', id, 'bivariada']`; a troca de tipo (`features/variaveis/api.ts`) invalida também essa chave (a limpeza já invalida o prefixo inteiro).
- Análise: "Continuar para Bivariada" (`CAMINHOS.bivariada`); Relatório: "Voltar para Bivariada".
- **Testes:** `etapas.test.ts` (5 não é futura; 6 e 7 continuam `v0.3`); `rotas.test.tsx` (`/bivariada` renderiza a página); `BarraEtapas.test.tsx` (Bivariada liberada após importar); `PaginaAnalise.test.tsx` e `PaginaRelatorio.test.tsx` (textos dos botões novos).
- Nesta tarefa `PaginaBivariada` é um esqueleto com `PaginaEtapa` + `SemDataset` (a Tarefa 9 completa).

**Commit:** `feat(frontend): libera a etapa Bivariada e ajusta a navegação`

---

### Tarefa 3: papel `divergente` no tema do Plotly

**Arquivos:** `shared/graficos/temaPlotly.ts`, `temaPlotly.test.ts`

**Teste (falha):**
```ts
it('pinta o heatmap divergente com graf-2, fundo e graf-1', () => {
  const figura = { data: [{ type: 'heatmap', meta: 'divergente', z: [[1]] }], layout: {} };
  const traco = montarFigura(figura, TOKENS).data[0] as Record<string, unknown>;
  expect(traco.colorscale).toEqual([[0, TOKENS.series[1]], [0.5, TOKENS.fundo], [1, TOKENS.series[0]]]);
  expect(traco).not.toHaveProperty('marker');
});
```
**Implementar:** `pintarTraco(traco, tokens)` (recebe os tokens, não só as séries) com tabela de despacho por papel: `principal`/`referencia` → cor da série (como hoje); `divergente` → `colorscale` (a opacidade 0,6 já vem do backend). Mesma regra do `tema.py` do backend (M2.3), sem duplicar a paleta (D83).

**Commit:** `feat(graficos): escala divergente do heatmap pelo tema ativo`

---

### Tarefa 4: base da feature

**Arquivos:** criar `features/bivariada/tipos.ts`, `api.ts` (+ teste), `parametros.ts` (+ teste), `hooks/useParametrosBivariada.ts`, `textos.ts`, `testes/fixtures/bivariada.ts`; modificar `shared/api/colunas.ts` (+ `filtrarNumericas`, `useColunasNumericas`)

- `api.ts`: `chavesBivariada.par(id, x, y)`, `.matriz(id)`, `.previsao(id, x, y, valor)` sob `chavesDataset.bivariada(id)`; `caminhoBivariada`, `caminhoPrevisao`, `caminhoCorrelacoes`; `useBivariada(id, par | null)`, `useMatriz(id)` (as duas disparam juntas na página), `usePrevisao(id, par, valor | null)` (`enabled: valor !== null`); `podeTentarDeNovo` com os 4 códigos definitivos.
- `parametros.ts`: `lerPar(busca)`, `parEscolhido(pedido, colunas) -> { x, y } | null` (padrão = duas primeiras; descarta coluna inexistente; nunca devolve x = y), `comPar`, `trocado`.
- **Testes:** `parEscolhido` com URL vazia, com URL válida, com coluna que deixou de ser numérica, com `x = y` na URL (cai no padrão), com uma só numérica (`null`); `trocado` inverte; caminhos codificam nomes com espaço/acentos; `filtrarNumericas` mantém só `discreta` e `continua`.
- Fixtures: `bivariadaAlturaPeso` (números do print 5a: r 0,78 forte positiva, R² 61%, reta "Ŷ = −98,4 + 98,1·X"), `matrizExemplo` (idade, altura_m, peso_kg), `previsaoExtrapolada` (2,1 → 107,6, com aviso), `previsaoDentro`.

**Commit:** `feat(bivariada): base da feature (API, par na URL, fixtures)`

---

### Tarefa 5: `SeletoresPar`

Props: `{ colunas: readonly TipoColuna[]; par: Par; aoMudar: (par: Par) => void }`. Dois `Select` (altura 44, `ajuda` nenhuma) + `Botao` "Trocar X e Y" (ícone `swap_horiz`, só ícone com `aria-label`).

**Testes (falham):** a opção escolhida em Y aparece desabilitada no Select de X (e vice-versa); mudar X chama `aoMudar({ x: novo, y })`; clicar em "Trocar X e Y" chama `aoMudar({ x: y, y: x })`.

**Commit:** `feat(bivariada): seletores de X e Y com troca`

---

### Tarefa 6: cards r, R², reta

**Arquivos:** `features/bivariada/cartoes.ts` (+ teste), `components/CardsBivariada.tsx`

`cartoesBivariada(b: Bivariada): DefinicaoCartao[]` — selo `SELO_CORRELACAO[forca][sentido]` ("Correlação positiva forte", "Correlação fraca" quando fraca); interpretação do r = `pearson.interpretacao` + " " + `teste_t.interpretacao`; R² com `unidade: '%'` e 3 casas significativas; reta com valor = `regressao.equacao`.

**Testes:** com a fixture do print: rótulos "Correlação de Pearson (r)", "Coeficiente de determinação (R²)", "Reta de regressão"; valores "0,78", "61", "Ŷ = −98,4 + 98,1·X"; selo "Correlação positiva forte"; "Ver fórmula" do r mostra a fórmula de Pearson e o Spearman como apoio.

**Commit:** `feat(bivariada): cards de correlação, R² e reta`

---

### Tarefa 7: painel "Prever Y para X ="

**Arquivos:** `hooks/usePrevisao.ts` (estado do texto + valor confirmado + consulta), `components/PainelPrevisao.tsx` (+ `.module.css`, teste)

**Testes (falham):**
- digitar "1,7" e clicar "Prever" mostra "peso_kg previsto" e "68,4" (fixture) e a frase em região `aria-live`;
- "2,1" mostra o banner "Fora da faixa observada." com o texto do aviso;
- "abc" mostra o erro no campo e não chama a API (`fetch` falso sem chamadas);
- trocar o par (rerender com outro `par`) limpa o resultado.

**Commit:** `feat(bivariada): previsão de Y por X com aviso de extrapolação`

---

### Tarefa 8: matriz e resíduos

**Arquivos:** `components/CardMatriz.tsx`, `components/CardResiduos.tsx` (+ `.module.css`, testes)

- `CardMatriz({ consulta })`: carregando (`EstadoCarregando forma="grafico"`), erro (`EstadoErro` com "Tentar de novo"), pronta (gráfico + resumo).
- `CardResiduos({ figura })`: gráfico à esquerda, "Como ler os resíduos" (h3) + resumo à direita; em < 1280 px empilha.

**Testes:** títulos e resumos das fixtures; erro da matriz não derruba os cards da bivariada (teste na página, Tarefa 9).

**Commit:** `feat(bivariada): matriz de correlação e gráfico de resíduos`

---

### Tarefa 9: página, estados e layout

**Arquivos:** `estadoBivariada.ts` (+ teste), `PaginaBivariada.tsx` (+ teste), `components/CorpoBivariada.tsx`, `PaginaBivariada.module.css`

`estadoDaBivariada(colunas, consulta, par)` → união discriminada `carregando-colunas | poucas-colunas | calculando | erro | pronta` (como `estadoDaAnalise`). `PaginaBivariada`: `PaginaEtapa` (etapa 5, título "Análise bivariada", ajuda "Veja se duas colunas numéricas andam juntas e use a reta para prever uma a partir da outra." do print) com `SeletoresPar` em `acoesTopo`; `CorpoBivariada` por `switch` exaustivo; barra de ações.

**Testes (`PaginaBivariada.test.tsx`, com `fetch` falso de `testes/api.ts`):** fluxo feliz (cards, 3 gráficos, painel de previsão); URL `?x=peso_kg&y=altura_m` respeitada; uma só coluna numérica → estado vazio com "Ir para Variáveis"; `POUCOS_PARES` → `EstadoErro` sem "Tentar de novo"; matriz com erro e bivariada ok → cards visíveis + erro só no card da matriz; sem dataset → `SemDataset`.

**Commit:** `feat(bivariada): tela Bivariada (5a)`

---

### Tarefa 10: documentação
- `docs/specs/15-frontend.md`: tela 5 (URL, padrão, estados), layout (etapas 6–7 ainda bloqueadas), barra de ações das etapas 4, 5 e 8.
- `docs/design/telas.md`: notas de implementação da tela 5 (unidades omitidas; resíduos × X; texto do vazio com uma só numérica).
- `docs/decisions.md`: D103 e D104; atualizar a coluna "Decisão" da D89 só por referência ("ver D104"), sem reescrever a linha antiga.
- `CHANGELOG.md` › Adicionado: "Etapa 5 Bivariada: correlação, reta de regressão, resíduos, previsão de Y por X e matriz de correlação." · Alterado: "Análise univariada continua para Bivariada; Relatório volta para Bivariada."

**Commit:** `docs: tela Bivariada`

### Tarefa 11: verificação, teste manual e PR
1. Verificação completa (frontend, backend, jscpd).
2. Preview (`backend` + `frontend`), viewport 1440×900: exemplo → Bivariada pela barra lateral e pelo "Continuar" da Análise; `altura_m × peso_kg` com os 3 cards, dispersão com legenda e reta laranja (`--graf-2`), prever 1,7 e 2,1 (banner), heatmap com escala divergente e números, resíduos com linha zero tracejada; "Trocar X e Y"; recarregar mantém `?x=&y=`; tema escuro (cores do heatmap pelo DOM); 1024 px (barra recolhida) sem rolagem horizontal; `notas_turma.csv` (`nota_p1 × nota_p2`). Conferir o console sem erros.
3. Resumo ao usuário antes do push; com o ok, push e PR. Encerrar servidores (e conferir `node …vite.js` na 5173).

## Critérios de pronto do M2.4
- Tela igual ao print 5a (fora as unidades), nos dois temas, com estados carregando/vazio/erro.
- Etapa 5 liberada; navegação Análise → Bivariada → Relatório.
- Cartões de métrica num só lugar (`shared/metricas/`); jscpd 0; componentes ≤ 150 linhas.
