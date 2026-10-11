# M3 — Gerador + Detector: visão geral dos blocos

> Índice do M3. Cada bloco tem plano, branch e PR próprios. Os contratos abaixo são a **fonte única** entre os blocos: quem implementa um bloco não muda um contrato sem atualizar este arquivo e avisar no PR.

**Objetivo do marco:** o usuário gera dados artificiais univariados (preservando as estatísticas de uma coluna ou com novos parâmetros) e bivariados (médias, desvios e correlação alvo), compara original × gerado, baixa o CSV, usa o resultado como novo dataset ou o anexa ao atual; depois roda o detector, que aplica as 11 regras da spec 12 e explica cada alerta em linguagem simples (spec 16), com as linhas na tabela. O relatório ganha as seções Gerador e Detector (escolha do usuário em 10/10/2026). Prazo **27/11/2026**, versão **v0.3.0** (`roadmap.md`).

**Critérios de pronto** (pedido do M3, `roadmap.md` e checklist do professor):
- "Gerador univariado", "Gerador bivariado com correlação" e "Detector com resumo" funcionando de ponta a ponta com `pesquisa_saude.txt` e os datasets de demonstração novos.
- Telas 6 (6a, 6b) e 7 (7a–7d) conferem com `docs/design/telas.md` e os prints, nos temas claro e escuro, com os estados carregando, vazio e erro.
- Tolerâncias da spec 11 cobertas por testes (média/DP exatos com reescala; |r − ρ| < 1e-9 com ajuste exato; < 0,03 sem ajuste com n = 10.000; mesma semente → mesmo resultado).
- Falsos positivos da spec 12: em 100 amostras Normais (n = 500) e 100 Exponenciais, cada regra (exceto R7) dispara em < 5%; cada dataset plantado dispara as regras esperadas.
- Relatório com as seções Gerador e Detector.
- Cobertura ≥ 80% em `dominios/` e `compartilhado/`; CI verde (`backend`, `frontend`, `duplicacao`) em todos os PRs.

## Blocos

| Bloco | Plano | Branch | Conteúdo |
|---|---|---|---|
| **M3.0** Gerador (backend) | `2026-10-10-m3-0-gerador-backend.md` | `feat/gerador-backend` | Domínio `gerador`: estratégias por tipo, reescala exata, Cholesky, comparação, explicação, gerações em memória, CSV, adotar (novo/anexar); figura de sobreposição |
| **M3.1** Tela Gerador | `2026-10-10-m3-1-tela-gerador.md` | `feat/frontend-gerador` | Etapa 6 liberada: abas Univariado/Bivariado, formulários, Original × Gerado, gráfico, "Como geramos", Baixar CSV / Anexar / Usar como novo dataset |
| **M3.2** Detector: base e regras de uma coluna | `2026-10-10-m3-2-detector-base.md` | `feat/detector-base` | `regras/base.py` (Template Method), `registro.py`, `textos.py`, endpoint, resumo; R3, R4, R5, R7, R8, R9; `GET /linhas` para o drawer |
| **M3.3** Detector: regras de bloco e ordem + demonstração | `2026-10-10-m3-3-detector-blocos.md` | `feat/detector-blocos` | R1, R2, R6, R10, R11; figuras do detector; datasets plantados (script com semente); exemplos escolhíveis; teste de falsos positivos |
| **M3.4** Tela Detector | `2026-10-10-m3-4-tela-detector.md` | `feat/frontend-detector` | Etapa 7 liberada: resumo, filtros, agrupar, CartaoAlerta, Drawer "Ver na tabela", regras não verificadas, vazio; exemplos na tela Importar |
| **M3.5** Relatório: Gerador e Detector | `2026-10-10-m3-5-relatorio.md` | `feat/relatorio-gerador-detector` | Duas seções novas no HTML e na tela 8 |
| **M3.6** Documentação e release | `2026-10-10-m3-6-documentacao-release.md` | `docs/revisao-m3`, `chore/release-v0.3.0` | Specs, critérios de pronto, teste manual completo, `v0.3.0`, sincronização `main → develop` depois do release |

**Por que 7 blocos:** separar backend e tela mantém os PRs perto de 1.000–1.800 linhas e deixa testar cada contrato no Swagger antes da tela. O detector tem 11 regras: dividir em "uma coluna" (M3.2) e "blocos, pares e ordem" (M3.3) deixa o M3.2 entregar o esqueleto completo (endpoint, textos, resumo) com regras simples, e o M3.3 concentrar as simulações, os datasets plantados e o teste de falsos positivos, que precisa de todas as regras.

## Dependências e ordem

| Bloco | Depende de (mergeado em `develop`) | Pode andar em paralelo com |
|---|---|---|
| M3.0 | — | M3.2 (conflitos só em `main.py`, `config.py` e `compartilhado/`) |
| M3.1 | M3.0 | M3.2, M3.3 |
| M3.2 | — | M3.0, M3.1 |
| M3.3 | M3.2 (e M3.0, que o script dos datasets plantados usa) | M3.1 |
| M3.4 | M3.3 (e M3.1, pela navegação Gerador → Detector) | — |
| M3.5 | M3.0 e M3.3 (backend); a parte da tela 8 depois do M3.4 | — |
| M3.6 | todos | — |

```
backend : M3.0 ─────────── M3.2 ── M3.3 ──────────┐
frontend:        M3.1 ──────────────────── M3.4 ──┴── M3.5 ── M3.6 (release v0.3.0)
```
Execução prevista (um bloco por vez): M3.0 → M3.1 → M3.2 → M3.3 → M3.4 → M3.5 → M3.6. Datas sugeridas: M3.0 17/10 · M3.1 24/10 · M3.2 30/10 · M3.3 06/11 · M3.4 13/11 · M3.5 18/11 · release 20/11 (folga até 27/11).

## Convenções que valem para todos os blocos

- Regras de `CLAUDE.md` e `padroes-codigo.md`. Rodar **antes de cada push**:
  - backend (em `backend/`, venv `.venv`): `ruff check . && ruff format --check . && mypy app && complexipy app --max-complexity-allowed 15 && pytest`
  - frontend (em `frontend/`): `npm run lint && npm run format && npm run test && npm run build`
  - raiz: `npx --yes jscpd@4 backend/app backend/tests frontend/src`
- Worktree novo: `python -m venv .venv` + `.venv/Scripts/python -m pip install -e ".[dev]"` em `backend/`; `npm ci` em `frontend/`.
- Depois de mudar a API: `python scripts/exportar_openapi.py` (em `backend/`) → `npm run gerar:tipos` (em `frontend/`) → commit do `schema.d.ts` **no mesmo bloco do backend** (M3.0, M3.2, M3.3, M3.5).
- TDD em toda tarefa: teste falhando → código → teste passando → commit (Conventional Commits em português, **sem atribuição de IA**).
- Nunca silenciar lint, tipos ou complexidade (`noqa`, `eslint-disable`, `type: ignore`, `pragma: no cover`, overrides). Sem parâmetro booleano que escolhe comportamento (sonarjs `no-selector-parameter`); sem ref dentro de objeto devolvido por hook (`react-hooks/refs`); o ruff recusa `assert a and b`.
- Nomes que começam com "test" são coletados pelo pytest: nos testes, importe o módulo (ex.: `estatistica.teste_binomial`, `estatistica.teste_runs`).
- **pandas 3**: nunca comparar `dtype == object`. O `to_excel` do pandas grava horários como texto (use o openpyxl direto nos testes). Arquivos escritos por script: LF, UTF-8.
- Números exibidos com o sinal de menos (−) (`formatar_com_sinal`, D107).
- Aleatoriedade sempre com `np.random.default_rng(semente)`; nada de `np.random.seed` global. Testes com semente fixa.
- Toda decisão nova vai para `docs/decisions.md` com o **próximo número livre** (D108–D114 no M3.0, D115–D117 no M3.1; próxima D118); os números abaixo são os previstos na ordem dos blocos. Toda entrega vai para `CHANGELOG.md` › *Não lançado*.
- Teste manual no preview (`.claude/launch.json`: `backend` 8000, `frontend` 5173) antes do push de cada bloco com tela; viewport fixa com `resize_window` e conferência pelo DOM. Depois de editar o backend, o `--reload` apaga os datasets: recarregue o exemplo antes de testar.
- PR, merge e release só com o ok do usuário; merge só com os 3 checks verdes (`gh pr merge N --merge`).

## Contratos do backend

### Compartilhado
- `ServicoAnalise.resumo_numerico(valores: np.ndarray) -> ResumoNumerico` (fachada da análise, função pura sem dataset): `n, media, mediana, desvio_padrao (amostral), minimo, maximo, assimetria (G₁), curtose (G₂)` — com `None` onde não se aplica (n < 3 para G₁, n < 4 para G₂, DP zero). Usada pelo gerador (original × gerado) e pelo detector (R10), sem repetir as fórmulas da análise (D108).
- `compartilhado/estatistica.py` ganha os testes usados por mais de um domínio ou com fórmula própria na spec 12: `teste_binomial_unilateral(k, n, p0)` (P(X ≥ k)), `teste_qui_quadrado(observados, esperados)` (estatística, gl, p), `teste_runs(acima: np.ndarray)` (Z e p bilateral da spec 12), `autocorrelacao_lag1(valores)`.
- `Severidade = StrEnum("info", "atencao", "alta")` em `compartilhado/tipos.py`, com `ORDEM_SEVERIDADE = (alta, atencao, info)`.

### Gerador (M3.0) — domínio `gerador`
```
Origem       {dataset_id: str, coluna: str}
PedidoUnivariado {
  origem: Origem | None,
  tipo: "continua" | "discreta" | "binaria" | None,      # obrigatório sem origem; ignorado com origem
  x: int (1..1_000_000),
  modo: "preservar" | "parametros",                     # sem origem: só "parametros"
  media: float | None, desvio: float | None (> 0),      # modo parametros (contínua e discreta)
  p: float | None (0..1), rotulos: [str, str] | None,   # binária em parâmetros; sem origem, rótulos padrão ["0", "1"] (sucesso = o 2º)
  semente: int | None (0..2³²−1),                       # sem semente, o servidor sorteia uma e devolve
  limitar_faixa: bool = False                           # só com origem numérica
}
OrigemPar    {dataset_id: str, x: str, y: str}
PedidoBivariado {
  origem: OrigemPar | None,
  n: int (3..1_000_000),
  media_x, media_y, desvio_x, desvio_y: float | None,   # sem origem: obrigatórios; com origem: omitido = copiado do par
  rho: float | None (−1..1),                            # idem (r de Pearson do par)
  nome_x, nome_y: str | None,                           # sem origem: padrão "x" e "y"
  ajuste_exato: bool = True,
  semente: int | None
}
ParametroGeracao {nome: str, valor: str}                 # já formatado: "Média" · "70,31" (nome no OpenAPI: não conflita com o Parametro da análise)
LinhaComparacao  {estatistica: str, original: float | None, gerado: float | None, diferenca: float | None}
Gerado {
  gerado_id: str, tipo: "univariado" | "bivariado",
  colunas: [str], n: int, semente: int,
  origem: {dataset_id, nome_arquivo, colunas: [str]} | None,
  metodo: str,                                          # "Normal com reescala" · "KDE com reescala" · "Poisson" · "Empírica" · "Bernoulli" · "Sorteio pelas frequências" · "Cholesky"
  explicacao: str,                                      # "Como geramos" (spec 11, linguagem simples)
  parametros: [ParametroGeracao],
  amostra: [ {coluna: valor} ],                          # primeiras 50 linhas
  comparacao: [LinhaComparacao],
  figuras: [Figura]                                     # univariado: sobreposicao; bivariado: dispersao
}
Adotado { dataset_id: str, nome_arquivo: str, n_linhas: int, modo: "novo" | "anexar" }
```
| Método | Rota | Corpo/Query | Resposta |
|---|---|---|---|
| POST | `/gerador/univariado` | `PedidoUnivariado` | `Gerado` (201) |
| POST | `/gerador/bivariado` | `PedidoBivariado` | `Gerado` (201) |
| GET | `/gerador/{gid}` | — | `Gerado` (para o relatório e para reabrir) |
| GET | `/gerador/{gid}/csv` | — | `text/csv` (`;` e vírgula decimal, como o app lê; nome `gerado-{colunas}.csv`) |
| POST | `/gerador/{gid}/adotar` | `{modo: "novo" | "anexar", dataset_id?: str}` | `Adotado` (201) |
| GET | `/gerador/origem` | `dataset_id`, `coluna` | `ResumoOrigem` (M3.1, D116) |
| GET | `/gerador/origem-par` | `dataset_id`, `x`, `y` | `ResumoOrigemPar` (M3.1, D116) |

- **Comparação** (univariado numérico): n, Média, Mediana, Desvio padrão, Mínimo, Máximo, Assimetria, Curtose; `diferenca = gerado − original` (absoluta, como no print 6a; D110); sem origem, `original = None` e `diferenca = None`. Qualitativas: uma linha "fr% · {categoria}" por categoria (diferença em pontos percentuais). Bivariado: Média X, Média Y, DP X, DP Y e "Correlação (r)" com o alvo (ρ) na coluna `original` quando não há origem.
- **Gerações em memória:** `RepositorioGerados` no domínio `gerador` (limite `max_gerados = 20`, o mais antigo sai), injetado como o de datasets (ADR 0009). Sumiu → 404 `GERADO_NAO_ENCONTRADO`.
- **Adotar "novo":** monta o CSV da geração e chama `ServicoDatasets.importar` (classificação e "ler de novo" funcionam como num upload). **"anexar":** `ServicoDatasets.anexar_linhas(dataset_id, linhas, frase)` (método novo): todas as colunas geradas precisam existir no dataset (senão 400 `COLUNAS_INCOMPATIVEIS`); as linhas entram no fim da versão atual (demais colunas faltantes), viram uma entrada do log ("Anexamos 500 linhas geradas em peso_kg.") e somem com "Desfazer limpeza" (D111).

### Detector (M3.2 e M3.3) — domínio `detector`
```
ExemploAviso   {linhas: [int], valores: [str], texto: str}        # "Linhas 120 a 138: 70, 75, 80, 75, 70…"
DetalhesAviso  {medida: str, valor: str, limiar: str, teste: str | None, p_valor: float | None,
                p_em_palavras: str | None, formula: str | None}
Aviso {
  regra: "R1".."R11", nome_regra: str, severidade: Severidade, colunas: [str],
  titulo: str, resumo: str, por_que: str, exemplo: ExemploAviso | None,
  pode_ser_normal: str, o_que_fazer: str, detalhes: DetalhesAviso,
  figura: Figura | None                                           # R1, R8, R9 (M3.3; spec 08)
}
RegraNaoAplicada {regra: str, nome_regra: str, coluna: str | None, motivo: str, frase: str}
ResumoDetector {
  total: int, por_severidade: {alta: int, atencao: int, info: int},
  colunas_afetadas: [str], regras_verificadas: int, regras_nao_aplicadas: int,
  frase: str,                                                      # "Encontramos 5 alertas em 3 colunas"
  detalhe: str,                                                    # "altura_m, peso_kg e idade · 9 regras verificadas, 2 não se aplicam a este arquivo"
  vazio: str | None                                                # texto da spec 16 quando total = 0
}
ResultadoDetector {resumo: ResumoDetector, avisos: [Aviso], nao_aplicadas: [RegraNaoAplicada]}
```
| Método | Rota | Query | Resposta |
|---|---|---|---|
| GET | `/datasets/{id}/detector` | `regras` (lista `R1`..`R11`; sem = todas; outro → 422) | `ResultadoDetector` |
| GET | `/datasets/{id}/linhas` | `de`, `ate` (índices das linhas, inclusive; no máximo 200) | `[LinhaDados]` da versão atual |
| GET | `/datasets/exemplos` | — | `[{arquivo, descricao}]` (M3.3) |
| POST | `/datasets/exemplo` | `arquivo` (padrão `pesquisa_saude.txt`) | `DatasetCriado` (M3.3; fora da lista → 404 `EXEMPLO_NAO_ENCONTRADO`) |

- **Ordem dos avisos:** severidade (alta → atenção → info), depois código da regra, depois coluna. `regras_verificadas` = regras aplicáveis a pelo menos uma coluna/par; `regras_nao_aplicadas` = as que não se aplicam a nada no arquivo; `nao_aplicadas` lista cada (regra, coluna) não verificada, com a frase da spec 16.
- **Linhas:** `exemplo.linhas` usa o mesmo número de `LinhaDados.linha` (índice da linha no dataset, o que a prévia mostra); o drawer pede `GET /linhas?de=&ate=` com ±3 linhas de contexto.
- **Entrada das regras** (domínio puro): `TabelaDetector {n_linhas, linhas: np.ndarray (índices), colunas: dict[str, ColunaDetector]}` com `ColunaDetector {nome, tipo, numeros: np.ndarray | None (NaN nos faltantes, na ordem das linhas), textos: tuple[str | None, ...], datas: np.ndarray | None}` — montada pelo `ServicoDetector(datasets, analise)` a partir de `ServicoDatasets.coluna_para_analise` (+ `reconhecer_datas` para as colunas `data` e, no M3.3, G₁/G₂ de `ServicoAnalise.resumo_numerico` para a R10).

### Relatório (M3.5)
- `Secao` ganha `gerador` e `detector` (ordem: leitura, tipos, limpeza, analises, distribuicoes, bivariada, gerador, detector); sem `?secoes=` → as 8.
- `?gerado={gid}`: a seção Gerador mostra essa geração (parâmetros, método, explicação, comparação e figura); sem `gerado` ou com geração expirada, a seção não entra (a tela 8 desabilita a caixa).
- Seção Detector: resumo, avisos completos com os detalhes técnicos abertos e a figura, e as regras não verificadas.

### Códigos de erro novos
| Código | HTTP | Mensagem (spec 16) | Bloco |
|---|---|---|---|
| `GERADO_NAO_ENCONTRADO` | 404 | Os dados gerados não estão mais disponíveis. Gere de novo na etapa Gerador. | M3.0 |
| `MODO_NAO_APLICAVEL` | 400 | Novos parâmetros não se aplicam a {tipo}: só dá para preservar as frequências. | M3.0 |
| `PARAMETROS_INCOMPLETOS` | 400 | Informe {campos} para gerar com novos parâmetros. | M3.0 |
| `COLUNA_NAO_GERAVEL` | 400 | A coluna {col} {é um identificador \| tem datas} e não pode servir de origem. | M3.0 |
| `COLUNAS_INCOMPATIVEIS` | 400 | O dataset não tem a coluna {col}. Use "Usar como novo dataset". | M3.0 |
| `INTERVALO_INVALIDO` | 400 | Peça no máximo 200 linhas, com "de" menor ou igual a "até". | M3.2 |
| `EXEMPLO_NAO_ENCONTRADO` | 404 | Não encontramos o exemplo {arquivo}. | M3.3 |

## Contratos do frontend

| Bloco | O que muda |
|---|---|
| M3.1 | `CAMINHOS.gerador`; etapa 6 sem `disponivelEm`; `shared/ui/CartaoOpcao` (rádio em cartão), `shared/ui/Slider`; consulta da análise de uma coluna em `shared/api` (se ainda estiver em `features/analise`); `sessao.ultimoGerado?: {id, descricao}` (para o relatório); trocar para o dataset adotado reaproveita o fluxo de "Trocar arquivo" |
| M3.4 | `CAMINHOS.detector`; etapa 7 sem `disponivelEm`; `shared/ui/Drawer`, `ChipFiltro` (`role="checkbox"`), `BadgeSeveridade`, `Accordion`; filtros e agrupamento na URL (`?sev=&agrupar=`, como D78); lista de exemplos na tela Importar |
| M3.5 | `SECOES_RELATORIO` com `gerador` e `detector`; caixa "Gerador" desabilitada sem `sessao.ultimoGerado` (nota "Gere dados na etapa Gerador para incluir esta seção."); `?gerado=` no pedido |

**Navegação:** M3.1: Bivariada "Continuar para Gerador" · Gerador "Voltar para Bivariada" / "Continuar para Relatório" · Relatório "Voltar para Gerador". M3.4: Gerador "Continuar para Detector" · Detector "Voltar para Gerador" / "Continuar para Relatório" · Relatório "Voltar para Detector".

## Decisões previstas (entram em `docs/decisions.md` no bloco indicado; use o próximo número livre)
| # | Decisão | Bloco |
|---|---|---|
| D108 | `ServicoAnalise.resumo_numerico(valores)` como função pura da fachada: gerador e detector reaproveitam média, DP, G₁ e G₂ sem repetir fórmulas | M3.0 |
| D109 | Semente opcional: sem semente o servidor sorteia uma (0..2³²−1) e a devolve, para o usuário repetir o resultado | M3.0 |
| D110 | Comparação com diferença absoluta (gerado − original), como no print 6a (a spec 11 falava em %); qualitativas em pontos percentuais | M3.0 |
| D111 | Adotar "novo" reaproveita `importar` (CSV da geração); "anexar" vira entrada do log da limpeza e sai com "Desfazer limpeza"; colunas que não existem no dataset → `COLUNAS_INCOMPATIVEIS` | M3.0 |
| D112 | "Limitar à faixa original": valores fora de [mín, máx] são sorteados de novo e a reescala é refeita (até 20 rodadas; depois recorte); média e DP ficam muito próximos, mas não exatos (texto do print 6a) | M3.0 |
| D113 | Sobreposição com classes comuns (faixa da união, k de Sturges da menor série) em frequência relativa, barras `overlay` 0,55 (`graficos-plotly.md`); qualitativas com barras agrupadas | M3.0 |
| D114 | Bivariado com ajuste exato não arredonda (r = ρ exato); sem ajuste, casas das colunas de origem (2 sem origem); contrato `Figura` em `core/esquemas.py` | M3.0 |
| D115 | Tela 6: aba na URL, gerador sem dataset, campo sem edição = valor exato da origem, diferença na precisão dos valores, `ultimoGerado` na sessão | M3.1 |
| D116 | `GET /gerador/origem` e `/gerador/origem-par` para o formulário | M3.1 |
| D117 | Leitura: `;` vence vírgulas decimais (defeito achado no teste do M3.1) | M3.1 |
| D118 | Detector: Template Method (`RegraBase.executar` = alvos → aplicável? → medir → dispara? → aviso) com textos só em `textos.py`; entrada `TabelaDetector` montada pelo serviço | M3.2 |
| D119 | R4/R9: "dígito final" = último dígito na resolução da coluna (maior nº de casas observado); regra não se aplica se esse dígito é constante | M3.2 |
| D120 | R5: duplicatas exatas sempre; quase duplicatas só até 5.000 linhas (distância par a par O(n²)), com o motivo nas não aplicadas acima disso | M3.2 |
| D121 | R1: referência por simulação com semente fixa e somas acumuladas (vetorizado); R2 em todos os pares de numéricas | M3.3 |
| D122 | Figuras do detector (R1 média por bloco, R8 Benford, R9 último dígito) dentro dos detalhes técnicos (spec 08; os prints não mostram gráficos) | M3.3 |
| D123 | Datasets plantados gerados por `backend/scripts/gerar_exemplos_detector.py` (semente fixa, reprodutível); `vendas_correlacao_puxada.txt` ganha coluna `data` para demonstrar também a R6; exemplos escolhíveis em `POST /datasets/exemplo?arquivo=` | M3.3 |
| D124 | Tela 7: filtros e agrupamento na URL; 1º alerta de cada grupo aberto; drawer com ±3 linhas de contexto; "Exportar estas linhas" gera o CSV no navegador | M3.4 |
| D125 | Relatório com `gerador` (via `?gerado=`) e `detector` já no M3 (escolha do usuário em 10/10/2026); padrão = 8 seções | M3.5 |

## Dependências novas
- Nenhuma: `numpy` e `scipy` (KDE, Poisson, testes) já estão no backend; o frontend usa só componentes próprios.

## Tamanho dos PRs
| Bloco | Linhas estimadas (código + testes) |
|---|---|
| M3.0 | ~1.800 |
| M3.1 | ~1.500 |
| M3.2 | ~1.600 |
| M3.3 | ~1.500 (+ arquivos de dados) |
| M3.4 | ~1.700 |
| M3.5 | ~700 |
| M3.6 | ~150 (docs e versões) |

## Pontos de atenção encontrados nas specs e no design
1. **Diferença na comparação:** a spec 11 pede `diferenca_pct`; o print 6a mostra a diferença absoluta (+0,3, −0,27). Seguimos o print (D110) e atualizamos a spec 11.
2. **Limitar à faixa × reescala exata:** recortar depois da reescala quebra a média e o DP exatos. O print 6a diz "Valores fora de 43,8 a 92,9 foram sorteados de novo": resorteio + reescala iterativa (D112). A tolerância de 1% da spec vale sem `limitar_faixa`.
3. **Discreta "preservar" com x̄ = 0:** o critério de Poisson divide por x̄; com x̄ = 0 vai para a empírica.
4. **Binária:** o "sucesso" segue a regra da análise (`sucesso_padrao`, spec 05), para p̂ bater com a tela 4.
5. **Sobreposição com até 1.000.000 valores:** a figura leva só as alturas das barras (ADR 0003), nunca os valores; dispersão com no máximo 5.000 pontos (D101).
6. **R4/R9 "casa variável":** a spec não define o dígito final de números com casas diferentes; D119.
7. **R5 quase duplicatas** é O(n²); limite de 5.000 linhas (D120).
8. **Detector × gráficos:** spec 08 lista figuras por regra, os prints não mostram; ficam nos detalhes técnicos (D122).
9. **Contagem de regras do resumo:** o print diz "9 regras verificadas, 2 não se aplicam a este arquivo" e lista não verificações por coluna; definimos as duas contagens por regra e a lista por (regra, coluna) (contrato acima).
10. **Falsos positivos:** as amostras do teste são arredondadas a 2 casas (como medições reais); sem isso, R4 e R9 não se aplicam (dígito final de float é ruído) e o teste não mede nada.
