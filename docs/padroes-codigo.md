# Padrões de código

> Regras obrigatórias para qualquer pessoa ou agente que escreva código neste projeto. Em conflito com outra fonte, **este arquivo vence** (exceto o enunciado do professor). Mudança aqui exige entrada em `decisions.md`.

## 1. Limites de qualidade (verificados no CI)

| Métrica | Limite | Python | TypeScript |
|---|---|---|---|
| Linhas por arquivo | **≤ 500** | `scripts/verificar_tamanho.py` | ESLint `max-lines: 500` |
| Complexidade ciclomática por função | **≤ 10** | ruff `C901` (`max-complexity = 10`) | ESLint `complexity: 10` |
| Complexidade cognitiva por função | **≤ 15** | `complexipy --max-complexity-allowed 15` | `sonarjs/cognitive-complexity: 15` |
| Aninhamento | **≤ 3 níveis** | ruff `PLR1702` (`max-nested-blocks = 3`, preview) | ESLint `max-depth: 3` |
| Duplicação | **0 blocos** ≥ 50 tokens | `jscpd --min-tokens 50` | `jscpd` + `sonarjs/no-identical-functions` |
| Parâmetros por função | ≤ 5 (acima → objeto/dataclass) | ruff `PLR0913` | ESLint `max-params: 5` |
| Tamanho de função | ≤ 50 linhas (meta: ≤ 30) | ruff `PLR0915` (statements ≤ 40) | ESLint `max-lines-per-function: 50` |

Passou do limite → **refatore** (extrair função, early return, tabela de despacho, Strategy). Nunca silencie a regra com `# noqa`/`eslint-disable` sem justificativa no PR e entrada em `decisions.md`.

### Como reduzir complexidade e aninhamento
- **Early return / guard clauses** no lugar de `if` aninhado.
- **Tabela de despacho** (`dict[Tipo, Callable]` / `Record<Tipo, Componente>`) no lugar de cadeias `if/elif` por tipo de variável.
- **Extrair predicados** com nome: `if eh_numerica_inteira(serie):` em vez de condição composta.
- Laços: extrair o corpo para função; preferir operações vetorizadas do pandas/numpy a `for`.

## 2. Arquitetura: monólito em camadas com separação por domínio

Uma aplicação backend (um processo) e um frontend. Dentro do backend, o código é dividido por **domínio**, e cada domínio tem **camadas**.

### Backend
```
backend/app/
├── main.py                  # create_app(): routers, handlers, CORS, lifespan
├── core/                    # transversal: config (pydantic-settings), erros, handlers, logging
├── compartilhado/           # utils reutilizáveis SEM regra de negócio
│   ├── numeros.py           #   casas decimais, arredondamento, formatação pt-BR
│   ├── textos.py            #   p-valor traduzido, pluralização, "N× o esperado"
│   ├── series.py            #   helpers de pandas (valores válidos, é inteira, etc.)
│   ├── estatistica.py       #   helpers comuns (testes χ², binomial) usados por >1 domínio
│   └── tipos.py             #   enums e value objects compartilhados (TipoVariavel, Severidade)
└── dominios/
    ├── datasets/            # leitura, classificação de tipos, limpeza, repositório
    ├── analise/             # frequências, tendência, separatrizes, dispersão, distribuições, correlação
    ├── graficos/            # fábrica de figuras Plotly + tema
    ├── gerador/             # estratégias de geração uni/bivariada
    ├── detector/            # regras R1–R11, registro, textos
    └── relatorio/           # montagem HTML (Jinja2)
```

### Camadas dentro de cada domínio
| Arquivo | Camada | Pode importar | Não pode |
|---|---|---|---|
| `router.py` | Apresentação (HTTP) | `schemas`, `servico`, `core`, `fastapi` | lógica de negócio, pandas |
| `schemas.py` | Contrato (Pydantic) | `pydantic`, `compartilhado.tipos` | `servico`, módulos de domínio |
| `servico.py` | Aplicação (casos de uso, fachada do domínio) | módulos do próprio domínio, `repositorio`, **`servico` de outros domínios** | `fastapi`, `schemas` de outros domínios |
| `*.py` (ex.: `frequencias.py`) | Domínio (regras puras) | `pandas`, `numpy`, `scipy`, `compartilhado` | `fastapi`, `pydantic`, `repositorio`, outros domínios |
| `repositorio.py` | Infraestrutura (estado/IO) | `core`, `compartilhado` | `fastapi` |

**Regras de dependência**
1. Fluxo: `router → servico → domínio/repositório`. Nunca ao contrário.
2. Domínios conversam **só via `servico.py`** do outro domínio (fachada pública). Proibido importar `dominios.X.frequencias` de dentro de `dominios.Y`.
3. Código de domínio é **puro e determinístico**: recebe `Series`/`DataFrame` + parâmetros, devolve dataclass. Sem IO, sem estado global, sem `print`.
4. Algo usado por ≥ 2 domínios e sem regra de negócio → `compartilhado/`. Com regra de negócio → fica no domínio dono e é exposto pelo `servico`.
5. Verificação automática: `import-linter` com contratos de camadas e independência entre domínios.

### Frontend (organização por feature)
```
frontend/src/
├── app/                 # rotas, providers (QueryClient, tema), layout
├── features/            # 1 pasta por etapa/domínio: importar, variaveis, limpeza, analise, bivariada, gerador, detector, relatorio
│   └── <feature>/
│       ├── api.ts        #   chamadas e hooks react-query da feature
│       ├── components/   #   componentes da feature
│       ├── hooks/        #   hooks locais
│       └── tipos.ts      #   tipos derivados dos gerados (não redefinir)
└── shared/
    ├── api/              # cliente HTTP, tratamento de erro, tipos gerados do OpenAPI
    ├── ui/               # componentes de design system (Botao, Card, Chip, Aviso, Tabela…)
    ├── graficos/         # wrapper Plotly carregado sob demanda
    └── lib/              # formatadores pt-BR, utils puros
```
Regras: `features/A` não importa de `features/B` (o que for comum vai para `shared/`); `shared/` não importa de `features/`.

## 3. Padrões de projeto adotados (usar só onde resolvem um problema real)

| Padrão | Onde | Por quê |
|---|---|---|
| **Fachada (Facade)** | `servico.py` de cada domínio | Ponto único de entrada; esconde módulos internos |
| **Repositório** | `datasets/repositorio.py` | Isola o armazenamento em memória (ADR 0004); troca futura sem mexer no resto |
| **Strategy** | `gerador/estrategias/` (uma por tipo de variável); `analise` por tipo | Elimina `if tipo == ...`; cada tipo isolado e testável |
| **Chain of Responsibility** | `datasets/classificacao.py` (regras 1–6 da spec 02) | Regras ordenadas; a primeira que casar responde com tipo + motivo |
| **Registro / Plugin** | `detector/registro.py` + `detector/regras/rNN_*.py` | Adicionar regra = criar arquivo + registrar; nada mais muda |
| **Template Method** | `detector/regras/base.py` (`RegraBase.executar()` = aplicável? → avaliar → montar textos) | Fluxo comum sem duplicação nas 11 regras |
| **Fábrica (Factory)** | `graficos/fabrica.py` (tipo → figuras) | Regra "melhor gráfico por tipo" num só lugar (ADR 0003) |
| **Injeção de dependência** | `Depends()` para settings, repositório e serviços | Testes trocam dependências com `app.dependency_overrides` |
| **Value Object** | `@dataclass(frozen=True, slots=True)` para resultados | Imutável, comparável, sem efeitos colaterais |

Evitar: Singleton manual (usar `Depends` + `lru_cache`), herança profunda (máx. 1 nível; preferir composição e `Protocol`), padrões "por precaução" (YAGNI).

## 4. Python (3.12+)

**Estilo e tipos**
- `ruff format` (linha 100) + `ruff check` com regras: `E,F,W,I,N,UP,B,C4,C90,SIM,RET,PL,PERF,RUF,PT,ARG,ERA`.
- Tipagem em toda função pública (parâmetros e retorno); `mypy --strict` no domínio e em `compartilhado/`. Sintaxe moderna: `list[int]`, `X | None`, `type Alias = ...`.
- Nomes em **português**, `snake_case`; classes `PascalCase`; constantes `MAIUSCULAS`. Sem abreviações obscuras (`media_amostral`, não `ma`).
- Docstring curta (1 linha) em toda função pública de domínio, citando a fórmula quando houver: `"""Variância amostral: s² = Σ(xᵢ − x̄)² / (n − 1)."""`.
- Comentários explicam **por quê**, não o quê. Sem código comentado (ruff `ERA`).

**Funções e dados**
- Funções pequenas, uma responsabilidade, sem efeitos colaterais no domínio.
- Retornos de domínio = dataclasses congeladas; nunca `dict` solto atravessando camadas.
- Sem números mágicos: limiares em `core/config.py` (ex.: `LIMIAR_DISCRETA = 30`) ou constantes nomeadas no módulo.
- Não mutar a entrada: `serie.copy()` antes de alterar; operações do pandas que retornam novo objeto.
- Vetorizar (pandas/numpy) em vez de `for` sobre linhas; `df.apply` só quando não houver alternativa vetorizada.

**FastAPI**
- Endpoints **`def` (síncronos)**: o trabalho é CPU-bound (pandas/scipy); o FastAPI os executa em threadpool. `async def` só para IO real (upload streaming).
- `Annotated` para dependências e validação: `Repo = Annotated[RepositorioDatasets, Depends(obter_repositorio)]`.
- `response_model`/tipo de retorno explícito em todo endpoint; `summary` e `tags` por domínio (OpenAPI legível).
- Router só: valida (schema) → chama serviço → retorna schema. **Zero lógica** no router.
- Configuração via `pydantic-settings` (`core/config.py`), nunca `os.environ` espalhado.
- `create_app()` (fábrica) em `main.py` + `lifespan` para inicialização; registrar handlers de erro centralizados.

**Erros**
- Domínio levanta exceções próprias derivadas de `ErroAplicacao(codigo, mensagem, sugestao)` (`core/erros.py`).
- `core/handlers.py` converte para HTTP `{codigo, mensagem, sugestao}` (spec 17). Sem stack trace na resposta; log com `logging` estruturado.
- Nunca `except Exception: pass`. Capturar o mais específico possível.
- "Não se aplica" **não é erro**: retornar `NaoAplicavel(item, motivo)`.

**Testes**
- `pytest`; 1 arquivo de teste por módulo de domínio (`tests/dominios/analise/test_frequencias.py`).
- Padrão AAA (Arrange, Act, Assert); nomes descritivos: `test_variancia_amostral_usa_n_menos_1`.
- `pytest.mark.parametrize` em vez de testes copiados; fixtures compartilhadas em `conftest.py`.
- API testada com `TestClient` + `dependency_overrides`.
- Cobertura ≥ 80% em `dominios/` e `compartilhado/`.

## 5. TypeScript (strict)

**`tsconfig`**: `strict: true`, `noUncheckedIndexedAccess`, `noImplicitOverride`, `noFallthroughCasesInSwitch`, `exactOptionalPropertyTypes`, `verbatimModuleSyntax`.

**Tipos**
- **Tipos da API gerados** do OpenAPI do FastAPI com `openapi-typescript` → `shared/api/schema.d.ts`. Nunca redefinir à mão um tipo que vem da API (fonte única, sem duplicação).
- Proibido `any` (ESLint `no-explicit-any`); usar `unknown` + narrowing. Sem `as` para "forçar" tipos, exceto em testes.
- **Uniões discriminadas** para variantes: `TipoVariavel`, `Severidade`, estados de tela (`{ status: 'carregando' } | { status: 'erro', erro } | { status: 'ok', dados }`). `switch` exaustivo com `assertNever`.
- `type` para uniões e composições; `interface` para props de componentes e objetos extensíveis.
- `as const` + `satisfies` para tabelas de configuração (ex.: mapa tipo → ícone/cor).
- Inferência quando óbvia; anotar retornos de funções exportadas.

**Lint**: `typescript-eslint` (`strict-type-checked` + `stylistic-type-checked`), `eslint-plugin-react-hooks`, `eslint-plugin-sonarjs`, `eslint-plugin-jsx-a11y`; Prettier para formatação.

## 6. React (Vite SPA)

**Componentes**
- Componentes funcionais; 1 componente exportado por arquivo; `PascalCase.tsx`; hooks `useAlgo.ts`.
- Componente ≤ 150 linhas; passou → extrair subcomponentes/hooks. Lógica em hooks, JSX enxuto.
- Props tipadas com `interface`; sem prop drilling > 2 níveis (usar composição/children ou contexto da feature).
- Renderização condicional com **ternário** (`cond ? <A/> : null`), não `&&` com números.
- JSX estático (ícones fixos, listas constantes) **içado** para fora do componente.

**Dados (react-query)**
- Toda chamada à API via `@tanstack/react-query` (deduplicação e cache automáticos); `queryKey` centralizadas por feature (`chavesAnalise.coluna(id, col)`).
- Requisições independentes **em paralelo** (`useQueries` / `Promise.all`), nunca em cascata.
- Mutations invalidam só as `queryKey` afetadas.
- Estados de carregamento, vazio e erro obrigatórios (spec 15) — via componentes de `shared/ui` (`<EstadoCarregando/>`, `<EstadoVazio/>`, `<EstadoErro/>`).

**Desempenho**
- **Plotly carregado sob demanda** (`React.lazy(() => import('...'))` + `Suspense`): é a maior dependência do bundle.
- Rotas com `lazy()` por feature (code splitting).
- Importar direto do módulo, sem barrel files (`index.ts` reexportando tudo).
- Estado derivado é **calculado**, não guardado em `useState` + `useEffect`.
- `setState` funcional quando depende do anterior; `useState(() => inicial())` para inicialização cara.
- Dependências de efeito primitivas; `useMemo`/`memo` só para cálculo caro comprovado (não por padrão).
- `startTransition` para atualizações não urgentes (trocar coluna, filtros do detector).
- Listas longas (tabela de dados, percentis): virtualização ou `content-visibility: auto`.
- JS: `Map`/`Set` para buscas repetidas; `toSorted()`/`toReversed()` (imutáveis); early return; RegExp içada para fora de loops.

**Acessibilidade** (spec 15): elementos semânticos (`button`, não `div` clicável), `aria-*` corretos, foco visível, navegação por teclado, `jsx-a11y` sem erros.

## 7. Anti-padrões proibidos (code smells)

- Duplicação (copiar e colar) → extrair função/util/componente.
- Função ou componente "Deus" (faz tudo) → dividir por responsabilidade.
- Boilerplate repetido (try/except igual em todo router, fetch manual em toda tela) → centralizar (handlers, cliente HTTP, hooks).
- Cadeias longas de `if/elif` por tipo → tabela de despacho / Strategy.
- Números e strings mágicos → constantes nomeadas / `textos`.
- Textos de interface no meio da lógica → `detector/textos.py`, `compartilhado/textos.py` (spec 16).
- Flags booleanas que mudam o comportamento da função (`calcular(x, modo_especial=True)`) → duas funções.
- Estado global mutável (exceto o repositório, injetado via `Depends`).
- `print`/`console.log` esquecidos; `TODO` sem issue.
- Comentários desatualizados ou óbvios; código morto.

## 8. Git e revisão

- Branch por tarefa: `feat/<dominio>-<descricao>`, `fix/...`, `docs/...`, `refactor/...`.
- Conventional Commits em português: `feat(analise): calcula moda de Czuber`.
- PR pequeno (ideal < 400 linhas alteradas), com spec relacionada citada e checklist abaixo.
- **Sem coautoria de IA** em commits, PRs ou código.

### Checklist do PR
- [ ] Segue a camada certa (router sem lógica; domínio puro; domínios via `servico`)
- [ ] Limites da seção 1 respeitados (CI verde)
- [ ] Sem duplicação; utilitários reaproveitados de `compartilhado/` ou `shared/`
- [ ] Tipos completos (mypy/tsc sem erros); sem `any`
- [ ] Testes novos/atualizados; cobertura mantida
- [ ] Textos de UI seguem `specs/16-ux-writing.md`
- [ ] Spec atualizada se o comportamento mudou; `CHANGELOG.md` atualizado
