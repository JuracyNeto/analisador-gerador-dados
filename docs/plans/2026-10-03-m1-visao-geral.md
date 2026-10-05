# M1 — Prévia completa: visão geral dos blocos

> Índice do M1. Cada bloco tem plano, branch e PR próprios. Os contratos abaixo são a **fonte única** entre os blocos: quem implementa um bloco não muda um contrato sem atualizar este arquivo e avisar no PR.

**Objetivo do marco:** com um TXT/CSV de `dados-exemplo/`, o usuário importa, confere os tipos, limpa, analisa uma coluna (frequências, tendência central, separatrizes, dispersão, gráficos) e baixa um mini relatório. Prazo **30/10/2026**, versão **v0.1.0**.

**Critérios de pronto** (vêm do pedido do M1 e do `roadmap.md`):
- Itens do M1 no checklist do professor funcionando de ponta a ponta com `dados-exemplo/pesquisa_saude.txt`.
- Cobertura ≥ 80% em `dominios/` e `compartilhado/`; CI verde (`backend`, `frontend`, `duplicacao`) em todos os PRs.
- Telas 1–4 e 8 conferem com `docs/design/telas.md` nos temas claro e escuro, com os estados carregando, vazio e erro.

## Blocos

| Bloco | Plano | Branch | Conteúdo |
|---|---|---|---|
| **M1.1** Base visual | `2026-10-03-m1-1-base-visual.md` | `chore/frontend-base-visual` | Fontes locais, tokens, tema, layout (BarraEtapas, Cabecalho, PaginaEtapa), componentes de `shared/ui`, formatadores pt-BR, sessão do dataset, wrapper Plotly |
| **M1.2** Datasets: leitura e tipos | `2026-10-03-m1-2-datasets-leitura-tipos.md` | `feat/datasets-leitura-tipos` | `compartilhado/` (tipos, números, séries, textos), leitura (spec 01), classificação (02), repositório (ADR 0004), endpoints de importação e colunas (14), `dados-exemplo` no fluxo |
| **M1.3** Datasets: limpeza | `2026-10-03-m1-3-datasets-limpeza.md` | `feat/datasets-limpeza` | Diagnóstico, ações, log em frases, desfazer, reclassificação (spec 03) |
| **M1.4** Análise descritiva | `2026-10-03-m1-4-analise-descritiva.md` | `feat/analise-descritiva` | Frequências (04), tendência (05), separatrizes e "onde está meu valor" (06), dispersão (07), endpoints `analise` e `posicao` |
| **M1.5** Gráficos e mini relatório | `2026-10-03-m1-5-graficos-relatorio.md` | `feat/graficos-relatorio` | Fábrica de figuras por tipo + tema (08, ADR 0003), figuras na `Analise`, relatório HTML (13) |
| **M1.6** Telas 1–3 | `2026-10-03-m1-6-telas-importar-variaveis-limpeza.md` | `feat/frontend-importar-variaveis-limpeza` | ChipTipo, telas Importar, Variáveis e Limpeza |
| **M1.7** Telas 4 e 8 | `2026-10-03-m1-7-telas-univariada-relatorio.md` | `feat/frontend-univariada-relatorio` | Tela Análise univariada (sem "Forma") e tela Relatório |

**Por que 7 blocos e não 5:** o domínio `datasets` e as telas ficariam com PRs de 2.000+ linhas (o ideal em `padroes-codigo.md` §8 é < 400). Separar a limpeza (M1.3) e dividir as telas em dois blocos (M1.6, M1.7) mantém PRs revisáveis e libera trabalho em paralelo: cada grupo de telas depende de backends diferentes.

## Dependências

| Bloco | Depende de (mergeado em `develop`) | Pode andar em paralelo com |
|---|---|---|
| M1.1 | — | M1.2, M1.3, M1.4, M1.5 |
| M1.2 | — | M1.1 |
| M1.3 | M1.2 | M1.4, M1.1 |
| M1.4 | M1.2 | M1.3, M1.1 |
| M1.5 | M1.3 (log no relatório) e M1.4 (estatísticas) | M1.6 |
| M1.6 | M1.1, M1.2, M1.3 | M1.4, M1.5 |
| M1.7 | M1.1, M1.4, M1.5 e M1.6 (reutiliza `shared/api/dataset.ts`, helpers de teste, `SemDataset`, `useValorAtrasado`) | — |

```
backend : M1.2 ──┬── M1.3 ──┐
                 └── M1.4 ──┴── M1.5 ──┐
frontend: M1.1 ─────────────── M1.6 ───┴── M1.7 ── release v0.1.0
                 (M1.6 espera M1.3)
```
Caminho crítico: M1.2 → M1.3 → M1.6 → M1.7 (o M1.4 → M1.5 corre em paralelo com o M1.6).

**Antes de tudo:** o PR desta branch (`docs/plano-m1`) entra em `develop`, porque os testes do M1.2 em diante usam `dados-exemplo/pesquisa_saude.txt`. O teste de tema do M1.5 lê o primeiro bloco `{…}` do `frontend/src/shared/ui/tokens.css` (o `:root` claro); o M1.1 não deve pôr outro bloco antes dele. Os módulos puros da fábrica de gráficos (M1.5, tarefas 1–4) só dependem de `compartilhado/` e podem começar assim que o M1.2 entrar.

## Convenções que valem para todos os blocos

- Comandos de qualidade e regras de `CLAUDE.md`/`padroes-codigo.md`. Rodar **antes de cada commit**:
  - backend (em `backend/`, venv ativo): `ruff check . && ruff format --check . && mypy app && complexipy app --max-complexity-allowed 15 && pytest`
  - frontend (em `frontend/`): `npm run lint && npm run format && npm run test && npm run build`
  - raiz: `npx --yes jscpd@4 backend/app backend/tests frontend/src`
- **pandas 3** está instalado (`pandas 3.0`, copy-on-write e dtype `str` para textos). Usar `pd.api.types.is_numeric_dtype`/`is_string_dtype`, nunca comparar `dtype == object`.
- Arquivos escritos por script: LF, UTF-8.
- Sem atribuição de IA em commits e PRs.
- Depois de mudar a API: `python scripts/exportar_openapi.py` (em `backend/`) → `npm run gerar:tipos` (em `frontend/`) → commit do `schema.d.ts`.
- Toda decisão nova vai para `docs/decisions.md` (próxima: **D48**); estrutural vira ADR (próxima: **0009**). Toda entrega vai para `CHANGELOG.md` › *Não lançado*.

## Contratos do backend

### Injeção de dependência entre domínios (ADR 0009 proposto)
- Cada domínio expõe em `servico.py` uma classe `Servico<Dominio>` (fachada) e um provedor sem FastAPI:
  ```python
  @lru_cache
  def obter_servico_datasets() -> ServicoDatasets: ...
  ```
- O `router.py` é o único lugar com `Depends`. Domínios que usam outro recebem a fachada no construtor, montada no router:
  ```python
  def _servico(datasets: Annotated[ServicoDatasets, Depends(obter_servico_datasets)]) -> ServicoAnalise:
      return ServicoAnalise(datasets)
  ```
- Testes de API trocam só `obter_servico_datasets` em `app.dependency_overrides`; os demais domínios herdam a troca.

### `compartilhado/` (M1.2)
| Módulo | Conteúdo |
|---|---|
| `tipos.py` | `TipoVariavel(StrEnum)`: `nominal, ordinal, discreta, continua, binaria, identificador`; `OrigemTipo(StrEnum)`: `auto, manual`; `TIPOS_NUMERICOS`, `TIPOS_CATEGORICOS` |
| `numeros.py` | `formatar_numero(valor, casas_significativas=4)`, `formatar_inteiro(n)`, `formatar_percentual(valor_0a100, casas=1)`, todos pt-BR |
| `series.py` | `converter_para_numero(serie, decimal)`, `proporcao_numerica(serie, decimal)`, `eh_inteira(serie)`, `casas_decimais(serie)` |
| `textos.py` | `normalizar_texto(texto)` (minúsculas, sem acento, espaços colapsados), `pluralizar(n, singular, plural)` |

### Linhas e números de linha
O `DataFrame` lido recebe índice `1..n` (número da linha de dados no arquivo). O índice **não é refeito** depois da limpeza: "linha 45" sempre se refere à mesma linha do arquivo original (D49).

### Endpoints do M1 (prefixo `/api`)
| Método | Rota | Corpo / query | Resposta | Bloco |
|---|---|---|---|---|
| POST | `/datasets` | multipart `arquivo` + form `separador?`, `decimal?`, `codificacao?`, `aba?`, `tem_cabecalho?` | `DatasetCriado` (201) | M1.2 |
| POST | `/datasets/exemplo` | — | `DatasetCriado` (201) | M1.2 |
| GET | `/datasets/{id}` | `?pagina=1&tamanho=20&versao=atual\|original` | `PaginaDataset` | M1.2 |
| DELETE | `/datasets/{id}` | — | 204 | M1.2 |
| GET | `/datasets/{id}/colunas` | — | `TipoColuna[]` | M1.2 |
| PATCH | `/datasets/{id}/colunas/{coluna}` | `AlteracaoTipo` | `TipoColuna` | M1.2 |
| GET | `/datasets/{id}/diagnostico` | `?limites={"idade":{"min":1,"max":110}}` (JSON) | `Diagnostico` | M1.3 |
| POST | `/datasets/{id}/limpeza` | `PedidoLimpeza` | `ResultadoLimpeza` | M1.3 |
| POST | `/datasets/{id}/limpeza/desfazer` | — | `ResultadoLimpeza` | M1.3 |
| GET | `/datasets/{id}/colunas/{coluna}/analise` | `?classes=3..30&sucesso=` | `Analise` | M1.4 (figuras no M1.5) |
| GET | `/datasets/{id}/colunas/{coluna}/posicao` | `?valor=&tipo=quartil\|decil\|percentil` | `Posicao` | M1.4 |
| GET | `/datasets/{id}/relatorio` | `?secoes=leitura&secoes=tipos&secoes=limpeza&secoes=analises&colunas=a&colunas=b&offline=false` | `text/html` | M1.5 |

### Schemas (nomes exatos; viram `components['schemas'][Nome]` no frontend)
`Celula = str | float | int | bool | None`

**datasets (M1.2)**
- `Aviso {codigo: str, mensagem: str}`
- `MetadadosLeitura {formato: "txt"|"csv"|"tsv"|"xlsx"|"json", codificacao: str|None, separador: str|None, decimal: str|None, tem_cabecalho: bool|None, n_linhas: int, n_colunas: int, abas: list[str], avisos: list[Aviso], motivos: dict[str, str]}` — `motivos` tem as chaves `formato, separador, decimal, codificacao, cabecalho` (textos da tela 1a, D53).
- `TipoColuna {coluna, tipo: TipoVariavel, motivo, origem: "auto"|"manual", n_validos, n_faltantes, n_distintos, exemplos: list[str], categorias_ordem: list[str], contagens: dict[str, int]}` — `contagens` só é preenchido para colunas categóricas (editor de ordem mostra "{n} linhas").
- `LinhaDados {linha: int, valores: dict[str, Celula]}`
- `DatasetCriado {dataset_id, nome_arquivo, metadados: MetadadosLeitura, previa: list[LinhaDados], colunas: list[TipoColuna]}`
- `ResumoDataset {dataset_id, nome_arquivo, metadados, n_linhas, n_linhas_original, n_colunas, log_limpeza: list[EntradaLog]}`
- `PaginaDataset {resumo: ResumoDataset, versao: "atual"|"original", pagina, tamanho, total_paginas, linhas: list[LinhaDados]}`
- `AlteracaoTipo {tipo: TipoVariavel, categorias_ordem: list[str] | None = None}`

**limpeza (M1.3)**
- `Limites {min: float|None, max: float|None}`
- `ValoresSugeridos {media: float|None, mediana: float|None, moda: Celula}`
- `FaltantesColuna {coluna, n, linhas: list[int], sugeridos: ValoresSugeridos}`
- `GrupoDuplicado {linha_original: int, copias: list[int]}`
- `Ocorrencia {linha: int, valor: Celula}`
- `ForaDeFaixaColuna {coluna, limite_inferior: float, limite_superior: float, origem: "iqr"|"usuario", ocorrencias: list[Ocorrencia]}`
- `Grafia {texto: str, n: int}` · `GrupoGrafias {forma_preferida: str, variacoes: list[Grafia]}` · `InconsistenciaColuna {coluna, grupos: list[GrupoGrafias]}`
- `TipoMistoColuna {coluna, ocorrencias: list[Ocorrencia]}`
- `Diagnostico {n_linhas, faltantes, duplicados, fora_de_faixa, inconsistencias, tipo_misto}` (listas dos itens acima)
- `AcaoLimpeza {problema: "faltantes"|"duplicados"|"fora_de_faixa"|"inconsistencia"|"tipo_misto", acao: "manter"|"remover_linhas"|"preencher_media"|"preencher_mediana"|"preencher_moda"|"preencher_valor"|"remover"|"limitar"|"marcar_faltante"|"unificar", coluna: str|None, valor: Celula, limites: Limites|None, grupo: str|None}`
- `PedidoLimpeza {acoes: list[AcaoLimpeza]}`
- `EntradaLog {problema, acao, coluna: str|None, linhas_afetadas: list[int], antes_exemplo: str, depois_exemplo: str, quando: datetime, frase: str}`
- `ResultadoLimpeza {log: list[EntradaLog], n_linhas, n_linhas_original, colunas: list[TipoColuna]}` — `log` é o acumulado desde a importação (ou desde o último "Desfazer tudo").

**analise (M1.4)**
- `NaoAplicavel {item: str, motivo: str}`
- `Formula {chave: str, nome: str, latex: str, texto: str}` — `chave` estável (`media`, `mediana`, `moda`, `moda_czuber`, `proporcao`, `frequencia_relativa`, `frequencia_acumulada`, `sturges`, `amplitude_classe`, `ponto_medio`, `quantil`, `posicao_percentil`, `amplitude`, `variancia`, `variancia_populacional`, `desvio_padrao`, `iqr`, `cv`, `variancia_binaria`)
- `Medida {valor: float|str|None, aplicavel: bool, motivo: str|None, calculo: str|None, interpretacao: str|None, formula: str|None}` — `formula` é a `chave` da fórmula; o card acha a sua com `formulas.find(f => f.chave === medida.formula)`. Escalas: `cv.valor` em % (0–100), `proporcao.valor` de 0 a 1.
- `LinhaFrequencia {rotulo: str, valor: float|str|None, limite_inferior: float|None, limite_superior: float|None, ponto_medio: float|None, fi: int, fri: float, fr_pct: float, f_acum: int|None, fr_acum: float|None, fr_acum_pct: float|None}`
- `TabelaFrequencia {tipo, linhas, total: int, k: int|None, k_sturges: int|None, h: float|None, metodo_classes: "sturges"|"usuario"|None, acumulada_aplicavel: bool, motivo_acumulada: str|None, indice_modal: int|None}`
- `Moda {valores: list[float|str], classificacao: "amodal"|"unimodal"|"bimodal"|"multimodal", interpretacao: str}`
- `Tendencia {media: Medida, mediana: Medida, moda: Moda, moda_czuber: Medida, proporcao: Medida}`
- `ValorSeparatriz {rotulo: str, p: float, valor: float|str}`
- `Separatrizes {quartis, decis, percentis: list[ValorSeparatriz], destaques: list[str]}` — `percentis` tem P1..P99; `destaques` = `["P1","P5","P10","P25","P50","P75","P90","P95","P99"]`.
- `Dispersao {amplitude, variancia, variancia_populacional, desvio_padrao, desvio_padrao_populacional, iqr, cv: Medida, classificacao_cv: "baixa"|"media"|"alta"|None}`
- `Figura {id: str, rotulo: str, titulo: str, resumo: str, porque: str, recomendado: bool, dados: dict[str, Any]}` — `rotulo` é o nome curto para o Segmented ("Histograma", "Bastões", "Barras", "Boxplot", "Ogiva", "Acumulada", "Pizza"); `dados` é o JSON do Plotly (`{"data": [...], "layout": {...}}`), **sem** template (o frontend aplica o tema).
- `Analise {coluna, tipo, n, n_faltantes, aplicavel: dict[str, bool], nao_aplicavel: list[NaoAplicavel], frequencias: TabelaFrequencia, tendencia: Tendencia, separatrizes: Separatrizes|None, dispersao: Dispersao|None, interpretacoes: list[str], formulas: list[Formula], figuras: list[Figura]}`
  - Chaves de `aplicavel`: `acumulada, media, mediana, moda_czuber, proporcao, separatrizes, posicao, dispersao, variancia, cv`. O frontend desabilita a aba "Separatrizes" se `aplicavel.separatrizes` é falso e a aba "Dispersão" se `aplicavel.dispersao` é falso, usando o `motivo` do item em `nao_aplicavel` como tooltip.
  - No M1.4 `figuras` vem `[]`; o M1.5 preenche.
- `Posicao {valor: float, tipo: "quartil"|"decil"|"percentil", regiao: str, indice: int, limite_inferior: float|None, limite_superior: float|None, posicao_percentil: float, fora_da_faixa: "abaixo"|"acima"|None, minimo: float, maximo: float, marcas: list[ValorSeparatriz], frase: str}` — `marcas` tem no máximo 9: 3 (quartil), 9 (decil) ou os 9 destaques (percentil).
- `LinhaFrequencia.rotulo` já vem formatado ("60,0 ⊢ 65,5", "3", "bom"); `motivo_acumulada` e todo `motivo` são frases completas.

**Ids de figuras (M1.5)**: `principal` (sempre), `boxplot` (discreta, contínua), `ogiva` (contínua), `acumulada` (ordinal, discreta), `pizza` (nominal com ≤ 5 categorias).

### Códigos de erro novos
| Código | HTTP | Mensagem (spec 16) | Bloco |
|---|---|---|---|
| `ARQUIVO_VAZIO` | 400 | O arquivo está vazio. | M1.2 |
| `FORMATO_NAO_SUPORTADO` | 400 | Este tipo de arquivo não é aceito. Use TXT, CSV, TSV, XLSX ou JSON. | M1.2 |
| `ARQUIVO_GRANDE` | 413 | O arquivo passa de 50 MB. | M1.2 |
| `JSON_INVALIDO` | 400 | Não conseguimos ler este JSON. Verifique se é uma lista de registros. | M1.2 |
| `ARQUIVO_ILEGIVEL` | 400 | Não conseguimos ler este arquivo como tabela. | M1.2 |
| `DATASET_NAO_ENCONTRADO` | 404 | Sua sessão expirou. | M1.2 |
| `COLUNA_NAO_ENCONTRADA` | 404 | Não encontramos a coluna *{col}*. | M1.2 |
| `TIPO_INCOMPATIVEL` | 400 | Esta coluna tem textos; não pode ser numérica. | M1.2 |
| `LIMITES_INVALIDOS` | 400 | O mínimo precisa ser menor que o máximo ({max}). | M1.3 |
| `ACAO_INCOMPATIVEL` | 400 | Esta ação não serve para a coluna *{col}*. | M1.3 |
| `COLUNA_IGNORADA` | 400 | A coluna *{col}* é um identificador e fica fora das análises. | M1.4 |
| `COLUNA_VAZIA` | 400 | A coluna *{col}* não tem valores para analisar. | M1.4 |
| `POSICAO_NAO_APLICAVEL` | 400 | "Onde está meu valor?" só funciona com colunas numéricas. | M1.4 |

## Contratos do frontend (M1.1 entrega; M1.6 e M1.7 usam)

### Rotas (`app/rotas.ts` + `app/roteador.ts`, cada página com `lazy()`)
`/` → redireciona para `/importar` · `/importar` · `/variaveis` · `/limpeza` · `/analise` · `/relatorio` · `/bivariada`, `/gerador`, `/detector` (bloqueadas no M1, D60). Todas dentro de `LayoutApp` (barra lateral + cabeçalho + `<Outlet/>`).

### Etapas (`app/etapas.ts`)
```ts
export const ETAPAS = [
  { numero: 1, nome: 'Importar', caminho: '/importar' },
  { numero: 2, nome: 'Variáveis', caminho: '/variaveis' },
  { numero: 3, nome: 'Limpeza', caminho: '/limpeza' },
  { numero: 4, nome: 'Análise univariada', caminho: '/analise' },
  { numero: 5, nome: 'Bivariada', caminho: '/bivariada', disponivelEm: 'v0.2' },
  { numero: 6, nome: 'Gerador', caminho: '/gerador', disponivelEm: 'v0.3' },
  { numero: 7, nome: 'Detector', caminho: '/detector', disponivelEm: 'v0.3' },
  { numero: 8, nome: 'Relatório', caminho: '/relatorio' },
] as const;
```

### Sessão, tema e formatação
| Módulo | API |
|---|---|
| `shared/sessao/SessaoProvider.tsx` + `useSessao.ts` | `{ dataset: { id: string; nomeArquivo: string } \| null; definirDataset(d): void; encerrar(): void; etapasVisitadas: ReadonlySet<number>; marcarVisitada(n: number): void }`, persistido em `localStorage('sessao')` (D61) |
| `shared/tema/TemaProvider.tsx` + `useTema.ts` | `{ tema: 'claro' \| 'escuro'; definirTema(t): void }`; `aplicarTemaInicial()` chamado em `main.tsx` antes do render; `localStorage('tema')`, padrão de `prefers-color-scheme` |
| `shared/lib/formatar.ts` | `formatarNumero(v, casasSignificativas = 4)`, `formatarInteiro(n)`, `formatarPercentual(v0a100, casas = 1)`, `lerNumeroPtBr(texto): number \| null` |
| `shared/api/erros.ts` | `ehDatasetNaoEncontrado(erro: unknown): boolean`, `textoDoErro(erro: unknown): { mensagem: string; sugestao: string }` |

### Componentes de `shared/ui` (props mínimas; detalhes visuais em `docs/design/componentes.md`)
| Componente | Props |
|---|---|
| `Icone` | `nome: string; preenchido?: boolean; tamanho?: number; rotulo?: string` (sem `rotulo` → `aria-hidden`) |
| `Botao` | `variante?: 'primario'\|'secundario'\|'fantasma'\|'perigo'; tamanho?: 'md'\|'lg'; icone?: string; iconeFinal?: string; carregando?: boolean; textoCarregando?: string` + atributos de `<button>` |
| `Card` | `titulo?: ReactNode; subtitulo?: ReactNode; acoes?: ReactNode; children` |
| `PaginaEtapa` | `etapa: number; titulo: string; ajuda: string; acoesTopo?: ReactNode; children` ("Etapa N de 8" + h1 + ajuda; marca a etapa como visitada) |
| `Banner` | `variante: 'info'\|'atencao'\|'erro'\|'sucesso'; titulo?: string; children; acoes?: ReactNode` |
| `EstadoCarregando` | `mensagem: string; forma?: 'cards'\|'tabela'\|'grafico'` (skeleton + `role="status"`) |
| `EstadoVazio` | `icone: string; titulo: string; descricao: string; acao?: ReactNode` |
| `EstadoErro` | `erro: unknown; aoTentarDeNovo?: () => void; acoes?: ReactNode` (usa `textoDoErro`; `role="alert"`) |
| `ToastProvider` + `useToast()` | `mostrar({ tipo: 'sucesso'\|'erro'; titulo: string; descricao?: string; acao?: { rotulo: string; aoClicar: () => void } })`; some em 6 s, pausa com hover/foco |
| `Tooltip` | `texto: string; children: ReactElement` |
| `Select<T extends string>` | `rotulo: string; valor: T; opcoes: readonly { valor: T; rotulo: string; desabilitada?: boolean }[]; aoMudar(v: T); ajuda?: string; rotuloOculto?: boolean; altura?: 36\|40\|44` (nativo) |
| `CampoNumero` | `rotulo: string; valor: string; aoMudar(texto: string); erro?: string; ajuda?: string` (aceita vírgula) |
| `Segmented<T extends string>` | `rotulo: string; opcoes: readonly { valor: T; rotulo: string; selo?: string }[]; valor: T; aoMudar(v: T)` (`role="radiogroup"`) |
| `Abas<T extends string>` | `rotulo: string; abas: readonly { id: T; rotulo: string; desabilitada?: boolean; motivo?: string }[]; ativa: T; aoMudar(id: T); children` (setas ←/→) |
| `CaixaSelecao` | `rotulo: ReactNode; marcada: boolean; aoMudar(m: boolean); desabilitada?: boolean` |
| `CardMetrica` | `rotulo: string; valor: string; unidade?: string; interpretacao?: string; selo?: string; formula?: { expressao: string; calculo?: string }; naoAplicavel?: { motivo: string }` |
| `Tabela<L>` | `legenda: string; colunas: readonly ColunaTabela<L>[]; linhas: readonly L[]; chave(l: L): string; alturaMaxima?: number; destacada?(l: L): boolean; rodape?: ReactNode`; `ColunaTabela<L> = { id: string; titulo: ReactNode; celula(l: L): ReactNode; alinhamento?: 'esquerda'\|'direita'; mono?: boolean }` |
| `shared/graficos/Grafico` | `titulo: string; resumo: string; figura: Record<string, unknown>; altura?: number` (lazy + tema; título em `<figcaption>`) |
| `ChipTipo` (**M1.6**) | `tipo: TipoVariavel; curto?: boolean; corrigido?: boolean` + `shared/ui/tiposVariavel.ts` com `TIPOS_VARIAVEL as const satisfies Record<TipoVariavel, …>` |

## Datasets de exemplo
| Arquivo | Uso |
|---|---|
| `dados-exemplo/pesquisa_saude.txt` | `;` + vírgula decimal, UTF-8, 230 linhas × 8 colunas, com problemas plantados para a tela Limpeza (faltantes, 3 duplicatas da linha 44, valores fora de faixa, grafias "Goiania"/"Anapolis"). Mesmo arquivo dos mockups. Link "Abrir … de exemplo" da tela 1. |
| `dados-exemplo/notas_turma.csv` | `,` + ponto decimal, sem problemas; testa o caminho CSV "limpo". |
| `backend/scripts/gerar_exemplos.py` | Gera os dois arquivos com semente fixa (reprodutível). |

## Decisões propostas (entram em `docs/decisions.md` no bloco indicado)
| # | Decisão | Bloco |
|---|---|---|
| D48 | Coluna de texto é tratada como numérica se ≥ 90% dos valores válidos viram número (`limiar_numerico = 0,9`); os demais aparecem como "tipo misto" na limpeza | M1.2 |
| D49 | Índice das linhas = número da linha no arquivo (1…n), mantido após a limpeza | M1.2 |
| D50 | Duplicados ignoram colunas `identificador` (como no design 3a: "iguais, exceto id") | M1.3 |
| D51 | "pós" é sinônimo de "pós-graduação" na escala de escolaridade (design 2a: fundamental < médio < superior < pós) | M1.2 |
| D52 | `POST /api/datasets/exemplo` carrega `dados-exemplo/pesquisa_saude.txt` | M1.2 |
| D53 | `MetadadosLeitura.motivos` explica cada detecção (tela 1a) | M1.2 |
| D54 | Fachada `Servico<Dominio>` + provedor `obter_servico_<dominio>()` em `servico.py`; `Depends` só no `router.py` (**ADR 0009**). Domínios sem estado nem dependências (graficos) expõem funções | M1.2 |
| D55 | `GET /datasets/{id}` devolve `resumo` (nome, metadados, linhas atuais/originais, log da limpeza) junto com a página de linhas | M1.2 |
| D56 | Figuras: discreta em bastões (spec 08); histograma montado das classes da spec 04; boxplot com estatísticas pré-calculadas (nunca pontos brutos; cumpre ADR 0003 para n > 5.000); curva Normal no histograma fica para o M2 | M1.5 |
| D57 | Relatório do M1 aceita só as seções `leitura, tipos, limpeza, analises`; o resto entra nos marcos seguintes | M1.5 |
| D58 | Testes de componentes com Vitest + jsdom + Testing Library | M1.1 |
| D59 | Ícones Material Symbols Rounded locais via `@fontsource-variable/material-symbols-rounded` | M1.1 |
| D60 | No M1, etapas 5–7 aparecem bloqueadas com o motivo "Disponível na versão {v}"; a aba "Forma e distribuição" fica oculta até o M2 | M1.1 / M1.7 |
| D61 | Sessão do frontend (id e nome do dataset, etapas visitadas) no `localStorage`; erro `DATASET_NAO_ENCONTRADO` encerra a sessão e leva para Importar | M1.1 |
| D62 | Editor de ordem dos ordinais com arrastar nativo (HTML5) + botões Subir/Descer, sem `@dnd-kit` | M1.6 |
| D63 | Gráficos com `react-plotly.js/factory` + `plotly.js-dist-min` (bundle menor que o `plotly.js` completo) | M1.1 |

Decisões novas fora da faixa D48–D63 (ex.: `Formula.chave`/`Figura.rotulo`, posição percentil com numpy, figuras como dicionários, decisões de tela do M1.6/M1.7) **não têm número fixo nos planos**: usam o próximo número livre em `docs/decisions.md` na hora do commit, porque os blocos entram em ordens diferentes.

## Dependências novas (todas em planos; nenhuma fora desta lista)
- Frontend (M1.1): `@fontsource/inter`, `@fontsource/jetbrains-mono`, `@fontsource-variable/material-symbols-rounded`, `react-plotly.js`, `plotly.js-dist-min`; dev: `jsdom@^29` (o 30 exige Node ≥ 22.22; a máquina local tem 22.14), `@testing-library/react`, `@testing-library/user-event`, `@testing-library/jest-dom` (+ `@types/plotly.js-dist-min` só se o `tsc` pedir).
  - Vêm junto como *peer* obrigatório: `@testing-library/dom` (pequeno) e `plotly.js` completo (~98 MB em `node_modules`, **fora do bundle**, mas pesa no `npm ci` do CI) — ver dúvida 9.
- Backend: nenhuma. Sem `chardet` (codificação pela ordem da spec 01), sem `scipy` no M1 (posição percentil com numpy) e sem importar `plotly` no app (figuras como dicionários; `plotly.min.js` lido do pacote) — os dois não têm tipos para o `mypy --strict`. No M2 (Shapiro-Wilk, Normal, Binomial) o `scipy` volta e vai precisar de `scipy-stubs` (pedir antes).

## Ajustes de contrato do frontend (vindos da escrita dos planos)
- Rotas em `app/rotas.ts` (sem JSX; `/` redireciona com `loader` + `redirect`) e o roteador do navegador em `app/roteador.ts`.
- Callbacks como propriedade (`aoMudar: (v: T) => void`), não método, por causa do `@typescript-eslint/unbound-method`.
- Extensões opcionais em `shared/ui`: `Botao.tamanho` aceita `'sm'` (36 px); `Card.preenchimento?: 'normal' | 'nenhum'`; `Tooltip.posicao?`; `ColunaTabela.cabecalhoLinha?` (`<th scope="row">`); `Icone.className?`; `EstadoCarregando.forma` aceita lista de formas.
- Helpers de teste em `frontend/src/testes/` (criados no M1.1, ampliados no M1.6).
- O M1.6 cria `shared/api/dataset.ts` (chaves `['datasets', id, recurso, …]` e a tabela de invalidação), `shared/navegacao/caminhos.ts` e utilitários de `shared/` (`ConteudoConsulta`, `BarraAcoes`, `ExigeDataset`, `SemDataset`, `useValorAtrasado`, `pluralizar`, `formatarCelula`…) e completa o `useSessaoExpirada` do M1.1. O M1.7 reutiliza tudo isso e acrescenta só `shared/api/colunas.ts` (filtro de colunas analisáveis sobre a mesma consulta do M1.6).
- Decisões do M1.6 ficam com rótulos provisórios `Dnn-<nome>` no plano; quem executa troca pelos números reais na Tarefa 18.

## Tamanho dos PRs
| Bloco | Linhas estimadas (código + testes) | Sugestão |
|---|---|---|
| M1.1 | 3.500–4.000 | 2 PRs: tarefas 1–13 (base e componentes) e 14–19 (Plotly, layout, rotas) |
| M1.2 | ~2.000 | 1 PR (ou 2: tarefas 1–8 domínio puro; 9–12 serviço e API) |
| M1.3 | ~1.000 | 1 PR |
| M1.4 | ~1.700 | 1 PR |
| M1.5 | ~1.300 | 1 PR |
| M1.6 | ~4.200 | 3 PRs: importar · variáveis · limpeza |
| M1.7 | 3.200–3.600 | 2 PRs: análise (tarefas 1–9) · relatório (10–12) |

Todos passam do ideal de 400 linhas do §8. Dividir em PRs menores na mesma branch do bloco (ou em sub-branches `feat/...-parte-1`) mantém a revisão possível sem mudar os planos.

## Dúvidas encontradas nas specs e no design (para o usuário decidir)
1. **`idade` discreta ou contínua?** O print 2a mostra discreta; pela regra 5 da spec 02 (inteiros com ≤ 30 valores distintos) o `pesquisa_saude.txt` tem 55 idades diferentes → contínua. Os planos seguem a regra; o usuário corrige na tela Variáveis.
2. **Ação "Corrigir para 1,72"** (print 3a, vírgula fora do lugar) não existe na spec 03. Fora do M1; dá para entrar no M3 junto com o detector.
3. **Limite de arquivo:** a AreaUpload do design diz 20 MB; spec e config dizem 50 MB. Os planos usam 50 MB.
4. **Discreta em bastões** (spec 08) ou **barras** (`graficos-plotly.md`)? Os planos seguem a spec (D56).
5. **Curva Normal no histograma:** a spec 08 põe no gráfico principal da contínua; o print 4b não mostra. Os planos deixam para o M2 (aba "Forma").
6. **Moda no card da contínua:** a spec 05 pede bruta + Czuber; o print 4c mostra só a bruta. O plano do M1.7 mostra a bruta no card e a de Czuber como apoio.
7. **Etapas 5–7 no M1:** aparecem bloqueadas com "Disponível na versão {v}" (D60) e com página própria dizendo quando chegam.
8. **Proporção da binária:** a API aceita `?sucesso=`, mas o design não tem onde escolher; o M1 usa a regra padrão (1/sim/s/true ou a menos frequente).
9. **`react-plotly.js` × wrapper próprio:** o `react-plotly.js` 4 exige o `plotly.js` completo como peer (~98 MB no `node_modules`, fora do bundle). Alternativa: um wrapper de ~30 linhas com `Plotly.react`/`Plotly.purge` sobre o `plotly.js-dist-min` (sem o peer). Os planos seguem o `react-plotly.js` (spec 15) até o usuário decidir.
10. **Detecção de separador/cabeçalho sem `csv.Sniffer`** e decimal só pelos números com separador (refinam a spec 01; D53). Ver plano do M1.2, Tarefa 4.
11. **Datas (`data`, spec 02)**: a detecção de colunas de data só serve ao detector (R6, M3); fica para o M3.
12. **Prévia do relatório** com `offline=true` (gráficos sem internet e impressão igual ao arquivo); "Funciona sem internet" vale para o arquivo baixado.
13. **Unidade (kg, m)** aparece no design ("70,3 kg", "Classe (kg)") mas não há unidade em nenhum dado. Os planos omitem a unidade.
