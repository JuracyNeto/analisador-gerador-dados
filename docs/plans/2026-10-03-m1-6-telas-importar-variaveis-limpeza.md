# M1.6 — Telas 1–3 (Importar, Variáveis, Limpeza): plano de implementação

> **Para o agente:** use a skill `executing-plans` (ou `subagent-driven-development`) para executar tarefa por tarefa. Antes de escrever código, leia `CLAUDE.md`, `docs/padroes-codigo.md` e os contratos em `docs/plans/2026-10-03-m1-visao-geral.md` (fonte única de endpoints, schemas e componentes de `shared/ui`).

**Objetivo:** entregar as telas 1 (Importar), 2 (Variáveis) e 3 (Limpeza) ligadas à API do M1.2/M1.3, com os estados carregando, vazio, erro e sucesso, nos temas claro e escuro, acessíveis por teclado, conforme `docs/design/telas.md` §1–3.

**Arquitetura:** três features (`features/importar`, `features/variaveis`, `features/limpeza`), cada uma com `api.ts` (react-query), `textos.ts`, funções puras testadas, `hooks/` e `components/`. O que mais de uma feature usa vai para `shared/`: chaves de query por dataset (`shared/api/dataset.ts`), `ChipTipo` + `tiposVariavel.ts`, `ConteudoConsulta`, `BarraAcoes`, `ExigeDataset` + `SemDataset`, `useAvisarErro`, pluralização e formatação de célula. No `app/`, este bloco completa o `useSessaoExpirada` do M1.1 (D61) e passa linhas × colunas ao Cabeçalho; as páginas reais entram nos mesmos arquivos das provisórias, então `app/rotas.ts` não muda.

**Stack:** React 19, Vite 8, TypeScript ~5.9 strict, @tanstack/react-query 5, react-router 7, Vitest 5 + jsdom + Testing Library (instalados no M1.1), ESLint 9 (strict-type-checked, sonarjs, jsx-a11y, react-hooks 7), Prettier, jscpd. **Nenhuma dependência nova.** Nada de `@dnd-kit` (D62).

**Branch:** `feat/frontend-importar-variaveis-limpeza` (sai de `develop`) → PR para `develop`.

**Prazo:** PR aberto até 27/10/2026 (marco M1: 30/10/2026).

**Depende de:** M1.1 (base visual), M1.2 (datasets: leitura e tipos) e M1.3 (limpeza) mergeados em `develop`.

---

## Antes de começar: conferir o que já está em `develop`

Este plano usa os contratos da visão geral do M1. Os arquivos do M1.1 não existiam quando o plano foi escrito, então confirme os caminhos e o estilo de exportação **antes da Tarefa 1** e ajuste só os `import` se algo divergir (não mude contratos sem atualizar a visão geral):

```bash
git switch develop && git pull && git switch -c feat/frontend-importar-variaveis-limpeza
ls frontend/src/shared/ui frontend/src/shared/sessao frontend/src/shared/lib frontend/src/shared/api frontend/src/app frontend/src/app/layout
grep -n "export" frontend/src/shared/sessao/useSessao.ts frontend/src/shared/ui/useToast.ts frontend/src/shared/api/erros.ts frontend/src/shared/lib/formatar.ts
grep -c "TipoColuna\|DatasetCriado\|Diagnostico\|AcaoLimpeza\|ResultadoLimpeza" frontend/src/shared/api/schema.d.ts
grep -n "fonte-mono\|raio-md\|esp-4" frontend/src/shared/ui/tokens.css
grep -n "environment\|setupFiles\|unstubGlobals" frontend/vite.config.ts
```

Premissas (o que o plano assume do M1.1):

| Item | Premissa |
|---|---|
| Componentes de `shared/ui` | `export default` em `shared/ui/<Nome>.tsx`: `Icone`, `Botao`, `Card`, `PaginaEtapa`, `Banner`, `EstadoCarregando`, `EstadoVazio`, `EstadoErro`, `ToastProvider`, `Tooltip`, `Select`, `CampoNumero`, `CardMetrica`, `Tabela` (este também exporta `type ColunaTabela`) |
| Hooks | `useToast` em `shared/ui/useToast.ts` e `useSessao` em `shared/sessao/useSessao.ts` (export nomeado); `SessaoProvider` default em `shared/sessao/SessaoProvider.tsx` |
| Funções | `formatarNumero`, `formatarInteiro`, `lerNumeroPtBr` em `shared/lib/formatar.ts`; `ehDatasetNaoEncontrado`, `textoDoErro` em `shared/api/erros.ts` |
| App | `app/rotas.ts` (rotas com `lazy()`; páginas provisórias `features/importar/PaginaImportar.tsx`, `features/variaveis/PaginaVariaveis.tsx`, `features/limpeza/PaginaLimpeza.tsx`, que este bloco **substitui**), `app/etapas.ts`, `app/App.tsx` (cria o `QueryClient`), `app/layout/LayoutApp.tsx`, `app/layout/Cabecalho.tsx` (props `nomeArquivo`, `nLinhas`, `nColunas`), `app/textos.ts` (`TEXTOS_APP`) e o hook `app/layout/useSessaoExpirada.ts` (Tarefa 18 do M1.1, já chamado no `LayoutApp`) |
| Tooltip | Abre em hover/foco e renderiza `role="tooltip"` |
| Tabela | Renderiza `<table>` nativa com nome acessível = `legenda` |
| Testes | Vitest com `environment: 'jsdom'`, `restoreMocks: true` e `setupFiles: ['./src/testes/configuracao.ts']` (jest-dom; o `afterEach` limpa a tela, desfaz `vi.stubGlobal`, volta aos timers reais e limpa o `localStorage`). Helpers de teste em `src/testes/`: o M1.1 criou `configuracao.ts`, `matchMedia.ts` e `renderizar.tsx` (`renderizarComRotas`, `renderizarComProvedores`); a Tarefa 1 deste bloco **amplia** o `renderizar.tsx` e cria os demais. O ESLint já desliga `max-lines-per-function` e `react-refresh/only-export-components` em `*.test.*` e `src/testes/**` (M1.1, Tarefa 1) |
| Tokens | `--fonte-mono`, `--raio-*` e `--esp-*` no `tokens.css` (tokens.md pede). Se faltarem, a Tarefa 2 adiciona |
| Schema | `schema.d.ts` já tem os schemas do M1.2 e M1.3 (se não tiver: `python scripts/exportar_openapi.py` em `backend/` e `npm run gerar:tipos` em `frontend/`) |

Se a API gerar nomes com sufixo (`AcaoLimpeza-Input`), use o nome gerado nos `type` de `features/limpeza/tipos.ts` — é o único lugar que referencia esses schemas.

## Regras que valem em todas as tarefas

- Antes de cada commit, em `frontend/`: `npm run lint && npm run format && npm run test`. No fim (Tarefa 19) também `npm run build` e o jscpd na raiz.
- `typescript-eslint` strict: número em template string só com `String(n)` ou formatador; arrow que devolve `void` sempre com chaves (`() => { fazer(); }`); promessas soltas com `void` (`void navegar(...)`).
- Props de componentes como `Readonly<Props>` (`sonarjs/prefer-read-only-props`). Retornos de componente sempre JSX (envolver `children(...)` em `<>…</>`), nunca misturar tipos.
- Para não esbarrar em `unbound-method`, não desestruture métodos de `useSessao()`/`useToast()`: use `sessao.definirDataset(...)`, `toast.mostrar(...)`.
- Props opcionais com `exactOptionalPropertyTypes`: não passe `undefined` explícito; use espalhamento condicional (`{...(erro === null ? {} : { erro })}`).
- CSS: CSS Modules, sempre `var(--token)`, variantes por `data-*` (sem concatenar classes). Medidas abaixo vêm de `docs/design/telas/Tela N *.dc.html`.
- Textos de interface só nos `textos.ts` (spec 16). Commits em Conventional Commits, em português, **sem** `Co-Authored-By` nem atribuição de IA.
- Se a tela precisar de algo que a API não tem, **não invente endpoint**: anote no PR.

## Convenção de chaves de query por dataset (Dnn-chaves — vale também para o M1.7)

Tudo que pertence a um dataset começa com `['datasets', id]`. Os prefixos usados por mais de uma feature ficam em `shared/api/dataset.ts` (`chavesDataset`); cada feature monta as chaves completas no próprio `api.ts` a partir desses prefixos.

| Chave | Dono | Conteúdo |
|---|---|---|
| `['datasets', id]` | `chavesDataset.todas` | prefixo de tudo (invalidado pela limpeza) |
| `['datasets', id, 'primeira-pagina']` | `chavesDataset.primeiraPagina` | `GET /datasets/{id}?pagina=1&tamanho=20` (`PaginaDataset`): cabeçalho, prévia, log da limpeza |
| `['datasets', id, 'colunas']` | `chavesDataset.colunas` | `GET /datasets/{id}/colunas` (`opcoesColunas`; o M1.7 filtra as analisáveis sobre esta mesma consulta) |
| `['datasets', id, 'diagnostico', limitesJson]` | `chavesLimpeza.diagnostico` | `GET …/diagnostico?limites=` |
| `['datasets', id, 'analise', coluna, classes]` | M1.7 (`chavesAnalise.analise`) | prefixo `chavesDataset.analises(id)` |
| `['datasets', id, 'analise', coluna, 'posicao', valor, tipo]` | M1.7 (`chavesAnalise.posicao`) | prefixo `chavesDataset.analises(id)`: "Onde está meu valor?" é invalidado junto com a análise |
| `['datasets', id, 'relatorio', …]` | M1.7 | prefixo `chavesDataset.relatorio(id)` |

Invalidação:

| Mutação | Invalida |
|---|---|
| `PATCH` tipo/ordem de coluna | `colunas`, `diagnostico`, `analise`, `relatorio` (não mexe na `primeira-pagina`: linhas não mudam) |
| Aplicar limpeza / Desfazer tudo | `['datasets', id]` inteiro (linhas, tipos, log, diagnóstico e análises mudam) |
| Importar | nada: cria um id novo; o cache de `colunas` do id novo é preenchido com `DatasetCriado.colunas` |

## Decisões deste bloco (entram em `docs/decisions.md` na Tarefa 18)

Numeração: D62 já está reservada pela visão geral. As demais **não têm número fixo**, porque os blocos entram em ordens diferentes: cada uma recebe **Dnn (próximo número livre em `docs/decisions.md` na hora do commit)**. Neste plano elas aparecem com um rótulo provisório `Dnn-<nome>`; ao registrar (Tarefa 18), troque cada rótulo pelo número real também nos comentários de código e nos docs (`grep -rn "Dnn-" frontend/src docs`).

| # | Decisão | Alternativa | Motivo |
|---|---|---|---|
| D62 | Editor de ordem dos ordinais com arrastar nativo (HTML5) + botões Subir/Descer + ↑/↓ na alça focada, com anúncio `aria-live` | `@dnd-kit/sortable` | Sem dependência nova; teclado e leitor de tela cobertos |
| Dnn-chaves | Chaves de query por dataset `['datasets', id, recurso, …]` em `shared/api/dataset.ts`; limpeza invalida o prefixo inteiro | Chaves soltas por feature | Invalidação previsível entre features sem importar uma da outra |
| Dnn-sessao | O `useSessaoExpirada` do M1.1 avisa uma vez por dataset e apaga o cache dele; consultas não repetem erros 4xx | Tratar 404 em cada tela | Um lugar só para D61; 404 aparece na hora, sem 3 retentativas nem toasts repetidos |
| Dnn-limites | Limites da limpeza refazem o diagnóstico 600 ms depois da última digitação, mostrando o diagnóstico anterior enquanto carrega | Botão "Aplicar limites" | O design não tem botão; a chave inclui os limites, então cada combinação fica em cache; só limites válidos entram na chave |
| Dnn-manter | Todas as ações da limpeza começam em "Manter"; "Aplicar limpeza" fica desabilitado até haver ação diferente de "Manter" | Pré-selecionar sugestões (como no print 3a) | Nada muda sem escolha explícita do usuário |
| Dnn-reler | "Ler de novo" relê o mesmo arquivo com detecção automática; corrigir a leitura exige o arquivo na memória da página (após recarregar, as detecções aparecem só para leitura) | Guardar o arquivo no `localStorage` | Arquivo pode ter 50 MB; a API não guarda os bytes para reler |
| Dnn-50mb | Área de envio mostra "Tamanho máximo: 50 MB" | 20 MB do print | `limite_arquivo_mb = 50` (config) e spec 01 |
| Dnn-corrigir | Ação "Corrigir para 1,72" (fora de faixa) fica fora do M1; a seção oferece "Remover o valor", "Limitar ao limite", "Remover a linha" e "Manter" | Inventar ação na API | `AcaoLimpeza` do M1.3 não tem essa ação |
| Dnn-caminhos | Caminhos das rotas em `shared/navegacao/caminhos.ts` | Features importarem `app/etapas.ts` | Features não dependem de `app/` |

(A regra de ESLint para helpers de teste já entra no M1.1, Tarefa 1; não é decisão deste bloco.)

## Desvios do design (registrar no PR e na Tarefa 18)

| Onde | Design | Implementação | Por quê |
|---|---|---|---|
| 1b/1c | "Tamanho máximo: 20 MB" | 50 MB | Dnn-50mb |
| 1c | Link "Como exportar para CSV" | Não entra | Não há página de ajuda para onde levar |
| 1a | Select "Formato" editável | Formato só leitura | `POST /datasets` não aceita `formato` |
| 1a | Prévia "63,0" | "63" | A API manda números; casas fixas por coluna não estão no contrato |
| 2a | Resumo "2 contínuas · 1 discreta…" com "·" (telas.md) | Itens separados por espaço, como no print | Print é a referência hi-fi |
| 3a | Ações pré-selecionadas | Tudo em "Manter" | Dnn-manter |
| 3a | "Corrigir para 1,72" | Fora | Dnn-corrigir |
| 3a | Cards de resumo com ícone | `CardMetrica` sem ícone | Reuso do componente do M1.1 (zero duplicação) |
| 3a | Duplicados com Select por grupo | 1 linha e 1 Select para todos os duplicados | `AcaoLimpeza` de duplicados não tem grupo |
| 3a | Seção "Fora de faixa" sem faixa | Linha extra "Faixa aceita: 1 a 110 (seus limites)" | Explica de onde veio o limite (princípio 2 do design) |

---

## Visão geral das tarefas

| # | Tarefa | Área |
|---|---|---|
| 1 | Infraestrutura de testes (`src/testes/`; amplia o `renderizar.tsx` do M1.1) | frontend |
| 2 | Utilidades compartilhadas (pluralizar, célula, atraso, corpo JSON, avisar erro, retentativa, caminhos, BarraAcoes) | shared |
| 3 | `tiposVariavel.ts` + `ChipTipo` | shared/ui |
| 4 | Consultas do dataset + linhas × colunas no Cabeçalho | shared/api, app |
| 5 | Sessão expirada (completa o hook do M1.1), `ExigeDataset` + `SemDataset`, `ConteudoConsulta` | app, shared |
| 6 | Importar: textos e mapeamentos puros | importar |
| 7 | Importar: `api.ts` e `useImportacao` | importar |
| 8 | Importar: `AreaUpload` | importar |
| 9 | Importar: detecções, prévia e banner de erro | importar |
| 10 | Importar: página e rota | importar |
| 11 | Variáveis: textos, regras puras e `api.ts` | variaveis |
| 12 | Variáveis: `TabelaVariaveis` e `ResumoTipos` | variaveis |
| 13 | Variáveis: `EditorOrdem` (D62) | variaveis |
| 14 | Variáveis: página e rota | variaveis |
| 15 | Limpeza: tipos, textos, descrições, seções e resumo | limpeza |
| 16 | Limpeza: limites, escolhas e `api.ts` | limpeza |
| 17 | Limpeza: componentes | limpeza |
| 18 | Limpeza: página, rota e documentação | limpeza, docs |
| 19 | Verificação final e teste manual pelo preview | todos |
| 20 | PR (só depois do ok do usuário) | GitHub |

Estrutura final (só arquivos novos ou alterados):

```
frontend/src/
├── testes/            api.ts · renderizar.tsx* · fixtures/datasets.ts · fixtures/limpeza.ts
├── app/               App.tsx* · etapas.ts* · textos.ts* · layout/LayoutApp.tsx* · layout/useSessaoExpirada.ts*
├── shared/
│   ├── api/           dataset.ts · corpoJson.ts · classificarErro.ts
│   ├── lib/           pluralizar.ts · formatarCelula.ts · useValorAtrasado.ts
│   ├── navegacao/     caminhos.ts
│   ├── sessao/        ExigeDataset.tsx · SemDataset.tsx · textos.ts
│   └── ui/            tiposVariavel.ts · ChipTipo.tsx · ConteudoConsulta.tsx · BarraAcoes.tsx · useAvisarErro.ts
└── features/          (textos.ts* e Pagina*.tsx* substituem os provisórios do M1.1)
    ├── importar/      api.ts · textos.ts* · opcoesLeitura.ts · apresentacao.ts · hooks/useImportacao.ts · PaginaImportar.tsx*
    │                  components/ AreaUpload · CardDeteccoes · PreviaDados · BannerErroImportacao · BotaoLink · ResultadoImportacao
    ├── variaveis/     api.ts · textos.ts* · regras.ts · PaginaVariaveis.tsx*
    │                  components/ TabelaVariaveis · ResumoTipos · EditorOrdem · ItemOrdem · ConteudoVariaveis
    └── limpeza/       api.ts · tipos.ts · textos.ts* · descricoes.ts · secoes.ts · resumo.ts · limites.ts · PaginaLimpeza.tsx*
                       hooks/ useLimitesPorColuna · useEscolhasLimpeza · useLimpeza
                       components/ SecaoProblema · CardsResumoLimpeza · LimitesPorColuna · PainelLog · ConteudoLimpeza
(* = alterado; cada componente com .module.css e .test.tsx ao lado)
```

---

### Tarefa 1: Infraestrutura de testes

Um helper só para renderizar com os provedores (o do M1.1, ampliado) e um falso de `fetch` reutilizado por todos os testes (evita duplicação no jscpd). O M1.7 usa os mesmos helpers.

**Arquivos:**
- Criar: `frontend/src/testes/api.ts`
- Modificar: `frontend/src/testes/renderizar.tsx` (criado no M1.1, Tarefa 15): acrescenta `criarClienteTeste`, `DATASET_TESTE`, `OpcoesRenderizar`, `renderizarHook` e o parâmetro opcional `opcoes` em `renderizarComProvedores`/`renderizarComRotas` (Passo 6)
- Criar: `frontend/src/testes/fixtures/datasets.ts`, `frontend/src/testes/fixtures/limpeza.ts`
- Teste: `frontend/src/testes/api.test.ts`
- Modificar: `frontend/src/shared/api/cliente.test.ts` (usar `respostaJson` do helper)

`vite.config.ts` e `eslint.config.js` não mudam: o M1.1 já desfaz `vi.stubGlobal` no `afterEach` de `src/testes/configuracao.ts` e já desliga `react-refresh/only-export-components` em `src/testes/**`.

**Passo 1: escrever o teste do falso de `fetch` (falha)**

`frontend/src/testes/api.test.ts`:
```ts
import { describe, expect, it } from 'vitest';
import { chamadasPara, simularApi } from './api';

const CAMINHO = '/datasets/ds-1/limpeza';

describe('simularApi', () => {
  it('responde pela rota que casa método e caminho, ignorando a query', async () => {
    simularApi([{ caminho: '/datasets/ds-1', corpo: { ok: true } }]);

    const resposta = await fetch('/api/datasets/ds-1?pagina=1&tamanho=20');

    expect(resposta.status).toBe(200);
    await expect(resposta.json()).resolves.toEqual({ ok: true });
  });

  it('devolve 500 com o código ROTA_NAO_SIMULADA quando nada casa', async () => {
    simularApi([]);

    const resposta = await fetch('/api/outra');

    expect(resposta.status).toBe(500);
    await expect(resposta.json()).resolves.toMatchObject({ codigo: 'ROTA_NAO_SIMULADA' });
  });

  it('registra as chamadas com o corpo JSON já lido', async () => {
    const falso = simularApi([{ metodo: 'POST', caminho: CAMINHO, corpo: {} }]);

    await fetch(`/api${CAMINHO}`, { method: 'POST', body: JSON.stringify({ acoes: [] }) });

    expect(chamadasPara(falso, 'POST', CAMINHO)).toEqual([
      { url: `/api${CAMINHO}`, corpo: { acoes: [] } },
    ]);
  });
});
```

**Passo 2: rodar e ver falhar**
`npx vitest run src/testes/api.test.ts` → FAIL (`Cannot find module './api'`)

**Passo 3: implementar `frontend/src/testes/api.ts`**
```ts
/** Falso de fetch para testes: responde por rota (método + caminho) e guarda as chamadas. */
import { type Mock, vi } from 'vitest';

export interface RotaFalsa {
  metodo?: 'GET' | 'POST' | 'PATCH' | 'DELETE';
  /** Caminho sem o prefixo /api e sem query, ex.: '/datasets/ds-1/colunas'. */
  caminho: string;
  status?: number;
  corpo?: unknown;
}

export interface ChamadaFeita {
  url: string;
  corpo: unknown;
}

export type FetchFalso = Mock<typeof fetch>;

export function respostaJson(status: number, corpo: unknown): Response {
  return new Response(JSON.stringify(corpo), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });
}

function urlDe(entrada: RequestInfo | URL): string {
  if (typeof entrada === 'string') return entrada;
  return entrada instanceof URL ? entrada.href : entrada.url;
}

function caminhoDe(entrada: RequestInfo | URL): string {
  const [caminho = ''] = urlDe(entrada).split('?');
  return caminho;
}

function lerCorpo(corpo: BodyInit | null | undefined): unknown {
  if (typeof corpo !== 'string') return corpo;
  const lido: unknown = JSON.parse(corpo);
  return lido;
}

function casa(rota: RotaFalsa, metodo: string, caminho: string): boolean {
  return (rota.metodo ?? 'GET') === metodo && `/api${rota.caminho}` === caminho;
}

/** Troca o fetch global (restaurado pelo `afterEach` de `src/testes/configuracao.ts`, M1.1). */
export function simularApi(rotas: readonly RotaFalsa[]): FetchFalso {
  const falso = vi.fn<typeof fetch>((entrada, opcoes) => {
    const metodo = opcoes?.method ?? 'GET';
    const caminho = caminhoDe(entrada);
    const rota = rotas.find((r) => casa(r, metodo, caminho));
    const resposta = rota
      ? respostaJson(rota.status ?? 200, rota.corpo ?? null)
      : respostaJson(500, { codigo: 'ROTA_NAO_SIMULADA', mensagem: `${metodo} ${caminho}`, sugestao: '' });
    return Promise.resolve(resposta);
  });
  vi.stubGlobal('fetch', falso);
  return falso;
}

export function chamadasPara(falso: FetchFalso, metodo: string, caminho: string): ChamadaFeita[] {
  return falso.mock.calls
    .filter(([entrada, opcoes]) => (opcoes?.method ?? 'GET') === metodo && caminhoDe(entrada) === `/api${caminho}`)
    .map(([entrada, opcoes]) => ({ url: urlDe(entrada), corpo: lerCorpo(opcoes?.body) }));
}
```

**Passo 4: rodar e ver passar**
`npx vitest run src/testes/api.test.ts` → 3 passed

**Passo 5: refatorar `cliente.test.ts`**

Apague a função local `respostaJson` e o `afterEach(vi.unstubAllGlobals)` e importe do helper:
```ts
import { describe, expect, it, vi } from 'vitest';
import { respostaJson } from '../../testes/api';
import { ErroApi, requisitar } from './cliente';
```
`npx vitest run src/shared/api` → 5 passed.

**Passo 6: ampliar `frontend/src/testes/renderizar.tsx` (criado no M1.1)**

O arquivo do M1.1 tem `renderizarComRotas(rotas, rotaInicial)` (provedores reais + `createMemoryRouter`, devolve `roteador` e `clienteConsultas`) e `renderizarComProvedores(elemento)`. Substitua o conteúdo pelo abaixo. O que muda: (1) `criarClienteTeste()` (sem retentativa e com `gcTime: Infinity`) no lugar do `QueryClient` montado à mão; (2) parâmetro opcional `opcoes` (`rota`, `dataset`, `cliente`) nas duas funções — chamadas do M1.1 sem `opcoes` continuam iguais; (3) retorno ganha `usuario` (`userEvent.setup()`) e `cliente` (o mesmo objeto de `clienteConsultas`); (4) novos `DATASET_TESTE`, `OpcoesRenderizar` e `renderizarHook`. **Não limpe o `localStorage` aqui**: o `afterEach` do M1.1 já limpa, e testes do M1.1 (`PaginaEtapa`, `useSessaoExpirada`, `LayoutApp`) gravam a sessão **antes** de renderizar.
```tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { render, renderHook, type RenderHookResult } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { type ReactElement, type ReactNode, useEffect, useRef } from 'react';
import { MemoryRouter, type RouteObject, RouterProvider, createMemoryRouter } from 'react-router';
import SessaoProvider from '../shared/sessao/SessaoProvider';
import { useSessao } from '../shared/sessao/useSessao';
import TemaProvider from '../shared/tema/TemaProvider';
import ToastProvider from '../shared/ui/ToastProvider';

export type DatasetSessao = NonNullable<ReturnType<typeof useSessao>['dataset']>;

export const DATASET_TESTE: DatasetSessao = { id: 'ds-1', nomeArquivo: 'pesquisa_saude.txt' };

export interface OpcoesRenderizar {
  rota?: string;
  dataset?: DatasetSessao | null;
  cliente?: QueryClient;
}

/** QueryClient novo por teste: sem retentativa e sem coleta de lixo no meio do teste. */
export function criarClienteTeste(): QueryClient {
  return new QueryClient({
    defaultOptions: { queries: { retry: false, gcTime: Infinity }, mutations: { retry: false } },
  });
}

/** Põe o dataset na sessão após a 1ª renderização; o formato do localStorage é detalhe do M1.1. */
function DefinirDataset({ dataset }: Readonly<{ dataset: DatasetSessao | null }>) {
  const sessao = useSessao();
  const definido = useRef(false);
  useEffect(() => {
    if (definido.current || dataset === null) return;
    definido.current = true;
    sessao.definirDataset(dataset);
  }, [dataset, sessao]);
  return null;
}

interface PropsProvedores {
  cliente: QueryClient;
  dataset: DatasetSessao | null;
  children: ReactNode;
}

/** Provedores reais, na mesma ordem do App.tsx. */
function Provedores({ cliente, dataset, children }: Readonly<PropsProvedores>) {
  return (
    <QueryClientProvider client={cliente}>
      <TemaProvider>
        <SessaoProvider>
          <ToastProvider>
            <DefinirDataset dataset={dataset} />
            {children}
          </ToastProvider>
        </SessaoProvider>
      </TemaProvider>
    </QueryClientProvider>
  );
}

export function renderizarComRotas(
  rotas: RouteObject[],
  rotaInicial = '/',
  opcoes: Omit<OpcoesRenderizar, 'rota'> = {},
) {
  const roteador = createMemoryRouter(rotas, { initialEntries: [rotaInicial] });
  const clienteConsultas = opcoes.cliente ?? criarClienteTeste();
  const usuario = userEvent.setup();
  const resultado = render(
    <Provedores cliente={clienteConsultas} dataset={opcoes.dataset ?? null}>
      <RouterProvider router={roteador} />
    </Provedores>,
  );
  return { ...resultado, roteador, clienteConsultas, cliente: clienteConsultas, usuario };
}

/** Um elemento numa rota coringa; `<Routes>` dentro dele também funcionam. */
export function renderizarComProvedores(elemento: ReactElement, opcoes: OpcoesRenderizar = {}) {
  const { rota = '/', ...resto } = opcoes;
  return renderizarComRotas([{ path: '*', element: elemento }], rota, resto);
}

export function renderizarHook<R>(hook: () => R, opcoes: OpcoesRenderizar = {}) {
  const { rota = '/', dataset = null } = opcoes;
  const cliente = opcoes.cliente ?? criarClienteTeste();
  const usuario = userEvent.setup();
  function Envoltorio({ children }: Readonly<{ children: ReactNode }>) {
    return (
      <Provedores cliente={cliente} dataset={dataset}>
        <MemoryRouter initialEntries={[rota]}>{children}</MemoryRouter>
      </Provedores>
    );
  }
  const resultado: RenderHookResult<R, unknown> = renderHook(hook, { wrapper: Envoltorio });
  return { ...resultado, cliente, usuario };
}
```
Como o dataset entra depois da 1ª renderização, as primeiras asserções dos testes de página usam `findBy…`. Rode `npx vitest run src/app src/shared/ui/PaginaEtapa.test.tsx` → os testes do M1.1 continuam verdes.

**Passo 7: fixtures — `frontend/src/testes/fixtures/datasets.ts`**
```ts
import type { components } from '../../shared/api/schema';

type Esquemas = components['schemas'];
type TipoColuna = Esquemas['TipoColuna'];
type MetadadosLeitura = Esquemas['MetadadosLeitura'];
type LinhaDados = Esquemas['LinhaDados'];
type ResumoDataset = Esquemas['ResumoDataset'];
type PaginaDataset = Esquemas['PaginaDataset'];
type DatasetCriado = Esquemas['DatasetCriado'];

export const ID_DATASET = 'ds-1';
export const NOME_ARQUIVO = 'pesquisa_saude.txt';

export function criarColuna(
  dados: Pick<TipoColuna, 'coluna' | 'tipo'> & Partial<TipoColuna>,
): TipoColuna {
  return {
    motivo: 'Motivo de teste.',
    origem: 'auto',
    n_validos: 230,
    n_faltantes: 0,
    n_distintos: 10,
    exemplos: [],
    categorias_ordem: [],
    contagens: {},
    ...dados,
  };
}

export const COLUNAS_SAUDE: TipoColuna[] = [
  criarColuna({ coluna: 'id', tipo: 'identificador', motivo: 'O nome da coluna indica um código (id).', n_distintos: 230, exemplos: ['1', '2', '3', '4'] }),
  criarColuna({ coluna: 'sexo', tipo: 'binaria', motivo: 'Tem só dois valores: F e M.', n_distintos: 2, exemplos: ['F', 'M'] }),
  criarColuna({ coluna: 'idade', tipo: 'discreta', motivo: 'Números inteiros com 28 valores diferentes (contagem).', n_validos: 229, n_faltantes: 1, exemplos: ['34', '27', '45', '52'] }),
  criarColuna({ coluna: 'altura_m', tipo: 'continua', motivo: 'Números com casas decimais.', n_validos: 229, n_faltantes: 1, exemplos: ['1,62', '1,78', '1,58'] }),
  criarColuna({ coluna: 'peso_kg', tipo: 'continua', motivo: 'Números com casas decimais.', n_validos: 227, n_faltantes: 3, exemplos: ['58,2', '79,6', '63,0'] }),
  criarColuna({
    coluna: 'escolaridade',
    tipo: 'ordinal',
    motivo: 'Os valores seguem uma escala conhecida: fundamental < médio < superior < pós.',
    categorias_ordem: ['fundamental', 'médio', 'superior', 'pós'],
    contagens: { fundamental: 38, médio: 96, superior: 71, pós: 25 },
  }),
  criarColuna({ coluna: 'cidade', tipo: 'nominal', motivo: 'São categorias sem ordem natural (7 categorias).', n_validos: 228, n_faltantes: 2, exemplos: ['Goiânia', 'Anápolis'] }),
  criarColuna({
    coluna: 'satisfacao',
    tipo: 'ordinal',
    motivo: 'Os valores seguem uma escala conhecida: ruim < regular < bom < ótimo.',
    categorias_ordem: ['ruim', 'regular', 'bom', 'ótimo'],
    contagens: { ruim: 21, regular: 54, bom: 102, ótimo: 53 },
  }),
];

export const METADADOS_SAUDE: MetadadosLeitura = {
  formato: 'txt',
  codificacao: 'utf-8',
  separador: ';',
  decimal: ',',
  tem_cabecalho: true,
  n_linhas: 230,
  n_colunas: 8,
  abas: [],
  avisos: [],
  motivos: {
    formato: 'Pela extensão e pelo conteúdo.',
    separador: 'Aparece 7 vezes em todas as linhas.',
    decimal: 'Valores como 1,72 e 68,4.',
    codificacao: 'Acentos lidos sem erro (Goiânia).',
    cabecalho: 'A 1ª linha tem só nomes, sem números.',
  },
};

export const LINHAS_SAUDE: LinhaDados[] = [
  { linha: 1, valores: { id: 1, sexo: 'F', idade: 34, altura_m: 1.62, peso_kg: 58.2, escolaridade: 'médio', cidade: 'Goiânia', satisfacao: 'bom' } },
  { linha: 2, valores: { id: 2, sexo: 'M', idade: 27, altura_m: 1.78, peso_kg: null, escolaridade: 'fundamental', cidade: 'Goiania', satisfacao: 'regular' } },
  { linha: 3, valores: { id: 3, sexo: 'F', idade: 45, altura_m: 1.58, peso_kg: 63, escolaridade: 'pós', cidade: 'Anápolis', satisfacao: 'ruim' } },
];

export function criarResumo(dados: Partial<ResumoDataset> = {}): ResumoDataset {
  return {
    dataset_id: ID_DATASET,
    nome_arquivo: NOME_ARQUIVO,
    metadados: METADADOS_SAUDE,
    n_linhas: 230,
    n_linhas_original: 230,
    n_colunas: 8,
    log_limpeza: [],
    ...dados,
  };
}

export function criarPagina(resumo: ResumoDataset = criarResumo()): PaginaDataset {
  return { resumo, versao: 'atual', pagina: 1, tamanho: 20, total_paginas: 12, linhas: LINHAS_SAUDE };
}

export const DATASET_CRIADO: DatasetCriado = {
  dataset_id: ID_DATASET,
  nome_arquivo: NOME_ARQUIVO,
  metadados: METADADOS_SAUDE,
  previa: LINHAS_SAUDE,
  colunas: COLUNAS_SAUDE,
};
```
(Prettier quebra as linhas longas; o conteúdo é este.)

**Passo 8: fixtures — `frontend/src/testes/fixtures/limpeza.ts`**
```ts
import type { components } from '../../shared/api/schema';
import { COLUNAS_SAUDE } from './datasets';

type Esquemas = components['schemas'];
type Diagnostico = Esquemas['Diagnostico'];
type EntradaLog = Esquemas['EntradaLog'];
type ResultadoLimpeza = Esquemas['ResultadoLimpeza'];

export const DIAGNOSTICO_SAUDE: Diagnostico = {
  n_linhas: 230,
  faltantes: [
    { coluna: 'peso_kg', n: 3, linhas: [12, 141, 207], sugeridos: { media: 70.3, mediana: 69.8, moda: 72 } },
    { coluna: 'cidade', n: 2, linhas: [64, 190], sugeridos: { media: null, mediana: null, moda: 'Goiânia' } },
  ],
  duplicados: [{ linha_original: 44, copias: [45, 46, 47] }],
  fora_de_faixa: [
    {
      coluna: 'idade',
      limite_inferior: 1,
      limite_superior: 110,
      origem: 'usuario',
      ocorrencias: [{ linha: 19, valor: 0 }, { linha: 201, valor: 230 }],
    },
    {
      coluna: 'peso_kg',
      limite_inferior: 38.5,
      limite_superior: 102.1,
      origem: 'iqr',
      ocorrencias: [{ linha: 99, valor: 6.8 }, { linha: 160, valor: 712 }],
    },
  ],
  inconsistencias: [
    {
      coluna: 'cidade',
      grupos: [
        { forma_preferida: 'Goiânia', variacoes: [{ texto: 'Goiânia', n: 80 }, { texto: 'Goiania', n: 6 }, { texto: 'goiânia', n: 2 }] },
        { forma_preferida: 'Anápolis', variacoes: [{ texto: 'Anápolis', n: 40 }, { texto: 'Anapolis', n: 3 }] },
      ],
    },
  ],
  tipo_misto: [],
};

export const DIAGNOSTICO_VAZIO: Diagnostico = {
  n_linhas: 227,
  faltantes: [],
  duplicados: [],
  fora_de_faixa: [],
  inconsistencias: [],
  tipo_misto: [],
};

export function criarEntradaLog(dados: Partial<EntradaLog> = {}): EntradaLog {
  return {
    problema: 'duplicados',
    acao: 'remover',
    coluna: null,
    linhas_afetadas: [45, 46, 47],
    antes_exemplo: '',
    depois_exemplo: '',
    quando: '2026-10-20T10:00:00Z',
    frase: 'Removemos 3 linhas duplicadas.',
    ...dados,
  };
}

export function criarResultado(dados: Partial<ResultadoLimpeza> = {}): ResultadoLimpeza {
  return { log: [criarEntradaLog()], n_linhas: 227, n_linhas_original: 230, colunas: COLUNAS_SAUDE, ...dados };
}
```

**Passo 9: rodar tudo e commitar**
`npm run lint && npm run format && npm run test` → verde (inclusive os testes do M1.1 que usam `renderizarComRotas`/`renderizarComProvedores`).
```bash
git add frontend/src/testes frontend/src/shared/api/cliente.test.ts
git commit -m "test(frontend): amplia o helper de renderização e adiciona falso de fetch e fixtures"
```

---

### Tarefa 2: Utilidades compartilhadas

**Arquivos:**
- Criar: `frontend/src/shared/lib/pluralizar.ts` (+ `.test.ts`)
- Criar: `frontend/src/shared/lib/formatarCelula.ts` (+ `.test.ts`)
- Criar: `frontend/src/shared/lib/useValorAtrasado.ts` (+ `.test.ts`)
- Criar: `frontend/src/shared/api/corpoJson.ts` (+ `.test.ts`)
- Criar: `frontend/src/shared/api/classificarErro.ts` (+ `.test.ts`)
- Criar: `frontend/src/shared/ui/useAvisarErro.ts` (+ `.test.tsx`)
- Criar: `frontend/src/shared/navegacao/caminhos.ts`
- Criar: `frontend/src/shared/ui/BarraAcoes.tsx` + `BarraAcoes.module.css`
- Modificar: `frontend/src/app/textos.ts` (M1.1): `TEXTOS_APP.dimensoes` passa a usar `contarLinhas`/`contarColunas` e a função local `quantidade` sai (mesma regra em um lugar só)
- Modificar (se faltar): `frontend/src/shared/ui/tokens.css` (`--fonte-mono`, `--raio-*`, `--esp-*`)

**Passo 1: escrever os testes (falham)**

`frontend/src/shared/lib/pluralizar.test.ts`:
```ts
import { describe, expect, it } from 'vitest';
import { contarColunas, contarLinhas, escolherForma, pluralizar } from './pluralizar';

describe('pluralizar', () => {
  it.each([
    [0, '0 linhas'],
    [1, '1 linha'],
    [2, '2 linhas'],
    [1234, '1.234 linhas'],
  ])('%i → %s', (n, esperado) => {
    expect(pluralizar(n, 'linha', 'linhas')).toBe(esperado);
  });

  it('escolhe só a forma, sem o número', () => {
    expect(escolherForma(1, 'grupo', 'grupos')).toBe('grupo');
    expect(escolherForma(3, 'grupo', 'grupos')).toBe('grupos');
  });

  it('tem atalhos para linhas e colunas', () => {
    expect(`${contarLinhas(230)} × ${contarColunas(1)}`).toBe('230 linhas × 1 coluna');
  });
});
```

`frontend/src/shared/lib/formatarCelula.test.ts`:
```ts
import { describe, expect, it } from 'vitest';
import { formatarCelula } from './formatarCelula';

describe('formatarCelula', () => {
  it.each([
    [58.2, '58,2'],
    [1234.5, '1.234,5'],
    [null, '—'],
    [undefined, '—'],
    [true, 'Sim'],
    [false, 'Não'],
    ['Goiânia', 'Goiânia'],
  ])('%s → %s', (valor, esperado) => {
    expect(formatarCelula(valor)).toBe(esperado);
  });
});
```

`frontend/src/shared/lib/useValorAtrasado.test.ts`:
```ts
import { act, renderHook } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { useValorAtrasado } from './useValorAtrasado';

describe('useValorAtrasado', () => {
  afterEach(() => {
    vi.useRealTimers();
  });

  it('só devolve o valor novo depois do atraso', () => {
    vi.useFakeTimers();
    const { result, rerender } = renderHook(({ valor }) => useValorAtrasado(valor, 600), {
      initialProps: { valor: 'a' },
    });

    rerender({ valor: 'b' });
    act(() => {
      vi.advanceTimersByTime(599);
    });
    expect(result.current).toBe('a');

    act(() => {
      vi.advanceTimersByTime(1);
    });
    expect(result.current).toBe('b');
  });

  it('reinicia a contagem a cada mudança', () => {
    vi.useFakeTimers();
    const { result, rerender } = renderHook(({ valor }) => useValorAtrasado(valor, 600), {
      initialProps: { valor: 'a' },
    });

    rerender({ valor: 'b' });
    act(() => {
      vi.advanceTimersByTime(400);
    });
    rerender({ valor: 'c' });
    act(() => {
      vi.advanceTimersByTime(400);
    });
    expect(result.current).toBe('a');

    act(() => {
      vi.advanceTimersByTime(200);
    });
    expect(result.current).toBe('c');
  });
});
```

`frontend/src/shared/api/corpoJson.test.ts`:
```ts
import { describe, expect, it } from 'vitest';
import { corpoJson } from './corpoJson';

describe('corpoJson', () => {
  it('monta método, cabeçalho e corpo em JSON', () => {
    expect(corpoJson('PATCH', { tipo: 'ordinal' })).toEqual({
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: '{"tipo":"ordinal"}',
    });
  });
});
```

`frontend/src/shared/api/classificarErro.test.ts`:
```ts
import { describe, expect, it } from 'vitest';
import { ErroApi } from './cliente';
import { deveTentarDeNovo, ehErroDeEntrada } from './classificarErro';

const corpo = { codigo: 'X', mensagem: 'm', sugestao: 's' };

describe('classificarErro', () => {
  it('erro 4xx é de entrada e não se repete', () => {
    const erro = new ErroApi(404, corpo);
    expect(ehErroDeEntrada(erro)).toBe(true);
    expect(deveTentarDeNovo(0, erro)).toBe(false);
  });

  it('sem conexão (status 0) e 5xx tentam de novo até 2 vezes', () => {
    expect(deveTentarDeNovo(0, new ErroApi(0, corpo))).toBe(true);
    expect(deveTentarDeNovo(1, new ErroApi(500, corpo))).toBe(true);
    expect(deveTentarDeNovo(2, new ErroApi(500, corpo))).toBe(false);
  });

  it('erro que não veio da API não é de entrada', () => {
    expect(ehErroDeEntrada(new Error('x'))).toBe(false);
  });
});
```

`frontend/src/shared/ui/useAvisarErro.test.tsx`:
```tsx
import { screen } from '@testing-library/react';
import { act } from 'react';
import { describe, expect, it } from 'vitest';
import { renderizarHook } from '../../testes/renderizar';
import { ErroApi } from '../api/cliente';
import { useAvisarErro } from './useAvisarErro';

describe('useAvisarErro', () => {
  it('mostra mensagem e sugestão da API num toast', async () => {
    const { result } = renderizarHook(() => useAvisarErro());

    act(() => {
      result.current(new ErroApi(400, { codigo: 'TIPO_INCOMPATIVEL', mensagem: 'Esta coluna tem textos; não pode ser numérica.', sugestao: 'Escolha um tipo qualitativo.' }));
    });

    expect(await screen.findByText('Esta coluna tem textos; não pode ser numérica.')).toBeInTheDocument();
  });

  it('deixa a sessão expirada para o useSessaoExpirada', () => {
    const { result } = renderizarHook(() => useAvisarErro());

    act(() => {
      result.current(new ErroApi(404, { codigo: 'DATASET_NAO_ENCONTRADO', mensagem: 'Sua sessão expirou.', sugestao: 'Envie o arquivo novamente.' }));
    });

    expect(screen.queryByText('Sua sessão expirou.')).not.toBeInTheDocument();
  });
});
```

**Passo 2: rodar e ver falhar**
`npx vitest run src/shared` → FAIL (módulos não existem)

**Passo 3: implementar**

`frontend/src/shared/lib/pluralizar.ts`:
```ts
import { formatarInteiro } from './formatar';

export function escolherForma(n: number, singular: string, plural: string): string {
  return n === 1 ? singular : plural;
}

/** "1 linha", "230 linhas", "1.234 linhas". */
export function pluralizar(n: number, singular: string, plural: string): string {
  return `${formatarInteiro(n)} ${escolherForma(n, singular, plural)}`;
}

export function contarLinhas(n: number): string {
  return pluralizar(n, 'linha', 'linhas');
}

export function contarColunas(n: number): string {
  return pluralizar(n, 'coluna', 'colunas');
}
```

`frontend/src/shared/lib/formatarCelula.ts`:
```ts
import type { components } from '../api/schema';

export type Celula = components['schemas']['LinhaDados']['valores'][string];

const NUMERO_CELULA = new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 10 });
const VAZIO = '—';

/** Valor bruto de uma célula para exibir em tabela (sem arredondar casas significativas). */
export function formatarCelula(valor: Celula | undefined): string {
  if (valor === null || valor === undefined) return VAZIO;
  if (typeof valor === 'number') return NUMERO_CELULA.format(valor);
  if (typeof valor === 'boolean') return valor ? 'Sim' : 'Não';
  return valor;
}
```

`frontend/src/shared/lib/useValorAtrasado.ts`:
```ts
import { useEffect, useState } from 'react';

/** Devolve `valor` só depois de `atrasoMs` sem mudanças (debounce). */
export function useValorAtrasado<T>(valor: T, atrasoMs: number): T {
  const [atrasado, setAtrasado] = useState(valor);
  useEffect(() => {
    const espera = setTimeout(() => {
      setAtrasado(valor);
    }, atrasoMs);
    return () => {
      clearTimeout(espera);
    };
  }, [valor, atrasoMs]);
  return atrasado;
}
```

`frontend/src/shared/api/corpoJson.ts`:
```ts
/** Opções do fetch para enviar um corpo JSON. */
export function corpoJson(metodo: 'POST' | 'PATCH' | 'PUT', corpo: unknown): RequestInit {
  return {
    method: metodo,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(corpo),
  };
}
```

`frontend/src/shared/api/classificarErro.ts`:
```ts
import { ErroApi } from './cliente';

const MAX_RETENTATIVAS = 2;

/** 4xx: o pedido está errado (arquivo ilegível, sessão expirada…); repetir não resolve. */
export function ehErroDeEntrada(erro: unknown): boolean {
  return erro instanceof ErroApi && erro.status >= 400 && erro.status < 500;
}

/** Política de retentativa das consultas (Dnn-sessao): sem repetir 4xx; rede e 5xx até 2 vezes. */
export function deveTentarDeNovo(falhas: number, erro: unknown): boolean {
  return !ehErroDeEntrada(erro) && falhas < MAX_RETENTATIVAS;
}
```

`frontend/src/shared/ui/useAvisarErro.ts`:
```ts
import { useCallback } from 'react';
import { ehDatasetNaoEncontrado, textoDoErro } from '../api/erros';
import { useToast } from './useToast';

/** Mostra o erro num toast; "sessão expirada" fica com o `useSessaoExpirada` (D61) para não avisar duas vezes. */
export function useAvisarErro(): (erro: unknown) => void {
  const toast = useToast();
  return useCallback(
    (erro: unknown) => {
      if (ehDatasetNaoEncontrado(erro)) return;
      const { mensagem, sugestao } = textoDoErro(erro);
      toast.mostrar({ tipo: 'erro', titulo: mensagem, descricao: sugestao });
    },
    [toast],
  );
}
```

`frontend/src/shared/navegacao/caminhos.ts` (Dnn-caminhos):
```ts
/** Caminhos das etapas; `app/etapas.ts` e as features usam daqui. */
export const CAMINHOS = {
  importar: '/importar',
  variaveis: '/variaveis',
  limpeza: '/limpeza',
  analise: '/analise',
  relatorio: '/relatorio',
} as const;
```

`frontend/src/shared/ui/BarraAcoes.tsx` (ações no fim da tela, alinhadas à direita, primário por último — README do design):
```tsx
import type { ReactNode } from 'react';
import estilos from './BarraAcoes.module.css';

export default function BarraAcoes({ children }: Readonly<{ children: ReactNode }>) {
  return <div className={estilos.barra}>{children}</div>;
}
```

`BarraAcoes.module.css`:

| Seletor | Propriedades |
|---|---|
| `.barra` | `display:flex; flex-wrap:wrap; justify-content:flex-end; align-items:center; gap:12px` |

`frontend/src/app/textos.ts` (M1.1) — apague a função `quantidade` e o import de `formatarInteiro`; importe `contarColunas, contarLinhas` de `../shared/lib/pluralizar` e troque só a entrada `dimensoes`:
```ts
  dimensoes: (linhas: number, colunas: number): string => `${contarLinhas(linhas)} × ${contarColunas(colunas)}`,
```
Os testes do Cabeçalho do M1.1 ("230 linhas × 8 colunas", "1.234 linhas × 1 coluna") continuam valendo.

Tokens: se `grep` do início mostrou que faltam, acrescente no `:root` do `tokens.css` (valores de `tokens.md`): `--fonte-texto: Inter, system-ui, sans-serif; --fonte-mono: 'JetBrains Mono', monospace; --esp-4: 4px … --esp-64: 64px; --raio-xs: 4px; --raio-sm: 6px; --raio-md: 8px; --raio-lg: 12px`.

**Passo 4: rodar e ver passar**
`npx vitest run src/shared` → todos passam.

**Passo 5: lint, testes e commit**
```bash
git add frontend/src/shared frontend/src/app/textos.ts
git commit -m "feat(frontend): adiciona pluralização, formatação de célula, atraso, corpo JSON e aviso de erro"
```

---

### Tarefa 3: `tiposVariavel.ts` + `ChipTipo`

**Arquivos:**
- Criar: `frontend/src/shared/ui/tiposVariavel.ts` (+ `.test.ts`)
- Criar: `frontend/src/shared/ui/ChipTipo.tsx`, `ChipTipo.module.css` (+ `ChipTipo.test.tsx`)

**Passo 1: escrever os testes (falham)**

`frontend/src/shared/ui/tiposVariavel.test.ts`:
```ts
import { describe, expect, it } from 'vitest';
import { ehNumerico, estiloDoTipo, ORDEM_TIPOS, TIPOS_VARIAVEL } from './tiposVariavel';

describe('tiposVariavel', () => {
  it('ORDEM_TIPOS cobre os 6 tipos sem repetir', () => {
    expect(new Set(ORDEM_TIPOS).size).toBe(Object.keys(TIPOS_VARIAVEL).length);
  });

  it('usa rótulos e ícones do design', () => {
    expect(TIPOS_VARIAVEL.continua).toEqual({
      icone: 'straighten',
      rotuloCurto: 'Contínua',
      rotuloCompleto: 'Quantitativa contínua',
      token: '--tipo-continua',
    });
    expect(TIPOS_VARIAVEL.identificador.rotuloCompleto).toBe('Identificador (ignorada)');
  });

  it('cores saem dos tokens do tipo', () => {
    expect(estiloDoTipo('ordinal')).toEqual({
      color: 'var(--tipo-ordinal)',
      backgroundColor: 'var(--tipo-ordinal-suave)',
      borderColor: 'color-mix(in oklab, var(--tipo-ordinal) 35%, transparent)',
    });
  });

  it('só discreta e contínua são numéricas', () => {
    expect(ORDEM_TIPOS.filter(ehNumerico)).toEqual(['continua', 'discreta']);
  });
});
```

`frontend/src/shared/ui/ChipTipo.test.tsx`:
```tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it } from 'vitest';
import ChipTipo from './ChipTipo';

describe('ChipTipo', () => {
  it('mostra o rótulo curto e o nome completo no tooltip', async () => {
    const usuario = userEvent.setup();
    render(<ChipTipo tipo="continua" curto />);

    await usuario.hover(screen.getByText('Contínua'));

    expect(await screen.findByRole('tooltip')).toHaveTextContent('Quantitativa contínua');
  });

  it('usa o rótulo completo por padrão', () => {
    render(<ChipTipo tipo="nominal" />);
    expect(screen.getByText('Qualitativa nominal')).toBeInTheDocument();
  });

  it('marca o tipo corrigido pelo usuário com um selo', () => {
    render(<ChipTipo tipo="ordinal" curto corrigido />);
    expect(screen.getByText('corrigido')).toBeInTheDocument();
  });

  it('expõe o tipo em data-tipo (identificador ganha borda tracejada no CSS)', () => {
    render(<ChipTipo tipo="identificador" curto />);
    expect(screen.getByText('Identificador').closest('[data-tipo]')).toHaveAttribute(
      'data-tipo',
      'identificador',
    );
  });
});
```

**Passo 2: rodar e ver falhar**
`npx vitest run src/shared/ui/tiposVariavel.test.ts src/shared/ui/ChipTipo.test.tsx` → FAIL

**Passo 3: implementar**

`frontend/src/shared/ui/tiposVariavel.ts`:
```ts
/** Tipo de variável → ícone, rótulos e token de cor (tokens.md, "Tipos de variável"). */
import type { CSSProperties } from 'react';
import type { components } from '../api/schema';

export type TipoVariavel = components['schemas']['TipoVariavel'];

interface ConfiguracaoTipo {
  icone: string;
  rotuloCurto: string;
  rotuloCompleto: string;
  token: `--tipo-${TipoVariavel}`;
}

export const TIPOS_VARIAVEL = {
  nominal: { icone: 'sell', rotuloCurto: 'Nominal', rotuloCompleto: 'Qualitativa nominal', token: '--tipo-nominal' },
  ordinal: { icone: 'stairs', rotuloCurto: 'Ordinal', rotuloCompleto: 'Qualitativa ordinal', token: '--tipo-ordinal' },
  discreta: { icone: 'pin', rotuloCurto: 'Discreta', rotuloCompleto: 'Quantitativa discreta', token: '--tipo-discreta' },
  continua: { icone: 'straighten', rotuloCurto: 'Contínua', rotuloCompleto: 'Quantitativa contínua', token: '--tipo-continua' },
  binaria: { icone: 'toggle_on', rotuloCurto: 'Binária', rotuloCompleto: 'Binária', token: '--tipo-binaria' },
  identificador: { icone: 'fingerprint', rotuloCurto: 'Identificador', rotuloCompleto: 'Identificador (ignorada)', token: '--tipo-identificador' },
} as const satisfies Record<TipoVariavel, ConfiguracaoTipo>;

/** Ordem de exibição (resumo da tela 2 e Select "Corrigir tipo"). */
export const ORDEM_TIPOS = [
  'continua',
  'discreta',
  'ordinal',
  'nominal',
  'binaria',
  'identificador',
] as const satisfies readonly TipoVariavel[];

export const ROTULO_CORRIGIDO = 'corrigido';
export const DICA_CORRIGIDO = 'corrigido por você';

const TIPOS_NUMERICOS: ReadonlySet<TipoVariavel> = new Set<TipoVariavel>(['discreta', 'continua']);

export function ehNumerico(tipo: TipoVariavel): boolean {
  return TIPOS_NUMERICOS.has(tipo);
}

export function corDoTipo(tipo: TipoVariavel): string {
  return `var(${TIPOS_VARIAVEL[tipo].token})`;
}

/** Texto, fundo suave e borda 35% da cor do tipo (componentes.md, ChipTipo). */
export function estiloDoTipo(tipo: TipoVariavel): CSSProperties {
  const { token } = TIPOS_VARIAVEL[tipo];
  return {
    color: `var(${token})`,
    backgroundColor: `var(${token}-suave)`,
    borderColor: `color-mix(in oklab, var(${token}) 35%, transparent)`,
  };
}
```

`frontend/src/shared/ui/ChipTipo.tsx`:
```tsx
import estilos from './ChipTipo.module.css';
import Icone from './Icone';
import {
  DICA_CORRIGIDO,
  estiloDoTipo,
  ROTULO_CORRIGIDO,
  TIPOS_VARIAVEL,
  type TipoVariavel,
} from './tiposVariavel';
import Tooltip from './Tooltip';

interface PropsChipTipo {
  tipo: TipoVariavel;
  curto?: boolean;
  corrigido?: boolean;
}

/** Tipo de variável sempre com ícone + palavra + cor (princípio 4 do design). */
export default function ChipTipo({ tipo, curto = false, corrigido = false }: Readonly<PropsChipTipo>) {
  const config = TIPOS_VARIAVEL[tipo];
  const dica = corrigido ? `${config.rotuloCompleto} (${DICA_CORRIGIDO})` : config.rotuloCompleto;
  return (
    <Tooltip texto={dica}>
      <span className={estilos.chip} data-tipo={tipo} style={estiloDoTipo(tipo)}>
        <Icone nome={config.icone} tamanho={17} />
        {curto ? config.rotuloCurto : config.rotuloCompleto}
        {corrigido ? <span className={estilos.selo}>{ROTULO_CORRIGIDO}</span> : null}
      </span>
    </Tooltip>
  );
}
```

`ChipTipo.module.css` (componentes.md §ChipTipo; cores vêm do `style` com tokens):

| Seletor | Propriedades |
|---|---|
| `.chip` | `display:inline-flex; align-items:center; gap:6px; height:26px; padding:0 10px 0 8px; border:1px solid; border-radius:999px; font-size:13px; font-weight:600; line-height:1; white-space:nowrap` |
| `.chip[data-tipo='identificador']` | `border-style:dashed` |
| `.selo` | `margin-left:2px; padding:2px 6px; border-radius:999px; background:var(--cor-superficie); color:var(--cor-texto-2); font-size:11px; font-weight:500` |

**Passo 4: rodar e ver passar** → 8 passed.

**Passo 5: commit**
```bash
git add frontend/src/shared/ui/tiposVariavel.ts frontend/src/shared/ui/tiposVariavel.test.ts frontend/src/shared/ui/ChipTipo.*
git commit -m "feat(frontend): adiciona ChipTipo e tabela de tipos de variável"
```

---

### Tarefa 4: Consultas do dataset + linhas × colunas no Cabeçalho

O `Cabecalho` do M1.1 já recebe `nLinhas`/`nColunas` por props e formata com `TEXTOS_APP.dimensoes`; o ponto de integração previsto no M1.1 (Tarefa 17) é o `LayoutApp` buscar o resumo e passar os dois números. Nada de componente novo para isso.

**Arquivos:**
- Criar: `frontend/src/shared/api/dataset.ts` (+ `dataset.test.ts`)
- Modificar: `frontend/src/app/layout/LayoutApp.tsx` (M1.1): busca o resumo com `opcoesPrimeiraPagina` e passa `nLinhas`/`nColunas` ao `Cabecalho`
- Modificar: `frontend/src/app/layout/LayoutApp.test.tsx` (M1.1): acrescenta um caso

**Passo 1: escrever os testes (falham)**

`frontend/src/shared/api/dataset.test.ts`:
```ts
import { describe, expect, it } from 'vitest';
import { criarPagina, ID_DATASET } from '../../testes/fixtures/datasets';
import { chamadasPara, simularApi } from '../../testes/api';
import { criarClienteTeste } from '../../testes/renderizar';
import { caminhoDataset, chavesDataset, opcoesPrimeiraPagina } from './dataset';

describe('chavesDataset', () => {
  it('todas as chaves começam pelo prefixo do dataset', () => {
    const prefixo = chavesDataset.todas(ID_DATASET);
    for (const chave of [
      chavesDataset.primeiraPagina(ID_DATASET),
      chavesDataset.colunas(ID_DATASET),
      chavesDataset.diagnostico(ID_DATASET),
      chavesDataset.analises(ID_DATASET),
      chavesDataset.relatorio(ID_DATASET),
    ]) {
      expect(chave.slice(0, prefixo.length)).toEqual(prefixo);
    }
  });
});

describe('caminhoDataset', () => {
  it('codifica o id e acrescenta o sufixo', () => {
    expect(caminhoDataset('a/b', '/colunas')).toBe('/datasets/a%2Fb/colunas');
  });
});

describe('opcoesPrimeiraPagina', () => {
  it('busca a página 1 com 20 linhas', async () => {
    const falso = simularApi([{ caminho: `/datasets/${ID_DATASET}`, corpo: criarPagina() }]);

    const pagina = await criarClienteTeste().fetchQuery(opcoesPrimeiraPagina(ID_DATASET));

    expect(pagina.resumo.n_linhas).toBe(230);
    expect(chamadasPara(falso, 'GET', `/datasets/${ID_DATASET}`)[0]?.url).toBe(
      `/api/datasets/${ID_DATASET}?pagina=1&tamanho=20`,
    );
  });
});
```

Acrescentar ao fim de `frontend/src/app/layout/LayoutApp.test.tsx` (M1.1; reaproveita `ROTAS_TESTE` do arquivo):
```tsx
it('mostra linhas atuais × colunas do dataset da sessão', async () => {
  simularApi([{ caminho: `/datasets/${ID_DATASET}`, corpo: criarPagina(criarResumo({ n_linhas: 227 })) }]);

  renderizarComRotas(ROTAS_TESTE, '/importar', { dataset: DATASET_TESTE });

  expect(await screen.findByText('227 linhas × 8 colunas')).toBeInTheDocument();
});
```
(imports novos: `simularApi` de `../../testes/api`, `criarPagina, criarResumo, ID_DATASET` de `../../testes/fixtures/datasets` e `DATASET_TESTE` junto do `renderizarComRotas`.)

**Passo 2: rodar e ver falhar** → FAIL

**Passo 3: implementar `frontend/src/shared/api/dataset.ts`**
```ts
/** Consultas e chaves de um dataset compartilhadas entre features (Dnn-chaves). */
import { queryOptions, skipToken } from '@tanstack/react-query';
import { requisitar } from './cliente';
import type { components } from './schema';

export type PaginaDataset = components['schemas']['PaginaDataset'];
export type ResumoDataset = components['schemas']['ResumoDataset'];
export type TipoColuna = components['schemas']['TipoColuna'];
export type LinhaDados = components['schemas']['LinhaDados'];

export const TAMANHO_PREVIA = 20;

export const chavesDataset = {
  todas: (id: string) => ['datasets', id] as const,
  primeiraPagina: (id: string) => ['datasets', id, 'primeira-pagina'] as const,
  colunas: (id: string) => ['datasets', id, 'colunas'] as const,
  diagnostico: (id: string) => ['datasets', id, 'diagnostico'] as const,
  analises: (id: string) => ['datasets', id, 'analise'] as const,
  relatorio: (id: string) => ['datasets', id, 'relatorio'] as const,
};

export function caminhoDataset(id: string, sufixo = ''): string {
  return `/datasets/${encodeURIComponent(id)}${sufixo}`;
}

/** Página 1 (20 linhas) + resumo: cabeçalho, prévia da tela 1 e log da limpeza usam a mesma chave. */
export function opcoesPrimeiraPagina(id: string | null) {
  return queryOptions({
    queryKey: chavesDataset.primeiraPagina(id ?? ''),
    queryFn:
      id === null
        ? skipToken
        : () =>
            requisitar<PaginaDataset>(
              caminhoDataset(id, `?pagina=1&tamanho=${String(TAMANHO_PREVIA)}`),
            ),
  });
}

export function opcoesColunas(id: string | null) {
  return queryOptions({
    queryKey: chavesDataset.colunas(id ?? ''),
    queryFn: id === null ? skipToken : () => requisitar<TipoColuna[]>(caminhoDataset(id, '/colunas')),
  });
}
```

`frontend/src/app/layout/LayoutApp.tsx` (M1.1) — acrescente a consulta do resumo e troque a linha do `Cabecalho` (o comentário `M1.6: passar nLinhas/nColunas…` sai). O resumo atualiza sozinho depois da limpeza, porque a limpeza invalida o prefixo do dataset:
```tsx
import { useQuery } from '@tanstack/react-query';
import { opcoesPrimeiraPagina } from '../../shared/api/dataset';
// ...
  const { dataset } = useSessao();
  const { data: resumo } = useQuery({
    ...opcoesPrimeiraPagina(dataset?.id ?? null),
    select: (pagina) => pagina.resumo,
  });
// ...
        <Cabecalho nomeArquivo={dataset?.nomeArquivo} nLinhas={resumo?.n_linhas} nColunas={resumo?.n_colunas} />
```
O `Cabecalho` não muda (as props aceitam `undefined`; sem resumo, as dimensões ficam ocultas).

**Passo 4: rodar e ver passar** → 4 passed (+ testes do `LayoutApp` e do `Cabecalho` do M1.1 continuam verdes).

**Passo 5: commit**
```bash
git add frontend/src/shared/api/dataset.* frontend/src/app/layout
git commit -m "feat(frontend): adiciona chaves por dataset e mostra linhas × colunas no cabeçalho"
```

---

### Tarefa 5: Sessão expirada (completa o hook do M1.1), `ExigeDataset` + `SemDataset`, `ConteudoConsulta`

O M1.1 (Tarefa 18) já entrega `app/layout/useSessaoExpirada.ts`, chamado no `LayoutApp`: escuta erros dos caches de consultas **e** mutações e, em `DATASET_NAO_ENCONTRADO`, encerra a sessão, mostra o toast e navega para Importar. Este bloco **não cria outro hook**: só acrescenta ao do M1.1 (a) aviso **uma vez** por dataset — com várias consultas falhando juntas, um toast só —, (b) `removeQueries` do prefixo do dataset expirado e (c) `CAMINHOS.importar` no lugar de `ETAPAS[0].caminho`.

**Arquivos:**
- Modificar: `frontend/src/app/layout/useSessaoExpirada.ts` (M1.1) e `useSessaoExpirada.test.tsx` (M1.1: acrescenta um caso)
- Criar: `frontend/src/shared/sessao/SemDataset.tsx`, `frontend/src/shared/sessao/ExigeDataset.tsx`, `frontend/src/shared/sessao/textos.ts` (+ `ExigeDataset.test.tsx`)
- Criar: `frontend/src/shared/ui/ConteudoConsulta.tsx` (+ `.test.tsx`)
- Modificar: `frontend/src/app/App.tsx` (`retry: deveTentarDeNovo`), `frontend/src/app/etapas.ts` (usar `CAMINHOS`)

`LayoutApp.tsx` não muda nesta tarefa: já chama `useSessaoExpirada()` dentro do roteador e dos provedores.

**Passo 1: escrever os testes (falham)**

Acrescentar ao fim de `frontend/src/app/layout/useSessaoExpirada.test.tsx` (M1.1; os dois casos do M1.1 continuam):
```tsx
import { Route, Routes } from 'react-router';
import { requisitar } from '../../shared/api/cliente';
import { simularApi } from '../../testes/api';
import { DATASET_TESTE, renderizarComProvedores } from '../../testes/renderizar';

const SESSAO_EXPIRADA = {
  codigo: 'DATASET_NAO_ENCONTRADO',
  mensagem: 'Sua sessão expirou.',
  sugestao: 'Envie o arquivo novamente.',
};

function ComVigia() {
  useSessaoExpirada();
  return null;
}

function DuasConsultasQueFalham() {
  useQuery({ queryKey: ['datasets', 'ds-1', 'colunas'], queryFn: () => requisitar('/datasets/ds-1/colunas') });
  useQuery({ queryKey: ['datasets', 'ds-1', 'primeira-pagina'], queryFn: () => requisitar('/datasets/ds-1') });
  return <p>Tela de variáveis</p>;
}

describe('useSessaoExpirada com várias consultas', () => {
  it('encerra a sessão, avisa uma vez e volta para Importar', async () => {
    simularApi([
      { caminho: '/datasets/ds-1/colunas', status: 404, corpo: SESSAO_EXPIRADA },
      { caminho: '/datasets/ds-1', status: 404, corpo: SESSAO_EXPIRADA },
    ]);

    renderizarComProvedores(
      <>
        <ComVigia />
        <Routes>
          <Route path="/variaveis" element={<DuasConsultasQueFalham />} />
          <Route path="/importar" element={<p>Tela de importar</p>} />
        </Routes>
      </>,
      { rota: '/variaveis', dataset: DATASET_TESTE },
    );

    expect(await screen.findByText('Tela de importar')).toBeInTheDocument();
    expect(screen.getAllByText('Sua sessão expirou.')).toHaveLength(1);
  });
});
```
(Junte os imports novos aos do topo: o arquivo do M1.1 já importa `useQuery`, `screen`, `waitFor`, `expect` e `it`; acrescente `describe`.)

`frontend/src/shared/sessao/ExigeDataset.test.tsx`:
```tsx
import { screen } from '@testing-library/react';
import { Route, Routes } from 'react-router';
import { describe, expect, it } from 'vitest';
import { DATASET_TESTE, renderizarComProvedores } from '../../testes/renderizar';
import ExigeDataset from './ExigeDataset';

describe('ExigeDataset', () => {
  it('sem dataset, orienta e leva para Importar', async () => {
    const { usuario } = renderizarComProvedores(
      <Routes>
        <Route path="/limpeza" element={<ExigeDataset>{(id) => <p>{id}</p>}</ExigeDataset>} />
        <Route path="/importar" element={<p>Tela de importar</p>} />
      </Routes>,
      { rota: '/limpeza' },
    );

    expect(screen.getByText('Nenhum arquivo importado')).toBeInTheDocument();
    await usuario.click(screen.getByRole('button', { name: 'Ir para Importar' }));
    expect(screen.getByText('Tela de importar')).toBeInTheDocument();
  });

  it('com dataset, entrega o id para o conteúdo', async () => {
    renderizarComProvedores(<ExigeDataset>{(id) => <p>Dataset {id}</p>}</ExigeDataset>, {
      dataset: DATASET_TESTE,
    });

    expect(await screen.findByText('Dataset ds-1')).toBeInTheDocument();
  });
});
```

`frontend/src/shared/ui/ConteudoConsulta.test.tsx`:
```tsx
import { useQuery } from '@tanstack/react-query';
import { screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { requisitar } from '../api/cliente';
import { simularApi } from '../../testes/api';
import { renderizarComProvedores } from '../../testes/renderizar';
import ConteudoConsulta from './ConteudoConsulta';

function Exemplo() {
  const consulta = useQuery({ queryKey: ['exemplo'], queryFn: () => requisitar<{ nome: string }>('/exemplo') });
  return (
    <ConteudoConsulta consulta={consulta} carregando="Carregando o exemplo…" forma="cards">
      {(dados) => <p>Olá, {dados.nome}</p>}
    </ConteudoConsulta>
  );
}

describe('ConteudoConsulta', () => {
  it('mostra o carregando e depois os dados', async () => {
    simularApi([{ caminho: '/exemplo', corpo: { nome: 'mundo' } }]);
    renderizarComProvedores(<Exemplo />);

    // O ToastProvider também tem região role="status"; por isso a busca é pelo texto.
    expect(screen.getByText('Carregando o exemplo…')).toBeInTheDocument();
    expect(await screen.findByText('Olá, mundo')).toBeInTheDocument();
  });

  it('mostra o erro da API com "tentar de novo"', async () => {
    simularApi([
      { caminho: '/exemplo', status: 400, corpo: { codigo: 'X', mensagem: 'Deu errado.', sugestao: 'Tente outra coisa.' } },
    ]);
    renderizarComProvedores(<Exemplo />);

    expect(await screen.findByText('Deu errado.')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /tentar de novo/i })).toBeInTheDocument();
  });
});
```

**Passo 2: rodar e ver falhar** → FAIL

**Passo 3: implementar**

`frontend/src/app/layout/useSessaoExpirada.ts` (M1.1) — substitua o corpo pelo abaixo. Mesma assinatura e mesmo lugar; o que entra: `useRef` com o último id avisado, saída antecipada sem dataset, `removeQueries` do prefixo e `CAMINHOS.importar` (o import de `ETAPAS` sai):
```ts
import { useQueryClient } from '@tanstack/react-query';
import { useEffect, useRef } from 'react';
import { useNavigate } from 'react-router';
import { chavesDataset } from '../../shared/api/dataset';
import { ehDatasetNaoEncontrado, textoDoErro } from '../../shared/api/erros';
import { CAMINHOS } from '../../shared/navegacao/caminhos';
import { useSessao } from '../../shared/sessao/useSessao';
import { useToast } from '../../shared/ui/useToast';

/**
 * D61/Dnn-sessao: DATASET_NAO_ENCONTRADO em qualquer consulta ou mutação encerra a sessão,
 * avisa uma vez por dataset ("Sua sessão expirou. Envie o arquivo novamente."), apaga o cache dele e volta para Importar.
 */
export function useSessaoExpirada(): void {
  const clienteConsultas = useQueryClient();
  const { dataset, encerrar } = useSessao();
  const { mostrar } = useToast();
  const navegar = useNavigate();
  const idAtual = dataset?.id ?? null;
  const ultimoAvisado = useRef<string | null>(null);

  useEffect(() => {
    if (idAtual === null) return undefined;
    const id = idAtual;
    const aoFalhar = (erro: unknown): void => {
      if (!ehDatasetNaoEncontrado(erro) || ultimoAvisado.current === id) return;
      ultimoAvisado.current = id;
      const { mensagem, sugestao } = textoDoErro(erro);
      encerrar();
      clienteConsultas.removeQueries({ queryKey: chavesDataset.todas(id) });
      mostrar({ tipo: 'erro', titulo: mensagem, descricao: sugestao });
      void navegar(CAMINHOS.importar);
    };
    const pararConsultas = clienteConsultas.getQueryCache().subscribe((evento) => {
      if (evento.type === 'updated' && evento.action.type === 'error') aoFalhar(evento.action.error);
    });
    const pararMutacoes = clienteConsultas.getMutationCache().subscribe((evento) => {
      if (evento.type === 'updated' && evento.action.type === 'error') aoFalhar(evento.action.error);
    });
    return () => {
      pararConsultas();
      pararMutacoes();
    };
  }, [clienteConsultas, idAtual, encerrar, mostrar, navegar]);
}
```
(Desestruturar `useSessao()`/`useToast()` aqui é seguro: o M1.1 declara os callbacks como propriedades, não métodos. Mantenha o estilo do arquivo do M1.1.)

`frontend/src/shared/sessao/textos.ts`:
```ts
export const TEXTOS_SESSAO = {
  semDatasetTitulo: 'Nenhum arquivo importado',
  semDatasetDescricao: 'Importe um arquivo na etapa 1 para continuar.',
  irParaImportar: 'Ir para Importar',
} as const;
```

`frontend/src/shared/sessao/SemDataset.tsx` (estado vazio reutilizável; o M1.7 usa nas telas 4 e 8 com uma descrição própria):
```tsx
import { useNavigate } from 'react-router';
import { CAMINHOS } from '../navegacao/caminhos';
import Botao from '../ui/Botao';
import EstadoVazio from '../ui/EstadoVazio';
import { TEXTOS_SESSAO as T } from './textos';

interface PropsSemDataset {
  descricao?: string;
}

/** Estado vazio das etapas 2–8 quando se chega sem arquivo (URL direta ou sessão encerrada). */
export default function SemDataset({ descricao = T.semDatasetDescricao }: Readonly<PropsSemDataset>) {
  const navegar = useNavigate();
  return (
    <EstadoVazio
      icone="upload_file"
      titulo={T.semDatasetTitulo}
      descricao={descricao}
      acao={
        <Botao
          onClick={() => {
            void navegar(CAMINHOS.importar);
          }}
        >
          {T.irParaImportar}
        </Botao>
      }
    />
  );
}
```

`frontend/src/shared/sessao/ExigeDataset.tsx`:
```tsx
import type { ReactNode } from 'react';
import SemDataset from './SemDataset';
import { useSessao } from './useSessao';

interface PropsExigeDataset {
  children: (datasetId: string) => ReactNode;
}

/** Entrega o id do dataset da sessão ao conteúdo; sem dataset, mostra `SemDataset`. */
export default function ExigeDataset({ children }: Readonly<PropsExigeDataset>) {
  const sessao = useSessao();
  return sessao.dataset === null ? <SemDataset /> : <>{children(sessao.dataset.id)}</>;
}
```

`frontend/src/shared/ui/ConteudoConsulta.tsx`:
```tsx
import type { UseQueryResult } from '@tanstack/react-query';
import type { ReactNode } from 'react';
import EstadoCarregando from './EstadoCarregando';
import EstadoErro from './EstadoErro';

interface PropsConteudoConsulta<T> {
  consulta: UseQueryResult<T>;
  carregando: string;
  forma: 'cards' | 'tabela' | 'grafico';
  children: (dados: T) => ReactNode;
}

/** Estados obrigatórios (spec 15) de uma consulta: carregando → erro com "tentar de novo" → dados. */
export default function ConteudoConsulta<T>({
  consulta,
  carregando,
  forma,
  children,
}: Readonly<PropsConteudoConsulta<T>>) {
  if (consulta.isPending) return <EstadoCarregando mensagem={carregando} forma={forma} />;
  if (consulta.isError) {
    return (
      <EstadoErro
        erro={consulta.error}
        aoTentarDeNovo={() => {
          void consulta.refetch();
        }}
      />
    );
  }
  return <>{children(consulta.data)}</>;
}
```

Outras alterações no `app/`:
- `App.tsx`: `new QueryClient({ defaultOptions: { queries: { retry: deveTentarDeNovo } } })` (import de `../shared/api/classificarErro`).
- `etapas.ts`: troque os literais de `caminho` por `CAMINHOS.importar`, `CAMINHOS.variaveis` etc. (bivariada/gerador/detector continuam literais até existirem). O formato de `ETAPAS` não muda.

**Passo 4: rodar e ver passar** → 5 passed; testes do M1.1 continuam verdes.

**Passo 5: commit**
```bash
git add frontend/src/app frontend/src/shared/sessao frontend/src/shared/ui/ConteudoConsulta.*
git commit -m "feat(frontend): avisa uma vez a sessão expirada, adiciona ExigeDataset e padroniza estados de consulta"
```

---

### Tarefa 6: Importar — textos e mapeamentos puros

Rótulo da tela ↔ valor da API em funções puras, com testes. Os campos aparecem conforme os metadados (D53): `separador`, `decimal` e `codificacao` nulos (XLSX/JSON) somem; `aba` só aparece para XLSX.

**Arquivos:**
- Substituir: `frontend/src/features/importar/textos.ts` (provisório do M1.1; mantém `titulo` e `ajuda` como estão)
- Criar: `frontend/src/features/importar/opcoesLeitura.ts` (+ `.test.ts`)
- Criar: `frontend/src/features/importar/apresentacao.ts` (+ `.test.ts`)

**Passo 1: escrever os testes (falham)**

`frontend/src/features/importar/opcoesLeitura.test.ts`:
```ts
import { describe, expect, it } from 'vitest';
import { METADADOS_SAUDE } from '../../testes/fixtures/datasets';
import { aplicarCorrecao, descreverDeteccoes, montarFormulario } from './opcoesLeitura';

const XLSX = {
  ...METADADOS_SAUDE,
  formato: 'xlsx' as const,
  separador: null,
  decimal: null,
  codificacao: null,
  abas: ['Dados', 'Resumo'],
};

describe('descreverDeteccoes', () => {
  it('TXT mostra os 5 campos do design, com rótulo e motivo', () => {
    const campos = descreverDeteccoes(METADADOS_SAUDE, {});

    expect(campos.map((c) => c.campo)).toEqual(['formato', 'separador', 'decimal', 'codificacao', 'cabecalho']);
    expect(campos[1]).toMatchObject({
      rotulo: 'Separador',
      valor: ';',
      rotuloValor: 'Ponto e vírgula ( ; )',
      motivo: 'Aparece 7 vezes em todas as linhas.',
      corrigivel: true,
    });
    expect(campos[0]).toMatchObject({ rotuloValor: 'Texto (TXT)', corrigivel: false });
    expect(campos[4]).toMatchObject({ valor: 'sim', rotuloValor: 'Sim, 1ª linha' });
  });

  it('XLSX troca separador, decimal e codificação pela aba', () => {
    const campos = descreverDeteccoes(XLSX, { aba: 'Resumo' });

    expect(campos.map((c) => c.campo)).toEqual(['formato', 'aba', 'cabecalho']);
    expect(campos[1]?.valor).toBe('Resumo');
  });

  it('valor detectado fora da lista vira uma opção extra', () => {
    const [, separador] = descreverDeteccoes({ ...METADADOS_SAUDE, separador: '#' }, {});

    expect(separador?.opcoes.at(-1)).toEqual({ valor: '#', rotulo: 'Outro ( # )' });
  });
});

describe('aplicarCorrecao', () => {
  it('cabeçalho vira booleano e mantém as correções anteriores', () => {
    expect(aplicarCorrecao({ separador: ',' }, 'cabecalho', 'nao')).toEqual({
      separador: ',',
      tem_cabecalho: false,
    });
  });

  it('formato não é corrigível', () => {
    expect(aplicarCorrecao({}, 'formato', 'csv')).toEqual({});
  });
});

describe('montarFormulario', () => {
  it('envia o arquivo e só as opções definidas', () => {
    const arquivo = new File(['a;b'], 'dados.txt', { type: 'text/plain' });

    const formulario = montarFormulario(arquivo, { separador: ',', decimal: null, tem_cabecalho: false });

    expect(formulario.get('arquivo')).toBe(arquivo);
    expect(formulario.get('separador')).toBe(',');
    expect(formulario.has('decimal')).toBe(false);
    expect(formulario.get('tem_cabecalho')).toBe('false');
  });
});
```

`frontend/src/features/importar/apresentacao.test.ts`:
```ts
import { describe, expect, it } from 'vitest';
import { ErroApi } from '../../shared/api/cliente';
import { LINHAS_SAUDE } from '../../testes/fixtures/datasets';
import { colunasDaPrevia, descreverErroImportacao } from './apresentacao';

describe('colunasDaPrevia', () => {
  it('mantém a ordem do arquivo e alinha à direita colunas com números', () => {
    const colunas = colunasDaPrevia(LINHAS_SAUDE);

    expect(colunas.map((c) => c.nome)).toEqual(['id', 'sexo', 'idade', 'altura_m', 'peso_kg', 'escolaridade', 'cidade', 'satisfacao']);
    expect(colunas.filter((c) => c.numerica).map((c) => c.nome)).toEqual(['id', 'idade', 'altura_m', 'peso_kg']);
  });

  it('sem linhas, sem colunas', () => {
    expect(colunasDaPrevia([])).toEqual([]);
  });
});

describe('descreverErroImportacao', () => {
  it('erro de leitura (4xx) cita o arquivo no título', () => {
    const erro = new ErroApi(400, {
      codigo: 'FORMATO_NAO_SUPORTADO',
      mensagem: 'Este tipo de arquivo não é aceito. Use TXT, CSV, TSV, XLSX ou JSON.',
      sugestao: 'Salve como CSV e envie de novo.',
    });

    expect(descreverErroImportacao(erro, 'relatorio_final.pdf')).toEqual({
      titulo: 'Não conseguimos ler este arquivo: relatorio_final.pdf',
      texto: 'Este tipo de arquivo não é aceito. Use TXT, CSV, TSV, XLSX ou JSON. Salve como CSV e envie de novo.',
    });
  });

  it('sem conexão usa a mensagem como título', () => {
    const erro = new ErroApi(0, {
      codigo: 'SEM_CONEXAO',
      mensagem: 'Não conseguimos falar com o servidor.',
      sugestao: 'Verifique se o backend está rodando e tente novamente.',
    });

    expect(descreverErroImportacao(erro, 'a.csv').titulo).toBe('Não conseguimos falar com o servidor.');
  });
});
```

**Passo 2: rodar e ver falhar** → `npx vitest run src/features/importar` FAIL

**Passo 3: implementar**

`frontend/src/features/importar/textos.ts` (textos finais de telas.md §1; Dnn-50mb):
```ts
import { formatarInteiro } from '../../shared/lib/formatar';
import { contarColunas, contarLinhas } from '../../shared/lib/pluralizar';

export const NOME_EXEMPLO = 'pesquisa_saude.txt';

function linhasEColunas(linhas: number, colunas: number): string {
  return `${contarLinhas(linhas)} e ${contarColunas(colunas)}`;
}

export const TEXTOS_IMPORTAR = {
  titulo: 'Importar arquivo',
  ajuda: 'Envie sua tabela de dados. Nós descobrimos sozinhos como ela foi escrita, e você confere antes de seguir.',
  area: {
    titulo: 'Arraste e solte seu arquivo aqui',
    soltar: 'Solte para enviar',
    apoio: 'ou escolha no computador. Tamanho máximo: 50 MB.',
    botao: 'Escolher arquivo',
    rotuloEntrada: 'Arquivo de dados',
    rotuloFormatos: 'Formatos aceitos',
    rotuloProgresso: 'Envio em andamento',
    enviando: (nome: string) => `Enviando ${nome}…`,
  },
  formatosAceitos: ['.txt', '.csv', '.tsv', '.xlsx', '.json'],
  exemplo: { pergunta: 'Sem dados à mão?', link: `Abrir ${NOME_EXEMPLO} de exemplo` },
  erro: {
    titulo: (nome: string) => `Não conseguimos ler este arquivo: ${nome}`,
    usarExemplo: 'Usar o arquivo de exemplo',
  },
  deteccoes: {
    titulo: 'O que detectamos',
    lemos: (linhas: number, colunas: number) => `Lemos ${linhasEColunas(linhas, colunas)}.`,
    corrijaAbaixo: 'Se algo estiver diferente do seu arquivo, corrija abaixo.',
    semArquivo: 'Para corrigir a leitura, envie o arquivo de novo.',
  },
  campos: {
    formato: 'Formato',
    separador: 'Separador',
    decimal: 'Decimal',
    codificacao: 'Codificação',
    aba: 'Aba',
    cabecalho: 'Cabeçalho',
  },
  valorDetectado: (valor: string) => `Outro ( ${valor} )`,
  previa: {
    titulo: 'Prévia',
    subtitulo: (n: number, total: number) => `${formatarInteiro(n)} primeiras linhas de ${formatarInteiro(total)}`,
    legenda: 'Prévia dos dados importados',
    carregando: 'Carregando a prévia do arquivo…',
  },
  acoes: { lerDeNovo: 'Ler de novo', lendo: 'Lendo…', continuar: 'Continuar para Variáveis' },
  toast: {
    titulo: (linhas: number, colunas: number) => `Arquivo lido: ${linhasEColunas(linhas, colunas)}.`,
    descricao: 'As etapas 2 a 8 foram liberadas.',
  },
} as const;

export const ROTULOS_FORMATO = {
  txt: 'Texto (TXT)',
  csv: 'CSV',
  tsv: 'TSV (tabulação)',
  xlsx: 'Planilha (XLSX)',
  json: 'JSON',
} as const;

export const OPCOES_SEPARADOR = [
  { valor: ';', rotulo: 'Ponto e vírgula ( ; )' },
  { valor: ',', rotulo: 'Vírgula ( , )' },
  { valor: '\t', rotulo: 'Tabulação' },
  { valor: '|', rotulo: 'Barra vertical ( | )' },
  { valor: ' ', rotulo: 'Espaço' },
] as const;

export const OPCOES_DECIMAL = [
  { valor: ',', rotulo: 'Vírgula ( , )' },
  { valor: '.', rotulo: 'Ponto ( . )' },
] as const;

export const OPCOES_CODIFICACAO = [
  { valor: 'utf-8', rotulo: 'UTF-8' },
  { valor: 'utf-8-sig', rotulo: 'UTF-8 com BOM' },
  { valor: 'cp1252', rotulo: 'Windows-1252' },
  { valor: 'latin-1', rotulo: 'Latin-1 (ISO-8859-1)' },
] as const;

export const OPCOES_CABECALHO = [
  { valor: 'sim', rotulo: 'Sim, 1ª linha' },
  { valor: 'nao', rotulo: 'Não, só dados' },
] as const;
```
> Confira com o M1.2 o valor que a API devolve para "espaço múltiplo" (spec 01). Se não for `' '`, ajuste `OPCOES_SEPARADOR`; um valor desconhecido aparece como "Outro ( … )" sem quebrar a tela.

`frontend/src/features/importar/opcoesLeitura.ts`:
```ts
/** Detecções da leitura (MetadadosLeitura) ↔ campos da tela 1a ↔ formulário do POST /datasets. */
import type { components, paths } from '../../shared/api/schema';
import {
  OPCOES_CABECALHO,
  OPCOES_CODIFICACAO,
  OPCOES_DECIMAL,
  OPCOES_SEPARADOR,
  ROTULOS_FORMATO,
  TEXTOS_IMPORTAR as T,
} from './textos';

export type MetadadosLeitura = components['schemas']['MetadadosLeitura'];
type CorpoImportacao = NonNullable<
  paths['/api/datasets']['post']['requestBody']
>['content']['multipart/form-data'];
/** Opções de leitura que sobrescrevem a detecção (separador, decimal, codificacao, aba, tem_cabecalho). */
export type OpcoesLeitura = Partial<Omit<CorpoImportacao, 'arquivo'>>;

export type CampoDeteccao = keyof typeof T.campos;

export interface OpcaoLeitura {
  valor: string;
  rotulo: string;
}

export interface DescricaoCampo {
  campo: CampoDeteccao;
  rotulo: string;
  valor: string;
  rotuloValor: string;
  opcoes: readonly OpcaoLeitura[];
  motivo: string;
  corrigivel: boolean;
}

type Construtor = (meta: MetadadosLeitura, opcoes: OpcoesLeitura) => DescricaoCampo | null;

const ORDEM_CAMPOS: readonly CampoDeteccao[] = ['formato', 'separador', 'decimal', 'codificacao', 'aba', 'cabecalho'];

function comDetectado(lista: readonly OpcaoLeitura[], valor: string): readonly OpcaoLeitura[] {
  return lista.some((o) => o.valor === valor) ? lista : [...lista, { valor, rotulo: T.valorDetectado(valor) }];
}

function descrever(
  campo: CampoDeteccao,
  valor: string | null | undefined,
  lista: readonly OpcaoLeitura[],
  meta: MetadadosLeitura,
): DescricaoCampo | null {
  if (valor === null || valor === undefined) return null;
  const opcoes = comDetectado(lista, valor);
  return {
    campo,
    rotulo: T.campos[campo],
    valor,
    rotuloValor: opcoes.find((o) => o.valor === valor)?.rotulo ?? valor,
    opcoes,
    motivo: meta.motivos[campo] ?? '',
    corrigivel: campo !== 'formato',
  };
}

function valorCabecalho(tem: boolean | null): string | null {
  if (tem === null) return null;
  return tem ? 'sim' : 'nao';
}

function descreverAba(meta: MetadadosLeitura, opcoes: OpcoesLeitura): DescricaoCampo | null {
  const lista = meta.abas.map((aba) => ({ valor: aba, rotulo: aba }));
  return descrever('aba', opcoes.aba ?? meta.abas[0], lista, meta);
}

const CONSTRUTORES: Record<CampoDeteccao, Construtor> = {
  formato: (m) => descrever('formato', m.formato, [{ valor: m.formato, rotulo: ROTULOS_FORMATO[m.formato] }], m),
  separador: (m) => descrever('separador', m.separador, OPCOES_SEPARADOR, m),
  decimal: (m) => descrever('decimal', m.decimal, OPCOES_DECIMAL, m),
  codificacao: (m) => descrever('codificacao', m.codificacao, OPCOES_CODIFICACAO, m),
  aba: descreverAba,
  cabecalho: (m) => descrever('cabecalho', valorCabecalho(m.tem_cabecalho), OPCOES_CABECALHO, m),
};

export function descreverDeteccoes(meta: MetadadosLeitura, opcoes: OpcoesLeitura): DescricaoCampo[] {
  return ORDEM_CAMPOS.map((campo) => CONSTRUTORES[campo](meta, opcoes)).filter(
    (descricao): descricao is DescricaoCampo => descricao !== null,
  );
}

/** Acumula a correção escolhida no Select; a releitura manda todas as correções juntas. */
export function aplicarCorrecao(opcoes: OpcoesLeitura, campo: CampoDeteccao, valor: string): OpcoesLeitura {
  if (campo === 'formato') return opcoes;
  if (campo === 'cabecalho') return { ...opcoes, tem_cabecalho: valor === 'sim' };
  return { ...opcoes, [campo]: valor };
}

export function montarFormulario(arquivo: File, opcoes: OpcoesLeitura): FormData {
  const formulario = new FormData();
  formulario.append('arquivo', arquivo);
  for (const [chave, valor] of Object.entries(opcoes)) {
    if (valor !== null && valor !== undefined) formulario.append(chave, String(valor));
  }
  return formulario;
}
```
> Se o `tsc` reclamar de `paths['/api/datasets']['post']['requestBody']`, confira no `schema.d.ts` o nome do schema do corpo multipart (`Body_…`) e use `components['schemas']['Body_…']` no lugar — é o mesmo tipo.

`frontend/src/features/importar/apresentacao.ts`:
```ts
import { ehErroDeEntrada } from '../../shared/api/classificarErro';
import type { LinhaDados } from '../../shared/api/dataset';
import { textoDoErro } from '../../shared/api/erros';
import { TEXTOS_IMPORTAR as T } from './textos';

export interface ColunaPrevia {
  nome: string;
  numerica: boolean;
}

/** Ordem das colunas = ordem das chaves da 1ª linha (a API preserva a ordem do arquivo). */
export function colunasDaPrevia(linhas: readonly LinhaDados[]): ColunaPrevia[] {
  const primeira = linhas[0];
  if (primeira === undefined) return [];
  return Object.keys(primeira.valores).map((nome) => ({
    nome,
    numerica: linhas.some((linha) => typeof linha.valores[nome] === 'number'),
  }));
}

export interface ErroImportacao {
  titulo: string;
  texto: string;
}

/** Banner 1c: erro do arquivo cita o nome; falha de rede/servidor usa a mensagem do cliente HTTP. */
export function descreverErroImportacao(erro: unknown, nomeArquivo: string): ErroImportacao {
  const { mensagem, sugestao } = textoDoErro(erro);
  if (ehErroDeEntrada(erro)) {
    return { titulo: T.erro.titulo(nomeArquivo), texto: `${mensagem} ${sugestao}`.trim() };
  }
  return { titulo: mensagem, texto: sugestao };
}
```

**Passo 4: rodar e ver passar** → 9 passed.

**Passo 5: commit**
```bash
git add frontend/src/features/importar
git commit -m "feat(importar): mapeia detecções da leitura para os campos da tela"
```

---

### Tarefa 7: Importar — `api.ts` e `useImportacao`

**Arquivos:**
- Criar: `frontend/src/features/importar/api.ts`
- Criar: `frontend/src/features/importar/hooks/useImportacao.ts` (+ `useImportacao.test.tsx`)

**Passo 1: escrever o teste (falha)**

`frontend/src/features/importar/hooks/useImportacao.test.tsx`:
```tsx
import { act, screen, waitFor } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { chavesDataset } from '../../../shared/api/dataset';
import { useSessao } from '../../../shared/sessao/useSessao';
import { chamadasPara, simularApi } from '../../../testes/api';
import { COLUNAS_SAUDE, DATASET_CRIADO, ID_DATASET } from '../../../testes/fixtures/datasets';
import { renderizarHook } from '../../../testes/renderizar';
import { useImportacao } from './useImportacao';

const ARQUIVO = new File(['id;sexo'], 'pesquisa_saude.txt', { type: 'text/plain' });

function usarTudo() {
  return { importacao: useImportacao(), sessao: useSessao() };
}

describe('useImportacao', () => {
  it('envia o arquivo, define a sessão, guarda as colunas no cache e avisa', async () => {
    const falso = simularApi([{ metodo: 'POST', caminho: '/datasets', status: 201, corpo: DATASET_CRIADO }]);
    const { result, cliente } = renderizarHook(usarTudo);

    act(() => {
      result.current.importacao.enviar(ARQUIVO);
    });

    await waitFor(() => {
      expect(result.current.sessao.dataset).toEqual({ id: ID_DATASET, nomeArquivo: 'pesquisa_saude.txt' });
    });
    expect(cliente.getQueryData(chavesDataset.colunas(ID_DATASET))).toEqual(COLUNAS_SAUDE);
    expect(await screen.findByText('Arquivo lido: 230 linhas e 8 colunas.')).toBeInTheDocument();
    const corpo = chamadasPara(falso, 'POST', '/datasets')[0]?.corpo as FormData;
    expect(corpo.get('arquivo')).toBe(ARQUIVO);
  });

  it('corrigir relê o mesmo arquivo com a correção acumulada', async () => {
    const falso = simularApi([{ metodo: 'POST', caminho: '/datasets', status: 201, corpo: DATASET_CRIADO }]);
    const { result } = renderizarHook(usarTudo);
    act(() => {
      result.current.importacao.enviar(ARQUIVO);
    });
    await waitFor(() => {
      expect(result.current.importacao.corrigir).not.toBeNull();
    });

    act(() => {
      result.current.importacao.corrigir?.('separador', ',');
    });

    await waitFor(() => {
      expect(chamadasPara(falso, 'POST', '/datasets')).toHaveLength(2);
    });
    const segunda = chamadasPara(falso, 'POST', '/datasets')[1]?.corpo as FormData;
    expect(segunda.get('arquivo')).toBe(ARQUIVO);
    expect(segunda.get('separador')).toBe(',');
  });

  it('expõe o erro e o nome do arquivo para o banner', async () => {
    simularApi([
      { metodo: 'POST', caminho: '/datasets', status: 400, corpo: { codigo: 'ARQUIVO_VAZIO', mensagem: 'O arquivo está vazio.', sugestao: 'Escolha outro arquivo.' } },
    ]);
    const { result } = renderizarHook(usarTudo);

    act(() => {
      result.current.importacao.enviar(ARQUIVO);
    });

    await waitFor(() => {
      expect(result.current.importacao.erro?.message).toBe('O arquivo está vazio.');
    });
    expect(result.current.importacao.nomeArquivo).toBe('pesquisa_saude.txt');
    expect(result.current.sessao.dataset).toBeNull();
  });

  it('o exemplo não pode ser corrigido, mas pode ser lido de novo', async () => {
    simularApi([{ metodo: 'POST', caminho: '/datasets/exemplo', status: 201, corpo: DATASET_CRIADO }]);
    const { result } = renderizarHook(usarTudo);

    act(() => {
      result.current.importacao.abrirExemplo();
    });

    await waitFor(() => {
      expect(result.current.sessao.dataset).not.toBeNull();
    });
    expect(result.current.importacao.corrigir).toBeNull();
    expect(result.current.importacao.lerDeNovo).not.toBeNull();
  });
});
```

**Passo 2: rodar e ver falhar** → FAIL

**Passo 3: implementar**

`frontend/src/features/importar/api.ts`:
```ts
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { requisitar } from '../../shared/api/cliente';
import { chavesDataset } from '../../shared/api/dataset';
import type { components } from '../../shared/api/schema';
import { useSessao } from '../../shared/sessao/useSessao';
import { useToast } from '../../shared/ui/useToast';
import { montarFormulario, type OpcoesLeitura } from './opcoesLeitura';
import { TEXTOS_IMPORTAR as T } from './textos';

export type DatasetCriado = components['schemas']['DatasetCriado'];

export interface PedidoImportacao {
  arquivo: File;
  opcoes: OpcoesLeitura;
}

/** Leituras em fila: trocar dois Selects rápido não deixa a resposta antiga vencer a nova. */
const ESCOPO_IMPORTACAO = { id: 'importacao' };

function enviarArquivo({ arquivo, opcoes }: PedidoImportacao): Promise<DatasetCriado> {
  return requisitar<DatasetCriado>('/datasets', { method: 'POST', body: montarFormulario(arquivo, opcoes) });
}

function abrirExemplo(): Promise<DatasetCriado> {
  return requisitar<DatasetCriado>('/datasets/exemplo', { method: 'POST' });
}

/** Sucesso de qualquer leitura: sessão nova, etapa 1 visitada, colunas no cache e toast. */
function useConcluirImportacao(): (criado: DatasetCriado) => void {
  const cliente = useQueryClient();
  const sessao = useSessao();
  const toast = useToast();
  return (criado) => {
    cliente.setQueryData(chavesDataset.colunas(criado.dataset_id), criado.colunas);
    sessao.definirDataset({ id: criado.dataset_id, nomeArquivo: criado.nome_arquivo });
    sessao.marcarVisitada(1);
    toast.mostrar({
      tipo: 'sucesso',
      titulo: T.toast.titulo(criado.metadados.n_linhas, criado.metadados.n_colunas),
      descricao: T.toast.descricao,
    });
  };
}

export function useImportarArquivo() {
  const concluir = useConcluirImportacao();
  return useMutation({ mutationFn: enviarArquivo, onSuccess: concluir, scope: ESCOPO_IMPORTACAO });
}

export function useAbrirExemplo() {
  const concluir = useConcluirImportacao();
  return useMutation({ mutationFn: abrirExemplo, onSuccess: concluir, scope: ESCOPO_IMPORTACAO });
}
```

`frontend/src/features/importar/hooks/useImportacao.ts`:
```ts
import { useState } from 'react';
import { useAbrirExemplo, useImportarArquivo } from '../api';
import { aplicarCorrecao, type CampoDeteccao, type OpcoesLeitura } from '../opcoesLeitura';
import { NOME_EXEMPLO } from '../textos';

type Origem = { tipo: 'arquivo'; arquivo: File; opcoes: OpcoesLeitura } | { tipo: 'exemplo' };

export interface Importacao {
  nomeArquivo: string;
  enviando: boolean;
  erro: Error | null;
  opcoes: OpcoesLeitura;
  enviar: (arquivo: File) => void;
  abrirExemplo: () => void;
  /** null quando não há arquivo na memória da página (exemplo ou página recarregada) — Dnn-reler. */
  corrigir: ((campo: CampoDeteccao, valor: string) => void) | null;
  lerDeNovo: (() => void) | null;
}

/** Fluxo da tela 1: enviar, abrir exemplo, corrigir a leitura (relê o mesmo File) e "Ler de novo". */
export function useImportacao(): Importacao {
  const [origem, setOrigem] = useState<Origem | null>(null);
  const importar = useImportarArquivo();
  const exemplo = useAbrirExemplo();

  function lerArquivo(arquivo: File, opcoes: OpcoesLeitura): void {
    exemplo.reset();
    setOrigem({ tipo: 'arquivo', arquivo, opcoes });
    importar.mutate({ arquivo, opcoes });
  }

  function abrirExemplo(): void {
    importar.reset();
    setOrigem({ tipo: 'exemplo' });
    exemplo.mutate();
  }

  const atual = origem?.tipo === 'arquivo' ? origem : null;

  return {
    nomeArquivo: atual === null ? NOME_EXEMPLO : atual.arquivo.name,
    enviando: importar.isPending || exemplo.isPending,
    erro: importar.error ?? exemplo.error,
    opcoes: atual === null ? {} : atual.opcoes,
    enviar: (arquivo) => {
      lerArquivo(arquivo, {});
    },
    abrirExemplo,
    corrigir:
      atual === null
        ? null
        : (campo, valor) => {
            lerArquivo(atual.arquivo, aplicarCorrecao(atual.opcoes, campo, valor));
          },
    lerDeNovo:
      origem === null
        ? null
        : () => {
            if (atual === null) abrirExemplo();
            else lerArquivo(atual.arquivo, {});
          },
  };
}
```

**Passo 4: rodar e ver passar** → 4 passed.

**Passo 5: commit**
```bash
git add frontend/src/features/importar
git commit -m "feat(importar): envia arquivo ou exemplo e relê com as correções"
```

---

### Tarefa 8: Importar — `AreaUpload`

Estados normal / arrastando / enviando / erro (componentes.md §AreaUpload). Acessível por teclado: o foco vai para o botão "Escolher arquivo", que abre o `<input type="file">` escondido.

**Arquivos:**
- Criar: `frontend/src/features/importar/components/AreaUpload.tsx`, `AreaUpload.module.css` (+ `AreaUpload.test.tsx`)

**Passo 1: escrever o teste (falha)**
```tsx
import { fireEvent, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import AreaUpload from './AreaUpload';

const ARQUIVO = new File(['a;b'], 'pesquisa_saude.txt', { type: 'text/plain' });
const TITULO = 'Arraste e solte seu arquivo aqui';

function renderizar(props: Partial<Parameters<typeof AreaUpload>[0]> = {}) {
  const aoEscolher = vi.fn();
  render(<AreaUpload enviando={false} nomeEnviando="pesquisa_saude.txt" comErro={false} aoEscolher={aoEscolher} {...props} />);
  return { aoEscolher, area: screen.getByText(TITULO).closest('[data-estado]') };
}

describe('AreaUpload', () => {
  it('mostra o limite de 50 MB e os formatos aceitos', () => {
    renderizar();

    expect(screen.getByText('ou escolha no computador. Tamanho máximo: 50 MB.')).toBeInTheDocument();
    expect(screen.getAllByRole('listitem').map((item) => item.textContent)).toEqual(['.txt', '.csv', '.tsv', '.xlsx', '.json']);
  });

  it('entrega o arquivo escolhido no seletor', async () => {
    const { aoEscolher } = renderizar();

    await userEvent.upload(screen.getByLabelText('Arquivo de dados'), ARQUIVO);

    expect(aoEscolher).toHaveBeenCalledWith(ARQUIVO);
  });

  it('pelo teclado, Enter no botão abre o seletor de arquivo', async () => {
    const clique = vi.spyOn(HTMLInputElement.prototype, 'click');
    renderizar();

    await userEvent.tab();
    await userEvent.keyboard('{Enter}');

    expect(screen.getByRole('button', { name: /Escolher arquivo/ })).toHaveFocus();
    expect(clique).toHaveBeenCalled();
  });

  it('arrastar por cima muda o texto e soltar entrega o arquivo', () => {
    const { aoEscolher, area } = renderizar();
    if (area === null) throw new Error('área não encontrada');

    fireEvent.dragOver(area);
    expect(area).toHaveAttribute('data-estado', 'arrastando');
    expect(screen.getByText('Solte para enviar')).toBeInTheDocument();

    fireEvent.drop(area, { dataTransfer: { files: [ARQUIVO] } });
    expect(aoEscolher).toHaveBeenCalledWith(ARQUIVO);
  });

  it('enviando mostra progresso e desabilita o botão', () => {
    renderizar({ enviando: true });

    expect(screen.getByRole('progressbar', { name: 'Envio em andamento' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Enviando pesquisa_saude.txt/ })).toBeDisabled();
  });

  it('erro deixa a área no estado de erro', () => {
    const { area } = renderizar({ comErro: true });
    expect(area).toHaveAttribute('data-estado', 'erro');
  });
});
```

**Passo 2: rodar e ver falhar** → FAIL

**Passo 3: implementar `AreaUpload.tsx`**
```tsx
import { type ChangeEvent, type DragEvent, useId, useRef, useState } from 'react';
import Botao from '../../../shared/ui/Botao';
import Icone from '../../../shared/ui/Icone';
import { TEXTOS_IMPORTAR as T } from '../textos';
import estilos from './AreaUpload.module.css';

interface PropsAreaUpload {
  enviando: boolean;
  nomeEnviando: string;
  comErro: boolean;
  aoEscolher: (arquivo: File) => void;
}

type EstadoArea = 'normal' | 'arrastando' | 'enviando' | 'erro';

function estadoDaArea(situacao: { arrastando: boolean; enviando: boolean; comErro: boolean }): EstadoArea {
  if (situacao.enviando) return 'enviando';
  if (situacao.arrastando) return 'arrastando';
  return situacao.comErro ? 'erro' : 'normal';
}

const FORMATOS = T.formatosAceitos.map((formato) => (
  <li key={formato} className={estilos.formato}>
    {formato}
  </li>
));

export default function AreaUpload({ enviando, nomeEnviando, comErro, aoEscolher }: Readonly<PropsAreaUpload>) {
  const entrada = useRef<HTMLInputElement>(null);
  const idApoio = useId();
  const [arrastando, setArrastando] = useState(false);

  function aoArrastarPorCima(evento: DragEvent<HTMLDivElement>): void {
    evento.preventDefault();
    setArrastando(true);
  }

  function aoSair(evento: DragEvent<HTMLDivElement>): void {
    const destino = evento.relatedTarget;
    if (destino instanceof Node && evento.currentTarget.contains(destino)) return;
    setArrastando(false);
  }

  function aoSoltar(evento: DragEvent<HTMLDivElement>): void {
    evento.preventDefault();
    setArrastando(false);
    const arquivo = evento.dataTransfer.files[0];
    if (arquivo !== undefined && !enviando) aoEscolher(arquivo);
  }

  function aoMudarEntrada(evento: ChangeEvent<HTMLInputElement>): void {
    const arquivo = evento.target.files?.[0];
    evento.target.value = ''; // permite escolher o mesmo arquivo de novo
    if (arquivo !== undefined) aoEscolher(arquivo);
  }

  return (
    <div
      className={estilos.area}
      data-estado={estadoDaArea({ arrastando, enviando, comErro })}
      onDragOver={aoArrastarPorCima}
      onDragLeave={aoSair}
      onDrop={aoSoltar}
    >
      <span className={estilos.circulo}>
        <Icone nome="upload_file" tamanho={36} />
      </span>
      <div className={estilos.textos}>
        <p className={estilos.titulo}>{arrastando ? T.area.soltar : T.area.titulo}</p>
        <p className={estilos.apoio} id={idApoio}>
          {T.area.apoio}
        </p>
      </div>
      {enviando ? <div role="progressbar" aria-label={T.area.rotuloProgresso} className={estilos.progresso} /> : null}
      <Botao
        tamanho="lg"
        icone="folder_open"
        carregando={enviando}
        textoCarregando={T.area.enviando(nomeEnviando)}
        aria-describedby={idApoio}
        onClick={() => {
          entrada.current?.click();
        }}
      >
        {T.area.botao}
      </Botao>
      <input
        ref={entrada}
        className={estilos.entrada}
        type="file"
        accept={T.formatosAceitos.join(',')}
        aria-label={T.area.rotuloEntrada}
        tabIndex={-1}
        onChange={aoMudarEntrada}
      />
      <ul className={estilos.formatos} aria-label={T.area.rotuloFormatos}>
        {FORMATOS}
      </ul>
    </div>
  );
}
```
(Se passar de 50 linhas no lint `max-lines-per-function`, extraia o `<input>` + `Botao` para um subcomponente `SeletorArquivo` no mesmo arquivo.)

`AreaUpload.module.css` (Tela 1, estado 1b):

| Seletor | Propriedades |
|---|---|
| `.area` | `display:flex; flex-direction:column; align-items:center; justify-content:center; gap:16px; min-height:400px; padding:48px; border:2px dashed var(--cor-borda-forte); border-radius:16px; background:var(--cor-superficie); text-align:center; transition:border-color 120ms, background-color 120ms` |
| `.area[data-estado='arrastando']` | `border-color:var(--cor-primaria); background:var(--cor-primaria-suave)` |
| `.area[data-estado='erro']` | `border-color:var(--cor-erro); background:var(--cor-erro-suave)` |
| `.circulo` | `display:grid; place-items:center; width:72px; height:72px; border-radius:50%; background:var(--cor-primaria-suave); color:var(--cor-primaria)` |
| `.textos` | `display:flex; flex-direction:column; gap:6px` |
| `.titulo` | `margin:0; font-size:20px; font-weight:600` |
| `.apoio` | `margin:0; font-size:15px; color:var(--cor-texto-2)` |
| `.progresso` | `width:min(320px, 100%); height:6px; border-radius:999px; background:var(--cor-superficie-2); overflow:hidden` |
| `.progresso::after` | `content:''; display:block; width:40%; height:100%; background:var(--cor-primaria); animation:deslizar 1.2s ease-in-out infinite` |
| `@keyframes deslizar` | `from { transform:translateX(-100%) } to { transform:translateX(250%) }` |
| `@media (prefers-reduced-motion: reduce)` › `.progresso::after` | `animation:none; width:100%` |
| `.entrada` | escondido visualmente: `position:absolute; width:1px; height:1px; overflow:hidden; clip-path:inset(50%); white-space:nowrap` |
| `.formatos` | `display:flex; flex-wrap:wrap; justify-content:center; gap:8px; margin:8px 0 0; padding:0; list-style:none` |
| `.formato` | `padding:4px 10px; border:1px solid var(--cor-borda); border-radius:var(--raio-sm); background:var(--cor-superficie-2); font:500 13px var(--fonte-mono)` |

**Passo 4: rodar e ver passar** → 6 passed. **Passo 5: commit**
```bash
git add frontend/src/features/importar/components/AreaUpload.*
git commit -m "feat(importar): adiciona área de envio com arrastar, teclado e estados"
```

---

### Tarefa 9: Importar — detecções, prévia e banner de erro

**Arquivos:**
- Criar em `frontend/src/features/importar/components/`: `CardDeteccoes.tsx` + `.module.css` + `.test.tsx`; `PreviaDados.tsx` + `.test.tsx`; `BannerErroImportacao.tsx` + `.test.tsx`; `BotaoLink.tsx` + `.module.css`

**Passo 1: escrever os testes (falham)**

`CardDeteccoes.test.tsx`:
```tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import { METADADOS_SAUDE } from '../../../testes/fixtures/datasets';
import CardDeteccoes from './CardDeteccoes';

describe('CardDeteccoes', () => {
  it('com o arquivo na memória, cada detecção é um Select com o motivo', async () => {
    const aoCorrigir = vi.fn();
    render(<CardDeteccoes metadados={METADADOS_SAUDE} opcoes={{}} aoCorrigir={aoCorrigir} />);

    expect(screen.getByText('Lemos 230 linhas e 8 colunas. Se algo estiver diferente do seu arquivo, corrija abaixo.')).toBeInTheDocument();
    const separador = screen.getByRole('combobox', { name: 'Separador' });
    expect(separador).toHaveValue(';');
    expect(screen.getByText('Aparece 7 vezes em todas as linhas.')).toBeInTheDocument();

    await userEvent.selectOptions(separador, ',');
    expect(aoCorrigir).toHaveBeenCalledWith('separador', ',');
  });

  it('formato é sempre só leitura', () => {
    render(<CardDeteccoes metadados={METADADOS_SAUDE} opcoes={{}} aoCorrigir={vi.fn()} />);

    expect(screen.queryByRole('combobox', { name: 'Formato' })).not.toBeInTheDocument();
    expect(screen.getByText('Texto (TXT)')).toBeInTheDocument();
  });

  it('sem o arquivo, mostra os valores e explica como corrigir', () => {
    render(<CardDeteccoes metadados={METADADOS_SAUDE} opcoes={{}} aoCorrigir={null} />);

    expect(screen.queryAllByRole('combobox')).toHaveLength(0);
    expect(screen.getByText('Ponto e vírgula ( ; )')).toBeInTheDocument();
    expect(screen.getByText(/Para corrigir a leitura, envie o arquivo de novo\./)).toBeInTheDocument();
  });
});
```

`PreviaDados.test.tsx`:
```tsx
import { render, screen, within } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { LINHAS_SAUDE } from '../../../testes/fixtures/datasets';
import PreviaDados from './PreviaDados';

describe('PreviaDados', () => {
  it('mostra as colunas do arquivo, números em pt-BR e faltante como —', () => {
    render(<PreviaDados linhas={LINHAS_SAUDE} totalLinhas={230} />);

    expect(screen.getByText('3 primeiras linhas de 230')).toBeInTheDocument();
    const tabela = screen.getByRole('table', { name: 'Prévia dos dados importados' });
    expect(within(tabela).getAllByRole('columnheader').map((c) => c.textContent)).toEqual([
      'id', 'sexo', 'idade', 'altura_m', 'peso_kg', 'escolaridade', 'cidade', 'satisfacao',
    ]);
    expect(within(tabela).getByText('1,62')).toBeInTheDocument();
    expect(within(tabela).getByText('—')).toBeInTheDocument();
  });
});
```

`BannerErroImportacao.test.tsx`:
```tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import { ErroApi } from '../../../shared/api/cliente';
import BannerErroImportacao from './BannerErroImportacao';

describe('BannerErroImportacao', () => {
  it('cita o arquivo, mostra a mensagem da API e oferece o exemplo', async () => {
    const aoUsarExemplo = vi.fn();
    const erro = new ErroApi(400, {
      codigo: 'FORMATO_NAO_SUPORTADO',
      mensagem: 'Este tipo de arquivo não é aceito. Use TXT, CSV, TSV, XLSX ou JSON.',
      sugestao: 'Salve como CSV e envie de novo.',
    });
    render(<BannerErroImportacao erro={erro} nomeArquivo="relatorio_final.pdf" aoUsarExemplo={aoUsarExemplo} />);

    expect(screen.getByText('Não conseguimos ler este arquivo: relatorio_final.pdf')).toBeInTheDocument();
    expect(screen.getByText(/Salve como CSV e envie de novo\./)).toBeInTheDocument();
    await userEvent.click(screen.getByRole('button', { name: 'Usar o arquivo de exemplo' }));
    expect(aoUsarExemplo).toHaveBeenCalled();
  });
});
```

**Passo 2: rodar e ver falhar** → FAIL

**Passo 3: implementar**

`BotaoLink.tsx` (ação com cara de link; é botão porque dispara um POST):
```tsx
import type { ButtonHTMLAttributes } from 'react';
import estilos from './BotaoLink.module.css';

type PropsBotaoLink = Omit<ButtonHTMLAttributes<HTMLButtonElement>, 'className' | 'type'>;

export default function BotaoLink(props: Readonly<PropsBotaoLink>) {
  return <button type="button" className={estilos.link} {...props} />;
}
```

| Seletor (`BotaoLink.module.css`) | Propriedades |
|---|---|
| `.link` | `padding:0; border:0; background:none; font:inherit; font-weight:500; color:var(--cor-primaria); text-decoration:underline; cursor:pointer` |
| `.link:hover` | `color:var(--cor-primaria-hover)` |
| `.link:focus-visible` | `outline:2px solid var(--cor-foco); outline-offset:2px; border-radius:var(--raio-xs)` |

`CardDeteccoes.tsx`:
```tsx
import Card from '../../../shared/ui/Card';
import Icone from '../../../shared/ui/Icone';
import Select from '../../../shared/ui/Select';
import {
  type CampoDeteccao as Campo,
  descreverDeteccoes,
  type DescricaoCampo,
  type MetadadosLeitura,
  type OpcoesLeitura,
} from '../opcoesLeitura';
import { TEXTOS_IMPORTAR as T } from '../textos';
import estilos from './CardDeteccoes.module.css';

type AoCorrigir = ((campo: Campo, valor: string) => void) | null;

interface PropsCardDeteccoes {
  metadados: MetadadosLeitura;
  opcoes: OpcoesLeitura;
  aoCorrigir: AoCorrigir;
}

function CampoDeteccao({ descricao, aoCorrigir }: Readonly<{ descricao: DescricaoCampo; aoCorrigir: AoCorrigir }>) {
  if (aoCorrigir === null || !descricao.corrigivel) {
    return (
      <div className={estilos.campo}>
        <span className={estilos.rotulo}>{descricao.rotulo}</span>
        <span className={estilos.valorFixo}>{descricao.rotuloValor}</span>
        <span className={estilos.motivo}>{descricao.motivo}</span>
      </div>
    );
  }
  return (
    <div className={estilos.campo}>
      <Select
        rotulo={descricao.rotulo}
        valor={descricao.valor}
        opcoes={descricao.opcoes}
        ajuda={descricao.motivo}
        aoMudar={(valor) => {
          aoCorrigir(descricao.campo, valor);
        }}
      />
    </div>
  );
}

/** Card "O que detectamos" (1a): mudar um Select relê o arquivo. */
export default function CardDeteccoes({ metadados, opcoes, aoCorrigir }: Readonly<PropsCardDeteccoes>) {
  const campos = descreverDeteccoes(metadados, opcoes);
  const complemento = aoCorrigir === null ? T.deteccoes.semArquivo : T.deteccoes.corrijaAbaixo;
  const titulo = (
    <span className={estilos.titulo}>
      <span className={estilos.icone}>
        <Icone nome="check_circle" preenchido tamanho={22} />
      </span>
      {T.deteccoes.titulo}
    </span>
  );
  return (
    <Card titulo={titulo} subtitulo={`${T.deteccoes.lemos(metadados.n_linhas, metadados.n_colunas)} ${complemento}`}>
      <div className={estilos.grade} style={{ gridTemplateColumns: `repeat(${String(campos.length)}, minmax(0, 1fr))` }}>
        {campos.map((descricao) => (
          <CampoDeteccao key={descricao.campo} descricao={descricao} aoCorrigir={aoCorrigir} />
        ))}
      </div>
    </Card>
  );
}
```

`CardDeteccoes.module.css` (o Card do M1.1 já dá borda, raio e sombra; se o padding do corpo do Card não for 0, use a variante `preenchimento="nenhum"` que o plano do M1.1 prevê):

| Seletor | Propriedades |
|---|---|
| `.titulo` | `display:flex; align-items:center; gap:12px` |
| `.icone` | `display:inline-flex; color:var(--cor-sucesso)` |
| `.grade` | `display:grid; border-top:1px solid var(--cor-borda)` |
| `.campo` | `display:flex; flex-direction:column; gap:8px; padding:18px 24px; border-right:1px solid var(--cor-borda); min-width:0` |
| `.campo:last-child` | `border-right:0` |
| `.rotulo` | `font-size:13px; font-weight:500; color:var(--cor-texto-2)` |
| `.valorFixo` | `display:flex; align-items:center; height:40px; font-size:14px; font-weight:500` |
| `.motivo` | `font-size:12.5px; line-height:1.4; color:var(--cor-texto-2)` |
| `@media (max-width:1279px)` › `.grade` | `grid-template-columns:repeat(2, minmax(0, 1fr)) !important` (o `style` inline perde para o `!important`; única exceção, para o responsivo) |

`PreviaDados.tsx`:
```tsx
import type { LinhaDados } from '../../../shared/api/dataset';
import { formatarCelula } from '../../../shared/lib/formatarCelula';
import Card from '../../../shared/ui/Card';
import Tabela, { type ColunaTabela } from '../../../shared/ui/Tabela';
import { colunasDaPrevia } from '../apresentacao';
import { TEXTOS_IMPORTAR as T } from '../textos';

const ALTURA_MAXIMA = 520;

interface PropsPreviaDados {
  linhas: readonly LinhaDados[];
  totalLinhas: number;
}

export default function PreviaDados({ linhas, totalLinhas }: Readonly<PropsPreviaDados>) {
  const colunas = colunasDaPrevia(linhas).map(
    (coluna): ColunaTabela<LinhaDados> => ({
      id: coluna.nome,
      titulo: coluna.nome,
      celula: (linha) => formatarCelula(linha.valores[coluna.nome]),
      alinhamento: coluna.numerica ? 'direita' : 'esquerda',
    }),
  );
  return (
    <Card titulo={T.previa.titulo} subtitulo={T.previa.subtitulo(linhas.length, totalLinhas)}>
      <Tabela
        legenda={T.previa.legenda}
        colunas={colunas}
        linhas={linhas}
        chave={(linha) => String(linha.linha)}
        alturaMaxima={ALTURA_MAXIMA}
      />
    </Card>
  );
}
```

`BannerErroImportacao.tsx`:
```tsx
import Banner from '../../../shared/ui/Banner';
import { descreverErroImportacao } from '../apresentacao';
import { TEXTOS_IMPORTAR as T } from '../textos';
import BotaoLink from './BotaoLink';

interface PropsBannerErroImportacao {
  erro: unknown;
  nomeArquivo: string;
  aoUsarExemplo: () => void;
}

/** Erro 1c: mensagem e sugestão vêm da API; o link "Como exportar para CSV" fica fora (sem destino). */
export default function BannerErroImportacao({ erro, nomeArquivo, aoUsarExemplo }: Readonly<PropsBannerErroImportacao>) {
  const { titulo, texto } = descreverErroImportacao(erro, nomeArquivo);
  return (
    <Banner variante="erro" titulo={titulo} acoes={<BotaoLink onClick={aoUsarExemplo}>{T.erro.usarExemplo}</BotaoLink>}>
      {texto}
    </Banner>
  );
}
```

**Passo 4: rodar e ver passar** → 5 passed. **Passo 5: commit**
```bash
git add frontend/src/features/importar/components
git commit -m "feat(importar): adiciona detecções corrigíveis, prévia e banner de erro"
```

---

### Tarefa 10: Importar — página e rota

**Arquivos:**
- Criar: `frontend/src/features/importar/components/ResultadoImportacao.tsx`
- Substituir: `frontend/src/features/importar/PaginaImportar.tsx` (placeholder do M1.1) + `PaginaImportar.module.css` + `PaginaImportar.test.tsx`
- Modificar: `frontend/src/app/rotas.ts` (só se a rota apontar para outro arquivo)

**Passo 1: escrever o teste (falha)** — `PaginaImportar.test.tsx`
```tsx
import { screen } from '@testing-library/react';
import { Route, Routes } from 'react-router';
import { describe, expect, it } from 'vitest';
import { chamadasPara, simularApi } from '../../testes/api';
import { criarPagina, DATASET_CRIADO, ID_DATASET } from '../../testes/fixtures/datasets';
import { DATASET_TESTE, renderizarComProvedores } from '../../testes/renderizar';
import PaginaImportar from './PaginaImportar';

const CAMINHO_PAGINA = `/datasets/${ID_DATASET}`;
const ARQUIVO = new File(['id;sexo'], 'pesquisa_saude.txt', { type: 'text/plain' });

function renderizarPagina(dataset: typeof DATASET_TESTE | null = null) {
  return renderizarComProvedores(
    <Routes>
      <Route path="/importar" element={<PaginaImportar />} />
      <Route path="/variaveis" element={<p>Tela de variáveis</p>} />
    </Routes>,
    { rota: '/importar', dataset },
  );
}

describe('PaginaImportar', () => {
  it('sem arquivo (1b): área de envio e link do exemplo', () => {
    renderizarPagina();

    expect(screen.getByText('Arraste e solte seu arquivo aqui')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Abrir pesquisa_saude.txt de exemplo' })).toBeInTheDocument();
  });

  it('envio com sucesso (1a): toast, detecções, prévia e continuar', async () => {
    simularApi([
      { metodo: 'POST', caminho: '/datasets', status: 201, corpo: DATASET_CRIADO },
      { caminho: CAMINHO_PAGINA, corpo: criarPagina() },
    ]);
    const { usuario } = renderizarPagina();

    await usuario.upload(screen.getByLabelText('Arquivo de dados'), ARQUIVO);

    expect(await screen.findByText('Arquivo lido: 230 linhas e 8 colunas.')).toBeInTheDocument();
    expect(await screen.findByRole('combobox', { name: 'Separador' })).toHaveValue(';');
    expect(screen.getByRole('table', { name: 'Prévia dos dados importados' })).toBeInTheDocument();
    await usuario.click(screen.getByRole('button', { name: /Continuar para Variáveis/ }));
    expect(screen.getByText('Tela de variáveis')).toBeInTheDocument();
  });

  it('erro (1c): banner com o nome do arquivo, área continua disponível', async () => {
    simularApi([
      { metodo: 'POST', caminho: '/datasets', status: 400, corpo: { codigo: 'FORMATO_NAO_SUPORTADO', mensagem: 'Este tipo de arquivo não é aceito. Use TXT, CSV, TSV, XLSX ou JSON.', sugestao: 'Salve como CSV e envie de novo.' } },
    ]);
    const { usuario } = renderizarPagina();

    await usuario.upload(screen.getByLabelText('Arquivo de dados'), new File(['%PDF'], 'relatorio_final.txt'));

    expect(await screen.findByText('Não conseguimos ler este arquivo: relatorio_final.txt')).toBeInTheDocument();
    expect(screen.getByText('Arraste e solte seu arquivo aqui')).toBeInTheDocument();
  });

  it('corrigir o separador relê o arquivo com a opção nova', async () => {
    const falso = simularApi([
      { metodo: 'POST', caminho: '/datasets', status: 201, corpo: DATASET_CRIADO },
      { caminho: CAMINHO_PAGINA, corpo: criarPagina() },
    ]);
    const { usuario } = renderizarPagina();
    await usuario.upload(screen.getByLabelText('Arquivo de dados'), ARQUIVO);

    await usuario.selectOptions(await screen.findByRole('combobox', { name: 'Separador' }), ',');

    const envios = chamadasPara(falso, 'POST', '/datasets');
    expect(envios).toHaveLength(2);
    expect((envios[1]?.corpo as FormData).get('separador')).toBe(',');
  });

  it('abrir o exemplo chama POST /datasets/exemplo', async () => {
    const falso = simularApi([
      { metodo: 'POST', caminho: '/datasets/exemplo', status: 201, corpo: DATASET_CRIADO },
      { caminho: CAMINHO_PAGINA, corpo: criarPagina() },
    ]);
    const { usuario } = renderizarPagina();

    await usuario.click(screen.getByRole('button', { name: 'Abrir pesquisa_saude.txt de exemplo' }));

    expect(await screen.findByText('O que detectamos')).toBeInTheDocument();
    expect(chamadasPara(falso, 'POST', '/datasets/exemplo')).toHaveLength(1);
  });

  it('voltando com sessão e sem o arquivo: detecções só para leitura', async () => {
    simularApi([{ caminho: CAMINHO_PAGINA, corpo: criarPagina() }]);
    renderizarPagina(DATASET_TESTE);

    expect(await screen.findByText(/Para corrigir a leitura, envie o arquivo de novo\./)).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'Ler de novo' })).not.toBeInTheDocument();
  });
});
```

**Passo 2: rodar e ver falhar** → FAIL

**Passo 3: implementar**

`components/ResultadoImportacao.tsx`:
```tsx
import { keepPreviousData, useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router';
import { opcoesPrimeiraPagina } from '../../../shared/api/dataset';
import { CAMINHOS } from '../../../shared/navegacao/caminhos';
import Banner from '../../../shared/ui/Banner';
import BarraAcoes from '../../../shared/ui/BarraAcoes';
import Botao from '../../../shared/ui/Botao';
import ConteudoConsulta from '../../../shared/ui/ConteudoConsulta';
import type { Importacao } from '../hooks/useImportacao';
import { TEXTOS_IMPORTAR as T } from '../textos';
import CardDeteccoes from './CardDeteccoes';
import PreviaDados from './PreviaDados';

interface PropsResultadoImportacao {
  datasetId: string;
  importacao: Importacao;
}

/** Estado 1a. Lê da API (não da mutação) para funcionar também depois de recarregar a página. */
export default function ResultadoImportacao({ datasetId, importacao }: Readonly<PropsResultadoImportacao>) {
  // keepPreviousData: ao reler com outra opção o id muda, mas a tela não pisca.
  const consulta = useQuery({ ...opcoesPrimeiraPagina(datasetId), placeholderData: keepPreviousData });
  const navegar = useNavigate();
  const { lerDeNovo } = importacao;
  return (
    <ConteudoConsulta consulta={consulta} carregando={T.previa.carregando} forma="tabela">
      {(pagina) => (
        <>
          {pagina.resumo.metadados.avisos.map((aviso) => (
            <Banner key={aviso.codigo} variante="atencao">
              {aviso.mensagem}
            </Banner>
          ))}
          <CardDeteccoes metadados={pagina.resumo.metadados} opcoes={importacao.opcoes} aoCorrigir={importacao.corrigir} />
          <PreviaDados linhas={pagina.linhas} totalLinhas={pagina.resumo.n_linhas} />
          <BarraAcoes>
            {lerDeNovo === null ? null : (
              <Botao variante="secundario" tamanho="lg" carregando={importacao.enviando} textoCarregando={T.acoes.lendo} onClick={lerDeNovo}>
                {T.acoes.lerDeNovo}
              </Botao>
            )}
            <Botao
              tamanho="lg"
              iconeFinal="arrow_forward"
              onClick={() => {
                void navegar(CAMINHOS.variaveis);
              }}
            >
              {T.acoes.continuar}
            </Botao>
          </BarraAcoes>
        </>
      )}
    </ConteudoConsulta>
  );
}
```

`PaginaImportar.tsx`:
```tsx
import { useSessao } from '../../shared/sessao/useSessao';
import PaginaEtapa from '../../shared/ui/PaginaEtapa';
import AreaUpload from './components/AreaUpload';
import BannerErroImportacao from './components/BannerErroImportacao';
import BotaoLink from './components/BotaoLink';
import ResultadoImportacao from './components/ResultadoImportacao';
import { type Importacao, useImportacao } from './hooks/useImportacao';
import estilos from './PaginaImportar.module.css';
import { TEXTOS_IMPORTAR as T } from './textos';

function EnvioArquivo({ importacao }: Readonly<{ importacao: Importacao }>) {
  return (
    <>
      <AreaUpload
        enviando={importacao.enviando}
        nomeEnviando={importacao.nomeArquivo}
        comErro={importacao.erro !== null}
        aoEscolher={importacao.enviar}
      />
      <p className={estilos.exemplo}>
        {T.exemplo.pergunta} <BotaoLink onClick={importacao.abrirExemplo}>{T.exemplo.link}</BotaoLink>
      </p>
    </>
  );
}

/** Etapa 1: 1b (sem arquivo), 1c (erro, banner acima) e 1a (arquivo lido). */
export default function PaginaImportar() {
  const importacao = useImportacao();
  const sessao = useSessao();
  return (
    <PaginaEtapa etapa={1} titulo={T.titulo} ajuda={T.ajuda}>
      <div className={estilos.conteudo}>
        {importacao.erro === null ? null : (
          <BannerErroImportacao erro={importacao.erro} nomeArquivo={importacao.nomeArquivo} aoUsarExemplo={importacao.abrirExemplo} />
        )}
        {sessao.dataset === null ? (
          <EnvioArquivo importacao={importacao} />
        ) : (
          <ResultadoImportacao datasetId={sessao.dataset.id} importacao={importacao} />
        )}
      </div>
    </PaginaEtapa>
  );
}
```

`PaginaImportar.module.css`:

| Seletor | Propriedades |
|---|---|
| `.conteudo` | `display:flex; flex-direction:column; gap:24px; max-width:1112px` |
| `.exemplo` | `margin:0; font-size:14px; color:var(--cor-texto-2)` |

Rota: o M1.1 já tem `lazy(() => import('../features/importar/PaginaImportar'))` em `app/rotas.ts`; como o arquivo foi substituído no mesmo caminho, nada muda. Confira com `grep -n importar frontend/src/app/rotas.ts`.

**Passo 4: rodar e ver passar** → 6 passed; `npm run lint && npm run format && npm run test` verde.

**Passo 5: commit**
```bash
git add frontend/src/features/importar frontend/src/app/rotas.ts
git commit -m "feat(importar): monta a tela Importar com estados vazio, erro e arquivo lido"
```

---

### Tarefa 11: Variáveis — textos, regras puras e `api.ts`

**Arquivos:**
- Substituir: `frontend/src/features/variaveis/textos.ts` (provisório do M1.1; mantém `titulo` e `ajuda`)
- Criar: `frontend/src/features/variaveis/regras.ts` (+ `regras.test.ts`), `api.ts` (+ `api.test.tsx`)

**Passo 1: escrever os testes (falham)**

`frontend/src/features/variaveis/regras.test.ts`:
```ts
import { describe, expect, it } from 'vitest';
import { COLUNAS_SAUDE } from '../../testes/fixtures/datasets';
import { aplicarAlteracao, contarPorTipo, juntarExemplos, moverItem } from './regras';

describe('contarPorTipo', () => {
  it('conta na ordem do resumo, sem zeros e sem identificador', () => {
    expect(contarPorTipo(COLUNAS_SAUDE)).toEqual([
      { tipo: 'continua', quantidade: 2 },
      { tipo: 'discreta', quantidade: 1 },
      { tipo: 'ordinal', quantidade: 2 },
      { tipo: 'nominal', quantidade: 1 },
      { tipo: 'binaria', quantidade: 1 },
    ]);
  });
});

describe('juntarExemplos', () => {
  it('usa vírgula entre textos e ponto e vírgula entre números com vírgula decimal', () => {
    expect(juntarExemplos(['F', 'M'])).toBe('F, M');
    expect(juntarExemplos(['1,62', '1,78', '1,58'])).toBe('1,62; 1,78; 1,58');
  });

  it('mostra no máximo 4', () => {
    expect(juntarExemplos(['1', '2', '3', '4', '5'])).toBe('1, 2, 3, 4');
  });
});

describe('moverItem', () => {
  const lista = ['ruim', 'regular', 'bom', 'ótimo'];

  it('move para baixo e para cima sem mudar a lista original', () => {
    expect(moverItem(lista, 0, 1)).toEqual(['regular', 'ruim', 'bom', 'ótimo']);
    expect(moverItem(lista, 3, 0)).toEqual(['ótimo', 'ruim', 'regular', 'bom']);
    expect(lista).toEqual(['ruim', 'regular', 'bom', 'ótimo']);
  });

  it('devolve null quando não há o que mover', () => {
    expect(moverItem(lista, 0, -1)).toBeNull();
    expect(moverItem(lista, 3, 4)).toBeNull();
    expect(moverItem(lista, 2, 2)).toBeNull();
    expect(moverItem(lista, 9, 0)).toBeNull();
  });
});

describe('aplicarAlteracao', () => {
  it('troca o tipo, marca como manual e mantém as demais colunas', () => {
    const novas = aplicarAlteracao(COLUNAS_SAUDE, 'cidade', { tipo: 'ordinal' });

    expect(novas?.find((c) => c.coluna === 'cidade')).toMatchObject({ tipo: 'ordinal', origem: 'manual' });
    expect(novas?.find((c) => c.coluna === 'idade')).toBe(COLUNAS_SAUDE[2]);
  });

  it('nova ordem de categorias substitui a anterior', () => {
    const novas = aplicarAlteracao(COLUNAS_SAUDE, 'satisfacao', {
      tipo: 'ordinal',
      categorias_ordem: ['ótimo', 'bom', 'regular', 'ruim'],
    });

    expect(novas?.find((c) => c.coluna === 'satisfacao')?.categorias_ordem).toEqual(['ótimo', 'bom', 'regular', 'ruim']);
  });

  it('sem cache, nada a fazer', () => {
    expect(aplicarAlteracao(undefined, 'x', { tipo: 'nominal' })).toBeUndefined();
  });
});
```

`frontend/src/features/variaveis/api.test.tsx`:
```tsx
import { act, waitFor } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { chavesDataset } from '../../shared/api/dataset';
import { chamadasPara, simularApi } from '../../testes/api';
import { COLUNAS_SAUDE, criarColuna, ID_DATASET } from '../../testes/fixtures/datasets';
import { criarClienteTeste, renderizarHook } from '../../testes/renderizar';
import { useAlterarTipo } from './api';

const CAMINHO_PATCH = `/datasets/${ID_DATASET}/colunas/cidade`;
const CAMINHO_COLUNAS = `/datasets/${ID_DATASET}/colunas`;

function prepararCliente() {
  const cliente = criarClienteTeste();
  cliente.setQueryData(chavesDataset.colunas(ID_DATASET), COLUNAS_SAUDE);
  cliente.setQueryData(chavesDataset.diagnostico(ID_DATASET), { qualquer: true });
  return cliente;
}

describe('useAlterarTipo', () => {
  it('envia o PATCH, atualiza o cache na hora e invalida o diagnóstico', async () => {
    const falso = simularApi([
      { metodo: 'PATCH', caminho: CAMINHO_PATCH, corpo: criarColuna({ coluna: 'cidade', tipo: 'ordinal', origem: 'manual' }) },
      { caminho: CAMINHO_COLUNAS, corpo: COLUNAS_SAUDE },
    ]);
    const cliente = prepararCliente();
    const { result } = renderizarHook(() => useAlterarTipo(ID_DATASET), { cliente });

    act(() => {
      result.current.mutate({ coluna: 'cidade', alteracao: { tipo: 'ordinal' } });
    });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });
    expect(chamadasPara(falso, 'PATCH', CAMINHO_PATCH)[0]?.corpo).toEqual({ tipo: 'ordinal' });
    expect(cliente.getQueryState(chavesDataset.diagnostico(ID_DATASET))?.isInvalidated).toBe(true);
  });

  it('desfaz a mudança otimista quando a API recusa', async () => {
    simularApi([
      { metodo: 'PATCH', caminho: CAMINHO_PATCH, status: 400, corpo: { codigo: 'TIPO_INCOMPATIVEL', mensagem: 'Esta coluna tem textos; não pode ser numérica.', sugestao: 'Escolha um tipo qualitativo.' } },
      { caminho: CAMINHO_COLUNAS, corpo: COLUNAS_SAUDE },
    ]);
    const cliente = prepararCliente();
    const { result } = renderizarHook(() => useAlterarTipo(ID_DATASET), { cliente });

    act(() => {
      result.current.mutate({ coluna: 'cidade', alteracao: { tipo: 'continua' } });
    });

    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });
    const colunas = cliente.getQueryData<typeof COLUNAS_SAUDE>(chavesDataset.colunas(ID_DATASET));
    expect(colunas?.find((c) => c.coluna === 'cidade')?.tipo).toBe('nominal');
  });
});
```

**Passo 2: rodar e ver falhar** → FAIL

**Passo 3: implementar**

`frontend/src/features/variaveis/textos.ts` (telas.md §2):
```ts
import { formatarInteiro } from '../../shared/lib/formatar';
import type { TipoVariavel } from '../../shared/ui/tiposVariavel';

export const TEXTOS_VARIAVEIS = {
  titulo: 'Variáveis',
  ajuda: 'Classificamos cada coluna pelo que ela contém. Confira o motivo e corrija o tipo se não concordar.',
  carregando: 'Carregando os tipos das colunas…',
  resumo: 'Resumo dos tipos',
  tabela: {
    legenda: 'Tipos detectados por coluna',
    coluna: 'Coluna',
    tipo: 'Tipo detectado',
    motivo: 'Por quê',
    validos: 'Válidos / faltantes',
    exemplos: 'Exemplos',
    corrigir: 'Corrigir tipo',
    rotuloSelect: (coluna: string) => `Tipo de ${coluna}`,
  },
  ordem: {
    titulo: 'Ordem das categorias',
    instrucao: 'Arraste para mudar a ordem, do menor para o maior. Pelo teclado: foque um item e use ↑ e ↓.',
    rotuloLista: (coluna: string) => `Ordem das categorias de ${coluna}`,
    movendo: 'Movendo…',
    mover: (nome: string) => `Mover ${nome}`,
    subir: (nome: string) => `Subir ${nome}`,
    descer: (nome: string) => `Descer ${nome}`,
    anuncio: (nome: string, posicao: number, total: number) =>
      `${nome} agora está na posição ${formatarInteiro(posicao)} de ${formatarInteiro(total)}.`,
  },
  toastTipo: (coluna: string, rotuloTipo: string) => `Tipo de ${coluna} alterado para ${rotuloTipo}.`,
  continuar: 'Continuar para Limpeza',
} as const;

/** Singular e plural no resumo do topo ("2 contínuas · 1 discreta"). */
export const NOMES_RESUMO = {
  continua: ['contínua', 'contínuas'],
  discreta: ['discreta', 'discretas'],
  ordinal: ['ordinal', 'ordinais'],
  nominal: ['nominal', 'nominais'],
  binaria: ['binária', 'binárias'],
  identificador: ['identificador', 'identificadores'],
} as const satisfies Record<TipoVariavel, readonly [string, string]>;
```

`frontend/src/features/variaveis/regras.ts`:
```ts
import type { TipoColuna } from '../../shared/api/dataset';
import type { components } from '../../shared/api/schema';
import { ORDEM_TIPOS, type TipoVariavel } from '../../shared/ui/tiposVariavel';

export type AlteracaoTipo = components['schemas']['AlteracaoTipo'];

export interface ContagemTipo {
  tipo: TipoVariavel;
  quantidade: number;
}

const MAX_EXEMPLOS = 4;

/** Resumo do topo da tela 2; identificador fica de fora (é ignorado nas análises). */
export function contarPorTipo(colunas: readonly TipoColuna[]): ContagemTipo[] {
  return ORDEM_TIPOS.filter((tipo) => tipo !== 'identificador')
    .map((tipo) => ({ tipo, quantidade: colunas.filter((c) => c.tipo === tipo).length }))
    .filter((contagem) => contagem.quantidade > 0);
}

/** "1,62; 1,78" quando há vírgula decimal (senão a vírgula separadora confunde); "F, M" no resto. */
export function juntarExemplos(exemplos: readonly string[]): string {
  const visiveis = exemplos.slice(0, MAX_EXEMPLOS);
  const separador = visiveis.some((exemplo) => exemplo.includes(',')) ? '; ' : ', ';
  return visiveis.join(separador);
}

/** Nova lista com o item de `de` em `para`; null se o movimento não é possível. */
export function moverItem<T>(lista: readonly T[], de: number, para: number): T[] | null {
  const item = lista[de];
  if (item === undefined || de === para || para < 0 || para >= lista.length) return null;
  return lista.toSpliced(de, 1).toSpliced(para, 0, item);
}

/** Atualização otimista do cache de colunas (o servidor confirma depois). */
export function aplicarAlteracao(
  colunas: readonly TipoColuna[] | undefined,
  coluna: string,
  alteracao: AlteracaoTipo,
): TipoColuna[] | undefined {
  return colunas?.map(
    (atual): TipoColuna =>
      atual.coluna === coluna
        ? {
            ...atual,
            tipo: alteracao.tipo,
            origem: 'manual',
            categorias_ordem: alteracao.categorias_ordem ?? atual.categorias_ordem,
          }
        : atual,
  );
}
```

`frontend/src/features/variaveis/api.ts`:
```ts
import { type QueryClient, useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { requisitar } from '../../shared/api/cliente';
import { corpoJson } from '../../shared/api/corpoJson';
import { caminhoDataset, chavesDataset, opcoesColunas, type TipoColuna } from '../../shared/api/dataset';
import { useAvisarErro } from '../../shared/ui/useAvisarErro';
import { type AlteracaoTipo, aplicarAlteracao } from './regras';

export interface PedidoAlteracao {
  coluna: string;
  alteracao: AlteracaoTipo;
}

export const chavesVariaveis = {
  alterarTipo: (id: string) => [...chavesDataset.colunas(id), 'alterar'] as const,
};

export function useColunas(datasetId: string | null) {
  return useQuery(opcoesColunas(datasetId));
}

function alterarTipo(datasetId: string, { coluna, alteracao }: PedidoAlteracao): Promise<TipoColuna> {
  const caminho = caminhoDataset(datasetId, `/colunas/${encodeURIComponent(coluna)}`);
  return requisitar<TipoColuna>(caminho, corpoJson('PATCH', alteracao));
}

/** Tipo e ordem das categorias mudam análises, diagnóstico e relatório (tabela de invalidação, Dnn-chaves). */
function invalidarDerivados(cliente: QueryClient, id: string): Promise<unknown> {
  const chaves = [chavesDataset.colunas(id), chavesDataset.diagnostico(id), chavesDataset.analises(id), chavesDataset.relatorio(id)];
  return Promise.all(chaves.map((queryKey) => cliente.invalidateQueries({ queryKey })));
}

/**
 * PATCH otimista em fila (scope): reordenar várias vezes seguidas manda os pedidos em ordem
 * e só a última resposta dispara a invalidação.
 */
export function useAlterarTipo(datasetId: string) {
  const cliente = useQueryClient();
  const avisarErro = useAvisarErro();
  const chave = chavesDataset.colunas(datasetId);
  const chaveMutacao = chavesVariaveis.alterarTipo(datasetId);
  return useMutation({
    mutationKey: chaveMutacao,
    scope: { id: chaveMutacao.join('/') },
    mutationFn: (pedido: PedidoAlteracao) => alterarTipo(datasetId, pedido),
    onMutate: async ({ coluna, alteracao }) => {
      await cliente.cancelQueries({ queryKey: chave });
      const anteriores = cliente.getQueryData<TipoColuna[]>(chave);
      cliente.setQueryData<TipoColuna[]>(chave, (atuais) => aplicarAlteracao(atuais, coluna, alteracao));
      return { anteriores };
    },
    onError: (erro, _pedido, contexto) => {
      cliente.setQueryData(chave, contexto?.anteriores);
      avisarErro(erro);
    },
    onSettled: () =>
      cliente.isMutating({ mutationKey: chaveMutacao }) > 1 ? undefined : invalidarDerivados(cliente, datasetId),
  });
}
```

**Passo 4: rodar e ver passar** → 11 passed. **Passo 5: commit**
```bash
git add frontend/src/features/variaveis
git commit -m "feat(variaveis): adiciona regras do resumo e alteração otimista de tipo"
```

---

### Tarefa 12: Variáveis — `TabelaVariaveis` e `ResumoTipos`

**Arquivos:**
- Criar em `frontend/src/features/variaveis/components/`: `TabelaVariaveis.tsx` + `.module.css` + `.test.tsx`; `ResumoTipos.tsx` + `.module.css` + `.test.tsx`

**Passo 1: escrever os testes (falham)**

`ResumoTipos.test.tsx`:
```tsx
import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { COLUNAS_SAUDE } from '../../../testes/fixtures/datasets';
import ResumoTipos from './ResumoTipos';

describe('ResumoTipos', () => {
  it('lista a quantidade por tipo com plural', () => {
    render(<ResumoTipos colunas={COLUNAS_SAUDE} />);

    const itens = screen.getAllByRole('listitem').map((item) => item.textContent);
    expect(itens).toEqual(['2 contínuas', '1 discreta', '2 ordinais', '1 nominal', '1 binária']);
  });
});
```

`TabelaVariaveis.test.tsx`:
```tsx
import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import { COLUNAS_SAUDE, criarColuna } from '../../../testes/fixtures/datasets';
import TabelaVariaveis from './TabelaVariaveis';

describe('TabelaVariaveis', () => {
  it('mostra tipo, motivo, válidos/faltantes e exemplos de cada coluna', () => {
    render(<TabelaVariaveis colunas={COLUNAS_SAUDE} aoAlterarTipo={vi.fn()} />);

    const linha = screen.getByRole('row', { name: /peso_kg/ });
    expect(within(linha).getByText('Contínua')).toBeInTheDocument();
    expect(within(linha).getByText('Números com casas decimais.')).toBeInTheDocument();
    expect(within(linha).getByText('58,2; 79,6; 63,0')).toBeInTheDocument();
    expect(within(linha).getByRole('combobox', { name: 'Tipo de peso_kg' })).toHaveValue('continua');
  });

  it('corrigir o tipo chama aoAlterarTipo com coluna e tipo', async () => {
    const aoAlterarTipo = vi.fn();
    render(<TabelaVariaveis colunas={COLUNAS_SAUDE} aoAlterarTipo={aoAlterarTipo} />);

    await userEvent.selectOptions(screen.getByRole('combobox', { name: 'Tipo de cidade' }), 'ordinal');

    expect(aoAlterarTipo).toHaveBeenCalledWith('cidade', 'ordinal');
  });

  it('tipo escolhido pelo usuário aparece como corrigido', () => {
    render(<TabelaVariaveis colunas={[criarColuna({ coluna: 'cidade', tipo: 'ordinal', origem: 'manual' })]} aoAlterarTipo={vi.fn()} />);

    expect(screen.getByText('corrigido')).toBeInTheDocument();
  });
});
```

**Passo 2: rodar e ver falhar** → FAIL

**Passo 3: implementar**

`ResumoTipos.tsx`:
```tsx
import type { TipoColuna } from '../../../shared/api/dataset';
import { formatarInteiro } from '../../../shared/lib/formatar';
import { escolherForma } from '../../../shared/lib/pluralizar';
import { corDoTipo } from '../../../shared/ui/tiposVariavel';
import { contarPorTipo } from '../regras';
import { NOMES_RESUMO, TEXTOS_VARIAVEIS as T } from '../textos';
import estilos from './ResumoTipos.module.css';

export default function ResumoTipos({ colunas }: Readonly<{ colunas: readonly TipoColuna[] }>) {
  return (
    <ul className={estilos.resumo} aria-label={T.resumo}>
      {contarPorTipo(colunas).map(({ tipo, quantidade }) => (
        <li key={tipo} className={estilos.item}>
          <span className={estilos.numero} style={{ color: corDoTipo(tipo) }}>
            {formatarInteiro(quantidade)}
          </span>{' '}
          {escolherForma(quantidade, ...NOMES_RESUMO[tipo])}
        </li>
      ))}
    </ul>
  );
}
```

| Seletor (`ResumoTipos.module.css`) | Propriedades |
|---|---|
| `.resumo` | `display:flex; flex-wrap:wrap; justify-content:flex-end; gap:8px; margin:0; padding:0; list-style:none` |
| `.item` | `font-size:13px; color:var(--cor-texto-2); white-space:nowrap` |
| `.numero` | `font:600 13px var(--fonte-mono)` |

`TabelaVariaveis.tsx` (reusa a `Tabela` do M1.1; larguras do grid `140 200 1fr 120 170 200` via CSS do envoltório):
```tsx
import type { TipoColuna } from '../../../shared/api/dataset';
import { formatarInteiro } from '../../../shared/lib/formatar';
import ChipTipo from '../../../shared/ui/ChipTipo';
import Select from '../../../shared/ui/Select';
import Tabela, { type ColunaTabela } from '../../../shared/ui/Tabela';
import { ORDEM_TIPOS, TIPOS_VARIAVEL, type TipoVariavel } from '../../../shared/ui/tiposVariavel';
import { juntarExemplos } from '../regras';
import { TEXTOS_VARIAVEIS as T } from '../textos';
import estilos from './TabelaVariaveis.module.css';

const OPCOES_TIPO = ORDEM_TIPOS.map((tipo) => ({ valor: tipo, rotulo: TIPOS_VARIAVEL[tipo].rotuloCompleto }));

interface PropsTabelaVariaveis {
  colunas: readonly TipoColuna[];
  aoAlterarTipo: (coluna: string, tipo: TipoVariavel) => void;
}

function ValidosFaltantes({ coluna }: Readonly<{ coluna: TipoColuna }>) {
  return (
    <>
      {formatarInteiro(coluna.n_validos)}
      <span className={estilos.barra}> / </span>
      <span className={estilos.faltantes} data-zero={coluna.n_faltantes === 0}>
        {formatarInteiro(coluna.n_faltantes)}
      </span>
    </>
  );
}

export default function TabelaVariaveis({ colunas, aoAlterarTipo }: Readonly<PropsTabelaVariaveis>) {
  const definicao: readonly ColunaTabela<TipoColuna>[] = [
    { id: 'coluna', titulo: T.tabela.coluna, mono: true, celula: (c) => c.coluna },
    { id: 'tipo', titulo: T.tabela.tipo, celula: (c) => <ChipTipo tipo={c.tipo} curto corrigido={c.origem === 'manual'} /> },
    { id: 'motivo', titulo: T.tabela.motivo, celula: (c) => c.motivo },
    { id: 'validos', titulo: T.tabela.validos, alinhamento: 'direita', mono: true, celula: (c) => <ValidosFaltantes coluna={c} /> },
    { id: 'exemplos', titulo: T.tabela.exemplos, mono: true, celula: (c) => <span className={estilos.exemplos}>{juntarExemplos(c.exemplos)}</span> },
    {
      id: 'corrigir',
      titulo: T.tabela.corrigir,
      celula: (c) => (
        <Select
          rotulo={T.tabela.rotuloSelect(c.coluna)}
          rotuloOculto
          altura={36}
          valor={c.tipo}
          opcoes={OPCOES_TIPO}
          aoMudar={(tipo) => {
            aoAlterarTipo(c.coluna, tipo);
          }}
        />
      ),
    },
  ];
  return (
    <div className={estilos.envoltorio}>
      <Tabela legenda={T.tabela.legenda} colunas={definicao} linhas={colunas} chave={(c) => c.coluna} />
    </div>
  );
}
```
> O teste `getByRole('row', { name: /peso_kg/ })` depende de a `Tabela` usar `<th scope="row">` ou de o nome da linha incluir o texto da célula. Se não casar, troque por `screen.getByText('peso_kg').closest('tr')`.

`TabelaVariaveis.module.css` (Tela 2; seletores de elemento dentro do envoltório não são renomeados pelo CSS Modules):

| Seletor | Propriedades |
|---|---|
| `.envoltorio table` | `table-layout:fixed; width:100%` |
| `.envoltorio th:nth-child(1)` | `width:140px` |
| `.envoltorio th:nth-child(2)` | `width:200px` |
| `.envoltorio th:nth-child(4)` | `width:120px` |
| `.envoltorio th:nth-child(5)` | `width:170px` |
| `.envoltorio th:nth-child(6)` | `width:200px` |
| `.envoltorio td` | `vertical-align:middle; font-size:14px; line-height:1.45` |
| `.barra` | `color:var(--cor-texto-2)` |
| `.faltantes[data-zero='true']` | `color:var(--cor-texto-2)` |
| `.exemplos` | `display:block; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; color:var(--cor-texto-2); font-size:13px` |
| `@media (max-width:1279px)` › `.envoltorio` | `overflow-x:auto` (tabela rola em vez de espremer) |

**Passo 4: rodar e ver passar** → 4 passed. **Passo 5: commit**
```bash
git add frontend/src/features/variaveis/components
git commit -m "feat(variaveis): adiciona tabela de tipos e resumo por tipo"
```

---

### Tarefa 13: Variáveis — `EditorOrdem` (D62)

Arrastar nativo (HTML5) + botões Subir/Descer (28×28) + ↑/↓ na alça focada. Depois de mover, o foco volta para o mesmo controle do item movido (ou para a alça, se o botão ficou desabilitado no topo/fundo) e um `aria-live` anuncia a nova posição. A ordem vem do cache de colunas (atualização otimista) — sem estado duplicado.

**Arquivos:**
- Criar em `frontend/src/features/variaveis/components/`: `EditorOrdem.tsx`, `ItemOrdem.tsx`, `EditorOrdem.module.css`, `EditorOrdem.test.tsx`

**Passo 1: escrever o teste (falha)**
```tsx
import { fireEvent, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import { COLUNAS_SAUDE, criarColuna } from '../../../testes/fixtures/datasets';
import EditorOrdem from './EditorOrdem';

const ESCOLARIDADE = COLUNAS_SAUDE[5] ?? criarColuna({ coluna: 'escolaridade', tipo: 'ordinal' });
const TRANSFERENCIA = { dataTransfer: { setData: vi.fn(), effectAllowed: 'none' } };

function item(nome: string): HTMLElement {
  const li = screen.getByText(nome).closest('li');
  if (li === null) throw new Error(`item ${nome} não encontrado`);
  return li;
}

describe('EditorOrdem', () => {
  it('lista as categorias com posição, contagem e a escala', () => {
    render(<EditorOrdem coluna={ESCOLARIDADE} aoReordenar={vi.fn()} />);

    expect(screen.getByRole('list', { name: 'Ordem das categorias de escolaridade' })).toBeInTheDocument();
    expect(screen.getByText('96 linhas')).toBeInTheDocument();
    expect(screen.getByText('fundamental < médio < superior < pós')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Subir fundamental' })).toBeDisabled();
    expect(screen.getByRole('button', { name: 'Descer pós' })).toBeDisabled();
  });

  it('↓ na alça focada desce o item e anuncia a nova posição', async () => {
    const aoReordenar = vi.fn();
    render(<EditorOrdem coluna={ESCOLARIDADE} aoReordenar={aoReordenar} />);

    screen.getByRole('button', { name: 'Mover fundamental' }).focus();
    await userEvent.keyboard('{ArrowDown}');

    expect(aoReordenar).toHaveBeenCalledWith(['médio', 'fundamental', 'superior', 'pós']);
    expect(screen.getByText('fundamental agora está na posição 2 de 4.')).toBeInTheDocument();
  });

  it('botão Subir sobe o item', async () => {
    const aoReordenar = vi.fn();
    render(<EditorOrdem coluna={ESCOLARIDADE} aoReordenar={aoReordenar} />);

    await userEvent.click(screen.getByRole('button', { name: 'Subir pós' }));

    expect(aoReordenar).toHaveBeenCalledWith(['fundamental', 'médio', 'pós', 'superior']);
  });

  it('arrastar e soltar move para a posição do alvo', () => {
    const aoReordenar = vi.fn();
    render(<EditorOrdem coluna={ESCOLARIDADE} aoReordenar={aoReordenar} />);

    fireEvent.dragStart(item('pós'), TRANSFERENCIA);
    expect(screen.getByText('Movendo…')).toBeInTheDocument();
    fireEvent.dragOver(item('fundamental'));
    fireEvent.drop(item('fundamental'));

    expect(aoReordenar).toHaveBeenCalledWith(['pós', 'fundamental', 'médio', 'superior']);
  });

  it('depois que a nova ordem chega, o foco continua no item movido', async () => {
    const { rerender } = render(<EditorOrdem coluna={ESCOLARIDADE} aoReordenar={vi.fn()} />);
    screen.getByRole('button', { name: 'Mover fundamental' }).focus();
    await userEvent.keyboard('{ArrowDown}');

    rerender(<EditorOrdem coluna={{ ...ESCOLARIDADE, categorias_ordem: ['médio', 'fundamental', 'superior', 'pós'] }} aoReordenar={vi.fn()} />);

    expect(screen.getByRole('button', { name: 'Mover fundamental' })).toHaveFocus();
  });
});
```

**Passo 2: rodar e ver falhar** → FAIL

**Passo 3: implementar**

`ItemOrdem.tsx`:
```tsx
import type { DragEvent, KeyboardEvent } from 'react';
import { contarLinhas } from '../../../shared/lib/pluralizar';
import Icone from '../../../shared/ui/Icone';
import { TEXTOS_VARIAVEIS as T } from '../textos';
import estilos from './EditorOrdem.module.css';

export type Controle = 'alca' | 'subir' | 'descer';
type Passo = -1 | 1;

export interface PropsItemOrdem {
  nome: string;
  posicao: number;
  total: number;
  quantidade: number;
  arrastando: boolean;
  idInstrucao: string;
  registrar: (controle: Controle, elemento: HTMLButtonElement | null) => void;
  aoMover: (passo: Passo, controle: Controle) => void;
  aoIniciarArraste: () => void;
  aoSoltar: () => void;
  aoTerminarArraste: () => void;
}

const PASSO_POR_TECLA: Partial<Record<string, Passo>> = { ArrowUp: -1, ArrowDown: 1 };

function permitirSoltar(evento: DragEvent<HTMLLIElement>): void {
  evento.preventDefault();
}

function BotoesMover({ nome, posicao, total, registrar, aoMover }: Readonly<PropsItemOrdem>) {
  return (
    <span className={estilos.botoes}>
      <button type="button" className={estilos.botaoIcone} ref={(el) => { registrar('subir', el); }} aria-label={T.ordem.subir(nome)} disabled={posicao === 1} onClick={() => { aoMover(-1, 'subir'); }}>
        <Icone nome="arrow_upward" tamanho={18} />
      </button>
      <button type="button" className={estilos.botaoIcone} ref={(el) => { registrar('descer', el); }} aria-label={T.ordem.descer(nome)} disabled={posicao === total} onClick={() => { aoMover(1, 'descer'); }}>
        <Icone nome="arrow_downward" tamanho={18} />
      </button>
    </span>
  );
}

export default function ItemOrdem(props: Readonly<PropsItemOrdem>) {
  const { nome, posicao, quantidade, arrastando, idInstrucao, registrar, aoMover } = props;

  function aoIniciar(evento: DragEvent<HTMLLIElement>): void {
    evento.dataTransfer.effectAllowed = 'move';
    evento.dataTransfer.setData('text/plain', nome); // Firefox só arrasta com dado
    props.aoIniciarArraste();
  }

  function aoSoltarAqui(evento: DragEvent<HTMLLIElement>): void {
    evento.preventDefault();
    props.aoSoltar();
  }

  function aoTeclar(evento: KeyboardEvent<HTMLButtonElement>): void {
    const passo = PASSO_POR_TECLA[evento.key];
    if (passo === undefined) return;
    evento.preventDefault();
    aoMover(passo, 'alca');
  }

  return (
    <li className={estilos.item} data-arrastando={arrastando} draggable onDragStart={aoIniciar} onDragOver={permitirSoltar} onDrop={aoSoltarAqui} onDragEnd={props.aoTerminarArraste}>
      <button type="button" className={estilos.alca} ref={(el) => { registrar('alca', el); }} aria-label={T.ordem.mover(nome)} aria-describedby={idInstrucao} onKeyDown={aoTeclar}>
        <Icone nome="drag_indicator" tamanho={20} />
      </button>
      <span className={estilos.posicao}>{posicao}</span>
      <span className={estilos.nome}>{nome}</span>
      {arrastando ? <span className={estilos.movendo}>{T.ordem.movendo}</span> : <span className={estilos.quantidade}>{contarLinhas(quantidade)}</span>}
      <BotoesMover {...props} />
    </li>
  );
}
```
(Prettier quebra os atributos em várias linhas.)

`EditorOrdem.tsx`:
```tsx
import { useEffect, useId, useRef, useState } from 'react';
import type { TipoColuna } from '../../../shared/api/dataset';
import Card from '../../../shared/ui/Card';
import ChipTipo from '../../../shared/ui/ChipTipo';
import { moverItem } from '../regras';
import { TEXTOS_VARIAVEIS as T } from '../textos';
import estilos from './EditorOrdem.module.css';
import ItemOrdem, { type Controle } from './ItemOrdem';

interface PropsEditorOrdem {
  coluna: TipoColuna;
  aoReordenar: (categorias: string[]) => void;
}

interface Foco {
  nome: string;
  controle: Controle;
}

/** Card "Ordem das categorias · {coluna}" (2a, D62). */
export default function EditorOrdem({ coluna, aoReordenar }: Readonly<PropsEditorOrdem>) {
  const categorias = coluna.categorias_ordem;
  const idInstrucao = useId();
  const [arrastando, setArrastando] = useState<string | null>(null);
  const [anuncio, setAnuncio] = useState('');
  const controles = useRef(new Map<string, HTMLButtonElement>());
  const focoPendente = useRef<Foco | null>(null);

  // Reordenar move nós do DOM e o foco se perde; devolve ao controle usado quando a nova ordem chega.
  useEffect(() => {
    const alvo = focoPendente.current;
    focoPendente.current = null;
    if (alvo === null) return;
    const botao = controles.current.get(`${alvo.nome}:${alvo.controle}`);
    const destino = botao && !botao.disabled ? botao : controles.current.get(`${alvo.nome}:alca`);
    destino?.focus();
  }, [categorias]);

  function mover(de: number, para: number, controle: Controle): void {
    const nova = moverItem(categorias, de, para);
    const nome = categorias[de];
    if (nova === null || nome === undefined) return;
    focoPendente.current = { nome, controle };
    setAnuncio(T.ordem.anuncio(nome, para + 1, categorias.length));
    aoReordenar(nova);
  }

  function soltarEm(alvo: number): void {
    const de = arrastando === null ? -1 : categorias.indexOf(arrastando);
    setArrastando(null);
    mover(de, alvo, 'alca');
  }

  const registrar = (nome: string) => (controle: Controle, elemento: HTMLButtonElement | null) => {
    const chave = `${nome}:${controle}`;
    if (elemento === null) controles.current.delete(chave);
    else controles.current.set(chave, elemento);
  };

  const titulo = (
    <>
      {T.ordem.titulo} · <span className={estilos.mono}>{coluna.coluna}</span>
    </>
  );

  return (
    <Card titulo={titulo} acoes={<ChipTipo tipo="ordinal" curto />}>
      <p id={idInstrucao} className={estilos.instrucao}>{T.ordem.instrucao}</p>
      <ol className={estilos.lista} aria-label={T.ordem.rotuloLista(coluna.coluna)}>
        {categorias.map((nome, indice) => (
          <ItemOrdem
            key={nome}
            nome={nome}
            posicao={indice + 1}
            total={categorias.length}
            quantidade={coluna.contagens[nome] ?? 0}
            arrastando={arrastando === nome}
            idInstrucao={idInstrucao}
            registrar={registrar(nome)}
            aoMover={(passo, controle) => { mover(indice, indice + passo, controle); }}
            aoIniciarArraste={() => { setArrastando(nome); }}
            aoSoltar={() => { soltarEm(indice); }}
            aoTerminarArraste={() => { setArrastando(null); }}
          />
        ))}
      </ol>
      <p className={estilos.escala}>{categorias.join(' < ')}</p>
      <p className={estilos.somenteLeitor} aria-live="polite">{anuncio}</p>
    </Card>
  );
}
```

`EditorOrdem.module.css` (Tela 2, card de ordinais):

| Seletor | Propriedades |
|---|---|
| `.mono` | `font-family:var(--fonte-mono)` |
| `.instrucao` | `margin:0 0 14px; font-size:14px; line-height:1.5; color:var(--cor-texto-2)` |
| `.lista` | `display:flex; flex-direction:column; gap:6px; margin:0; padding:0; list-style:none` |
| `.item` | `display:flex; align-items:center; gap:12px; height:44px; padding:0 12px; border:1px solid var(--cor-borda); border-radius:var(--raio-md); background:var(--cor-superficie)` |
| `.item[data-arrastando='true']` | `border-color:var(--cor-primaria); background:var(--cor-superficie-elevada); box-shadow:var(--sombra-2); outline:2px solid var(--cor-foco); outline-offset:1px` |
| `.alca` | `display:grid; place-items:center; width:28px; height:28px; padding:0; border:0; border-radius:var(--raio-sm); background:none; color:var(--cor-texto-2); cursor:grab` |
| `.item[data-arrastando='true'] .alca`, `.item[data-arrastando='true'] .posicao` | `color:var(--cor-primaria)` |
| `.posicao` | `width:18px; font:600 13px var(--fonte-mono); color:var(--cor-texto-2)` |
| `.nome` | `flex:1; font-size:14px` |
| `.item[data-arrastando='true'] .nome` | `font-weight:600` |
| `.quantidade` | `font:12.5px var(--fonte-mono); color:var(--cor-texto-2)` |
| `.movendo` | `font-size:12.5px; font-weight:500; color:var(--cor-primaria)` |
| `.botoes` | `display:flex; gap:2px` |
| `.botaoIcone` | `display:grid; place-items:center; width:28px; height:28px; padding:0; border:0; border-radius:var(--raio-sm); background:none; color:var(--cor-texto-2); cursor:pointer` |
| `.botaoIcone:hover:not(:disabled)`, `.alca:hover` | `background:var(--cor-superficie-2); color:var(--cor-texto)` |
| `.botaoIcone:disabled` | `color:var(--cor-texto-desab); cursor:default` |
| `.alca:focus-visible`, `.botaoIcone:focus-visible` | `outline:2px solid var(--cor-foco); outline-offset:2px` |
| `.escala` | `margin:14px 0 0; font:500 13px var(--fonte-mono); color:var(--cor-texto-2)` |
| `.somenteLeitor` | `position:absolute; width:1px; height:1px; overflow:hidden; clip-path:inset(50%); white-space:nowrap` |

**Passo 4: rodar e ver passar** → 5 passed. **Passo 5: commit**
```bash
git add frontend/src/features/variaveis/components
git commit -m "feat(variaveis): adiciona editor de ordem com arrastar, botões e teclado"
```

---

### Tarefa 14: Variáveis — página e rota

**Arquivos:**
- Criar: `frontend/src/features/variaveis/components/ConteudoVariaveis.tsx` + `ConteudoVariaveis.module.css`
- Substituir: `frontend/src/features/variaveis/PaginaVariaveis.tsx` (placeholder do M1.1) + `PaginaVariaveis.test.tsx`

**Passo 1: escrever o teste (falha)** — `PaginaVariaveis.test.tsx`
```tsx
import { screen, waitFor } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { chamadasPara, simularApi } from '../../testes/api';
import { COLUNAS_SAUDE, criarColuna, ID_DATASET } from '../../testes/fixtures/datasets';
import { DATASET_TESTE, renderizarComProvedores } from '../../testes/renderizar';
import PaginaVariaveis from './PaginaVariaveis';

const CAMINHO_COLUNAS = `/datasets/${ID_DATASET}/colunas`;
const CAMINHO_CIDADE = `${CAMINHO_COLUNAS}/cidade`;
const SELECT_CIDADE = { name: 'Tipo de cidade' };

describe('PaginaVariaveis', () => {
  it('mostra o resumo, a tabela e um editor por ordinal', async () => {
    simularApi([{ caminho: CAMINHO_COLUNAS, corpo: COLUNAS_SAUDE }]);
    renderizarComProvedores(<PaginaVariaveis />, { rota: '/variaveis', dataset: DATASET_TESTE });

    expect(await screen.findByText('Tipos detectados por coluna')).toBeInTheDocument();
    expect(screen.getByRole('list', { name: 'Resumo dos tipos' })).toHaveTextContent('2 contínuas');
    expect(screen.getAllByRole('list', { name: /Ordem das categorias de/ })).toHaveLength(2);
  });

  it('corrigir o tipo manda o PATCH e confirma com toast', async () => {
    const falso = simularApi([
      { caminho: CAMINHO_COLUNAS, corpo: COLUNAS_SAUDE },
      { metodo: 'PATCH', caminho: CAMINHO_CIDADE, corpo: criarColuna({ coluna: 'cidade', tipo: 'ordinal', origem: 'manual' }) },
    ]);
    const { usuario } = renderizarComProvedores(<PaginaVariaveis />, { dataset: DATASET_TESTE });

    await usuario.selectOptions(await screen.findByRole('combobox', SELECT_CIDADE), 'ordinal');

    expect(await screen.findByText('Tipo de cidade alterado para Qualitativa ordinal.')).toBeInTheDocument();
    expect(chamadasPara(falso, 'PATCH', CAMINHO_CIDADE)[0]?.corpo).toEqual({ tipo: 'ordinal' });
  });

  it('tipo recusado pela API mostra o erro e volta ao tipo anterior', async () => {
    simularApi([
      { caminho: CAMINHO_COLUNAS, corpo: COLUNAS_SAUDE },
      { metodo: 'PATCH', caminho: CAMINHO_CIDADE, status: 400, corpo: { codigo: 'TIPO_INCOMPATIVEL', mensagem: 'Esta coluna tem textos; não pode ser numérica.', sugestao: 'Escolha um tipo qualitativo.' } },
    ]);
    const { usuario } = renderizarComProvedores(<PaginaVariaveis />, { dataset: DATASET_TESTE });

    await usuario.selectOptions(await screen.findByRole('combobox', SELECT_CIDADE), 'continua');

    expect(await screen.findByText('Esta coluna tem textos; não pode ser numérica.')).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByRole('combobox', SELECT_CIDADE)).toHaveValue('nominal');
    });
  });

  it('sem dataset, orienta a importar', () => {
    renderizarComProvedores(<PaginaVariaveis />);
    expect(screen.getByText('Nenhum arquivo importado')).toBeInTheDocument();
  });
});
```

**Passo 2: rodar e ver falhar** → FAIL

**Passo 3: implementar**

`components/ConteudoVariaveis.tsx`:
```tsx
import { useNavigate } from 'react-router';
import { CAMINHOS } from '../../../shared/navegacao/caminhos';
import BarraAcoes from '../../../shared/ui/BarraAcoes';
import Botao from '../../../shared/ui/Botao';
import ConteudoConsulta from '../../../shared/ui/ConteudoConsulta';
import { TIPOS_VARIAVEL, type TipoVariavel } from '../../../shared/ui/tiposVariavel';
import { useToast } from '../../../shared/ui/useToast';
import { useAlterarTipo, useColunas } from '../api';
import { TEXTOS_VARIAVEIS as T } from '../textos';
import estilos from './ConteudoVariaveis.module.css';
import EditorOrdem from './EditorOrdem';
import TabelaVariaveis from './TabelaVariaveis';

export default function ConteudoVariaveis({ datasetId }: Readonly<{ datasetId: string }>) {
  const consulta = useColunas(datasetId);
  const alterar = useAlterarTipo(datasetId);
  const toast = useToast();
  const navegar = useNavigate();

  function alterarTipo(coluna: string, tipo: TipoVariavel): void {
    alterar.mutate(
      { coluna, alteracao: { tipo } },
      {
        onSuccess: () => {
          toast.mostrar({ tipo: 'sucesso', titulo: T.toastTipo(coluna, TIPOS_VARIAVEL[tipo].rotuloCompleto) });
        },
      },
    );
  }

  function reordenar(coluna: string, categorias: string[]): void {
    alterar.mutate({ coluna, alteracao: { tipo: 'ordinal', categorias_ordem: categorias } });
  }

  return (
    <ConteudoConsulta consulta={consulta} carregando={T.carregando} forma="tabela">
      {(colunas) => (
        <div className={estilos.conteudo}>
          <TabelaVariaveis colunas={colunas} aoAlterarTipo={alterarTipo} />
          <div className={estilos.ordinais}>
            {colunas
              .filter((c) => c.tipo === 'ordinal' && c.categorias_ordem.length > 0)
              .map((c) => (
                <EditorOrdem key={c.coluna} coluna={c} aoReordenar={(ordem) => { reordenar(c.coluna, ordem); }} />
              ))}
          </div>
          <BarraAcoes>
            <Botao tamanho="lg" iconeFinal="arrow_forward" onClick={() => { void navegar(CAMINHOS.limpeza); }}>
              {T.continuar}
            </Botao>
          </BarraAcoes>
        </div>
      )}
    </ConteudoConsulta>
  );
}
```

| Seletor (`ConteudoVariaveis.module.css`) | Propriedades |
|---|---|
| `.conteudo` | `display:flex; flex-direction:column; gap:24px` |
| `.ordinais` | `display:grid; grid-template-columns:repeat(auto-fit, minmax(min(100%, 420px), 1fr)); gap:20px` |
| `.ordinais:empty` | `display:none` |

`PaginaVariaveis.tsx`:
```tsx
import ExigeDataset from '../../shared/sessao/ExigeDataset';
import { useSessao } from '../../shared/sessao/useSessao';
import PaginaEtapa from '../../shared/ui/PaginaEtapa';
import { useColunas } from './api';
import ConteudoVariaveis from './components/ConteudoVariaveis';
import ResumoTipos from './components/ResumoTipos';
import { TEXTOS_VARIAVEIS as T } from './textos';

/** Resumo no topo à direita (2a); usa a mesma consulta do conteúdo (react-query deduplica). */
function ResumoDoDataset() {
  const sessao = useSessao();
  const { data: colunas } = useColunas(sessao.dataset?.id ?? null);
  return colunas ? <ResumoTipos colunas={colunas} /> : null;
}

export default function PaginaVariaveis() {
  return (
    <PaginaEtapa etapa={2} titulo={T.titulo} ajuda={T.ajuda} acoesTopo={<ResumoDoDataset />}>
      <ExigeDataset>{(id) => <ConteudoVariaveis datasetId={id} />}</ExigeDataset>
    </PaginaEtapa>
  );
}
```
Rota: mesma do placeholder (`app/rotas.ts` já aponta para este arquivo).

**Passo 4: rodar e ver passar** → 4 passed; lint e testes verdes.

**Passo 5: commit**
```bash
git add frontend/src/features/variaveis
git commit -m "feat(variaveis): monta a tela Variáveis com correção de tipo e ordem dos ordinais"
```

---

### Tarefa 15: Limpeza — tipos, textos, descrições, seções e resumo

As 5 seções do diagnóstico (faltantes, duplicados, fora de faixa, grafias, tipo misto) têm o mesmo formato visual (`120px 1fr 250px`). Em vez de 5 componentes, funções puras transformam cada parte do `Diagnostico` em `SecaoDiagnostico` e **um** componente genérico (`SecaoProblema`, Tarefa 17) desenha todas. Cada linha já traz a `acaoBase` (o `AcaoLimpeza` sem a ação), então montar o `PedidoLimpeza` é só juntar a escolha.

**Arquivos:**
- Substituir: `frontend/src/features/limpeza/textos.ts` (provisório do M1.1; mantém `titulo` e `ajuda`)
- Criar em `frontend/src/features/limpeza/`: `tipos.ts`, `descricoes.ts` (+ `.test.ts`), `secoes.ts` (+ `.test.ts`), `resumo.ts` (+ `.test.ts`)

**Passo 1: escrever os testes (falham)**

`descricoes.test.ts`:
```ts
import { describe, expect, it } from 'vitest';
import { criarEntradaLog } from '../../testes/fixtures/limpeza';
import { descreverLinhas, descreverOcorrencias, detalheDoLog, listarNumeros, primeiraMaiuscula } from './descricoes';

describe('descricoes', () => {
  it('lista até 5 números e resume o resto', () => {
    expect(listarNumeros([12, 141, 207])).toBe('12, 141, 207');
    expect(listarNumeros([1, 2, 3, 4, 5, 6, 7])).toBe('1, 2, 3, 4, 5 e mais 2');
  });

  it('descreve linhas no singular e no plural', () => {
    expect(descreverLinhas([88])).toBe('linha 88');
    expect(descreverLinhas([45, 46, 47])).toBe('linhas 45, 46, 47');
    expect(primeiraMaiuscula('linha 44')).toBe('Linha 44');
  });

  it('descreve ocorrências com linhas e valores em pt-BR', () => {
    expect(descreverOcorrencias([{ linha: 77, valor: 17.2 }])).toBe('Linha 77: 17,2');
    expect(descreverOcorrencias([{ linha: 19, valor: 0 }, { linha: 201, valor: 230 }])).toBe('Linhas 19 e 201: 0 e 230');
  });

  it('detalhe do log junta linhas e antes → depois', () => {
    expect(detalheDoLog(criarEntradaLog())).toBe('linhas 45, 46, 47');
    expect(detalheDoLog(criarEntradaLog({ linhas_afetadas: [77], antes_exemplo: '17,2', depois_exemplo: '1,72' }))).toBe('linha 77 · 17,2 → 1,72');
  });
});
```

`secoes.test.ts`:
```ts
import { describe, expect, it } from 'vitest';
import { DIAGNOSTICO_SAUDE, DIAGNOSTICO_VAZIO } from '../../testes/fixtures/limpeza';
import { montarPedido, montarSecoes } from './secoes';

describe('montarSecoes', () => {
  const secoes = montarSecoes(DIAGNOSTICO_SAUDE);
  const porId = (id: string) => secoes.find((s) => s.id === id);

  it('só traz seções com problemas, na ordem do design', () => {
    expect(secoes.map((s) => s.id)).toEqual(['faltantes', 'duplicados', 'fora_de_faixa', 'inconsistencia']);
    expect(montarSecoes(DIAGNOSTICO_VAZIO)).toEqual([]);
  });

  it('faltantes: valores sugeridos nos rótulos e moda para texto', () => {
    const [peso, cidade] = porId('faltantes')?.linhas ?? [];
    expect(porId('faltantes')?.subtitulo).toBe('5 células vazias');
    expect(peso?.descricao).toBe('3 · linhas 12, 141, 207');
    expect(peso?.opcoes.map((o) => o.rotulo)).toEqual([
      'Preencher com a mediana (69,8)',
      'Preencher com a média (70,3)',
      'Preencher com a moda (72)',
      'Remover a linha',
      'Manter como "não informado"',
    ]);
    expect(cidade?.opcoes.map((o) => o.valor)).toEqual(['preencher_moda', 'remover_linhas', 'manter']);
  });

  it('duplicados: uma linha só, com as cópias e a original', () => {
    const [linha] = porId('duplicados')?.linhas ?? [];
    expect(linha).toMatchObject({ rotulo: '45, 46, 47', descricao: 'Linha 44 (todas as colunas iguais, exceto as de identificador)' });
  });

  it('fora de faixa: ocorrências, faixa usada e limites na ação', () => {
    const [idade, peso] = porId('fora_de_faixa')?.linhas ?? [];
    expect(idade?.descricao).toBe('Linhas 19 e 201: 0 e 230');
    expect(idade?.detalhe).toBe('Faixa aceita: 1 a 110 (seus limites)');
    expect(peso?.detalhe).toBe('Faixa aceita: 38,5 a 102,1 (regra do IQR)');
    expect(idade?.acaoBase.limites).toEqual({ min: 1, max: 110 });
  });

  it('grafias: variações sem a forma preferida', () => {
    const [goiania] = porId('inconsistencia')?.linhas ?? [];
    expect(porId('inconsistencia')?.subtitulo).toBe('2 grupos em cidade');
    expect(goiania?.descricao).toBe('"Goiania" (6), "goiânia" (2)');
    expect(goiania?.opcoes[0]?.rotulo).toBe("Unificar 'Goiania', 'goiânia' → 'Goiânia'");
  });
});

describe('montarPedido', () => {
  it('leva só as ações diferentes de "manter", completas', () => {
    const pedido = montarPedido(montarSecoes(DIAGNOSTICO_SAUDE), {
      'faltantes:peso_kg': 'preencher_mediana',
      duplicados: 'remover',
      'inconsistencia:cidade:Goiânia': 'unificar',
      'faltantes:cidade': 'manter',
    });

    expect(pedido.acoes).toEqual([
      { problema: 'faltantes', acao: 'preencher_mediana', coluna: 'peso_kg', valor: null, limites: null, grupo: null },
      { problema: 'duplicados', acao: 'remover', coluna: null, valor: null, limites: null, grupo: null },
      { problema: 'inconsistencia', acao: 'unificar', coluna: 'cidade', valor: null, limites: null, grupo: 'Goiânia' },
    ]);
  });
});
```

`resumo.test.ts`:
```ts
import { describe, expect, it } from 'vitest';
import { criarResultado, DIAGNOSTICO_SAUDE, DIAGNOSTICO_VAZIO } from '../../testes/fixtures/limpeza';
import { avisoLimpezaAplicada, avisoLimpezaDesfeita, resumirDiagnostico, temProblemas } from './resumo';

describe('resumirDiagnostico', () => {
  it('monta os 4 cards do design', () => {
    expect(resumirDiagnostico(DIAGNOSTICO_SAUDE)).toEqual([
      { id: 'faltantes', rotulo: 'Faltantes', valor: '5', unidade: 'células', frase: 'Em 2 colunas; peso_kg tem 3.' },
      { id: 'duplicados', rotulo: 'Duplicados', valor: '3', unidade: 'linhas', frase: 'Cópias exatas da linha 44.' },
      { id: 'fora_de_faixa', rotulo: 'Fora de faixa', valor: '4', unidade: 'valores', frase: 'Fora dos limites que você definiu.' },
      { id: 'grafias', rotulo: 'Grafias diferentes', valor: '2', unidade: 'grupos', frase: 'Mesmo texto escrito de jeitos diferentes.' },
    ]);
  });

  it('sem problemas, frases de "nenhum"', () => {
    expect(resumirDiagnostico(DIAGNOSTICO_VAZIO)[0]).toMatchObject({ valor: '0', unidade: 'células', frase: 'Nenhum valor faltando.' });
    expect(temProblemas(DIAGNOSTICO_VAZIO)).toBe(false);
    expect(temProblemas(DIAGNOSTICO_SAUDE)).toBe(true);
  });
});

describe('avisos', () => {
  it('toast de limpeza aplicada: verbo no passado + quantidade', () => {
    expect(avisoLimpezaAplicada(230, criarResultado({ n_linhas: 227 }), 3)).toEqual({
      tipo: 'sucesso',
      titulo: 'Limpeza aplicada: 3 linhas removidas.',
      descricao: '3 ações aplicadas.',
    });
    expect(avisoLimpezaAplicada(230, criarResultado({ n_linhas: 230 }), 1).titulo).toBe('Limpeza aplicada: nenhuma linha removida.');
  });

  it('toast de desfazer', () => {
    expect(avisoLimpezaDesfeita(criarResultado({ n_linhas: 230 })).titulo).toBe('Limpeza desfeita: voltamos às 230 linhas do arquivo.');
  });
});
```

**Passo 2: rodar e ver falhar** → FAIL

**Passo 3: implementar**

`tipos.ts`:
```ts
import type { components } from '../../shared/api/schema';

type Esquemas = components['schemas'];

export type Diagnostico = Esquemas['Diagnostico'];
export type AcaoLimpeza = Esquemas['AcaoLimpeza'];
export type TipoAcao = AcaoLimpeza['acao'];
export type Problema = AcaoLimpeza['problema'];
export type PedidoLimpeza = Esquemas['PedidoLimpeza'];
export type ResultadoLimpeza = Esquemas['ResultadoLimpeza'];
export type EntradaLog = Esquemas['EntradaLog'];
export type Limites = Esquemas['Limites'];
export type ValoresSugeridos = Esquemas['ValoresSugeridos'];
export type ForaDeFaixaColuna = Esquemas['ForaDeFaixaColuna'];
export type InconsistenciaColuna = Esquemas['InconsistenciaColuna'];
export type GrupoGrafias = Esquemas['GrupoGrafias'];
export type Ocorrencia = Esquemas['Ocorrencia'];

export interface OpcaoAcao {
  valor: TipoAcao;
  rotulo: string;
}

/** Uma linha de seção: rótulo (coluna/grupo), descrição, Select de ação e o pedido sem a ação. */
export interface LinhaProblema {
  chave: string;
  rotulo: string;
  descricao: string;
  detalhe: string | null;
  opcoes: readonly OpcaoAcao[];
  acaoBase: Omit<AcaoLimpeza, 'acao'>;
}

export interface SecaoDiagnostico {
  id: Problema;
  titulo: string;
  subtitulo: string;
  cabecalhos: readonly [string, string];
  linhas: readonly LinhaProblema[];
}

export type EscolhasLimpeza = Readonly<Record<string, TipoAcao>>;
```

`textos.ts` (telas.md §3 e spec 16):
```ts
import { formatarInteiro } from '../../shared/lib/formatar';
import { contarLinhas, pluralizar } from '../../shared/lib/pluralizar';

export const TEXTOS_LIMPEZA = {
  titulo: 'Limpeza',
  ajuda: 'Encontramos alguns problemas comuns. Escolha o que fazer com cada um; nada muda até você clicar em "Aplicar limpeza".',
  carregando: 'Procurando problemas nos dados…',
  linhas: { singular: 'linha', plural: 'linhas', eMais: (n: number) => ` e mais ${formatarInteiro(n)}` },
  cards: {
    faltantes: {
      rotulo: 'Faltantes',
      unidade: ['célula', 'células'],
      nenhum: 'Nenhum valor faltando.',
      frase: (colunas: number, maior: string, n: number) =>
        `Em ${pluralizar(colunas, 'coluna', 'colunas')}; ${maior} tem ${formatarInteiro(n)}.`,
    },
    duplicados: {
      rotulo: 'Duplicados',
      unidade: ['linha', 'linhas'],
      nenhum: 'Nenhuma linha repetida.',
      umaOrigem: (linha: number) => `Cópias exatas da linha ${formatarInteiro(linha)}.`,
      variasOrigens: (n: number) => `Cópias de ${pluralizar(n, 'linha', 'linhas')}.`,
    },
    foraDeFaixa: {
      rotulo: 'Fora de faixa',
      unidade: ['valor', 'valores'],
      nenhum: 'Nenhum valor fora da faixa.',
      usuario: 'Fora dos limites que você definiu.',
      iqr: 'Longe demais dos outros valores da coluna.',
    },
    grafias: {
      rotulo: 'Grafias diferentes',
      unidade: ['grupo', 'grupos'],
      nenhum: 'Nenhuma grafia diferente.',
      frase: 'Mesmo texto escrito de jeitos diferentes.',
    },
  },
  secoes: {
    cabecalhoAcao: 'Ação',
    rotuloAcao: (item: string) => `Ação para ${item}`,
    faltantes: {
      titulo: 'Faltantes',
      cabecalhos: ['Coluna', 'Linhas afetadas'],
      subtitulo: (n: number) => pluralizar(n, 'célula vazia', 'células vazias'),
    },
    duplicados: {
      titulo: 'Duplicados',
      cabecalhos: ['Linhas', 'Igual a'],
      subtitulo: (n: number) => pluralizar(n, 'linha igual', 'linhas iguais'),
      igualA: (linhas: string) => `${linhas} (todas as colunas iguais, exceto as de identificador)`,
    },
    foraDeFaixa: {
      titulo: 'Fora de faixa',
      cabecalhos: ['Coluna', 'Valores'],
      subtitulo: (n: number) => pluralizar(n, 'valor', 'valores'),
      faixa: (min: string, max: string, origem: string) => `Faixa aceita: ${min} a ${max} (${origem})`,
      origem: { iqr: 'regra do IQR', usuario: 'seus limites' },
    },
    grafias: {
      titulo: 'Grafias diferentes',
      cabecalhos: ['Grupo', 'Variações encontradas'],
      subtitulo: (n: number, colunas: string) => `${pluralizar(n, 'grupo', 'grupos')} em ${colunas}`,
      naColuna: (coluna: string) => `na coluna ${coluna}`,
    },
    tipoMisto: {
      titulo: 'Textos em colunas de números',
      cabecalhos: ['Coluna', 'Valores'],
      subtitulo: (n: number) => pluralizar(n, 'valor', 'valores'),
    },
  },
  acoes: {
    manter: 'Manter',
    manterNaoInformado: 'Manter como "não informado"',
    preencherMediana: (v: string) => `Preencher com a mediana (${v})`,
    preencherMedia: (v: string) => `Preencher com a média (${v})`,
    preencherModa: (v: string) => `Preencher com a moda (${v})`,
    removerLinha: 'Remover a linha',
    remover: 'Remover',
    removerValor: 'Remover o valor',
    limitar: (min: string, max: string) => `Limitar ao limite (${min} a ${max})`,
    unificar: (variacoes: string, forma: string) => `Unificar ${variacoes} → '${forma}'`,
  },
  limites: {
    titulo: 'Limites por coluna',
    subtitulo: 'Opcional. Valores fora destes limites contam como "fora de faixa".',
    minimo: 'Mínimo',
    maximo: 'Máximo',
    erroNumero: 'Use só números, com vírgula para decimais (ex.: 1,72).',
    erroOrdem: (max: string) => `O mínimo precisa ser menor que o máximo (${max}). Ajuste um dos dois.`,
  },
  log: {
    titulo: 'O que fizemos',
    rotulo: 'Registro das ações',
    carregando: 'Carregando o registro…',
    vazio: 'Nada aplicado ainda. As ações que você aplicar aparecem aqui.',
    resultado: 'Resultado:',
    eram: (n: number) => ` (eram ${formatarInteiro(n)}).`,
  },
  botoes: {
    desfazer: 'Desfazer tudo',
    desfazendo: 'Desfazendo…',
    aplicar: 'Aplicar limpeza',
    aplicando: 'Aplicando…',
    semAcoes: 'Escolha ao menos uma ação diferente de "Manter".',
  },
  vazio: {
    titulo: 'Nenhum problema encontrado',
    descricao: 'Não encontramos problemas comuns: sem faltantes, duplicados, valores fora de faixa ou grafias diferentes.',
    continuar: 'Continuar para Análise',
  },
  toast: {
    aplicada: (removidas: number) =>
      removidas === 0
        ? 'Limpeza aplicada: nenhuma linha removida.'
        : `Limpeza aplicada: ${pluralizar(removidas, 'linha removida', 'linhas removidas')}.`,
    acoes: (n: number) => `${pluralizar(n, 'ação aplicada', 'ações aplicadas')}.`,
    desfeita: (n: number) => `Limpeza desfeita: voltamos às ${contarLinhas(n)} do arquivo.`,
  },
} as const;
```

`descricoes.ts`:
```ts
import { formatarInteiro } from '../../shared/lib/formatar';
import { formatarCelula } from '../../shared/lib/formatarCelula';
import { escolherForma } from '../../shared/lib/pluralizar';
import { TEXTOS_LIMPEZA as T } from './textos';
import type { EntradaLog, Ocorrencia } from './tipos';

const MAX_NUMEROS = 5;
const MAX_OCORRENCIAS = 3;
const LISTA_PT = new Intl.ListFormat('pt-BR', { style: 'long', type: 'conjunction' });

export function soma(valores: readonly number[]): number {
  return valores.reduce((total, valor) => total + valor, 0);
}

export function listarComE(itens: readonly string[]): string {
  return LISTA_PT.format(itens);
}

export function primeiraMaiuscula(texto: string): string {
  return texto.charAt(0).toUpperCase() + texto.slice(1);
}

/** "12, 141, 207" ou "1, 2, 3, 4, 5 e mais 2". */
export function listarNumeros(numeros: readonly number[], maximo = MAX_NUMEROS): string {
  const visiveis = numeros.slice(0, maximo).map(formatarInteiro).join(', ');
  const resto = numeros.length - maximo;
  return resto > 0 ? `${visiveis}${T.linhas.eMais(resto)}` : visiveis;
}

/** "linha 88" / "linhas 45, 46, 47". */
export function descreverLinhas(linhas: readonly number[]): string {
  return `${escolherForma(linhas.length, T.linhas.singular, T.linhas.plural)} ${listarNumeros(linhas)}`;
}

/** "Linhas 19 e 201: 0 e 230" (até 3 ocorrências + "e mais N"). */
export function descreverOcorrencias(ocorrencias: readonly Ocorrencia[]): string {
  const visiveis = ocorrencias.slice(0, MAX_OCORRENCIAS);
  const prefixo = primeiraMaiuscula(escolherForma(ocorrencias.length, T.linhas.singular, T.linhas.plural));
  const linhas = listarComE(visiveis.map((o) => formatarInteiro(o.linha)));
  const valores = listarComE(visiveis.map((o) => formatarCelula(o.valor)));
  const resto = ocorrencias.length - visiveis.length;
  return `${prefixo} ${linhas}: ${valores}${resto > 0 ? T.linhas.eMais(resto) : ''}`;
}

/** Detalhe mono do log: "linhas 45, 46, 47" · "17,2 → 1,72". */
export function detalheDoLog(entrada: EntradaLog): string {
  const partes: string[] = [];
  if (entrada.linhas_afetadas.length > 0) partes.push(descreverLinhas(entrada.linhas_afetadas));
  if (entrada.antes_exemplo !== '' && entrada.depois_exemplo !== '') {
    partes.push(`${entrada.antes_exemplo} → ${entrada.depois_exemplo}`);
  }
  return partes.join(' · ');
}

export function chaveDoLog(entrada: EntradaLog): string {
  return [entrada.quando, entrada.problema, entrada.acao, entrada.coluna ?? ''].join('|');
}
```

`secoes.ts`:
```ts
import { formatarInteiro, formatarNumero } from '../../shared/lib/formatar';
import { formatarCelula } from '../../shared/lib/formatarCelula';
import { descreverLinhas, descreverOcorrencias, listarComE, listarNumeros, primeiraMaiuscula, soma } from './descricoes';
import { TEXTOS_LIMPEZA as T } from './textos';
import type {
  Diagnostico,
  EscolhasLimpeza,
  ForaDeFaixaColuna,
  InconsistenciaColuna,
  LinhaProblema,
  OpcaoAcao,
  PedidoLimpeza,
  Problema,
  SecaoDiagnostico,
  ValoresSugeridos,
} from './tipos';

type BaseAcao = LinhaProblema['acaoBase'];

interface TextosSecao {
  titulo: string;
  cabecalhos: readonly [string, string];
}

const MANTER: OpcaoAcao = { valor: 'manter', rotulo: T.acoes.manter };
const OPCOES_DUPLICADOS: readonly OpcaoAcao[] = [{ valor: 'remover', rotulo: T.acoes.remover }, MANTER];
const OPCOES_TIPO_MISTO: readonly OpcaoAcao[] = [{ valor: 'marcar_faltante', rotulo: T.acoes.removerValor }, MANTER];
const MAX_COPIAS_ROTULO = 3;

function baseAcao(problema: Problema, extras: Partial<Omit<BaseAcao, 'problema'>> = {}): BaseAcao {
  return { problema, coluna: null, valor: null, limites: null, grupo: null, ...extras };
}

function secao(id: Problema, textos: TextosSecao, subtitulo: string, linhas: LinhaProblema[]): SecaoDiagnostico {
  return { id, titulo: textos.titulo, subtitulo, cabecalhos: textos.cabecalhos, linhas };
}

function opcoesFaltantes({ media, mediana, moda }: ValoresSugeridos): OpcaoAcao[] {
  const opcoes: OpcaoAcao[] = [];
  if (mediana !== null) opcoes.push({ valor: 'preencher_mediana', rotulo: T.acoes.preencherMediana(formatarNumero(mediana)) });
  if (media !== null) opcoes.push({ valor: 'preencher_media', rotulo: T.acoes.preencherMedia(formatarNumero(media)) });
  if (moda !== null) opcoes.push({ valor: 'preencher_moda', rotulo: T.acoes.preencherModa(formatarCelula(moda)) });
  opcoes.push({ valor: 'remover_linhas', rotulo: T.acoes.removerLinha }, { valor: 'manter', rotulo: T.acoes.manterNaoInformado });
  return opcoes;
}

function secaoFaltantes(itens: Diagnostico['faltantes']): SecaoDiagnostico {
  const linhas = itens.map((item) => ({
    chave: `faltantes:${item.coluna}`,
    rotulo: item.coluna,
    descricao: `${formatarInteiro(item.n)} · ${descreverLinhas(item.linhas)}`,
    detalhe: null,
    opcoes: opcoesFaltantes(item.sugeridos),
    acaoBase: baseAcao('faltantes', { coluna: item.coluna }),
  }));
  const textos = T.secoes.faltantes;
  return secao('faltantes', textos, textos.subtitulo(soma(itens.map((i) => i.n))), linhas);
}

/** A API aplica "remover duplicados" a todos os grupos de uma vez: uma linha, um Select. */
function secaoDuplicados(grupos: Diagnostico['duplicados']): SecaoDiagnostico {
  const copias = grupos.flatMap((g) => g.copias);
  const originais = descreverLinhas(grupos.map((g) => g.linha_original));
  const textos = T.secoes.duplicados;
  const linhas: LinhaProblema[] =
    grupos.length === 0
      ? []
      : [{
          chave: 'duplicados',
          rotulo: listarNumeros(copias, MAX_COPIAS_ROTULO),
          descricao: textos.igualA(primeiraMaiuscula(originais)),
          detalhe: null,
          opcoes: OPCOES_DUPLICADOS,
          acaoBase: baseAcao('duplicados'),
        }];
  return secao('duplicados', textos, textos.subtitulo(copias.length), linhas);
}

function opcoesForaDeFaixa(item: ForaDeFaixaColuna): OpcaoAcao[] {
  const limites = T.acoes.limitar(formatarNumero(item.limite_inferior), formatarNumero(item.limite_superior));
  return [
    { valor: 'marcar_faltante', rotulo: T.acoes.removerValor },
    { valor: 'limitar', rotulo: limites },
    { valor: 'remover_linhas', rotulo: T.acoes.removerLinha },
    MANTER,
  ];
}

function secaoForaDeFaixa(itens: Diagnostico['fora_de_faixa']): SecaoDiagnostico {
  const textos = T.secoes.foraDeFaixa;
  const linhas = itens.map((item) => ({
    chave: `fora_de_faixa:${item.coluna}`,
    rotulo: item.coluna,
    descricao: descreverOcorrencias(item.ocorrencias),
    detalhe: textos.faixa(formatarNumero(item.limite_inferior), formatarNumero(item.limite_superior), textos.origem[item.origem]),
    opcoes: opcoesForaDeFaixa(item),
    acaoBase: baseAcao('fora_de_faixa', { coluna: item.coluna, limites: { min: item.limite_inferior, max: item.limite_superior } }),
  }));
  return secao('fora_de_faixa', textos, textos.subtitulo(soma(itens.map((i) => i.ocorrencias.length))), linhas);
}

function linhasGrafias(item: InconsistenciaColuna): LinhaProblema[] {
  return item.grupos.map((grupo) => {
    const variacoes = grupo.variacoes.filter((v) => v.texto !== grupo.forma_preferida);
    const unificar = T.acoes.unificar(variacoes.map((v) => `'${v.texto}'`).join(', '), grupo.forma_preferida);
    return {
      chave: `inconsistencia:${item.coluna}:${grupo.forma_preferida}`,
      rotulo: grupo.forma_preferida,
      descricao: variacoes.map((v) => `"${v.texto}" (${formatarInteiro(v.n)})`).join(', '),
      detalhe: T.secoes.grafias.naColuna(item.coluna),
      opcoes: [{ valor: 'unificar', rotulo: unificar }, MANTER],
      acaoBase: baseAcao('inconsistencia', { coluna: item.coluna, grupo: grupo.forma_preferida }),
    };
  });
}

function secaoGrafias(itens: Diagnostico['inconsistencias']): SecaoDiagnostico {
  const linhas = itens.flatMap(linhasGrafias);
  const textos = T.secoes.grafias;
  return secao('inconsistencia', textos, textos.subtitulo(linhas.length, listarComE(itens.map((i) => i.coluna))), linhas);
}

function secaoTipoMisto(itens: Diagnostico['tipo_misto']): SecaoDiagnostico {
  const linhas = itens.map((item) => ({
    chave: `tipo_misto:${item.coluna}`,
    rotulo: item.coluna,
    descricao: descreverOcorrencias(item.ocorrencias),
    detalhe: null,
    opcoes: OPCOES_TIPO_MISTO,
    acaoBase: baseAcao('tipo_misto', { coluna: item.coluna }),
  }));
  const textos = T.secoes.tipoMisto;
  return secao('tipo_misto', textos, textos.subtitulo(soma(itens.map((i) => i.ocorrencias.length))), linhas);
}

/** Seções com pelo menos uma linha, na ordem do design 3a (tipo misto só aparece se houver). */
export function montarSecoes(diagnostico: Diagnostico): SecaoDiagnostico[] {
  return [
    secaoFaltantes(diagnostico.faltantes),
    secaoDuplicados(diagnostico.duplicados),
    secaoForaDeFaixa(diagnostico.fora_de_faixa),
    secaoGrafias(diagnostico.inconsistencias),
    secaoTipoMisto(diagnostico.tipo_misto),
  ].filter((s) => s.linhas.length > 0);
}

/** Dnn-manter: só vão para a API as linhas cuja escolha é diferente de "manter". */
export function montarPedido(secoes: readonly SecaoDiagnostico[], escolhas: EscolhasLimpeza): PedidoLimpeza {
  const acoes = secoes
    .flatMap((s) => s.linhas)
    .flatMap((linha) => {
      const acao = escolhas[linha.chave] ?? 'manter';
      return acao === 'manter' ? [] : [{ ...linha.acaoBase, acao }];
    });
  return { acoes };
}
```
> Se o `schema.d.ts` gerar `valor`/`limites`/`grupo` como opcionais, o objeto completo continua válido. Se gerar `AcaoLimpeza-Input`, ajuste só `tipos.ts`.

`resumo.ts`:
```ts
import { formatarInteiro } from '../../shared/lib/formatar';
import { escolherForma } from '../../shared/lib/pluralizar';
import { soma } from './descricoes';
import { TEXTOS_LIMPEZA as T } from './textos';
import type { Diagnostico, ResultadoLimpeza } from './tipos';

export interface CardResumo {
  id: string;
  rotulo: string;
  valor: string;
  unidade: string;
  frase: string;
}

export interface AvisoLimpeza {
  tipo: 'sucesso';
  titulo: string;
  descricao: string;
}

interface TextosCard {
  rotulo: string;
  unidade: readonly [string, string];
}

function card(id: string, textos: TextosCard, total: number, frase: string): CardResumo {
  return { id, rotulo: textos.rotulo, valor: formatarInteiro(total), unidade: escolherForma(total, ...textos.unidade), frase };
}

function fraseFaltantes(itens: Diagnostico['faltantes']): string {
  const maior = itens.toSorted((a, b) => b.n - a.n)[0];
  if (maior === undefined) return T.cards.faltantes.nenhum;
  return T.cards.faltantes.frase(itens.length, maior.coluna, maior.n);
}

function fraseDuplicados(grupos: Diagnostico['duplicados']): string {
  const primeiro = grupos[0];
  if (primeiro === undefined) return T.cards.duplicados.nenhum;
  return grupos.length === 1 ? T.cards.duplicados.umaOrigem(primeiro.linha_original) : T.cards.duplicados.variasOrigens(grupos.length);
}

function fraseForaDeFaixa(itens: Diagnostico['fora_de_faixa']): string {
  if (itens.length === 0) return T.cards.foraDeFaixa.nenhum;
  return itens.some((i) => i.origem === 'usuario') ? T.cards.foraDeFaixa.usuario : T.cards.foraDeFaixa.iqr;
}

/** 4 cards do topo da tela 3 (tipo misto não tem card no design; aparece só como seção). */
export function resumirDiagnostico(d: Diagnostico): CardResumo[] {
  const grupos = soma(d.inconsistencias.map((i) => i.grupos.length));
  return [
    card('faltantes', T.cards.faltantes, soma(d.faltantes.map((f) => f.n)), fraseFaltantes(d.faltantes)),
    card('duplicados', T.cards.duplicados, soma(d.duplicados.map((g) => g.copias.length)), fraseDuplicados(d.duplicados)),
    card('fora_de_faixa', T.cards.foraDeFaixa, soma(d.fora_de_faixa.map((i) => i.ocorrencias.length)), fraseForaDeFaixa(d.fora_de_faixa)),
    card('grafias', T.cards.grafias, grupos, grupos === 0 ? T.cards.grafias.nenhum : T.cards.grafias.frase),
  ];
}

export function temProblemas(d: Diagnostico): boolean {
  return [d.faltantes, d.duplicados, d.fora_de_faixa, d.inconsistencias, d.tipo_misto].some((lista) => lista.length > 0);
}

export function avisoLimpezaAplicada(nAntes: number, resultado: ResultadoLimpeza, nAcoes: number): AvisoLimpeza {
  return { tipo: 'sucesso', titulo: T.toast.aplicada(nAntes - resultado.n_linhas), descricao: T.toast.acoes(nAcoes) };
}

export function avisoLimpezaDesfeita(resultado: ResultadoLimpeza): AvisoLimpeza {
  return { tipo: 'sucesso', titulo: T.toast.desfeita(resultado.n_linhas), descricao: T.log.vazio };
}
```

**Passo 4: rodar e ver passar** → 14 passed. **Passo 5: commit**
```bash
git add frontend/src/features/limpeza
git commit -m "feat(limpeza): transforma o diagnóstico em seções, cards e pedido de limpeza"
```

---

### Tarefa 16: Limpeza — limites, escolhas e `api.ts`

**Arquivos:**
- Criar em `frontend/src/features/limpeza/`: `limites.ts` (+ `.test.ts`), `hooks/useLimitesPorColuna.ts`, `hooks/useEscolhasLimpeza.ts` (+ `hooks/hooks.test.ts`), `api.ts` (+ `api.test.tsx`)

**Passo 1: escrever os testes (falham)**

`limites.test.ts`:
```ts
import { describe, expect, it } from 'vitest';
import { serializarLimites, validarLimite } from './limites';

describe('validarLimite', () => {
  it('aceita vírgula decimal e um lado só', () => {
    expect(validarLimite({ min: '1,20', max: '' })).toEqual({ limites: { min: 1.2, max: null }, erroMin: null, erroMax: null });
  });

  it('vazio não é erro nem limite', () => {
    expect(validarLimite({ min: '', max: ' ' })).toEqual({ limites: null, erroMin: null, erroMax: null });
  });

  it('texto que não é número avisa no campo', () => {
    expect(validarLimite({ min: 'abc', max: '10' }).erroMin).toBe('Use só números, com vírgula para decimais (ex.: 1,72).');
  });

  it('mínimo maior ou igual ao máximo avisa com o máximo formatado', () => {
    expect(validarLimite({ min: '120', max: '110' })).toEqual({
      limites: null,
      erroMin: 'O mínimo precisa ser menor que o máximo (110). Ajuste um dos dois.',
      erroMax: null,
    });
  });
});

describe('serializarLimites', () => {
  it('JSON estável (colunas em ordem) só com limites válidos', () => {
    expect(serializarLimites({ peso_kg: { min: '10', max: '5' }, idade: { min: '1', max: '110' }, altura_m: { min: '1,2', max: '' } })).toBe(
      '{"altura_m":{"min":1.2,"max":null},"idade":{"min":1,"max":110}}',
    );
    expect(serializarLimites({})).toBe('');
  });
});
```

`hooks/hooks.test.ts`:
```ts
import { act, renderHook } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { useEscolhasLimpeza } from './useEscolhasLimpeza';
import { useLimitesPorColuna } from './useLimitesPorColuna';

describe('useLimitesPorColuna', () => {
  it('guarda o texto digitado e expõe o JSON dos limites válidos', () => {
    const { result } = renderHook(() => useLimitesPorColuna());

    act(() => {
      result.current.alterar('idade', 'min', '1');
    });
    act(() => {
      result.current.alterar('idade', 'max', '110');
    });

    expect(result.current.textos.idade).toEqual({ min: '1', max: '110' });
    expect(result.current.json).toBe('{"idade":{"min":1,"max":110}}');
  });
});

describe('useEscolhasLimpeza', () => {
  it('escolhe por chave e limpa tudo', () => {
    const { result } = renderHook(() => useEscolhasLimpeza());

    act(() => {
      result.current.escolher('duplicados', 'remover');
    });
    expect(result.current.valores).toEqual({ duplicados: 'remover' });

    act(() => {
      result.current.limpar();
    });
    expect(result.current.valores).toEqual({});
  });
});
```

`api.test.tsx`:
```tsx
import { act } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { chavesDataset } from '../../shared/api/dataset';
import { chamadasPara, simularApi } from '../../testes/api';
import { COLUNAS_SAUDE, ID_DATASET } from '../../testes/fixtures/datasets';
import { criarResultado } from '../../testes/fixtures/limpeza';
import { criarClienteTeste, renderizarHook } from '../../testes/renderizar';
import { caminhoDiagnostico, useAplicarLimpeza } from './api';

const CAMINHO_LIMPEZA = `/datasets/${ID_DATASET}/limpeza`;

describe('caminhoDiagnostico', () => {
  it('sem limites não manda a query', () => {
    expect(caminhoDiagnostico(ID_DATASET, '')).toBe(`/datasets/${ID_DATASET}/diagnostico`);
  });

  it('codifica os limites em JSON na query', () => {
    expect(caminhoDiagnostico(ID_DATASET, '{"idade":{"min":1,"max":110}}')).toBe(
      `/datasets/${ID_DATASET}/diagnostico?limites=%7B%22idade%22%3A%7B%22min%22%3A1%2C%22max%22%3A110%7D%7D`,
    );
  });
});

describe('useAplicarLimpeza', () => {
  it('envia o pedido e invalida tudo do dataset', async () => {
    const falso = simularApi([{ metodo: 'POST', caminho: CAMINHO_LIMPEZA, corpo: criarResultado() }]);
    const cliente = criarClienteTeste();
    cliente.setQueryData(chavesDataset.colunas(ID_DATASET), COLUNAS_SAUDE);
    const { result } = renderizarHook(() => useAplicarLimpeza(ID_DATASET), { cliente });
    const pedido = { acoes: [] };

    await act(async () => {
      await result.current.mutateAsync(pedido);
    });

    expect(chamadasPara(falso, 'POST', CAMINHO_LIMPEZA)[0]?.corpo).toEqual(pedido);
    expect(cliente.getQueryState(chavesDataset.colunas(ID_DATASET))?.isInvalidated).toBe(true);
  });
});
```

**Passo 2: rodar e ver falhar** → FAIL

**Passo 3: implementar**

`limites.ts`:
```ts
import { formatarNumero, lerNumeroPtBr } from '../../shared/lib/formatar';
import { TEXTOS_LIMPEZA as T } from './textos';
import type { Limites } from './tipos';

export interface TextoLimite {
  min: string;
  max: string;
}

export interface ResultadoLimite {
  limites: Limites | null;
  erroMin: string | null;
  erroMax: string | null;
}

export const LIMITE_VAZIO: TextoLimite = { min: '', max: '' };

type Leitura = { estado: 'vazio' } | { estado: 'invalido' } | { estado: 'ok'; numero: number };

function lerCampo(texto: string): Leitura {
  if (texto.trim() === '') return { estado: 'vazio' };
  const numero = lerNumeroPtBr(texto);
  return numero === null ? { estado: 'invalido' } : { estado: 'ok', numero };
}

function numeroDe(leitura: Leitura): number | null {
  return leitura.estado === 'ok' ? leitura.numero : null;
}

function erroDe(leitura: Leitura): string | null {
  return leitura.estado === 'invalido' ? T.limites.erroNumero : null;
}

/** Campos Mínimo/Máximo de uma coluna → limite para a API ou mensagem de erro no campo. */
export function validarLimite(texto: TextoLimite): ResultadoLimite {
  const min = lerCampo(texto.min);
  const max = lerCampo(texto.max);
  const erroMin = erroDe(min);
  const erroMax = erroDe(max);
  if (erroMin !== null || erroMax !== null) return { limites: null, erroMin, erroMax };
  const vMin = numeroDe(min);
  const vMax = numeroDe(max);
  if (vMin === null && vMax === null) return { limites: null, erroMin: null, erroMax: null };
  if (vMin !== null && vMax !== null && vMin >= vMax) {
    return { limites: null, erroMin: T.limites.erroOrdem(formatarNumero(vMax)), erroMax: null };
  }
  return { limites: { min: vMin, max: vMax }, erroMin: null, erroMax: null };
}

/** JSON da query `?limites=` (colunas em ordem para a chave do cache ser estável); '' sem limites. */
export function serializarLimites(textos: Readonly<Record<string, TextoLimite>>): string {
  const validos = Object.entries(textos)
    .toSorted(([a], [b]) => a.localeCompare(b))
    .flatMap(([coluna, texto]) => {
      const { limites } = validarLimite(texto);
      return limites === null ? [] : [[coluna, limites] as const];
    });
  return validos.length === 0 ? '' : JSON.stringify(Object.fromEntries(validos));
}
```

`hooks/useLimitesPorColuna.ts`:
```ts
import { useCallback, useState } from 'react';
import { LIMITE_VAZIO, serializarLimites, type TextoLimite } from '../limites';

export function useLimitesPorColuna() {
  const [textos, setTextos] = useState<Readonly<Record<string, TextoLimite>>>({});
  const alterar = useCallback((coluna: string, campo: keyof TextoLimite, texto: string) => {
    setTextos((atuais) => ({ ...atuais, [coluna]: { ...(atuais[coluna] ?? LIMITE_VAZIO), [campo]: texto } }));
  }, []);
  return { textos, alterar, json: serializarLimites(textos) };
}
```

`hooks/useEscolhasLimpeza.ts`:
```ts
import { useCallback, useState } from 'react';
import type { EscolhasLimpeza, TipoAcao } from '../tipos';

/** Escolha por linha de seção; ausente = "manter" (Dnn-manter). */
export function useEscolhasLimpeza() {
  const [valores, setValores] = useState<EscolhasLimpeza>({});
  const escolher = useCallback((chave: string, acao: TipoAcao) => {
    setValores((atuais) => ({ ...atuais, [chave]: acao }));
  }, []);
  const limpar = useCallback(() => {
    setValores({});
  }, []);
  return { valores, escolher, limpar };
}
```

`api.ts`:
```ts
import { keepPreviousData, useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { requisitar } from '../../shared/api/cliente';
import { corpoJson } from '../../shared/api/corpoJson';
import { caminhoDataset, chavesDataset } from '../../shared/api/dataset';
import { useAvisarErro } from '../../shared/ui/useAvisarErro';
import type { Diagnostico, PedidoLimpeza, ResultadoLimpeza } from './tipos';

/** Dnn-limites: o diagnóstico com limites novos espera 600 ms sem digitação. */
export const ATRASO_LIMITES_MS = 600;

export const chavesLimpeza = {
  diagnostico: (id: string, limitesJson: string) => [...chavesDataset.diagnostico(id), limitesJson] as const,
};

export function caminhoDiagnostico(id: string, limitesJson: string): string {
  const consulta = limitesJson === '' ? '' : `?limites=${encodeURIComponent(limitesJson)}`;
  return caminhoDataset(id, `/diagnostico${consulta}`);
}

export function useDiagnostico(datasetId: string, limitesJson: string) {
  return useQuery({
    queryKey: chavesLimpeza.diagnostico(datasetId, limitesJson),
    queryFn: () => requisitar<Diagnostico>(caminhoDiagnostico(datasetId, limitesJson)),
    placeholderData: keepPreviousData,
  });
}

/** Limpeza muda linhas, tipos, log, diagnóstico e análises: invalida o prefixo do dataset (Dnn-chaves). */
function useAoConcluirLimpeza(datasetId: string) {
  const cliente = useQueryClient();
  const avisarErro = useAvisarErro();
  return {
    onSuccess: () => cliente.invalidateQueries({ queryKey: chavesDataset.todas(datasetId) }),
    onError: avisarErro,
  };
}

export function useAplicarLimpeza(datasetId: string) {
  const callbacks = useAoConcluirLimpeza(datasetId);
  return useMutation({
    mutationFn: (pedido: PedidoLimpeza) =>
      requisitar<ResultadoLimpeza>(caminhoDataset(datasetId, '/limpeza'), corpoJson('POST', pedido)),
    ...callbacks,
  });
}

export function useDesfazerLimpeza(datasetId: string) {
  const callbacks = useAoConcluirLimpeza(datasetId);
  return useMutation({
    mutationFn: () => requisitar<ResultadoLimpeza>(caminhoDataset(datasetId, '/limpeza/desfazer'), { method: 'POST' }),
    ...callbacks,
  });
}
```

**Passo 4: rodar e ver passar** → 10 passed. **Passo 5: commit**
```bash
git add frontend/src/features/limpeza
git commit -m "feat(limpeza): valida limites por coluna e liga diagnóstico, aplicar e desfazer"
```

---

### Tarefa 17: Limpeza — componentes

**Arquivos:**
- Criar em `frontend/src/features/limpeza/components/`: `SecaoProblema.tsx`, `CardsResumoLimpeza.tsx`, `LimitesPorColuna.tsx`, `PainelLog.tsx`, cada um com `.module.css` (exceto `CardsResumoLimpeza`, que só tem a grade) e um `componentes.test.tsx` para os quatro

**Passo 1: escrever os testes (falham)** — `componentes.test.tsx`
```tsx
import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import { criarResumo } from '../../../testes/fixtures/datasets';
import { criarEntradaLog, DIAGNOSTICO_SAUDE } from '../../../testes/fixtures/limpeza';
import { montarSecoes } from '../secoes';
import CardsResumoLimpeza from './CardsResumoLimpeza';
import LimitesPorColuna from './LimitesPorColuna';
import PainelLog from './PainelLog';
import SecaoProblema from './SecaoProblema';

const [FALTANTES] = montarSecoes(DIAGNOSTICO_SAUDE);

describe('SecaoProblema', () => {
  it('lista as linhas com o Select em "Manter" e avisa a escolha', async () => {
    if (FALTANTES === undefined) throw new Error('fixture sem faltantes');
    const aoEscolher = vi.fn();
    render(<SecaoProblema secao={FALTANTES} escolhas={{}} aoEscolher={aoEscolher} />);

    const regiao = screen.getByRole('region', { name: 'Faltantes' });
    expect(within(regiao).getByText('5 células vazias')).toBeInTheDocument();
    const select = within(regiao).getByRole('combobox', { name: 'Ação para peso_kg' });
    expect(select).toHaveValue('manter');

    await userEvent.selectOptions(select, 'preencher_mediana');
    expect(aoEscolher).toHaveBeenCalledWith('faltantes:peso_kg', 'preencher_mediana');
  });
});

describe('CardsResumoLimpeza', () => {
  it('mostra os 4 cards', () => {
    render(<CardsResumoLimpeza diagnostico={DIAGNOSTICO_SAUDE} />);
    expect(screen.getByText('Cópias exatas da linha 44.')).toBeInTheDocument();
    expect(screen.getByText('Grafias diferentes')).toBeInTheDocument();
  });
});

describe('LimitesPorColuna', () => {
  it('um grupo por coluna numérica, com erro de ordem no mínimo', () => {
    render(<LimitesPorColuna colunas={['idade', 'peso_kg']} textos={{ idade: { min: '120', max: '110' } }} aoMudar={vi.fn()} />);

    const idade = screen.getByRole('group', { name: 'idade' });
    expect(within(idade).getByLabelText('Mínimo')).toHaveValue('120');
    expect(within(idade).getByText('O mínimo precisa ser menor que o máximo (110). Ajuste um dos dois.')).toBeInTheDocument();
  });

  it('sem colunas numéricas não aparece', () => {
    const { container } = render(<LimitesPorColuna colunas={[]} textos={{}} aoMudar={vi.fn()} />);
    expect(container).toBeEmptyDOMElement();
  });
});

describe('PainelLog', () => {
  it('frases com detalhe e o resultado', () => {
    render(<PainelLog resumo={criarResumo({ n_linhas: 227, log_limpeza: [criarEntradaLog()] })} />);

    const painel = screen.getByRole('complementary', { name: 'Registro das ações' });
    expect(within(painel).getByText('Removemos 3 linhas duplicadas.')).toBeInTheDocument();
    expect(within(painel).getByText('linhas 45, 46, 47')).toBeInTheDocument();
    expect(painel).toHaveTextContent('Resultado: 227 linhas (eram 230).');
  });

  it('sem ações, explica onde elas vão aparecer', () => {
    render(<PainelLog resumo={criarResumo()} />);
    expect(screen.getByText('Nada aplicado ainda. As ações que você aplicar aparecem aqui.')).toBeInTheDocument();
  });
});
```

**Passo 2: rodar e ver falhar** → FAIL

**Passo 3: implementar**

`SecaoProblema.tsx` (uma seção do 3a; reaproveitada pelas 5):
```tsx
import { useId } from 'react';
import Select from '../../../shared/ui/Select';
import { TEXTOS_LIMPEZA as T } from '../textos';
import type { EscolhasLimpeza, SecaoDiagnostico, TipoAcao } from '../tipos';
import estilos from './SecaoProblema.module.css';

interface PropsSecaoProblema {
  secao: SecaoDiagnostico;
  escolhas: EscolhasLimpeza;
  aoEscolher: (chave: string, acao: TipoAcao) => void;
}

export default function SecaoProblema({ secao, escolhas, aoEscolher }: Readonly<PropsSecaoProblema>) {
  const idTitulo = useId();
  return (
    <section className={estilos.secao} aria-labelledby={idTitulo}>
      <header className={estilos.cabecalho}>
        <h2 id={idTitulo} className={estilos.titulo}>{secao.titulo}</h2>
        <span className={estilos.subtitulo}>{secao.subtitulo}</span>
      </header>
      <table className={estilos.tabela} aria-labelledby={idTitulo}>
        <colgroup>
          <col className={estilos.colunaRotulo} />
          <col />
          <col className={estilos.colunaAcao} />
        </colgroup>
        <thead>
          <tr>
            <th scope="col">{secao.cabecalhos[0]}</th>
            <th scope="col">{secao.cabecalhos[1]}</th>
            <th scope="col">{T.secoes.cabecalhoAcao}</th>
          </tr>
        </thead>
        <tbody>
          {secao.linhas.map((linha) => (
            <tr key={linha.chave}>
              <th scope="row" className={estilos.rotulo}>{linha.rotulo}</th>
              <td className={estilos.descricao}>
                {linha.descricao}
                {linha.detalhe === null ? null : <span className={estilos.detalhe}>{linha.detalhe}</span>}
              </td>
              <td>
                <Select
                  rotulo={T.secoes.rotuloAcao(linha.rotulo)}
                  rotuloOculto
                  altura={36}
                  valor={escolhas[linha.chave] ?? 'manter'}
                  opcoes={linha.opcoes}
                  aoMudar={(acao) => { aoEscolher(linha.chave, acao); }}
                />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
```

`SecaoProblema.module.css` (Tela 3):

| Seletor | Propriedades |
|---|---|
| `.secao` | `background:var(--cor-superficie); border:1px solid var(--cor-borda); border-radius:var(--raio-lg); box-shadow:var(--sombra-1); overflow:hidden` |
| `.cabecalho` | `display:flex; align-items:baseline; gap:12px; padding:16px 20px; border-bottom:1px solid var(--cor-borda)` |
| `.titulo` | `margin:0; font-size:17px; font-weight:600` |
| `.subtitulo` | `font-size:14px; color:var(--cor-texto-2)` |
| `.tabela` | `width:100%; border-collapse:collapse; table-layout:fixed` |
| `.colunaRotulo` | `width:136px` (120 + padding) |
| `.colunaAcao` | `width:270px` (250 + padding) |
| `.tabela thead th` | `padding:8px 0 6px 20px; text-align:left; font-size:12.5px; font-weight:600; color:var(--cor-texto-2)` |
| `.tabela thead th:last-child`, `.tabela td:last-child` | `padding-right:20px` |
| `.tabela tbody tr` | `border-top:1px solid var(--cor-borda)` |
| `.tabela td`, `.rotulo` | `padding:10px 0 10px 20px; vertical-align:middle` |
| `.rotulo` | `text-align:left; font:600 13.5px var(--fonte-mono); overflow-wrap:anywhere` |
| `.descricao` | `font-size:14px; line-height:1.45; font-variant-numeric:tabular-nums` |
| `.detalhe` | `display:block; margin-top:2px; font-size:12.5px; color:var(--cor-texto-2)` |

`CardsResumoLimpeza.tsx`:
```tsx
import CardMetrica from '../../../shared/ui/CardMetrica';
import { resumirDiagnostico } from '../resumo';
import type { Diagnostico } from '../tipos';
import estilos from './CardsResumoLimpeza.module.css';

export default function CardsResumoLimpeza({ diagnostico }: Readonly<{ diagnostico: Diagnostico }>) {
  return (
    <div className={estilos.grade}>
      {resumirDiagnostico(diagnostico).map((card) => (
        <CardMetrica key={card.id} rotulo={card.rotulo} valor={card.valor} unidade={card.unidade} interpretacao={card.frase} />
      ))}
    </div>
  );
}
```

| Seletor (`CardsResumoLimpeza.module.css`) | Propriedades |
|---|---|
| `.grade` | `display:grid; grid-template-columns:repeat(4, minmax(0, 1fr)); gap:16px` |
| `@media (max-width:1279px)` › `.grade` | `grid-template-columns:repeat(2, minmax(0, 1fr))` |

`LimitesPorColuna.tsx`:
```tsx
import CampoNumero from '../../../shared/ui/CampoNumero';
import Card from '../../../shared/ui/Card';
import { LIMITE_VAZIO, type TextoLimite, validarLimite } from '../limites';
import { TEXTOS_LIMPEZA as T } from '../textos';
import estilos from './LimitesPorColuna.module.css';

type AoMudar = (coluna: string, campo: keyof TextoLimite, texto: string) => void;

interface PropsLimitesPorColuna {
  colunas: readonly string[];
  textos: Readonly<Record<string, TextoLimite>>;
  aoMudar: AoMudar;
}

function CamposLimite({ coluna, texto, aoMudar }: Readonly<{ coluna: string; texto: TextoLimite; aoMudar: AoMudar }>) {
  const { erroMin, erroMax } = validarLimite(texto);
  return (
    <fieldset className={estilos.coluna}>
      <legend className={estilos.nome}>{coluna}</legend>
      <div className={estilos.campos}>
        <CampoNumero
          rotulo={T.limites.minimo}
          valor={texto.min}
          aoMudar={(valor) => { aoMudar(coluna, 'min', valor); }}
          {...(erroMin === null ? {} : { erro: erroMin })}
        />
        <CampoNumero
          rotulo={T.limites.maximo}
          valor={texto.max}
          aoMudar={(valor) => { aoMudar(coluna, 'max', valor); }}
          {...(erroMax === null ? {} : { erro: erroMax })}
        />
      </div>
    </fieldset>
  );
}

/** Limites opcionais por coluna numérica (3a); só limites válidos entram no diagnóstico (Dnn-limites). */
export default function LimitesPorColuna({ colunas, textos, aoMudar }: Readonly<PropsLimitesPorColuna>) {
  if (colunas.length === 0) return null;
  return (
    <Card titulo={T.limites.titulo} subtitulo={T.limites.subtitulo}>
      <div className={estilos.grade}>
        {colunas.map((coluna) => (
          <CamposLimite key={coluna} coluna={coluna} texto={textos[coluna] ?? LIMITE_VAZIO} aoMudar={aoMudar} />
        ))}
      </div>
    </Card>
  );
}
```

| Seletor (`LimitesPorColuna.module.css`) | Propriedades |
|---|---|
| `.grade` | `display:grid; grid-template-columns:repeat(auto-fill, minmax(220px, 1fr)); gap:16px` |
| `.coluna` | `display:flex; flex-direction:column; gap:6px; margin:0; padding:0; border:0; min-width:0` |
| `.nome` | `padding:0; font:600 13.5px var(--fonte-mono)` |
| `.campos` | `display:grid; grid-template-columns:1fr 1fr; gap:8px; align-items:start` |

`PainelLog.tsx`:
```tsx
import type { ResumoDataset } from '../../../shared/api/dataset';
import { contarLinhas } from '../../../shared/lib/pluralizar';
import Icone from '../../../shared/ui/Icone';
import { chaveDoLog, detalheDoLog } from '../descricoes';
import { TEXTOS_LIMPEZA as T } from '../textos';
import type { EntradaLog } from '../tipos';
import estilos from './PainelLog.module.css';

function ListaLog({ log }: Readonly<{ log: readonly EntradaLog[] }>) {
  return (
    <ol className={estilos.lista}>
      {log.map((entrada) => {
        const detalhe = detalheDoLog(entrada);
        return (
          <li key={chaveDoLog(entrada)} className={estilos.item}>
            <span className={estilos.marca}>
              <Icone nome="check" tamanho={18} />
            </span>
            <span>
              {entrada.frase}
              {detalhe === '' ? null : <span className={estilos.detalhe}>{detalhe}</span>}
            </span>
          </li>
        );
      })}
    </ol>
  );
}

/** "O que fizemos" (3a): log acumulado vindo do resumo do dataset. */
export default function PainelLog({ resumo }: Readonly<{ resumo: ResumoDataset }>) {
  const log = resumo.log_limpeza;
  const mudou = resumo.n_linhas !== resumo.n_linhas_original;
  return (
    <aside className={estilos.painel} aria-label={T.log.rotulo}>
      <div className={estilos.topo}>
        <Icone nome="history" tamanho={20} />
        <h2 className={estilos.titulo}>{T.log.titulo}</h2>
      </div>
      {log.length === 0 ? <p className={estilos.vazio}>{T.log.vazio}</p> : <ListaLog log={log} />}
      <p className={estilos.resultado}>
        {T.log.resultado} <strong>{contarLinhas(resumo.n_linhas)}</strong>
        {mudou ? T.log.eram(resumo.n_linhas_original) : '.'}
      </p>
    </aside>
  );
}
```

| Seletor (`PainelLog.module.css`) | Propriedades |
|---|---|
| `.painel` | `display:flex; flex-direction:column; gap:14px; padding:18px 20px; background:var(--cor-superficie); border:1px solid var(--cor-borda); border-radius:var(--raio-lg); box-shadow:var(--sombra-1)` |
| `.topo` | `display:flex; align-items:center; gap:8px; color:var(--cor-texto-2)` |
| `.titulo` | `margin:0; font-size:16px; font-weight:600; color:var(--cor-texto)` |
| `.lista` | `display:flex; flex-direction:column; gap:12px; margin:0; padding:0; list-style:none` |
| `.item` | `display:flex; gap:10px; font-size:14px; line-height:1.5; text-wrap:pretty` |
| `.marca` | `color:var(--cor-sucesso); line-height:1.3` |
| `.detalhe` | `display:block; font:12px var(--fonte-mono); color:var(--cor-texto-2)` |
| `.vazio` | `margin:0; font-size:14px; color:var(--cor-texto-2)` |
| `.resultado` | `margin:0; padding:10px 12px; border-radius:var(--raio-md); background:var(--cor-superficie-2); font-size:13.5px; line-height:1.5; font-variant-numeric:tabular-nums` |

**Passo 4: rodar e ver passar** → 6 passed. **Passo 5: commit**
```bash
git add frontend/src/features/limpeza/components
git commit -m "feat(limpeza): adiciona seções de problemas, cards, limites e registro das ações"
```

---

### Tarefa 18: Limpeza — página, rota e documentação

**Arquivos:**
- Criar: `frontend/src/features/limpeza/hooks/useLimpeza.ts`
- Criar: `frontend/src/features/limpeza/components/ConteudoLimpeza.tsx` + `ConteudoLimpeza.module.css`
- Substituir: `frontend/src/features/limpeza/PaginaLimpeza.tsx` (placeholder do M1.1) + `PaginaLimpeza.test.tsx`
- Modificar: `CHANGELOG.md`, `docs/decisions.md`, `docs/design/telas.md`, `docs/design/componentes.md`, `docs/specs/03-limpeza.md`, `docs/specs/15-frontend.md`

**Passo 1: escrever o teste (falha)** — `PaginaLimpeza.test.tsx`
```tsx
import { screen, waitFor, within } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { chamadasPara, type RotaFalsa, simularApi } from '../../testes/api';
import { COLUNAS_SAUDE, criarPagina, criarResumo, ID_DATASET } from '../../testes/fixtures/datasets';
import { criarEntradaLog, criarResultado, DIAGNOSTICO_SAUDE, DIAGNOSTICO_VAZIO } from '../../testes/fixtures/limpeza';
import { DATASET_TESTE, renderizarComProvedores } from '../../testes/renderizar';
import PaginaLimpeza from './PaginaLimpeza';

const BASE = `/datasets/${ID_DATASET}`;
const APLICAR = { name: 'Aplicar limpeza' };

function rotas(extras: RotaFalsa[] = [], diagnostico = DIAGNOSTICO_SAUDE, resumo = criarResumo()): RotaFalsa[] {
  return [
    { caminho: `${BASE}/diagnostico`, corpo: diagnostico },
    { caminho: `${BASE}/colunas`, corpo: COLUNAS_SAUDE },
    { caminho: BASE, corpo: criarPagina(resumo) },
    ...extras,
  ];
}

function renderizar() {
  return renderizarComProvedores(<PaginaLimpeza />, { rota: '/limpeza', dataset: DATASET_TESTE });
}

describe('PaginaLimpeza', () => {
  it('mostra cards e seções com tudo em "Manter" e o aplicar desabilitado', async () => {
    simularApi(rotas());
    renderizar();

    const faltantes = await screen.findByRole('region', { name: 'Faltantes' });
    expect(within(faltantes).getByRole('combobox', { name: 'Ação para peso_kg' })).toHaveValue('manter');
    expect(screen.getByText('Cópias exatas da linha 44.')).toBeInTheDocument();
    expect(screen.getByRole('button', APLICAR)).toBeDisabled();
  });

  it('aplica a ação escolhida e confirma com toast', async () => {
    const falso = simularApi(rotas([{ metodo: 'POST', caminho: `${BASE}/limpeza`, corpo: criarResultado({ n_linhas: 230 }) }]));
    const { usuario } = renderizar();

    await usuario.selectOptions(await screen.findByRole('combobox', { name: 'Ação para peso_kg' }), 'preencher_mediana');
    await usuario.click(screen.getByRole('button', APLICAR));

    expect(await screen.findByText('Limpeza aplicada: nenhuma linha removida.')).toBeInTheDocument();
    expect(chamadasPara(falso, 'POST', `${BASE}/limpeza`)[0]?.corpo).toEqual({
      acoes: [{ problema: 'faltantes', acao: 'preencher_mediana', coluna: 'peso_kg', valor: null, limites: null, grupo: null }],
    });
  });

  it('limites válidos refazem o diagnóstico com ?limites=', async () => {
    const falso = simularApi(rotas());
    const { usuario } = renderizar();
    const idade = await screen.findByRole('group', { name: 'idade' });

    await usuario.type(within(idade).getByLabelText('Mínimo'), '120');
    await usuario.type(within(idade).getByLabelText('Máximo'), '110');
    expect(within(idade).getByText('O mínimo precisa ser menor que o máximo (110). Ajuste um dos dois.')).toBeInTheDocument();

    await usuario.clear(within(idade).getByLabelText('Mínimo'));
    await usuario.type(within(idade).getByLabelText('Mínimo'), '1');

    await waitFor(
      () => {
        const urls = chamadasPara(falso, 'GET', `${BASE}/diagnostico`).map((c) => c.url);
        expect(urls.some((url) => url.includes('limites=') && url.includes('idade'))).toBe(true);
      },
      { timeout: 2000 },
    );
  });

  it('sem problemas: estado vazio com "Continuar para Análise"', async () => {
    simularApi(rotas([], DIAGNOSTICO_VAZIO));
    renderizar();

    expect(await screen.findByText('Nenhum problema encontrado')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Continuar para Análise/ })).toBeInTheDocument();
  });

  it('desfazer tudo chama a API e avisa', async () => {
    const resumo = criarResumo({ n_linhas: 227, log_limpeza: [criarEntradaLog()] });
    const falso = simularApi(rotas([{ metodo: 'POST', caminho: `${BASE}/limpeza/desfazer`, corpo: criarResultado({ n_linhas: 230, log: [] }) }], DIAGNOSTICO_SAUDE, resumo));
    const { usuario } = renderizar();

    await screen.findByText('Removemos 3 linhas duplicadas.');
    await usuario.click(screen.getByRole('button', { name: 'Desfazer tudo' }));

    expect(await screen.findByText('Limpeza desfeita: voltamos às 230 linhas do arquivo.')).toBeInTheDocument();
    expect(chamadasPara(falso, 'POST', `${BASE}/limpeza/desfazer`)).toHaveLength(1);
  });
});
```

**Passo 2: rodar e ver falhar** → FAIL

**Passo 3: implementar**

`hooks/useLimpeza.ts`:
```ts
import { useQuery } from '@tanstack/react-query';
import { opcoesColunas, opcoesPrimeiraPagina } from '../../../shared/api/dataset';
import { useValorAtrasado } from '../../../shared/lib/useValorAtrasado';
import { ehNumerico } from '../../../shared/ui/tiposVariavel';
import { useToast } from '../../../shared/ui/useToast';
import { ATRASO_LIMITES_MS, useAplicarLimpeza, useDesfazerLimpeza, useDiagnostico } from '../api';
import { avisoLimpezaAplicada, avisoLimpezaDesfeita } from '../resumo';
import { montarPedido, montarSecoes } from '../secoes';
import { useEscolhasLimpeza } from './useEscolhasLimpeza';
import { useLimitesPorColuna } from './useLimitesPorColuna';

/** Orquestra a tela 3: limites (com atraso), diagnóstico, escolhas, pedido, aplicar e desfazer. */
export function useLimpeza(datasetId: string) {
  const limites = useLimitesPorColuna();
  const limitesAtrasados = useValorAtrasado(limites.json, ATRASO_LIMITES_MS);
  const diagnostico = useDiagnostico(datasetId, limitesAtrasados);
  const colunas = useQuery(opcoesColunas(datasetId));
  const resumo = useQuery({ ...opcoesPrimeiraPagina(datasetId), select: (pagina) => pagina.resumo });
  const escolhas = useEscolhasLimpeza();
  const aplicar = useAplicarLimpeza(datasetId);
  const desfazer = useDesfazerLimpeza(datasetId);
  const toast = useToast();

  const secoes = diagnostico.data ? montarSecoes(diagnostico.data) : [];
  const pedido = montarPedido(secoes, escolhas.valores);

  function aplicarLimpeza(): void {
    const nAntes = diagnostico.data?.n_linhas ?? 0;
    aplicar.mutate(pedido, {
      onSuccess: (resultado) => {
        toast.mostrar(avisoLimpezaAplicada(nAntes, resultado, pedido.acoes.length));
        escolhas.limpar();
      },
    });
  }

  function desfazerTudo(): void {
    desfazer.mutate(undefined, {
      onSuccess: (resultado) => {
        toast.mostrar(avisoLimpezaDesfeita(resultado));
        escolhas.limpar();
      },
    });
  }

  return {
    limites,
    diagnostico,
    resumo,
    secoes,
    escolhas,
    pedido,
    colunasNumericas: (colunas.data ?? []).filter((c) => ehNumerico(c.tipo)).map((c) => c.coluna),
    podeDesfazer: (resumo.data?.log_limpeza.length ?? 0) > 0,
    aplicando: aplicar.isPending,
    desfazendo: desfazer.isPending,
    aplicarLimpeza,
    desfazerTudo,
  };
}

export type Limpeza = ReturnType<typeof useLimpeza>;
```

`components/ConteudoLimpeza.tsx`:
```tsx
import { useId } from 'react';
import { useNavigate } from 'react-router';
import { CAMINHOS } from '../../../shared/navegacao/caminhos';
import BarraAcoes from '../../../shared/ui/BarraAcoes';
import Botao from '../../../shared/ui/Botao';
import ConteudoConsulta from '../../../shared/ui/ConteudoConsulta';
import EstadoVazio from '../../../shared/ui/EstadoVazio';
import { type Limpeza, useLimpeza } from '../hooks/useLimpeza';
import { TEXTOS_LIMPEZA as T } from '../textos';
import CardsResumoLimpeza from './CardsResumoLimpeza';
import estilos from './ConteudoLimpeza.module.css';
import LimitesPorColuna from './LimitesPorColuna';
import PainelLog from './PainelLog';
import SecaoProblema from './SecaoProblema';

function AcoesLimpeza({ limpeza }: Readonly<{ limpeza: Limpeza }>) {
  const idAjuda = useId();
  const semAcoes = limpeza.pedido.acoes.length === 0;
  const temSecoes = limpeza.secoes.length > 0;
  return (
    <BarraAcoes>
      {semAcoes && temSecoes ? <p id={idAjuda} className={estilos.ajuda}>{T.botoes.semAcoes}</p> : null}
      <Botao variante="perigo" tamanho="lg" icone="undo" disabled={!limpeza.podeDesfazer} carregando={limpeza.desfazendo} textoCarregando={T.botoes.desfazendo} onClick={limpeza.desfazerTudo}>
        {T.botoes.desfazer}
      </Botao>
      {temSecoes ? (
        <Botao tamanho="lg" icone="cleaning_services" disabled={semAcoes} aria-describedby={semAcoes ? idAjuda : undefined} carregando={limpeza.aplicando} textoCarregando={T.botoes.aplicando} onClick={limpeza.aplicarLimpeza}>
          {T.botoes.aplicar}
        </Botao>
      ) : null}
    </BarraAcoes>
  );
}

function SemProblemas() {
  const navegar = useNavigate();
  return (
    <EstadoVazio
      icone="verified"
      titulo={T.vazio.titulo}
      descricao={T.vazio.descricao}
      acao={<Botao iconeFinal="arrow_forward" onClick={() => { void navegar(CAMINHOS.analise); }}>{T.vazio.continuar}</Botao>}
    />
  );
}

export default function ConteudoLimpeza({ datasetId }: Readonly<{ datasetId: string }>) {
  const limpeza = useLimpeza(datasetId);
  return (
    <ConteudoConsulta consulta={limpeza.diagnostico} carregando={T.carregando} forma="cards">
      {(diagnostico) => (
        <div className={estilos.conteudo} aria-busy={limpeza.diagnostico.isPlaceholderData}>
          {limpeza.secoes.length > 0 ? <CardsResumoLimpeza diagnostico={diagnostico} /> : null}
          <div className={estilos.grade}>
            <div className={estilos.principal}>
              {limpeza.secoes.length > 0
                ? limpeza.secoes.map((s) => <SecaoProblema key={s.id} secao={s} escolhas={limpeza.escolhas.valores} aoEscolher={limpeza.escolhas.escolher} />)
                : <SemProblemas />}
              <LimitesPorColuna colunas={limpeza.colunasNumericas} textos={limpeza.limites.textos} aoMudar={limpeza.limites.alterar} />
              <AcoesLimpeza limpeza={limpeza} />
            </div>
            <ConteudoConsulta consulta={limpeza.resumo} carregando={T.log.carregando} forma="cards">
              {(resumo) => <PainelLog resumo={resumo} />}
            </ConteudoConsulta>
          </div>
        </div>
      )}
    </ConteudoConsulta>
  );
}
```
> `limpeza.secoes.length > 0` equivale a `temProblemas(diagnostico)` (seções vazias são filtradas); `temProblemas` fica em `resumo.ts` para o M1.7/relatório, se precisarem.

| Seletor (`ConteudoLimpeza.module.css`) | Propriedades |
|---|---|
| `.conteudo` | `display:flex; flex-direction:column; gap:24px` |
| `.conteudo[aria-busy='true']` | `opacity:0.7; transition:opacity 120ms` (diagnóstico com limites novos carregando) |
| `.grade` | `display:grid; grid-template-columns:minmax(0, 1fr) 320px; gap:20px; align-items:start` |
| `.principal` | `display:flex; flex-direction:column; gap:16px; min-width:0` |
| `.ajuda` | `margin:0 auto 0 0; font-size:13px; color:var(--cor-texto-2)` |
| `@media (max-width:1279px)` › `.grade` | `grid-template-columns:minmax(0, 1fr)` |

`PaginaLimpeza.tsx`:
```tsx
import ExigeDataset from '../../shared/sessao/ExigeDataset';
import PaginaEtapa from '../../shared/ui/PaginaEtapa';
import ConteudoLimpeza from './components/ConteudoLimpeza';
import { TEXTOS_LIMPEZA as T } from './textos';

export default function PaginaLimpeza() {
  return (
    <PaginaEtapa etapa={3} titulo={T.titulo} ajuda={T.ajuda}>
      <ExigeDataset>{(id) => <ConteudoLimpeza datasetId={id} />}</ExigeDataset>
    </PaginaEtapa>
  );
}
```
Rota: a mesma do placeholder.

**Passo 4: rodar e ver passar** → 5 passed; `npm run lint && npm run format && npm run test` verde.

**Passo 5: documentação**

- `CHANGELOG.md` › *Não lançado* › *Adicionado*:
  ```
  - Tela Importar: envio por arrastar/soltar ou teclado, arquivo de exemplo, detecções com motivo e correção da leitura, prévia de 20 linhas e erros da API (1a–1c).
  - Tela Variáveis: tipos com chip, motivo, válidos/faltantes e exemplos; correção do tipo; editor de ordem dos ordinais com arrastar, botões e teclado (2a).
  - Tela Limpeza: cards de resumo, ação por problema, limites por coluna, aplicar e desfazer tudo, registro "O que fizemos" (3a).
  - Cabeçalho com linhas × colunas do dataset; sessão expirada avisa uma só vez, mesmo com várias consultas falhando juntas.
  - `ChipTipo`, `ConteudoConsulta`, `BarraAcoes`, `ExigeDataset`, `SemDataset` e convenção de chaves de query por dataset.
  ```
- `docs/decisions.md`: uma linha por decisão da tabela "Decisões deste bloco" (D62 e as novas), no formato da tabela do arquivo, data do dia. Cada `Dnn-<nome>` recebe o próximo número livre do arquivo nesta hora; depois troque os rótulos pelos números em `frontend/src` e nos docs desta tarefa (`grep -rn "Dnn-" frontend/src docs` deve voltar vazio).
- `docs/design/telas.md`: §1 "Tamanho máximo: 50 MB" e nota "Link 'Como exportar para CSV' fora do M1"; §2 trocar a sugestão de `@dnd-kit/sortable` por "arrastar nativo + Subir/Descer + ↑/↓ (D62)"; §3 nota "Ações começam em 'Manter' (Dnn-manter); 'Corrigir para 1,72' fora do M1 (Dnn-corrigir)".
- `docs/design/componentes.md` › AreaUpload: "Tamanho máximo: 50 MB".
- `docs/specs/03-limpeza.md`: em "Regras", acrescentar "A tela começa com todas as ações em 'Manter' e envia só as diferentes (Dnn-manter). Duplicados têm uma ação para todos os grupos. Limites por coluna refazem o diagnóstico 600 ms depois da digitação (Dnn-limites)."
- `docs/specs/15-frontend.md`: na tabela de telas, linha 2 "editor de ordem: arrastar nativo, Subir/Descer e ↑/↓ (D62)"; em "Estados obrigatórios", "Sessão expirada (DATASET_NAO_ENCONTRADO) em qualquer consulta encerra a sessão e volta para Importar (D61/Dnn-sessao)".

**Passo 6: commit**
```bash
git add frontend/src/features/limpeza CHANGELOG.md docs
git commit -m "feat(limpeza): monta a tela Limpeza e registra decisões do M1.6"
```

---

### Tarefa 19: Verificação final e teste manual pelo preview

**Passo 1: qualidade completa**
```bash
cd frontend && npm run lint && npm run format && npm run test && npm run build
cd .. && npx --yes jscpd@4 backend/app backend/tests frontend/src
```
Esperado: tudo verde, jscpd com 0 clones. Se o jscpd acusar duplicação entre testes (ex.: blocos de `simularApi` parecidos), extraia uma função de rotas no próprio arquivo de teste (como `rotas()` em `PaginaLimpeza.test.tsx`). Se o build reclamar de tamanho, confira que as três páginas continuam com `lazy()` em `app/rotas.ts`.

**Passo 2: subir os servidores** pelo preview (`.claude/launch.json`): `backend` (porta 8000) e `frontend` (5173). Abrir `http://localhost:5173/importar`.

**Passo 3: roteiro manual** (marque cada item; anote prints dos que divergirem do design)

| # | Ação | Esperado |
|---|---|---|
| 1 | Abrir `/importar` sem sessão | 1b: área de envio, "Tamanho máximo: 50 MB", etapas 2–8 bloqueadas, "Nenhum arquivo importado" |
| 2 | Arrastar `dados-exemplo/pesquisa_saude.txt` para a área | Borda primária + "Solte para enviar"; ao soltar: barra de progresso, depois toast "Arquivo lido: 230 linhas e 8 colunas." / "As etapas 2 a 8 foram liberadas." |
| 3 | Conferir 1a | Formato "Texto (TXT)", Separador "Ponto e vírgula ( ; )", Decimal "Vírgula ( , )", Codificação "UTF-8", Cabeçalho "Sim, 1ª linha", cada um com motivo; prévia "20 primeiras linhas de 230", cabeçalho fixo ao rolar, faltante "—"; cabeçalho "pesquisa_saude.txt · 230 linhas × 8 colunas" |
| 4 | Trocar Separador para "Vírgula ( , )" | Releitura; aviso "Encontramos só uma coluna…" (se a API mandar) e prévia com 1 coluna; voltar para ";" restaura |
| 5 | Enviar um `.pdf` qualquer | 1c: banner "Não conseguimos ler este arquivo: x.pdf" + mensagem/sugestão da API + "Usar o arquivo de exemplo" (funciona) |
| 6 | Só teclado: Tab até "Escolher arquivo", Enter | Abre o seletor do sistema; foco visível em todos os controles |
| 7 | Continuar para Variáveis | 2a: resumo "2 contínuas 1 discreta 2 ordinais 1 nominal 1 binária"; chips com ícone; motivos; "229 / 1" etc.; editores de `escolaridade` e `satisfacao` |
| 8 | Corrigir `cidade` para Qualitativa ordinal | Toast "Tipo de cidade alterado para Qualitativa ordinal."; chip com "corrigido"; aparece editor de ordem de cidade |
| 9 | Corrigir `cidade` para Quantitativa contínua | Toast de erro com a mensagem `TIPO_INCOMPATIVEL`; Select volta ao tipo anterior |
| 10 | Editor de ordem: arrastar "pós" para o topo; depois foco na alça de "fundamental" e ↓ ↓; depois "Subir" | Item arrastado com borda primária e "Movendo…"; ordem muda; leitor de tela (NVDA/Narrador) anuncia "fundamental agora está na posição 3 de 4."; foco permanece no item; escala embaixo atualiza; recarregar a página mantém a ordem |
| 11 | Continuar para Limpeza | 3a: cards (faltantes, 3 duplicados da linha 44, fora de faixa, grafias Goiania/Anapolis); tudo em "Manter"; "Aplicar limpeza" desabilitado com a dica |
| 12 | Limites `idade` 120 / 110 | "O mínimo precisa ser menor que o máximo (110). Ajuste um dos dois."; corrigir para 1 / 110: após ~0,6 s o diagnóstico atualiza sem piscar e a faixa mostra "(seus limites)" |
| 13 | Escolher Remover duplicados, Unificar Goiânia/Anápolis, mediana em `peso_kg`, "Remover o valor" em `idade`; Aplicar | Toast "Limpeza aplicada: 3 linhas removidas."; "O que fizemos" com as frases e detalhes mono; "Resultado: 227 linhas (eram 230)."; cabeçalho "227 linhas × 8 colunas" |
| 14 | Desfazer tudo | Toast "Limpeza desfeita: voltamos às 230 linhas do arquivo."; log vazio; diagnóstico volta |
| 15 | Aplicar tudo até não sobrar problema | Estado vazio "Nenhum problema encontrado" + "Continuar para Análise" |
| 16 | Tema escuro (alternância no cabeçalho) nas três telas | Cores dos tokens escuros; chips legíveis; nenhum hex fixo aparecendo |
| 17 | Parar o backend e recarregar `/variaveis` | Skeleton e, após as retentativas, `EstadoErro` "Não conseguimos falar com o servidor." com "Tentar de novo"; na tela 1, enviar arquivo mostra o banner com essa mensagem (SEM_CONEXAO) |
| 18 | Religar o backend (memória zerada) e recarregar `/limpeza` | Toast "Sua sessão expirou." / "Envie o arquivo novamente." e volta para `/importar` (D61) |
| 19 | Largura 1024 px | Cards da limpeza em 2 colunas, log abaixo; tabela de variáveis rola na horizontal; detecções em 2 colunas |

**Passo 4:** corrigir o que divergir (commit `fix(<feature>): …`) e repetir os itens afetados. Pare os servidores do preview no fim.

---

### Tarefa 20: PR (só depois do ok do usuário)

Mostre ao usuário o resumo da Tarefa 19 (itens ok e divergências) e **espere a confirmação** antes de publicar.

```bash
git push -u origin feat/frontend-importar-variaveis-limpeza
gh pr create --base develop --title "feat(frontend): telas Importar, Variáveis e Limpeza (M1.6)" --body-file - <<'EOF'
## O que muda
- Telas 1 (Importar), 2 (Variáveis) e 3 (Limpeza) ligadas à API do M1.2/M1.3, com estados carregando, vazio, erro e sucesso, temas claro e escuro e navegação por teclado.
- `ChipTipo` + `tiposVariavel.ts`, `ConteudoConsulta`, `BarraAcoes`, `ExigeDataset`; convenção de chaves de query por dataset (Dnn-chaves); sessão expirada tratada em qualquer consulta/mutação (D61/Dnn-sessao).

## Specs e design
`docs/design/telas.md` §1–3, `docs/specs/01`, `02`, `03`, `14`, `15`, `16`, `17`. Decisões D62 e as novas do bloco (números definidos na hora do commit) em `docs/decisions.md`.

## Desvios do design
50 MB (não 20), sem "Como exportar para CSV", formato só leitura, ações começam em "Manter", sem "Corrigir para 1,72", cards de limpeza sem ícone, duplicados com uma ação só. Detalhes no plano `docs/plans/2026-10-03-m1-6-telas-importar-variaveis-limpeza.md`.

## Checklist
- [x] Camadas: features não importam umas das outras; `shared/` não importa `features/`
- [x] Limites de lint/complexidade e jscpd verdes
- [x] Tipos da API só derivados de `schema.d.ts`; sem `any`; `as` só em testes
- [x] Testes novos (Vitest + Testing Library)
- [x] Textos conforme spec 16; CHANGELOG e specs atualizados
- [x] Teste manual pelo preview (roteiro da Tarefa 19)
EOF
```
Sem `Co-Authored-By` e sem atribuição de IA no corpo do PR. Acompanhe o CI (`gh pr checks --watch`) e corrija o que falhar.

---

## Critérios de pronto

- As três telas conferem com os prints `1a`, `1b`, `1c`, `2a`, `3a` (com os desvios listados) nos temas claro e escuro.
- Estados obrigatórios em cada tela: carregando (skeleton), vazio com próximo passo, erro com mensagem da API e ação, sucesso com toast no formato da spec 16.
- Fluxo completo com `dados-exemplo/pesquisa_saude.txt`: importar → corrigir um tipo → reordenar um ordinal → definir limites → aplicar limpeza (227 linhas) → desfazer.
- Teclado: envio de arquivo, Selects, editor de ordem (↑/↓, Subir/Descer) e botões, com foco visível e anúncio `aria-live` da nova posição.
- `npm run lint && npm run format && npm run test && npm run build` e `npx --yes jscpd@4 backend/app backend/tests frontend/src` verdes; CI verde no PR.
- Nenhuma dependência nova; nenhum tipo da API escrito à mão; nenhum endpoint inventado.
- `CHANGELOG.md`, `docs/decisions.md`, `docs/design/telas.md`, `docs/design/componentes.md`, `docs/specs/03-limpeza.md` e `docs/specs/15-frontend.md` atualizados.

## Lacunas da API encontradas (não implementar aqui; levar ao PR e ao backend)

| Lacuna | Efeito na tela | Proposta |
|---|---|---|
| `POST /datasets` não aceita `formato` | Select "Formato" só leitura | Aceitar `formato?` no form, ou manter só leitura e registrar no design |
| `POST /datasets/exemplo` não aceita opções de leitura | Exemplo não pode ser corrigido (Dnn-reler) | Aceitar as mesmas opções do `POST /datasets` |
| `MetadadosLeitura` não diz a aba usada | Tela assume a 1ª aba ou a escolhida pelo usuário | Campo `aba: str \| None` em `MetadadosLeitura` |
| `TipoColuna` não diz quais tipos são permitidos | Select oferece os 6 e a API recusa com `TIPO_INCOMPATIVEL` | Campo `tipos_permitidos: list[TipoVariavel]` (o Select desabilitaria com motivo, como em componentes.md) |
| `AcaoLimpeza` de duplicados sem grupo | Uma ação para todos os grupos | `grupo` = `linha_original` quando houver mais de um grupo |
| Sem ação "corrigir para valor" em fora de faixa | "Corrigir para 1,72" fora (Dnn-corrigir) | Ação `substituir` com `valor` (M2) |
| Cliente HTTP falha com 204 (`resposta.json()` sem corpo) | Não dá para apagar o dataset antigo ao reler (`DELETE /datasets/{id}`) | `requisitar` devolver `undefined` em 204; a releitura apagaria o id anterior |
