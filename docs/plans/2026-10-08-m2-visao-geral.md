# M2 — Análise avançada: visão geral dos blocos

> Índice do M2. Cada bloco tem plano, branch e PR próprios. Os contratos abaixo são a **fonte única** entre os blocos: quem implementa um bloco não muda um contrato sem atualizar este arquivo e avisar no PR.

**Objetivo do marco:** com `dados-exemplo/pesquisa_saude.txt`, o usuário vê a forma de cada coluna numérica (assimetria, curtose, ajuste Normal/Binomial, histograma com curva e QQ-plot), escolhe duas colunas numéricas para ver correlação, reta de regressão, resíduos, matriz de correlação e prever Y por X, e leva distribuições e bivariada para o relatório. Antes disso, colunas de data e hora passam a ser reconhecidas (tipo auxiliar `data`) e ficam fora das análises (pedido do usuário em 08/10/2026). Prazo **13/11/2026**, versão **v0.2.0** (`roadmap.md`).

**Critérios de pronto** (pedido do M2, `roadmap.md` e checklist do professor):
- "Distribuições, assimetria, curtose" e "Correlação e regressão" funcionando de ponta a ponta com `pesquisa_saude.txt` e `notas_turma.csv`.
- Aba "Forma e distribuição" (4e, 4j) e tela 5 Bivariada (5a) conferem com `docs/design/telas.md` nos temas claro e escuro, com os estados carregando, vazio e erro.
- Relatório com as seções Distribuições e Bivariada (escolha do usuário em 08/10/2026).
- Colunas de data, hora ou data e hora classificadas como `data`, com motivo, chip e correção manual, fora das análises.
- Cobertura ≥ 80% em `dominios/` e `compartilhado/`; CI verde (`backend`, `frontend`, `duplicacao`) em todos os PRs.

## Blocos

| Bloco | Plano | Branch | Conteúdo |
|---|---|---|---|
| **M2.0** Tipo auxiliar `data` | `2026-10-08-m2-0-tipo-data.md` | `feat/datasets-tipo-data` | Datas, horários e data com hora reconhecidos por formato (spec 02); chip "Data" e correção manual na tela 2; fora das análises e do relatório por coluna |
| **M2.1** Forma e distribuições (backend) | `2026-10-08-m2-1-forma-distribuicoes.md` | `feat/analise-forma` | `scipy-stubs`; assimetria, curtose, ajuste Normal/Binomial/Bernoulli com testes de aderência (spec 09); figuras da forma; `Analise.forma`; `?tentativas=` |
| **M2.2** Aba Forma e distribuição | `2026-10-08-m2-2-aba-forma.md` | `feat/frontend-forma` | Aba 4e na tela univariada: cards, nota de Pearson/K, nº de tentativas (discreta), gráficos |
| **M2.3** Correlação e regressão (backend) | `2026-10-08-m2-3-correlacao-regressao.md` | `feat/analise-bivariada` | Pearson + teste t, Spearman, regressão, resíduos, previsão, matriz (spec 10); figuras dispersão/resíduos/heatmap; 3 endpoints |
| **M2.4** Tela Bivariada | `2026-10-08-m2-4-tela-bivariada.md` | `feat/frontend-bivariada` | Etapa 5 liberada; seletores X/Y na URL, cards r/R²/reta, dispersão, prever, heatmap, resíduos; cartões de métrica em `shared/` |
| **M2.5** Relatório: Distribuições e Bivariada | `2026-10-08-m2-5-relatorio.md` | `feat/relatorio-distribuicoes-bivariada` | Duas seções novas no HTML e na tela 8 |
| **M2.6** Documentação e release | `2026-10-08-m2-6-documentacao-release.md` | `chore/sincroniza-main-pos-v0.1.1`, `chore/release-v0.2.0` | Sincronizar `main → develop`, specs, critérios de pronto, `v0.2.0` |

**Por que 7 blocos:** separar backend e tela de cada assunto mantém os PRs perto de 1.000–1.600 linhas (como no M1) e deixa testar cada contrato no Swagger antes da tela. A ordem é em fatias verticais (forma inteira, depois bivariada inteira), para o usuário ver cada assunto pronto mais cedo.

## Dependências e ordem

| Bloco | Depende de (mergeado em `develop`) | Pode andar em paralelo com |
|---|---|---|
| M2.0 | — | M2.1, M2.3 (conflito só em `analise/textos.py` e `analise/servico.py`) |
| M2.1 | — | M2.0, M2.3 |
| M2.2 | M2.1 | M2.3 |
| M2.3 | — (conflitos só em `formulas.py`, `schemas.py`, `router.py`, `textos.py`, `tema.py`) | M2.1, M2.2 |
| M2.4 | M2.3 (e M2.2, pelos arquivos de `features/analise` que vão para `shared/`) | M2.5 (backend) |
| M2.5 | M2.1 e M2.3 (backend); a parte da tela 8 depois do M2.4 (botão Voltar) | — |
| M2.6 | todos | — |

```
backend : M2.0 ── M2.1 ────────── M2.3 ──────────┐
frontend:                M2.2 ──────────── M2.4 ──┴── M2.5 ── M2.6 (release v0.2.0)
```
Execução prevista (um bloco por vez): M2.0 → M2.1 → M2.2 → M2.3 → M2.4 → M2.5 → M2.6. Datas sugeridas: M2.0 11/10 · M2.1 15/10 · M2.2 20/10 · M2.3 24/10 · M2.4 30/10 · M2.5 04/11 · release 06/11 (folga até 13/11).

## Convenções que valem para todos os blocos

- Regras de `CLAUDE.md` e `padroes-codigo.md`. Rodar **antes de cada push**:
  - backend (em `backend/`, venv `.venv`): `ruff check . && ruff format --check . && mypy app && complexipy app --max-complexity-allowed 15 && pytest`
  - frontend (em `frontend/`): `npm run lint && npm run format && npm run test && npm run build`
  - raiz: `npx --yes jscpd@4 backend/app backend/tests frontend/src`
- Worktree novo: `python -m venv .venv` + `.venv/Scripts/python -m pip install -e ".[dev]"` em `backend/`; `npm ci` em `frontend/`.
- Depois de mudar a API: `python scripts/exportar_openapi.py` (em `backend/`) → `npm run gerar:tipos` (em `frontend/`) → commit do `schema.d.ts` **no mesmo bloco do backend** (M2.0, M2.1, M2.3, M2.5), para o frontend já nascer com os tipos.
- TDD em toda tarefa: teste falhando → código → teste passando → commit (Conventional Commits em português, **sem atribuição de IA**).
- Nunca silenciar lint, tipos ou complexidade (`noqa`, `eslint-disable`, `type: ignore`, `pragma: no cover`, overrides). Sem parâmetro booleano que escolhe comportamento (sonarjs `no-selector-parameter`); sem ref dentro de objeto devolvido por hook (`react-hooks/refs`).
- **pandas 3**: nunca comparar `dtype == object`. Arquivos escritos por script: LF, UTF-8.
- Toda decisão nova vai para `docs/decisions.md` com o **próximo número livre** (hoje D90); os números abaixo são os previstos na ordem dos blocos. Toda entrega vai para `CHANGELOG.md` › *Não lançado* (Adicionado/Alterado/Corrigido conferidos à mão em conflitos).
- Teste manual no preview (`.claude/launch.json`: `backend` 8000, `frontend` 5173) antes do push de cada bloco com tela; viewport fixa com `resize_window` e conferência pelo DOM.
- PR, merge e release só com o ok do usuário; merge só com os 3 checks verdes (`gh pr merge N --merge`).

## Contratos do backend

### Tipo auxiliar `data` (M2.0)
- `TipoVariavel` ganha `data`; `TIPOS_AUXILIARES = {identificador, data}` em `compartilhado/tipos.py`. Todo lugar que hoje testa `!= IDENTIFICADOR` para "fica fora das análises" passa a testar `in TIPOS_AUXILIARES` (análise, relatório, `filtrarAnalisaveis`). Duplicados (D50) continuam tirando só identificadores.
- `compartilhado/datas.py`: `reconhecer_datas(serie) -> LeituraDatas | None` (formato, proporção, exemplo) e `formatar_data(valor)`; o detector (R6, M3) reaproveita.
- Regra `_data` logo depois de `_vazia` na cadeia da spec 02; limiar `limiar_data = 0,9` em `config.py`.
- `GET /analise` e `/posicao` de coluna `data` → 400 `COLUNA_IGNORADA` (mensagem por tipo: "A coluna {col} tem datas e fica fora das análises."). Na bivariada (M2.3) uma coluna `data` cai em `COLUNA_NAO_NUMERICA`.

### Estatística compartilhada
- `ALFA = 0.05` (nível de significância, `00-visao-geral.md`) em `app/compartilhado/estatistica.py`, junto de `agrupar_esperados_pequenos(observados, esperados, minimo=5)` (usado pelo qui-quadrado da Normal e da Binomial; o detector do M3 vai reutilizar).
- `formatar_p_valor(p)` em `compartilhado/numeros.py`: `"p < 0,001"` quando p < 0,001; senão `"p = 0,21"` (3 casas significativas).
- `p_valor_em_palavras(p)` em `compartilhado/textos.py` (spec 16): `"menos de 1 em 1.000"` (p < 0,001) · `"cerca de 1 em 50"` (p ≈ 0,02) · `"mais de 1 em 2"` (p ≥ 0,5).

### Forma (M2.1) — `Analise.forma`
```
Parametro      {simbolo: str, nome: str, valor: float}            # μ̂, σ̂, n, p̂, E[X], Var
TesteAderencia {nome: str, estatistica: float, gl: int | None, p_valor: float, compativel: bool}
Ajuste {
  distribuicao: "normal" | "binomial" | "bernoulli",
  aplicavel: bool, motivo: str | None,                           # motivo no formato da spec 16
  parametros: list[Parametro],
  teste: TesteAderencia | None,                                  # Shapiro-Wilk | D'Agostino-Pearson K² | Qui-quadrado
  complementar: TesteAderencia | None,                           # Normal: qui-quadrado nas classes da spec 04
  frase: str | None,                                             # "Os dados são compatíveis com a distribuição Normal."
  calculo: str | None,                                           # "Shapiro-Wilk: W = 0,9933 · p = 0,399 ≥ 0,05"
  formula: str | None                                            # chave: normal | binomial | bernoulli
}
Forma {
  assimetria: Medida, assimetria_pearson_1: Medida, assimetria_pearson_2: Medida,
  curtose: Medida, curtose_percentilica: Medida,
  classificacao_assimetria: "simetrica" | "moderada" | "forte" | None,
  sentido_assimetria: "direita" | "esquerda" | None,
  classificacao_curtose: "mesocurtica" | "leptocurtica" | "platicurtica" | None,
  normal: Ajuste, binomial: Ajuste,
  tentativas: int | None,                                        # n da Binomial usado (discreta)
  interpretacao: str | None,                                     # frase conjunta da spec 09
  figuras: list[Figura]
}
Analise { …, forma: Forma | None, … }                            # None para nominal e ordinal
```
- `GET /datasets/{id}/colunas/{coluna}/analise?classes=&sucesso=&tentativas=` (`tentativas` ≥ 1; menor que o máximo observado → 400 `TENTATIVAS_INVALIDAS`).
- Novas chaves de `aplicavel`: `forma`, `assimetria`, `curtose`, `normal`, `binomial`. A aba "Forma e distribuição" fica desabilitada quando `aplicavel.forma` é falso, com o motivo de `nao_aplicavel` (item `forma`).
- Novas chaves de fórmula: `assimetria`, `assimetria_pearson_1`, `assimetria_pearson_2`, `curtose`, `curtose_percentilica`, `normal`, `binomial`, `bernoulli`, `qui_quadrado`.
- Ids de figuras da forma (em `Forma.figuras`, **não** em `Analise.figuras`): `histograma_normal` e `qqplot` (contínua); `bastoes_normal` (discreta com Normal aplicável) e `binomial` (discreta com Binomial aplicável). Binária não tem figura de forma.

| Tipo | Assimetria/curtose | Normal | Binomial |
|---|---|---|---|
| Contínua | G₁ (n ≥ 3), G₂ (n ≥ 4), As₁, As₂, K | Shapiro-Wilk (n ≤ 5.000) ou D'Agostino-Pearson (n > 5.000) + qui-quadrado complementar | não se aplica |
| Discreta | idem | se n ≥ 30 | se todos os valores são inteiros ≥ 0; n = máximo observado ou `?tentativas=`; qui-quadrado gl = k − 2 |
| Binária | não se aplicam | não se aplica | Bernoulli: p̂, E = p, Var = p(1 − p); sem teste (gl = 0) |
| Nominal/ordinal | `forma = null`, motivo "Distribuições Normal/Binomial exigem números." (spec 09) | | |

### Bivariada (M2.3)
```
Faixa       {minimo: float, maximo: float}
Regressao   {a: float, b: float, equacao: str, reta: Medida, r2: Medida, se: Medida}   # r2.valor em % (0–100), como o CV
Bivariada {
  x: str, y: str, n: int, n_descartados: int,                    # pares com X e Y válidos; descartados = linhas com faltante em X ou Y
  pearson: Medida, teste_t: Medida, spearman: Medida,             # teste_t.valor = p-valor
  forca: "fraca" | "moderada" | "forte", sentido: "positiva" | "negativa" | "nula",
  regressao: Regressao, faixa_x: Faixa,
  interpretacoes: list[str], formulas: list[Formula], figuras: list[Figura]   # figuras: dispersao, residuos
}
Previsao        {x: float, y_previsto: float, extrapolacao: bool, faixa_x: Faixa, frase: str, aviso: str | None}
MatrizCorrelacao {colunas: list[str], valores: list[list[float | None]], resumo: str, figura: Figura | None}
```
| Método | Rota | Query | Resposta |
|---|---|---|---|
| GET | `/datasets/{id}/bivariada` | `x`, `y` | `Bivariada` |
| GET | `/datasets/{id}/bivariada/prever` | `x`, `y`, `valor` | `Previsao` |
| GET | `/datasets/{id}/correlacoes` | — | `MatrizCorrelacao` (Pearson par a par de todas as discretas e contínuas) |

- O router do domínio `analise` passa a ter prefixo `/datasets/{dataset_id}`; as rotas da univariada continuam iguais (`/colunas/{coluna}/analise`, `/colunas/{coluna}/posicao`).
- Novas chaves de fórmula: `pearson`, `teste_t_correlacao`, `spearman`, `regressao`, `r2`, `erro_padrao_estimativa`, `residuo`.
- Ids de figuras: `dispersao`, `residuos` (em `Bivariada.figuras`), `matriz` (em `MatrizCorrelacao.figura`).
- Papel novo de traço: `meta: "divergente"` (heatmap). Quem desenha monta a escala `--graf-2` (−1) → fundo (0) → `--graf-1` (+1), com opacidade 0,6 (graficos-plotly.md: "intensidade máx. 60%").

### Relatório (M2.5)
- `Secao` ganha `distribuicoes` e `bivariada`; o padrão (sem `?secoes=`) passa a ter as 6 seções (`SECOES_M1` vira `SECOES_PADRAO`).
- `distribuicoes` usa as mesmas `colunas` de `analises` e entra dentro da seção de cada coluna; `bivariada` é uma seção própria: matriz + até 3 pares com |r| ≥ 0,3, do mais forte ao mais fraco.

### Códigos de erro novos
| Código | HTTP | Mensagem (spec 16) | Bloco |
|---|---|---|---|
| `COLUNA_IGNORADA` (mensagem nova para `data`) | 400 | A coluna *{col}* tem datas e fica fora das análises. | M2.0 |
| `TENTATIVAS_INVALIDAS` | 400 | O número de tentativas precisa ser pelo menos o maior valor observado ({max}). | M2.1 |
| `COLUNA_NAO_NUMERICA` | 400 | Escolha duas colunas numéricas. (*{col}* é {tipo}.) | M2.3 |
| `COLUNAS_IGUAIS` | 400 | X e Y precisam ser colunas diferentes. | M2.3 |
| `POUCOS_PARES` | 400 | Só há {n} linhas com *{x}* e *{y}* preenchidas; são precisas pelo menos 3. | M2.3 |
| `SEM_VARIACAO` | 400 | Todos os valores de *{col}* são iguais; não dá para medir a relação. | M2.3 |

## Contratos do frontend

| Bloco | O que muda |
|---|---|
| M2.0 | `TIPOS_VARIAVEL.data` (ícone `calendar_month`, "Data" / "Data ou hora (ignorada)", token `--tipo-data` oliva nos dois temas); `ORDEM_TIPOS` com `data` antes de `identificador`; `ehAuxiliar(tipo)`; `filtrarAnalisaveis` tira os auxiliares |
| M2.2 | `IdAba` ganha `forma` (ordem: Frequências · Tendência central · Separatrizes · Dispersão · Forma e distribuição · Gráficos); `?tentativas=` na URL junto de `coluna` e `classes` (D78), zerado ao trocar de coluna; `formatarPValor(p)` em `shared/lib/formatar.ts` |
| M2.4 | `GradeCardsMetrica`, `propsDoCartao`/`DefinicaoCartao` e `formatarValorMedida` saem de `features/analise` para `shared/metricas/` (a Bivariada usa os mesmos cartões; sem duplicar); `CAMINHOS.bivariada`; etapa 5 sem `disponivelEm`; `chavesDataset.bivariada(id)` incluída na invalidação da troca de tipo; papel `divergente` em `temaPlotly.ts`; `filtrarNumericas` em `shared/api/colunas.ts` |
| M2.5 | `SECOES_RELATORIO` com `distribuicoes` e `bivariada`; colunas habilitadas quando `analises` **ou** `distribuicoes` está marcada |

**Navegação (D89 atualizada no M2.4):** Análise univariada "Continuar para Bivariada" · Bivariada "Voltar para Análise univariada" / "Continuar para Relatório" · Relatório "Voltar para Bivariada". Gerador e Detector seguem bloqueados ("Disponível na versão v0.3").

## Decisões previstas (entram em `docs/decisions.md` no bloco indicado)
| # | Decisão | Bloco |
|---|---|---|
| D90 | Tipo auxiliar `data` (datas, horários, data e hora): ≥ 90% dos valores num mesmo formato explícito ou células de data do XLSX; regra logo depois de "vazia"; fora das análises como o identificador; o detector usa no M3 (pedido do usuário em 08/10/2026) | M2.0 |
| D91 | Dia primeiro (padrão brasileiro); mês primeiro só quando nenhum 1º campo passa de 12 e algum 2º campo passa | M2.0 |
| D92 | Correção manual para `data` exige ≥ 90% reconhecíveis; de `data` vai para nominal, ordinal, binária ou identificador; chip "Data" (`calendar_month`, `--tipo-data`) | M2.0 |
| D93 | `scipy-stubs` (1.18.x) nas dependências de desenvolvimento, para usar o scipy com `mypy --strict` sem overrides (escolha do usuário em 08/10/2026) | M2.1 |
| D94 | Forma no mesmo `GET /analise` (`Analise.forma`, `?tentativas=`); figuras da forma em `Forma.figuras`, fora do Segmented da aba Gráficos; a curva Normal sobre o histograma fica na aba Forma (cumpre D56) | M2.1 |
| D95 | Binária: Bernoulli com p̂, E e Var, sem teste de aderência (com p estimado dos dados, gl = 0 e o esperado repete o observado); assimetria e curtose não se aplicam a binárias | M2.1 |
| D96 | Discreta: Binomial só com todos os valores inteiros ≥ 0; n de tentativas = máximo observado ou o informado (≥ máximo); qui-quadrado agrupa as caudas com esperado < 5 e usa gl = k − 2 (sem teste se gl < 1) | M2.1 |
| D97 | Normal: Shapiro-Wilk até 5.000 valores, D'Agostino-Pearson acima; qui-quadrado nas classes da spec 04 como teste complementar (gl = k − 3); não se aplica com n < 3 ou desvio zero | M2.1 |
| D98 | As₁ usa a moda de Czuber na contínua e a moda bruta na discreta (só se unimodal); QQ-plot com no máximo 500 pontos (quantis igualmente espaçados) | M2.1 |
| D99 | Bivariada no domínio `analise` (`correlacao.py`, `regressao.py`, `bivariada.py`); router com prefixo `/datasets/{dataset_id}`; só pares com X e Y válidos; erros `COLUNA_NAO_NUMERICA`, `COLUNAS_IGUAIS`, `POUCOS_PARES`, `SEM_VARIACAO` | M2.3 |
| D100 | Dispersão e resíduos com no máximo 5.000 pontos (amostra com semente fixa, avisada no resumo), em vez de bins 2D (ADR 0003) | M2.3 |
| D101 | Resíduos × X (specs 08 e 10), não × Ŷ como no print 5a e em `graficos-plotly.md` (doc corrigido) | M2.3 |
| D102 | Heatmap com papel `divergente`: escala `--graf-2` → fundo → `--graf-1`, opacidade 0,6, pintada por quem desenha (estende D83) | M2.3 |
| D103 | Cartões de métrica (`GradeCardsMetrica`, `propsDoCartao`) em `shared/metricas/`, usados pela Análise e pela Bivariada | M2.4 |
| D104 | Tela 5: X e Y na URL (`?x=&y=`), padrão = as duas primeiras colunas numéricas; o Select de um lado desabilita a coluna do outro; "Prever" consulta a API só ao clicar; texto de extrapolação de `telas.md`; barra de ações com Voltar/Continuar (D89 atualizada) | M2.4 |
| D105 | Relatório com seções `distribuicoes` (dentro da seção de cada coluna) e `bivariada` (matriz + até 3 pares com \|r\| ≥ 0,3) já no M2 (escolha do usuário em 08/10/2026); D57 atualizada | M2.5 |

## Dependências novas
- Backend (dev): `scipy-stubs>=1.18,<1.19` (D93). O `scipy` já está em `dependencies`; nada novo em execução.
- Frontend: nenhuma.

## Tamanho dos PRs
| Bloco | Linhas estimadas (código + testes) |
|---|---|
| M2.0 | ~900 |
| M2.1 | ~1.600 |
| M2.2 | ~900 |
| M2.3 | ~1.500 |
| M2.4 | ~1.700 (inclui mover os cartões para `shared/`) |
| M2.5 | ~700 |
| M2.6 | ~150 (docs e versões) |

## Pontos de atenção encontrados nas specs e no design
1. **Bernoulli × qui-quadrado (spec 09):** com p estimado, gl = k − 1 − 1 = 0 na binária; o teste não existe. D95.
2. **"Discreta (contagem de sucessos em n tentativas)":** o sistema não sabe se a coluna é uma contagem; a Binomial aparece sempre que os valores são inteiros ≥ 0, com o n editável (padrão = máximo, como na spec). D96.
3. **Resíduos:** specs 08/10 pedem × X; print 5a e `graficos-plotly.md` mostram × Ŷ. Seguimos a spec (D101); para b > 0 a figura é a mesma a menos da escala do eixo.
4. **Unidades** ("kg", "cm" nos prints 5a/4e) não existem nos dados; os textos usam o nome da coluna (como a dúvida 13 do M1).
5. **Texto de extrapolação:** spec 10 e `telas.md` divergem; usamos o de `telas.md` (texto final da tela), registrado em D104 e na spec 10.
6. **Legendas:** os prints 4e/5a mostram legenda nas figuras com dois traços (barras + curva, pontos + reta); as figuras novas usam `showlegend: true` e `name` em cada traço.
