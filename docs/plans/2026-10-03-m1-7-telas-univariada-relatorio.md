# M1.7 — Telas 4 (Análise univariada) e 8 (Relatório): plano de implementação

> **Para o agente:** use a skill `executing-plans` (ou `subagent-driven-development`) para executar tarefa por tarefa. Antes de escrever código, leia `CLAUDE.md`, `docs/padroes-codigo.md` e a seção "Contratos do frontend" de `docs/plans/2026-10-03-m1-visao-geral.md`.

**Objetivo:** entregar a tela 4 (Análise univariada: Frequências · Tendência central · Separatrizes · Dispersão · Gráficos, sem a aba "Forma e distribuição", D60) e a tela 8 (Relatório: escolha de seções e colunas, prévia em `iframe`, baixar HTML e imprimir), fechando o M1 de ponta a ponta com `dados-exemplo/pesquisa_saude.txt`.

**Arquitetura:** duas features novas, `features/analise` e `features/relatorio`, que só falam com a API por hooks do react-query e só usam `shared/`. Toda regra de exibição que tem lógica (abas aplicáveis, colunas da tabela por tipo, `Medida` → props do `CardMetrica`, posição na régua, URL do relatório, estado da tela) fica em **funções puras testadas**; os componentes só montam JSX. O frontend **nunca decide aplicabilidade**: lê `aplicavel` e `nao_aplicavel` da `Analise`.

**Stack:** React 19 · Vite 8 · TypeScript ~5.9 strict (`exactOptionalPropertyTypes`, `noUncheckedIndexedAccess`) · @tanstack/react-query 5 · react-router 7 · Vitest 5 + jsdom + Testing Library · ESLint 9 (typescript-eslint strict-type-checked, sonarjs, jsx-a11y) · Prettier · `react-plotly.js/factory` + `plotly.js-dist-min` (via `shared/graficos/Grafico`).

**Branch:** `feat/frontend-univariada-relatorio` (sai de `develop`) → PR para `develop`.

**Prazo:** 30/10/2026 (fim do M1, versão `v0.1.0`).

**Depende de (mergeados em `develop`):** M1.1 (base visual: `shared/ui`, `Grafico`, `useSessao`, `formatar.ts`, `erros.ts`, rotas com placeholders), M1.4 (endpoints `analise` e `posicao`), M1.5 (figuras na `Analise` e `GET /relatorio`) e **M1.6** (entra antes deste bloco). Do M1.6 usa, sem recriar: `ChipTipo` + `shared/ui/tiposVariavel.ts`; `shared/api/dataset.ts` (`chavesDataset`, `caminhoDataset`, `opcoesColunas` e a tabela de invalidação); `shared/lib/useValorAtrasado.ts`; `shared/lib/pluralizar.ts`; `shared/sessao/SemDataset.tsx`; o `useSessaoExpirada` completado (sessão expirada avisada uma vez); e os helpers de teste `src/testes/api.ts` (`simularApi`, `chamadasPara`, `respostaJson`), `src/testes/renderizar.tsx` (`renderizarComProvedores`, `DATASET_TESTE`) e `src/testes/fixtures/datasets.ts` (`criarColuna`, `ID_DATASET`).

---

## Pressupostos sobre M1.1 e M1.6 (conferir antes da Tarefa 1)

Os módulos abaixo ainda não existiam quando este plano foi escrito. O plano usa os contratos da visão geral. **Antes de começar**, abra cada arquivo e ajuste só os imports se o nome exportado for diferente (não mude o contrato):

| Uso neste plano | Contrato (visão geral) | Pressuposto de exportação |
|---|---|---|
| `import PaginaEtapa from '../../shared/ui/PaginaEtapa'` (idem `Card`, `Banner`, `Botao`, `CardMetrica`, `Tabela`, `Abas`, `Segmented`, `Select`, `CampoNumero`, `CaixaSelecao`, `EstadoVazio`, `EstadoErro`, `EstadoCarregando`, `Icone`) | componentes de `shared/ui` | `export default`; `Tabela.tsx` também exporta o tipo `ColunaTabela<L>` |
| `import Grafico from '../../shared/graficos/Grafico'` | `titulo, resumo, figura, altura?` | `export default`; o `resumo` vira descrição acessível. **Se o `Grafico` também mostrar o resumo na tela**, apague o `<p>` de resumo do `CardGrafico` (Tarefa 5) para não repetir o texto |
| `import { useSessao } from '../../shared/sessao/useSessao'` | `{ dataset, definirDataset, encerrar, etapasVisitadas, marcarVisitada }` | export nomeado |
| `import { useToast } from '../../shared/ui/useToast'` e `import ToastProvider from '../shared/ui/ToastProvider'` | `mostrar({ tipo, titulo, descricao?, acao? })` | `useToast` nomeado, `ToastProvider` default (ajuste os caminhos se estiverem no mesmo arquivo) |
| `import { formatarNumero, formatarInteiro, lerNumeroPtBr } from '../../shared/lib/formatar'` | assinaturas da visão geral | exports nomeados |
| `import { textoDoErro } from '../../shared/api/erros'` | `textoDoErro(erro) → { mensagem, sugestao }` | export nomeado |
| `import ChipTipo from '../../shared/ui/ChipTipo'` | `tipo, curto?, corrigido?` (**criado no M1.6**) | `export default` |
| `import { caminhoDataset, chavesDataset, opcoesColunas, type TipoColuna } from '../../shared/api/dataset'` | convenção de chaves `['datasets', id, recurso, …]` (**criada no M1.6**) | exports nomeados |
| `import { useValorAtrasado } from '../../shared/lib/useValorAtrasado'` e `import { escolherForma, pluralizar } from '../../shared/lib/pluralizar'` | **criados no M1.6** | exports nomeados |
| `import SemDataset from '../../shared/sessao/SemDataset'` | `descricao?: string` ("Nenhum arquivo importado" + "Ir para Importar"; **criado no M1.6**) | `export default` |
| `src/testes/configuracao.ts` (jest-dom, limpeza no `afterEach`), `environment: 'jsdom'`, `restoreMocks: true` | D58 | criados no M1.1 |
| `simularApi`, `chamadasPara`, `respostaJson` (`src/testes/api.ts`); `renderizarComProvedores(ui, { rota?, dataset? })` e `DATASET_TESTE` (`src/testes/renderizar.tsx`); `criarColuna`, `ID_DATASET` (`src/testes/fixtures/datasets.ts`) | helpers de teste | criados/ampliados no M1.6 |
| `DATASET_NAO_ENCONTRADO` encerra a sessão e leva para Importar | D61 | tratado de forma global no `useSessaoExpirada` (M1.1, completado no M1.6); nada a fazer nas telas |

Tudo o que o M1.1 e o M1.6 já criaram é **reutilizado**; este plano só cria o que falta (zero duplicação). Se algum nome exportado divergir na hora, ajuste só o `import`.

---

## Visão geral das tarefas

| # | Tarefa | Área |
|---|---|---|
| 1 | Utilitários compartilhados: `urlDaApi`/`requisitarBlob`, colunas analisáveis, `baixarArquivo`, `formatarDecimal` | shared |
| 2 | Base da feature `analise`: tipos, textos, `api.ts`; falso do gráfico e fixtures | analise |
| 3 | Coluna e classes na URL, abas aplicáveis e estado da tela (funções puras) | analise |
| 4 | Cartões de métrica: `Medida` → props do `CardMetrica` + `GradeCardsMetrica` | analise |
| 5 | Aba Frequências (tabela por tipo, controle de classes, gráfico principal, resumo categórico) | analise |
| 6 | Abas Tendência central e Dispersão | analise |
| 7 | Aba Separatrizes + "Onde está meu valor?" + `ReguaSeparatrizes` | analise |
| 8 | Aba Gráficos | analise |
| 9 | `PaginaAnalise`: seletor de coluna, abas, estados (carregando, vazio, erro) e rota | analise |
| 10 | Base da feature `relatorio`: URL, nome do arquivo, seleção (funções puras) | relatorio |
| 11 | `PaginaRelatorio`: seções, colunas, prévia, baixar e imprimir; rota | relatorio |
| 12 | Documentação: CHANGELOG, decisões, specs 13 e 15 | docs |
| 13 | Verificação final e teste manual no preview | qualidade |
| 14 | PR para `develop` (só depois do ok do usuário) | GitHub |
| 15 | Critérios de pronto do M1 + **proposta** do release `v0.1.0` (só com autorização explícita) | release |

Arquivos novos (resumo; `(mod.)` = arquivo que já existe e só ganha o que está indicado):

```
frontend/src/
├── shared/api/cliente.ts            (mod.)  urlDaApi, requisitarBlob
├── shared/api/colunas.ts                    filtrarAnalisaveis, useColunasAnalisaveis (sobre opcoesColunas do M1.6)
├── shared/lib/formatar.ts           (mod.)  formatarDecimal
├── shared/lib/baixarArquivo.ts
├── testes/  graficoFalso.tsx · downloadFalso.ts · fixturesAnalise.ts   (api.ts e renderizar.tsx são do M1.6)
├── features/analise/
│   ├── api.ts · tipos.ts · textos.ts (mod.) · parametros.ts · abas.ts · estadoAnalise.ts
│   ├── formatacao.ts · cartoes.ts · frequencias.tsx · separatrizes.ts · figuras.ts
│   ├── hooks/  useParametrosAnalise.ts · useConsultaPosicao.ts
│   ├── components/  SeletorColuna · ConteudoAnalise · CorpoAnalise · GradeCardsMetrica · CardGrafico
│   │                TabelaFrequencias · ControleClasses · AbaFrequencias · AbaTendencia · AbaDispersao
│   │                ListaSeparatrizes · TabelaSeparatrizes · ReguaSeparatrizes · PainelPosicao · AbaSeparatrizes
│   │                AbaGraficos  (+ *.module.css, paineis.module.css)
│   └── PaginaAnalise.tsx (mod.: substitui a provisória do M1.1)
└── features/relatorio/
    ├── api.ts · selecao.ts · textos.ts (mod.)
    ├── hooks/  useSelecaoRelatorio.ts · usePreviaRelatorio.ts · useAcaoBaixar.ts
    ├── components/  GrupoCaixas · OpcoesRelatorio · PreviaRelatorio (+ *.module.css)
    └── PaginaRelatorio.tsx (mod.: substitui a provisória do M1.1)
```
`app/rotas.ts` não muda: o M1.1 já carrega `features/analise/PaginaAnalise` e `features/relatorio/PaginaRelatorio` com `lazy()`.

**Regras que valem em todo o plano** (o lint quebra se esquecer):
- Números em template string sempre com `String(n)` (`restrict-template-expressions` do strict).
- Props sempre `Readonly<Props>` (`sonarjs/prefer-read-only-props`).
- Arrow em `onClick` com chaves: `() => { aoMudar(k); }` (`no-confusing-void-expression`).
- Prop opcional nunca recebe `undefined` explícito (`exactOptionalPropertyTypes`): use espalhamento condicional `...(x === null ? {} : { prop: x })`.
- Sem ternário aninhado (`sonarjs/no-nested-conditional`): extraia subcomponente ou função.
- Cores, espaços e raios só com `var(--token)` (tokens de `tokens.css` + `--esp-*`, `--raio-*` e `--fonte-mono` criados no M1.1; se `--fonte-mono` não existir, use `'JetBrains Mono', monospace`).
- Antes de cada commit, em `frontend/`: `npm run lint && npm run format && npm run test && npm run build`; na raiz: `npx --yes jscpd@4 backend/app backend/tests frontend/src`.

---

### Tarefa 1: Utilitários compartilhados

**Arquivos:**
- Modificar: `frontend/src/shared/api/cliente.ts` · Teste: `frontend/src/shared/api/cliente.test.ts`
- Criar: `frontend/src/shared/api/colunas.ts` · Teste: `frontend/src/shared/api/colunas.test.ts`
- Criar: `frontend/src/shared/lib/baixarArquivo.ts` · Teste: `frontend/src/shared/lib/baixarArquivo.test.ts`
- Criar: `frontend/src/testes/downloadFalso.ts`
- Modificar: `frontend/src/shared/lib/formatar.ts` (M1.1; acrescenta `formatarDecimal`, que o M1.1 não tem) · Teste: `frontend/src/shared/lib/formatar.test.ts`

Reutilizados sem mudança: `useValorAtrasado` (debounce do campo "Valor de…" e da prévia; **criado no M1.6**) e `opcoesColunas`/`chavesDataset.colunas` (**M1.6**, `shared/api/dataset.ts`).

**Por quê:** a prévia do relatório precisa da URL completa (`/api/...`) para o `iframe`; o download precisa do corpo como `Blob`; Análise e Relatório usam a mesma lista de colunas analisáveis (features não importam uma da outra), filtrada sobre a consulta de colunas do M1.6; a tabela de frequências mostra porcentagens com 1 casa fixa ("4,0", "100,0").

**Passo 1: testes (falham)**

Acrescentar ao final de `shared/api/cliente.test.ts` (reaproveita o `respostaJson(status, corpo)` que o M1.6 passou a importar de `../../testes/api`; o `vi.stubGlobal` é desfeito pelo `afterEach` de `src/testes/configuracao.ts`):

```ts
describe('urlDaApi e requisitarBlob', () => {
  it('monta a URL com o prefixo /api', () => {
    expect(urlDaApi('/datasets/ds1/relatorio?offline=true')).toBe('/api/datasets/ds1/relatorio?offline=true');
  });

  it('devolve o corpo como Blob', async () => {
    const html = new Response('<html></html>', { status: 200, headers: { 'Content-Type': 'text/html' } });
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(html));

    const blob = await requisitarBlob('/datasets/ds1/relatorio');

    await expect(blob.text()).resolves.toBe('<html></html>');
  });

  it('converte o erro padronizado também quando o corpo esperado é Blob', async () => {
    const corpo = { codigo: 'COLUNA_VAZIA', mensagem: 'A coluna não tem valores.', sugestao: 'Escolha outra.' };
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(respostaJson(400, corpo)));

    await expect(requisitarBlob('/datasets/ds1/relatorio')).rejects.toMatchObject({ codigo: 'COLUNA_VAZIA' });
  });
});
```
(atualize o import do topo para `import { ErroApi, requisitar, requisitarBlob, urlDaApi } from './cliente';`)

`shared/api/colunas.test.ts`:

```ts
import { describe, expect, it } from 'vitest';
import { colunasPesquisa } from '../../testes/fixturesAnalise';
import { filtrarAnalisaveis } from './colunas';

describe('colunas', () => {
  it('deixa de fora as colunas identificador', () => {
    expect(filtrarAnalisaveis(colunasPesquisa).map((c) => c.coluna)).toEqual(['sexo', 'peso_kg', 'cidade']);
  });
});
```
(o arquivo `fixturesAnalise.ts` é criado na Tarefa 2; rode este teste só depois dela, ou crie agora só o `colunasPesquisa` e complete o arquivo na Tarefa 2.)

`testes/downloadFalso.ts` (usado aqui e na Tarefa 11):

```ts
import { vi } from 'vitest';

/** Substitui URL.createObjectURL e o clique em <a> (o jsdom não baixa arquivos). */
export function simularDownload() {
  const nomesBaixados: string[] = [];
  const liberar = vi.fn();
  Object.assign(URL, { createObjectURL: vi.fn(() => 'blob:teste'), revokeObjectURL: liberar });
  vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(function (this: HTMLAnchorElement) {
    nomesBaixados.push(this.download);
  });
  return { nomesBaixados, liberar };
}
```

`shared/lib/baixarArquivo.test.ts`:

```ts
import { afterEach, describe, expect, it, vi } from 'vitest';
import { simularDownload } from '../../testes/downloadFalso';
import { baixarArquivo } from './baixarArquivo';

describe('baixarArquivo', () => {
  afterEach(() => {
    vi.restoreAllMocks();
    vi.useRealTimers();
  });

  it('clica num link temporário com o nome do arquivo e libera a URL depois', () => {
    vi.useFakeTimers();
    const { nomesBaixados, liberar } = simularDownload();

    baixarArquivo(new Blob(['<html></html>']), 'relatorio-pesquisa_saude.html');
    vi.runAllTimers();

    expect(nomesBaixados).toEqual(['relatorio-pesquisa_saude.html']);
    expect(liberar).toHaveBeenCalledWith('blob:teste');
    expect(document.querySelector('a[download]')).toBeNull();
  });
});
```

O `formatar.ts` do M1.1 não tem formatador de casas fixas (`formatarPercentual` acrescenta "%" e `formatarNumero` corta zeros à direita). Acrescente em `formatar.test.ts`:

```ts
describe('formatarDecimal', () => {
  it.each([
    [40.43, 1, '40,4'],
    [100, 1, '100,0'],
    [4, 1, '4,0'],
    [1234.5, 2, '1.234,50'],
  ])('formata %d com %d casa(s) fixa(s): %s', (valor, casas, esperado) => {
    expect(formatarDecimal(valor, casas)).toBe(esperado);
  });
});
```

**Passo 2: rodar e ver falhar** — `npm run test` → FAIL (`urlDaApi`, `requisitarBlob`, `filtrarAnalisaveis`, `baixarArquivo`, `formatarDecimal` não existem).

**Passo 3: implementar**

`shared/api/cliente.ts` — extrair a parte comum de `requisitar` para `buscar` e acrescentar as duas funções (mantenha o que já estiver lá, por exemplo tratamento de 204 ou `FormData`):

```ts
export function urlDaApi(caminho: string): string {
  return `${PREFIXO_API}${caminho}`;
}

async function buscar(caminho: string, opcoes?: RequestInit): Promise<Response> {
  const resposta = await fetch(urlDaApi(caminho), opcoes).catch(() => {
    throw new ErroApi(0, SEM_CONEXAO);
  });
  if (!resposta.ok) {
    throw new ErroApi(resposta.status, await lerCorpoDeErro(resposta));
  }
  return resposta;
}

/**
 * Faz a requisição e devolve o corpo tipado.
 * O `as T` é o único cast permitido: T vem dos tipos gerados do OpenAPI (schema.d.ts).
 */
export async function requisitar<T>(caminho: string, opcoes?: RequestInit): Promise<T> {
  const resposta = await buscar(caminho, opcoes);
  return (await resposta.json()) as T;
}

/** Para respostas que não são JSON (ex.: relatório HTML para download). */
export async function requisitarBlob(caminho: string): Promise<Blob> {
  const resposta = await buscar(caminho);
  return resposta.blob();
}
```

`shared/api/colunas.ts` (só o filtro e o hook; a consulta e a chave `['datasets', id, 'colunas']` são as `opcoesColunas` do M1.6, então Variáveis, Análise e Relatório compartilham o mesmo cache):

```ts
/** Colunas analisáveis do dataset, compartilhadas por Análise e Relatório. */
import { useQuery, type UseQueryResult } from '@tanstack/react-query';
import { opcoesColunas, type TipoColuna } from './dataset';

/** Identificadores ficam fora das análises (D17). */
export function filtrarAnalisaveis(colunas: readonly TipoColuna[]): TipoColuna[] {
  return colunas.filter((coluna) => coluna.tipo !== 'identificador');
}

export function useColunasAnalisaveis(datasetId: string): UseQueryResult<TipoColuna[]> {
  return useQuery({ ...opcoesColunas(datasetId), select: filtrarAnalisaveis });
}
```

`shared/lib/baixarArquivo.ts`:

```ts
/** Salva um Blob no computador do usuário com o nome escolhido. */
export function baixarArquivo(conteudo: Blob, nomeArquivo: string): void {
  const url = URL.createObjectURL(conteudo);
  const link = document.createElement('a');
  link.href = url;
  link.download = nomeArquivo;
  link.hidden = true;
  document.body.append(link);
  link.click();
  link.remove();
  // Liberar no próximo ciclo: alguns navegadores ainda leem a URL logo depois do clique.
  window.setTimeout(() => {
    URL.revokeObjectURL(url);
  }, 0);
}
```

`shared/lib/formatar.ts` (acrescentar):

```ts
/** Número com casas decimais fixas, pt-BR: formatarDecimal(4) → "4,0". */
export function formatarDecimal(valor: number, casas = 1): string {
  return new Intl.NumberFormat('pt-BR', { minimumFractionDigits: casas, maximumFractionDigits: casas }).format(valor);
}
```

**Passo 4: rodar e ver passar** — `npm run test` → verdes · `npm run lint` → sem erros.

**Passo 5: commit**
```bash
git add frontend/src/shared frontend/src/testes/downloadFalso.ts
git commit -m "feat(frontend): adiciona URL e Blob da API, colunas analisáveis, casas fixas e download de arquivo"
```

---

### Tarefa 2: Base da feature `analise` + falso do gráfico e fixtures

**Arquivos:**
- Criar: `frontend/src/features/analise/tipos.ts`, `api.ts` · Teste: `api.test.ts`
- Substituir: `frontend/src/features/analise/textos.ts` (provisório do M1.1; `titulo` e `ajuda` continuam iguais)
- Criar: `frontend/src/testes/graficoFalso.tsx`, `frontend/src/testes/fixturesAnalise.ts`
- Reutilizar (M1.6, sem recriar): `src/testes/api.ts`, `src/testes/renderizar.tsx`, `src/testes/fixtures/datasets.ts`

**Passo 1: `tipos.ts`** (só aliases dos tipos gerados; nada redefinido à mão)

```ts
import type { components } from '../../shared/api/schema';

type Esquemas = components['schemas'];

export type Analise = Esquemas['Analise'];
export type TabelaFrequencia = Esquemas['TabelaFrequencia'];
export type LinhaFrequencia = Esquemas['LinhaFrequencia'];
export type Medida = Esquemas['Medida'];
export type Moda = Esquemas['Moda'];
export type Separatrizes = Esquemas['Separatrizes'];
export type ValorSeparatriz = Esquemas['ValorSeparatriz'];
export type Dispersao = Esquemas['Dispersao'];
export type Figura = Esquemas['Figura'];
export type Formula = Esquemas['Formula'];
export type Posicao = Esquemas['Posicao'];
export type TipoColuna = Esquemas['TipoColuna'];
export type TipoVariavel = Esquemas['TipoVariavel'];
export type TipoSeparatriz = Posicao['tipo'];

/** Abas da tela 4 no M1 (a aba "Forma e distribuição" fica oculta até o M2, D60). */
export type IdAba = 'frequencias' | 'tendencia' | 'separatrizes' | 'dispersao' | 'graficos';

/** Props comuns de todos os painéis de aba (tabela de despacho em ConteudoAnalise). */
export interface PropsPainel {
  analise: Analise;
  datasetId: string;
  atualizando: boolean;
  classes: number | null;
  aoMudarClasses: (k: number) => void;
}
```

**Passo 2: `textos.ts`** (substitui o provisório do M1.1; textos finais de `docs/design/telas.md` §4 e spec 16; nenhum texto no JSX). A fórmula de cada card vem da chave em `Medida.formula` (M1.4), e o rótulo de cada gráfico vem de `Figura.rotulo` (M1.5): nada disso fica neste arquivo.

```ts
import { escolherForma, pluralizar } from '../../shared/lib/pluralizar';
import type { IdAba, TipoSeparatriz } from './tipos';

export const TEXTOS_ANALISE = {
  titulo: 'Análise univariada',
  ajuda: 'Uma coluna por vez: como os valores se distribuem, onde fica o centro e quanto eles variam.',
  rotuloColuna: 'Coluna',
  rotuloAbas: 'Análises',
  abas: {
    frequencias: 'Frequências',
    tendencia: 'Tendência central',
    separatrizes: 'Separatrizes',
    dispersao: 'Dispersão',
    graficos: 'Gráficos',
  } satisfies Record<IdAba, string>,
  motivoPadrao: 'Não se aplica ao tipo desta coluna.',
  carregandoColunas: 'Carregando as colunas…',
  calculando: (coluna: string) => `Calculando as estatísticas de ${coluna}…`,
  semDataset: 'Importe um arquivo para analisar as colunas, uma de cada vez.',
  semColunas: {
    titulo: 'Nenhuma coluna para analisar',
    descricao: 'Todas as colunas estão como identificador e ficam fora das análises. Corrija os tipos na etapa Variáveis.',
    acao: 'Ir para Variáveis',
  },
  frequencias: {
    tituloClasses: 'Tabela de frequências por classe',
    titulo: (coluna: string) => `Frequências de ${coluna}`,
    classe: 'Classe',
    pontoMedio: 'Ponto médio',
    fi: 'fi',
    fr: 'fr%',
    fiAcumulada: 'Fi',
    frAcumulada: 'Fr%',
    frAcumuladaNaoAplicavel: 'Fr% acum.',
    total: 'Total',
    naoSeAplica: 'Não se aplica',
    notaClasses: (h: string) =>
      `⊢ inclui o limite da esquerda e exclui o da direita. Amplitude de cada classe: h = ${h}.`,
    faltantes: (n: number) => `${pluralizar(n, 'faltante', 'faltantes')} ${escolherForma(n, 'ficou', 'ficaram')} de fora.`,
    numeroClasses: 'Número de classes',
    menos: 'Diminuir o número de classes',
    mais: 'Aumentar o número de classes',
    sturges: (k: number) => `Sturges: ${String(k)}`,
  },
  cartoes: {
    media: 'Média',
    mediana: 'Mediana',
    moda: 'Moda',
    /** Linha de apoio do card "Moda" na contínua; `calculo` vem do backend e começa com "=". */
    apoioCzuber: (calculo: string) => `Moda de Czuber, pelas classes: Mo ${calculo}`,
    proporcao: 'Proporção',
    desvioPadrao: 'Desvio padrão',
    cv: 'Coeficiente de variação',
    iqr: 'Intervalo interquartil (IQR)',
    amplitude: 'Amplitude',
    variancia: 'Variância',
    semModa: 'Sem moda',
    seloModa: { amodal: undefined, unimodal: undefined, bimodal: 'Bimodal', multimodal: 'Multimodal' },
    seloCv: { baixa: 'Variação baixa', media: 'Variação moderada', alta: 'Variação alta' },
    notaVariancia: 'Fica na unidade dos dados ao quadrado; para ler, use o desvio padrão.',
    populacional: (desvio: string, variancia: string) =>
      `Valores amostrais (n − 1). Se os dados forem a população inteira: σ = ${desvio} e σ² = ${variancia}.`,
    faixasCv: 'CV abaixo de 15% indica variação baixa; de 15% a 30%, moderada; acima de 30%, alta.',
  },
  separatrizes: {
    titulo: (coluna: string) => `Separatrizes de ${coluna}`,
    quartis: 'Quartis',
    decis: 'Decis',
    percentis: 'Percentis',
    verTodos: 'Ver os 99 percentis',
    todosPercentis: 'Todos os percentis',
  },
  posicao: {
    titulo: 'Onde está meu valor?',
    campo: (coluna: string) => `Valor de ${coluna}`,
    comparar: 'Comparar com',
    tipos: { quartil: 'Quartil', decil: 'Decil', percentil: 'Percentil' } satisfies Record<TipoSeparatriz, string>,
    dica: 'Digite um valor para ver em que parte dos dados ele cai.',
    erroValor: 'Digite um número. Use vírgula para decimais, como 72,5.',
    foraTitulo: 'Fora da faixa observada.',
    abaixo: (minimo: string) => `O valor está abaixo do menor dado observado (${minimo}).`,
    acima: (maximo: string) => `O valor está acima do maior dado observado (${maximo}).`,
    minimo: 'mín',
    maximo: 'máx',
    descricaoRegua: (d: { minimo: string; maximo: string; marcas: string; valor: string; regiao: string }) =>
      `Régua de ${d.minimo} a ${d.maximo} com ${d.marcas}; o valor ${d.valor} fica no ${d.regiao}.`,
  },
  graficos: {
    tipoGrafico: 'Tipo de gráfico',
    recomendado: 'recomendado',
    porque: 'Por que este gráfico?',
    resumo: 'Resumo do gráfico',
    semFiguras: { titulo: 'Nenhum gráfico disponível', descricao: 'Não há gráficos para esta coluna.' },
  },
};
```

**Passo 3: utilitários de teste** — reutilize os do M1.6 (não crie `apiFalsa`, `sessaoFalsa` nem outro `renderizar`):
- `simularApi(rotas)` / `chamadasPara(falso, metodo, caminho)` (`src/testes/api.ts`): rotas sem o prefixo `/api` e sem query; erro = `{ caminho, status: 400, corpo: { codigo, mensagem, sugestao } }`; as URLs chamadas (com query) ficam em `chamadasPara(...).map((c) => c.url)`.
- `renderizarComProvedores(ui, { rota?, dataset? })` (`src/testes/renderizar.tsx`): provedores reais (sessão, tema, toasts, react-query sem retentativa) e roteador em memória; devolve `usuario` e `roteador` (a busca atual fica em `roteador.state.location.search`). Com `dataset: DATASET_TESTE` a sessão entra depois da 1ª renderização: use `findBy…` na primeira asserção. Sem `dataset`, a sessão começa vazia.
- `criarColuna`, `ID_DATASET` (`src/testes/fixtures/datasets.ts`; `ID_DATASET === DATASET_TESTE.id`).

Só o falso do gráfico é novo.

`testes/graficoFalso.tsx` (o Plotly não roda no jsdom):

```tsx
interface Props {
  titulo: string;
  resumo: string;
}

/** Uso: vi.mock('<caminho>/shared/graficos/Grafico', () => import('<caminho>/testes/graficoFalso')); */
export default function GraficoFalso({ titulo, resumo }: Readonly<Props>) {
  return (
    <figure aria-label={titulo} data-resumo={resumo}>
      <figcaption>{titulo}</figcaption>
    </figure>
  );
}
```

**Passo 4: `testes/fixturesAnalise.ts`** (fonte única de objetos grandes; os testes derivam variações com espalhamento). Contratos finais do M1.4/M1.5: cada `Formula` tem `chave`; cada `Medida` tem `formula` (a chave, ou `null`); cada `Figura` tem `rotulo`.

```ts
import { vi } from 'vitest';
import type { components } from '../shared/api/schema';
import type { PropsPainel } from '../features/analise/tipos';
import { criarColuna, ID_DATASET } from './fixtures/datasets';

type Esquemas = components['schemas'];
type Analise = Esquemas['Analise'];
type Medida = Esquemas['Medida'];
type LinhaFrequencia = Esquemas['LinhaFrequencia'];
type ValorSeparatriz = Esquemas['ValorSeparatriz'];
type TipoColuna = Esquemas['TipoColuna'];

export function medida(valor: Medida['valor'], extra: Partial<Medida> = {}): Medida {
  return { valor, aplicavel: true, motivo: null, calculo: null, interpretacao: null, formula: null, ...extra };
}

export function naoSeAplica(motivo: string): Medida {
  return { valor: null, aplicavel: false, motivo, calculo: null, interpretacao: null, formula: null };
}

export const colunasPesquisa: TipoColuna[] = [
  criarColuna({ coluna: 'id', tipo: 'identificador' }),
  criarColuna({ coluna: 'sexo', tipo: 'binaria' }),
  criarColuna({ coluna: 'peso_kg', tipo: 'continua' }),
  criarColuna({ coluna: 'cidade', tipo: 'nominal' }),
];

const N = 227;

function linhaClasse(rotulo: string, limites: readonly [number, number], fi: number, fAcumulada: number): LinhaFrequencia {
  const [inferior, superior] = limites;
  return {
    rotulo, valor: null, limite_inferior: inferior, limite_superior: superior, ponto_medio: (inferior + superior) / 2,
    fi, fri: fi / N, fr_pct: (fi / N) * 100, f_acum: fAcumulada, fr_acum: fAcumulada / N, fr_acum_pct: (fAcumulada / N) * 100,
  };
}

function linhaCategoria(rotulo: string, fi: number, total: number): LinhaFrequencia {
  return {
    rotulo, valor: rotulo, limite_inferior: null, limite_superior: null, ponto_medio: null,
    fi, fri: fi / total, fr_pct: (fi / total) * 100, f_acum: null, fr_acum: null, fr_acum_pct: null,
  };
}

function separatriz(prefixo: string, indice: number, p: number, valor: number): ValorSeparatriz {
  return { rotulo: `${prefixo}${String(indice)}`, p, valor };
}

export const quartisPeso: ValorSeparatriz[] = [
  separatriz('Q', 1, 0.25, 62.1),
  separatriz('Q', 2, 0.5, 69.8),
  separatriz('Q', 3, 0.75, 77.9),
];

function figura(id: string, rotulo: string, recomendado: boolean): Esquemas['Figura'] {
  return {
    id, rotulo, titulo: `Figura ${id} de peso_kg`, resumo: `Resumo de ${id}.`, porque: `Por que ${id}.`,
    recomendado, dados: { data: [], layout: {} },
  };
}

const APLICAVEL_NUMERICA = {
  acumulada: true, media: true, mediana: true, moda_czuber: true, proporcao: false,
  separatrizes: true, posicao: true, dispersao: true, variancia: true, cv: true,
};

export const analiseContinua: Analise = {
  coluna: 'peso_kg', tipo: 'continua', n: N, n_faltantes: 3,
  aplicavel: APLICAVEL_NUMERICA,
  nao_aplicavel: [{ item: 'proporcao', motivo: 'Proporção não se aplica a quantitativas contínuas: precisa de duas categorias.' }],
  frequencias: {
    tipo: 'continua', total: N, k: 3, k_sturges: 9, h: 16.5, metodo_classes: 'usuario',
    acumulada_aplicavel: true, motivo_acumulada: null, indice_modal: 1,
    linhas: [
      linhaClasse('43,5 ⊢ 60,0', [43.5, 60], 33, 33),
      linhaClasse('60,0 ⊢ 76,5', [60, 76.5], 132, 165),
      linhaClasse('76,5 ⊢ 93,0', [76.5, 93], 62, N),
    ],
  },
  tendencia: {
    media: medida(70.3, { calculo: '= 15.958,1 / 227 = 70,3', interpretacao: 'Em média, os valores ficam em 70,3.', formula: 'media' }),
    mediana: medida(69.8, { interpretacao: 'Metade dos valores fica até 69,8.', formula: 'mediana' }),
    moda: { valores: [72], classificacao: 'unimodal', interpretacao: 'O valor que mais se repete é 72 (9 vezes).' },
    moda_czuber: medida(68.9, { interpretacao: 'Estimada a partir da classe mais comum.', formula: 'moda_czuber' }),
    proporcao: naoSeAplica('Proporção não se aplica a quantitativas contínuas: precisa de duas categorias.'),
  },
  separatrizes: {
    quartis: quartisPeso,
    decis: Array.from({ length: 9 }, (_, i) => separatriz('D', i + 1, (i + 1) / 10, 56 + i * 3.6)),
    percentis: Array.from({ length: 99 }, (_, i) => separatriz('P', i + 1, (i + 1) / 100, 44 + i * 0.49)),
    destaques: ['P1', 'P5', 'P10', 'P25', 'P50', 'P75', 'P90', 'P95', 'P99'],
  },
  dispersao: {
    amplitude: medida(49.1, { interpretacao: 'Do menor (43,8) ao maior (92,9) valor.', formula: 'amplitude' }),
    variancia: medida(125.4, { formula: 'variancia' }),
    variancia_populacional: medida(124.85, { formula: 'variancia_populacional' }),
    desvio_padrao: medida(11.2, {
      calculo: '= √(28.348,2 / 226) = 11,2',
      interpretacao: 'Em geral, os valores ficam a cerca de 11,2 da média.',
      formula: 'desvio_padrao',
    }),
    desvio_padrao_populacional: medida(11.17),
    iqr: medida(15.8, { formula: 'iqr' }),
    cv: medida(15.9, { interpretacao: 'O desvio é 15,9% da média.', formula: 'cv' }),
    classificacao_cv: 'media',
  },
  interpretacoes: ['Média e mediana estão próximas (diferença de 0,5): os dados são quase simétricos.'],
  formulas: [
    { chave: 'media', nome: 'Média', latex: '\\bar{x}=\\frac{\\sum x_i}{n}', texto: 'x̄ = Σxᵢ / n' },
    { chave: 'moda_czuber', nome: 'Moda de Czuber', latex: 'Mo=L_i+\\frac{\\Delta_1}{\\Delta_1+\\Delta_2}\\cdot h', texto: 'Mo = Lᵢ + [Δ₁ / (Δ₁ + Δ₂)] · h' },
    { chave: 'desvio_padrao', nome: 'Desvio padrão', latex: 's=\\sqrt{\\frac{\\sum (x_i-\\bar{x})^2}{n-1}}', texto: 's = √[Σ(xᵢ − x̄)² / (n − 1)]' },
  ],
  figuras: [figura('principal', 'Histograma', true), figura('boxplot', 'Boxplot', false), figura('ogiva', 'Ogiva', false)],
};

const MOTIVO_DISPERSAO = 'Desvio padrão não se aplica a qualitativas: precisa de distâncias entre números.';
const TOTAL_CIDADES = 228;

export const analiseNominal: Analise = {
  coluna: 'cidade', tipo: 'nominal', n: TOTAL_CIDADES, n_faltantes: 2,
  aplicavel: {
    acumulada: false, media: false, mediana: false, moda_czuber: false, proporcao: false,
    separatrizes: false, posicao: false, dispersao: false, variancia: false, cv: false,
  },
  // O backend emite separatrizes, dispersao e posicao quando não se aplicam (M1.4).
  nao_aplicavel: [
    { item: 'separatrizes', motivo: 'Separatrizes não se aplicam a qualitativas nominais: as categorias não têm ordem.' },
    { item: 'dispersao', motivo: MOTIVO_DISPERSAO },
    { item: 'posicao', motivo: '"Onde está meu valor?" só funciona com colunas numéricas.' },
  ],
  frequencias: {
    tipo: 'nominal', total: TOTAL_CIDADES, k: null, k_sturges: null, h: null, metodo_classes: null,
    acumulada_aplicavel: false, indice_modal: 0,
    motivo_acumulada: 'Frequência acumulada não se aplica a qualitativas nominais: as cidades não têm uma ordem natural para somar "até aqui".',
    linhas: [linhaCategoria('Goiânia', 120, TOTAL_CIDADES), linhaCategoria('Anápolis', 70, TOTAL_CIDADES), linhaCategoria('Trindade', 38, TOTAL_CIDADES)],
  },
  tendencia: {
    media: naoSeAplica('Média não se aplica a categorias sem número: não dá para somar cidades.'),
    mediana: naoSeAplica('Mediana não se aplica a qualitativas nominais: as cidades não têm ordem.'),
    moda: { valores: ['Goiânia'], classificacao: 'unimodal', interpretacao: 'A cidade mais frequente: 120 de 228 pessoas (52,6%).' },
    moda_czuber: naoSeAplica('Moda de Czuber só vale para dados em classes.'),
    proporcao: naoSeAplica('Proporção não se aplica a qualitativas nominais: precisa de duas categorias.'),
  },
  separatrizes: null,
  dispersao: null,
  interpretacoes: [],
  formulas: [],
  figuras: [{ ...figura('principal', 'Barras', true), titulo: 'Pessoas por cidade (n = 228)' }],
};

export const analiseBinaria: Analise = {
  ...analiseNominal,
  coluna: 'sexo',
  tipo: 'binaria',
  aplicavel: { ...analiseNominal.aplicavel, proporcao: true },
  tendencia: {
    ...analiseNominal.tendencia,
    proporcao: medida(0.52, { interpretacao: '52% das linhas são M.', formula: 'proporcao' }),
  },
};

export const posicaoQuartil: Esquemas['Posicao'] = {
  valor: 75, tipo: 'quartil', regiao: '3º quartil (entre Q2 e Q3)', indice: 3,
  limite_inferior: 69.8, limite_superior: 77.9, posicao_percentil: 66, fora_da_faixa: null,
  minimo: 43.8, maximo: 92.9, marcas: quartisPeso,
  frase: 'O valor 75 está no 3º quartil (entre Q2 = 69,8 e Q3 = 77,9). Cerca de 66% dos dados são menores que ele.',
};

export const posicaoAcima: Esquemas['Posicao'] = {
  ...posicaoQuartil,
  valor: 120, regiao: '4º quartil (acima de Q3)', indice: 4, limite_inferior: 77.9, limite_superior: null,
  posicao_percentil: 100, fora_da_faixa: 'acima',
  frase: 'O valor 120 está no 4º quartil (acima de Q3 = 77,9). Todos os dados são menores que ele.',
};

export function propsPainel(analise: Analise): PropsPainel {
  return { analise, datasetId: ID_DATASET, atualizando: false, classes: null, aoMudarClasses: vi.fn() };
}
```
Se o `schema.d.ts` gerado marcar algum campo como opcional ou com outro nome, corrija a fixture — **o TypeScript acusa**, e esse é o objetivo de tipar as fixtures pelo schema.

**Passo 5: teste do `api.ts` (falha)** — `features/analise/api.test.ts`

```ts
import { describe, expect, it } from 'vitest';
import { ErroApi } from '../../shared/api/cliente';
import { chavesDataset } from '../../shared/api/dataset';
import { caminhoAnalise, caminhoPosicao, chavesAnalise, podeTentarDeNovo } from './api';

describe('caminhos da API de análise', () => {
  it('pede a análise sem classes quando o usuário não mudou o número de classes', () => {
    expect(caminhoAnalise('ds1', 'peso_kg', null)).toBe('/datasets/ds1/colunas/peso_kg/analise');
  });

  it('manda o número de classes escolhido', () => {
    expect(caminhoAnalise('ds1', 'peso_kg', 12)).toBe('/datasets/ds1/colunas/peso_kg/analise?classes=12');
  });

  it('codifica nomes de coluna com espaço e acento', () => {
    expect(caminhoAnalise('ds1', 'renda média', null)).toBe('/datasets/ds1/colunas/renda%20m%C3%A9dia/analise');
  });

  it('pede a posição com valor e tipo de separatriz', () => {
    expect(caminhoPosicao({ datasetId: 'ds1', coluna: 'peso_kg', valor: 72.5, tipo: 'decil' })).toBe(
      '/datasets/ds1/colunas/peso_kg/posicao?valor=72.5&tipo=decil',
    );
  });

  it('usa o prefixo de análises do M1.6 (limpeza e troca de tipo invalidam análise e posição)', () => {
    expect(chavesAnalise.analise('ds1', 'peso_kg', null)).toEqual(['datasets', 'ds1', 'analise', 'peso_kg', null]);
    expect(chavesAnalise.posicao('ds1', 'peso_kg', 75, 'quartil').slice(0, 3)).toEqual(chavesDataset.analises('ds1'));
  });
});

describe('podeTentarDeNovo', () => {
  it.each(['COLUNA_IGNORADA', 'COLUNA_VAZIA', 'COLUNA_NAO_ENCONTRADA'])('não oferece nova tentativa para %s', (codigo) => {
    expect(podeTentarDeNovo(new ErroApi(400, { codigo, mensagem: 'x', sugestao: 'y' }))).toBe(false);
  });

  it('oferece nova tentativa para falha de conexão', () => {
    expect(podeTentarDeNovo(new ErroApi(0, { codigo: 'SEM_CONEXAO', mensagem: 'x', sugestao: 'y' }))).toBe(true);
  });
});
```

**Passo 6: rodar e ver falhar** — `npm run test -- analise` → FAIL (`./api` não existe).

**Passo 7: implementar `features/analise/api.ts`**

```ts
import { keepPreviousData, useQuery, type UseQueryResult } from '@tanstack/react-query';
import { ErroApi, requisitar } from '../../shared/api/cliente';
import { caminhoDataset, chavesDataset } from '../../shared/api/dataset';
import type { Analise, Posicao, TipoSeparatriz } from './tipos';

export interface ConsultaPosicao {
  datasetId: string;
  coluna: string;
  valor: number | null;
  tipo: TipoSeparatriz;
}

/**
 * Chaves sob `chavesDataset.analises(id)` (convenção do M1.6): limpeza e troca de tipo
 * invalidam análise e posição de uma vez (tabela de invalidação do M1.6).
 */
export const chavesAnalise = {
  analise: (datasetId: string, coluna: string, classes: number | null) =>
    [...chavesDataset.analises(datasetId), coluna, classes] as const,
  posicao: (datasetId: string, coluna: string, valor: number | null, tipo: TipoSeparatriz) =>
    [...chavesDataset.analises(datasetId), coluna, 'posicao', valor, tipo] as const,
};

function caminhoColuna(datasetId: string, coluna: string): string {
  return caminhoDataset(datasetId, `/colunas/${encodeURIComponent(coluna)}`);
}

export function caminhoAnalise(datasetId: string, coluna: string, classes: number | null): string {
  const base = `${caminhoColuna(datasetId, coluna)}/analise`;
  return classes === null ? base : `${base}?${new URLSearchParams({ classes: String(classes) }).toString()}`;
}

export function caminhoPosicao(consulta: ConsultaPosicao & { valor: number }): string {
  const parametros = new URLSearchParams({ valor: String(consulta.valor), tipo: consulta.tipo });
  return `${caminhoColuna(consulta.datasetId, consulta.coluna)}/posicao?${parametros.toString()}`;
}

const CODIGOS_DEFINITIVOS = new Set(['COLUNA_IGNORADA', 'COLUNA_VAZIA', 'COLUNA_NAO_ENCONTRADA']);

/** Erros que não mudam ao repetir a requisição não ganham botão "Tentar de novo". */
export function podeTentarDeNovo(erro: unknown): boolean {
  return !(erro instanceof ErroApi && CODIGOS_DEFINITIVOS.has(erro.codigo));
}

export function useAnalise(datasetId: string, coluna: string | null, classes: number | null): UseQueryResult<Analise> {
  return useQuery({
    queryKey: chavesAnalise.analise(datasetId, coluna ?? '', classes),
    queryFn: () => requisitar<Analise>(caminhoAnalise(datasetId, coluna ?? '', classes)),
    enabled: coluna !== null,
    // Mantém a tabela na tela ao mudar o nº de classes; ao trocar de coluna mostra o carregando (4h).
    placeholderData: (anterior) => (anterior?.coluna === coluna ? anterior : undefined),
  });
}

export function usePosicao(consulta: ConsultaPosicao): UseQueryResult<Posicao> {
  const { datasetId, coluna, valor, tipo } = consulta;
  return useQuery({
    queryKey: chavesAnalise.posicao(datasetId, coluna, valor, tipo),
    queryFn: () => requisitar<Posicao>(caminhoPosicao({ datasetId, coluna, tipo, valor: valor ?? 0 })),
    enabled: valor !== null,
    placeholderData: keepPreviousData,
  });
}
```
`useColunasAnalisaveis` vem de `shared/api/colunas.ts` (Tarefa 1).

**Passo 8: rodar e ver passar** — `npm run test -- analise` → verdes · `npm run lint`.

**Passo 9: commit**
```bash
git add frontend/src/features/analise frontend/src/testes
git commit -m "feat(analise): adiciona tipos, textos, hooks da API e fixtures de teste da análise univariada"
```

---

### Tarefa 3: Coluna e classes na URL, abas aplicáveis e estado da tela

**Arquivos:**
- Criar: `frontend/src/features/analise/parametros.ts` · Teste: `parametros.test.ts`
- Criar: `frontend/src/features/analise/abas.ts` · Teste: `abas.test.ts`
- Criar: `frontend/src/features/analise/estadoAnalise.ts` · Teste: `estadoAnalise.test.ts`
- Criar: `frontend/src/features/analise/hooks/useParametrosAnalise.ts`

**Decisões desta tarefa:** a coluna escolhida e o nº de classes ficam na URL (`/analise?coluna=peso_kg&classes=12`): sobrevivem ao recarregar e o botão Voltar volta à coluna anterior. Trocar de coluna apaga `classes` (volta para Sturges). A aba ativa fica em estado local; se a aba pedida estiver desabilitada para a nova coluna, a tela mostra "Frequências" (estado derivado, sem `useEffect`) e volta à aba pedida quando outra coluna permitir.

**Passo 1: testes (falham)**

`parametros.test.ts`:

```ts
import { describe, expect, it } from 'vitest';
import { filtrarAnalisaveis } from '../../shared/api/colunas';
import { colunasPesquisa } from '../../testes/fixturesAnalise';
import { colunaEscolhida, comClasses, comColuna, lerParametros } from './parametros';

describe('lerParametros', () => {
  it('lê coluna e classes da URL', () => {
    expect(lerParametros(new URLSearchParams('coluna=peso_kg&classes=12'))).toEqual({ coluna: 'peso_kg', classes: 12 });
  });

  it('sem parâmetros: nenhuma coluna e classes de Sturges', () => {
    expect(lerParametros(new URLSearchParams())).toEqual({ coluna: null, classes: null });
  });

  it.each([
    ['2', 3],
    ['31', 30],
    ['abc', null],
    ['', null],
    ['7.5', null],
  ])('classes=%s vira %s', (texto, esperado) => {
    expect(lerParametros(new URLSearchParams({ classes: texto })).classes).toBe(esperado);
  });
});

describe('comColuna e comClasses', () => {
  it('trocar a coluna volta para Sturges e preserva o resto da busca', () => {
    expect(comColuna(new URLSearchParams('coluna=peso_kg&classes=12&x=1'), 'cidade').toString()).toBe('coluna=cidade&x=1');
  });

  it('limita o número de classes entre 3 e 30', () => {
    expect(comClasses(new URLSearchParams('coluna=peso_kg'), 40).get('classes')).toBe('30');
    expect(comClasses(new URLSearchParams('coluna=peso_kg'), 1).get('classes')).toBe('3');
  });
});

describe('colunaEscolhida', () => {
  const analisaveis = filtrarAnalisaveis(colunasPesquisa);

  it('usa a coluna da URL quando ela existe', () => {
    expect(colunaEscolhida('cidade', analisaveis)?.coluna).toBe('cidade');
  });

  it('cai na primeira coluna analisável quando a da URL não existe ou é identificador', () => {
    expect(colunaEscolhida('id', analisaveis)?.coluna).toBe('sexo');
    expect(colunaEscolhida(null, analisaveis)?.coluna).toBe('sexo');
  });

  it('devolve null quando não há colunas', () => {
    expect(colunaEscolhida('peso_kg', [])).toBeNull();
  });
});
```

`abas.test.ts`:

```ts
import { describe, expect, it } from 'vitest';
import { analiseContinua, analiseNominal } from '../../testes/fixturesAnalise';
import { abaEfetiva, abasDaAnalise } from './abas';
import { TEXTOS_ANALISE } from './textos';

describe('abasDaAnalise', () => {
  it('mostra as 5 abas do M1, sem "Forma e distribuição" (D60)', () => {
    expect(abasDaAnalise(analiseContinua).map((a) => a.rotulo)).toEqual([
      'Frequências',
      'Tendência central',
      'Separatrizes',
      'Dispersão',
      'Gráficos',
    ]);
  });

  it('contínua: nenhuma aba desabilitada', () => {
    expect(abasDaAnalise(analiseContinua).some((a) => a.desabilitada === true)).toBe(false);
  });

  it('nominal: Separatrizes e Dispersão desabilitadas com o motivo de nao_aplicavel', () => {
    const desabilitadas = abasDaAnalise(analiseNominal).filter((a) => a.desabilitada === true);

    expect(desabilitadas).toEqual([
      { id: 'separatrizes', rotulo: 'Separatrizes', desabilitada: true, motivo: analiseNominal.nao_aplicavel[0]?.motivo },
      { id: 'dispersao', rotulo: 'Dispersão', desabilitada: true, motivo: analiseNominal.nao_aplicavel[1]?.motivo },
    ]);
  });

  it('sem motivo no backend, usa o texto padrão', () => {
    const semMotivo = { ...analiseNominal, nao_aplicavel: [] };

    expect(abasDaAnalise(semMotivo).find((a) => a.id === 'dispersao')?.motivo).toBe(TEXTOS_ANALISE.motivoPadrao);
  });
});

describe('abaEfetiva', () => {
  it('mantém a aba pedida quando ela está habilitada', () => {
    expect(abaEfetiva('separatrizes', abasDaAnalise(analiseContinua))).toBe('separatrizes');
  });

  it('volta para Frequências quando a aba pedida não se aplica à coluna', () => {
    expect(abaEfetiva('separatrizes', abasDaAnalise(analiseNominal))).toBe('frequencias');
  });
});
```

`estadoAnalise.test.ts`:

```ts
import { describe, expect, it, vi } from 'vitest';
import { ErroApi } from '../../shared/api/cliente';
import { analiseContinua, colunasPesquisa } from '../../testes/fixturesAnalise';
import { estadoDaAnalise, type ConsultaSimples } from './estadoAnalise';
import type { Analise, TipoColuna } from './tipos';

function consulta<T>(parcial: Partial<ConsultaSimples<T>>): ConsultaSimples<T> {
  return { status: 'pending', data: undefined, error: null, isPlaceholderData: false, refetch: vi.fn(), ...parcial };
}

const colunasProntas = consulta<TipoColuna[]>({ status: 'success', data: colunasPesquisa });
const analisePendente = consulta<Analise>({});

describe('estadoDaAnalise', () => {
  it('carrega as colunas primeiro', () => {
    expect(estadoDaAnalise(consulta({}), analisePendente, null).status).toBe('carregando-colunas');
  });

  it('erro nas colunas pode ser tentado de novo', () => {
    const colunas = consulta<TipoColuna[]>({ status: 'error', error: new Error('rede') });
    const estado = estadoDaAnalise(colunas, analisePendente, null);

    expect(estado.status).toBe('erro');
    if (estado.status !== 'erro') return;
    estado.tentarDeNovo?.();
    expect(colunas.refetch).toHaveBeenCalled();
  });

  it('sem coluna analisável mostra o estado vazio', () => {
    expect(estadoDaAnalise(colunasProntas, analisePendente, null).status).toBe('sem-colunas');
  });

  it('enquanto a análise não chega, mostra "Calculando…" com o nome da coluna', () => {
    expect(estadoDaAnalise(colunasProntas, analisePendente, 'peso_kg')).toEqual({ status: 'calculando', coluna: 'peso_kg' });
  });

  it('COLUNA_IGNORADA não oferece "Tentar de novo"', () => {
    const erro = new ErroApi(400, { codigo: 'COLUNA_IGNORADA', mensagem: 'A coluna id é um identificador.', sugestao: '' });
    const estado = estadoDaAnalise(colunasProntas, consulta<Analise>({ status: 'error', error: erro }), 'id');

    expect(estado).toEqual({ status: 'erro', erro, tentarDeNovo: null });
  });

  it('com dados de outro nº de classes (placeholder), fica pronta e marcada como atualizando', () => {
    const analise = consulta<Analise>({ status: 'success', data: analiseContinua, isPlaceholderData: true });

    expect(estadoDaAnalise(colunasProntas, analise, 'peso_kg')).toEqual({
      status: 'pronta',
      analise: analiseContinua,
      atualizando: true,
    });
  });
});
```

**Passo 2: rodar e ver falhar** — `npm run test -- analise` → FAIL.

**Passo 3: implementar**

`parametros.ts`:

```ts
import type { TipoColuna } from './tipos';

export const LIMITES_CLASSES = { minimo: 3, maximo: 30 } as const;

export interface ParametrosAnalise {
  coluna: string | null;
  classes: number | null;
}

export function limitarClasses(k: number): number {
  return Math.min(LIMITES_CLASSES.maximo, Math.max(LIMITES_CLASSES.minimo, k));
}

function lerClasses(texto: string | null): number | null {
  if (texto === null || texto.trim() === '') return null;
  const k = Number(texto);
  return Number.isInteger(k) ? limitarClasses(k) : null;
}

export function lerParametros(busca: URLSearchParams): ParametrosAnalise {
  return { coluna: busca.get('coluna'), classes: lerClasses(busca.get('classes')) };
}

/** Trocar de coluna volta para o número de classes de Sturges. */
export function comColuna(busca: URLSearchParams, coluna: string): URLSearchParams {
  const nova = new URLSearchParams(busca);
  nova.set('coluna', coluna);
  nova.delete('classes');
  return nova;
}

export function comClasses(busca: URLSearchParams, k: number): URLSearchParams {
  const nova = new URLSearchParams(busca);
  nova.set('classes', String(limitarClasses(k)));
  return nova;
}

/** A coluna da URL, se ainda for analisável; senão a primeira da lista. */
export function colunaEscolhida(pedida: string | null, colunas: readonly TipoColuna[]): TipoColuna | null {
  return colunas.find((coluna) => coluna.coluna === pedida) ?? colunas[0] ?? null;
}
```

`abas.ts`:

```ts
import { TEXTOS_ANALISE } from './textos';
import type { Analise, IdAba } from './tipos';

export interface DefinicaoAba {
  id: IdAba;
  rotulo: string;
  desabilitada?: boolean;
  motivo?: string;
}

const ORDEM_ABAS: readonly IdAba[] = ['frequencias', 'tendencia', 'separatrizes', 'dispersao', 'graficos'];

/** Abas que dependem de `aplicavel` (contrato da visão geral); as demais valem para todo tipo. */
const CHAVE_APLICAVEL: Partial<Record<IdAba, string>> = { separatrizes: 'separatrizes', dispersao: 'dispersao' };

export function estaAplicavel(analise: Analise, chave: string): boolean {
  return analise.aplicavel[chave] === true;
}

export function motivoNaoAplicavel(analise: Analise, item: string): string {
  const encontrado = analise.nao_aplicavel.find((naoAplicavel) => naoAplicavel.item === item);
  return encontrado?.motivo ?? TEXTOS_ANALISE.motivoPadrao;
}

function definirAba(analise: Analise, id: IdAba): DefinicaoAba {
  const rotulo = TEXTOS_ANALISE.abas[id];
  const chave = CHAVE_APLICAVEL[id];
  if (chave === undefined || estaAplicavel(analise, chave)) return { id, rotulo };
  return { id, rotulo, desabilitada: true, motivo: motivoNaoAplicavel(analise, chave) };
}

export function abasDaAnalise(analise: Analise): DefinicaoAba[] {
  return ORDEM_ABAS.map((id) => definirAba(analise, id));
}

export function abaEfetiva(pedida: IdAba, abas: readonly DefinicaoAba[]): IdAba {
  const aba = abas.find((candidata) => candidata.id === pedida);
  return aba !== undefined && aba.desabilitada !== true ? pedida : 'frequencias';
}
```

`estadoAnalise.ts`:

```ts
import { podeTentarDeNovo } from './api';
import type { Analise, TipoColuna } from './tipos';

/** O pedaço de UseQueryResult que a tela usa (UseQueryResult é compatível por estrutura). */
export interface ConsultaSimples<T> {
  status: 'pending' | 'error' | 'success';
  data: T | undefined;
  error: unknown;
  isPlaceholderData: boolean;
  refetch: () => unknown;
}

export type EstadoAnalise =
  | { status: 'carregando-colunas' }
  | { status: 'sem-colunas' }
  | { status: 'calculando'; coluna: string }
  | { status: 'erro'; erro: unknown; tentarDeNovo: (() => void) | null }
  | { status: 'pronta'; analise: Analise; atualizando: boolean };

function estadoDeErro(consulta: ConsultaSimples<unknown>): EstadoAnalise {
  const tentarDeNovo = () => {
    void consulta.refetch();
  };
  return { status: 'erro', erro: consulta.error, tentarDeNovo: podeTentarDeNovo(consulta.error) ? tentarDeNovo : null };
}

export function estadoDaAnalise(
  colunas: ConsultaSimples<TipoColuna[]>,
  analise: ConsultaSimples<Analise>,
  coluna: string | null,
): EstadoAnalise {
  if (colunas.status === 'error') return estadoDeErro(colunas);
  if (colunas.status === 'pending') return { status: 'carregando-colunas' };
  if (coluna === null) return { status: 'sem-colunas' };
  if (analise.status === 'error') return estadoDeErro(analise);
  if (analise.data === undefined) return { status: 'calculando', coluna };
  return { status: 'pronta', analise: analise.data, atualizando: analise.isPlaceholderData };
}
```

`hooks/useParametrosAnalise.ts`:

```ts
import { startTransition } from 'react';
import { useSearchParams } from 'react-router';
import { comClasses, comColuna, lerParametros, type ParametrosAnalise } from '../parametros';

export interface ParametrosAnaliseNaUrl extends ParametrosAnalise {
  escolherColuna: (coluna: string) => void;
  mudarClasses: (k: number) => void;
}

export function useParametrosAnalise(): ParametrosAnaliseNaUrl {
  const [busca, definirBusca] = useSearchParams();

  return {
    ...lerParametros(busca),
    escolherColuna: (coluna) => {
      // Trocar de coluna não é urgente: o select responde na hora e o recálculo vem depois.
      startTransition(() => {
        definirBusca((atual) => comColuna(atual, coluna));
      });
    },
    mudarClasses: (k) => {
      definirBusca((atual) => comClasses(atual, k), { replace: true });
    },
  };
}
```

**Passo 4: rodar e ver passar** — `npm run test -- analise` · `npm run lint`.

**Passo 5: commit**
```bash
git add frontend/src/features/analise
git commit -m "feat(analise): guarda coluna e classes na URL e define abas e estados da tela por funções puras"
```

---

### Tarefa 4: Cartões de métrica (`Medida` → `CardMetrica`)

**Arquivos:**
- Criar: `frontend/src/features/analise/formatacao.ts`
- Criar: `frontend/src/features/analise/cartoes.ts` · Teste: `cartoes.test.ts`
- Criar: `frontend/src/features/analise/components/GradeCardsMetrica.tsx` + `GradeCardsMetrica.module.css`
- Criar: `frontend/src/features/analise/components/paineis.module.css` (classes comuns aos painéis)

**Ideia:** Tendência, Dispersão e o resumo categórico da aba Frequências (4g) descrevem os cards como listas de `DefinicaoCartao` (`{rotulo, medida, selo, unidade, apoio}`); um único `propsDoCartao` converte para as props do `CardMetrica` e um único `GradeCardsMetrica` desenha. Nada de JSX repetido entre as abas.

**Regras do mapeamento:**
- `medida.aplicavel === false` → `valor: '—'` + `naoAplicavel: { motivo }`. O `motivo` **já vem pronto do backend** no formato "{medida} não se aplica a {tipo}: {motivo}." (spec 16).
- Valor número → `formatarNumero`; texto (mediana ordinal, moda nominal) → como veio.
- Fórmula: `analise.formulas.find((f) => f.chave === medida.formula)` (a chave vem em cada `Medida`, M1.4); `expressao = formula.texto`, `calculo = medida.calculo` (se houver). Sem chave ou sem fórmula com essa chave → card sem "Ver fórmula". `Moda` não é `Medida` e não traz chave: o card da moda usa a chave fixa `moda`.
- 3º card da Tendência = **"Moda"** com a moda bruta de `tendencia.moda` em todos os tipos (várias modas juntas com " · ", selo "Bimodal"/"Multimodal"; amodal → "Sem moda"), como pede a spec 05 e mostra o print 4c. **Contínua** (`aplicavel.moda_czuber`): a moda de Czuber entra como **apoio** do mesmo card, no "Ver fórmula" (`expressao` = fórmula `moda_czuber`; `calculo` = "Moda de Czuber, pelas classes: Mo = …"). Sem card a mais e sem prop nova no `CardMetrica`. **Desvio a confirmar com o usuário** (ver Tarefa 12).
- Binária: `aplicavel.proporcao` → 1º card "Proporção" no lugar de "Média".
- Dispersão: Desvio padrão · CV (unidade "%", 3 algarismos, selo da `classificacao_cv`) · IQR · Amplitude · Variância (sem interpretação do backend → "Fica na unidade dos dados ao quadrado; para ler, use o desvio padrão."). Os valores populacionais (D18) aparecem numa nota abaixo dos cards.

**Passo 1: teste (falha)** — `cartoes.test.ts`

```ts
import { describe, expect, it } from 'vitest';
import { formatarNumero } from '../../shared/lib/formatar';
import { analiseBinaria, analiseContinua, analiseNominal, medida } from '../../testes/fixturesAnalise';
import {
  cartoesDispersao,
  cartoesResumoCategorico,
  cartoesTendencia,
  notaPopulacional,
  propsDoCartao,
} from './cartoes';
import { TEXTOS_ANALISE } from './textos';
import type { Analise, Dispersao, Moda } from './tipos';

const C = TEXTOS_ANALISE.cartoes;
const dispersao = analiseContinua.dispersao as Dispersao;

function comModa(analise: Analise, valores: (number | string)[], classificacao: Moda['classificacao']): Analise {
  return { ...analise, tendencia: { ...analise.tendencia, moda: { valores, classificacao, interpretacao: 'x' } } };
}

describe('propsDoCartao', () => {
  it('formata o valor e acha a fórmula pela chave da medida', () => {
    const definicao = { id: 'media', rotulo: C.media, medida: analiseContinua.tendencia.media };

    expect(propsDoCartao(definicao, analiseContinua.formulas)).toEqual({
      rotulo: 'Média',
      valor: formatarNumero(70.3),
      interpretacao: 'Em média, os valores ficam em 70,3.',
      formula: { expressao: 'x̄ = Σxᵢ / n', calculo: '= 15.958,1 / 227 = 70,3' },
    });
  });

  it('item não aplicável vira card esmaecido com o motivo do backend', () => {
    const definicao = { id: 'media', rotulo: C.media, medida: analiseNominal.tendencia.media };

    expect(propsDoCartao(definicao, [])).toEqual({
      rotulo: 'Média',
      valor: '—',
      naoAplicavel: { motivo: 'Média não se aplica a categorias sem número: não dá para somar cidades.' },
    });
  });

  it('sem fórmula com a chave da medida, o card não ganha "Ver fórmula"', () => {
    const definicao = { id: 'iqr', rotulo: C.iqr, medida: medida(15.8, { formula: 'iqr' }) };

    expect(propsDoCartao(definicao, analiseContinua.formulas)).not.toHaveProperty('formula');
  });

  it('valor de texto (mediana ordinal) aparece como veio', () => {
    expect(propsDoCartao({ id: 'mediana', rotulo: C.mediana, medida: medida('bom') }, []).valor).toBe('bom');
  });
});

describe('cartoesTendencia', () => {
  it('contínua: média, mediana e moda bruta, com a moda de Czuber no "Ver fórmula"', () => {
    const cartoes = cartoesTendencia(analiseContinua);
    const moda = cartoes[2];

    expect(cartoes.map((c) => c.rotulo)).toEqual(['Média', 'Mediana', 'Moda']);
    if (moda === undefined) throw new Error('falta o card da moda');
    expect(moda.medida.valor).toBe(formatarNumero(72));
    expect(propsDoCartao(moda, analiseContinua.formulas).formula).toEqual({
      expressao: 'Mo = Lᵢ + [Δ₁ / (Δ₁ + Δ₂)] · h',
      calculo: C.apoioCzuber(`= ${formatarNumero(68.9)}`),
    });
  });

  it('binária: proporção no lugar da média', () => {
    expect(cartoesTendencia(analiseBinaria).map((c) => c.rotulo)).toEqual(['Proporção', 'Mediana', 'Moda']);
  });

  it('nominal: média e mediana não se aplicam; a moda é a categoria', () => {
    const [media, mediana, moda] = cartoesTendencia(analiseNominal);

    expect([media?.medida.aplicavel, mediana?.medida.aplicavel]).toEqual([false, false]);
    expect(moda?.medida.valor).toBe('Goiânia');
  });

  it('várias modas aparecem juntas com o selo da classificação', () => {
    const moda = cartoesTendencia(comModa(analiseNominal, ['Goiânia', 'Anápolis'], 'bimodal'))[2];

    expect(moda?.medida.valor).toBe('Goiânia · Anápolis');
    expect(moda?.selo).toBe('Bimodal');
  });

  it('sem moda (amodal) mostra "Sem moda"', () => {
    expect(cartoesTendencia(comModa(analiseNominal, [], 'amodal'))[2]?.medida.valor).toBe('Sem moda');
  });
});

describe('cartoesDispersao', () => {
  it('segue a ordem do design, com selo do CV e nota da variância', () => {
    const cartoes = cartoesDispersao(dispersao);

    expect(cartoes.map((c) => c.id)).toEqual(['desvio_padrao', 'cv', 'iqr', 'amplitude', 'variancia']);
    expect(cartoes[1]).toMatchObject({ unidade: '%', selo: 'Variação moderada' });
    expect(cartoes[4]?.medida.interpretacao).toBe(C.notaVariancia);
  });
});

describe('cartoesResumoCategorico', () => {
  it('moda + média, mediana e desvio padrão não aplicáveis (design 4g)', () => {
    const cartoes = cartoesResumoCategorico(analiseNominal);

    expect(cartoes.map((c) => c.rotulo)).toEqual(['Moda', 'Média', 'Mediana', 'Desvio padrão']);
    expect(cartoes[3]?.medida).toMatchObject({ aplicavel: false, motivo: analiseNominal.nao_aplicavel[1]?.motivo });
  });
});

describe('notaPopulacional', () => {
  it('mostra σ e σ² ao lado dos valores amostrais (D18)', () => {
    expect(notaPopulacional(dispersao)).toBe(C.populacional(formatarNumero(11.17), formatarNumero(124.85)));
  });

  it('some quando os populacionais não se aplicam', () => {
    const semPopulacional = { ...dispersao, desvio_padrao_populacional: { ...dispersao.desvio_padrao, aplicavel: false } };

    expect(notaPopulacional(semPopulacional)).toBeNull();
  });
});
```

**Passo 2: rodar e ver falhar** — `npm run test -- cartoes` → FAIL.

**Passo 3: implementar**

`formatacao.ts`:

```ts
import { formatarNumero } from '../../shared/lib/formatar';
import type { Medida } from './tipos';

/** Número em pt-BR; texto (categoria) como veio; ausente vira travessão. */
export function formatarValorMedida(valor: Medida['valor'], casasSignificativas?: number): string {
  if (valor === null) return '—';
  return typeof valor === 'number' ? formatarNumero(valor, casasSignificativas) : valor;
}

export function formatarOpcional(valor: number | null, formatar: (v: number) => string): string {
  return valor === null ? '—' : formatar(valor);
}
```

`cartoes.ts`:

```ts
import type { ComponentProps } from 'react';
import type CardMetrica from '../../shared/ui/CardMetrica';
import { estaAplicavel, motivoNaoAplicavel } from './abas';
import { formatarValorMedida } from './formatacao';
import { TEXTOS_ANALISE } from './textos';
import type { Analise, Dispersao, Formula, Medida, Moda } from './tipos';

type PropsCardMetrica = ComponentProps<typeof CardMetrica>;

const C = TEXTOS_ANALISE.cartoes;

export interface DefinicaoCartao {
  id: string;
  rotulo: string;
  medida: Medida;
  /** Medida de apoio mostrada no "Ver fórmula" do card (moda de Czuber na contínua). */
  apoio?: Medida | undefined;
  selo?: string | undefined;
  unidade?: string | undefined;
  casasSignificativas?: number | undefined;
}

/** `Moda` não é `Medida` e não traz chave; no catálogo do M1.4 a fórmula da moda bruta é `moda`. */
const CHAVE_FORMULA_MODA = 'moda';

function acharFormula(formulas: readonly Formula[], chave: string | null): Formula | undefined {
  return chave === null ? undefined : formulas.find((formula) => formula.chave === chave);
}

function calculoDoCartao({ medida, apoio }: DefinicaoCartao): string | null {
  if (apoio === undefined) return medida.calculo;
  return C.apoioCzuber(apoio.calculo ?? `= ${formatarValorMedida(apoio.valor)}`);
}

function formulaDoCartao(definicao: DefinicaoCartao, formulas: readonly Formula[]): PropsCardMetrica['formula'] {
  const formula = acharFormula(formulas, (definicao.apoio ?? definicao.medida).formula);
  if (formula === undefined) return undefined;
  const calculo = calculoDoCartao(definicao);
  return calculo === null ? { expressao: formula.texto } : { expressao: formula.texto, calculo };
}

export function propsDoCartao(definicao: DefinicaoCartao, formulas: readonly Formula[]): PropsCardMetrica {
  const { rotulo, medida } = definicao;
  if (!medida.aplicavel) {
    return { rotulo, valor: '—', naoAplicavel: { motivo: medida.motivo ?? TEXTOS_ANALISE.motivoPadrao } };
  }
  const formula = formulaDoCartao(definicao, formulas);
  return {
    rotulo,
    valor: formatarValorMedida(medida.valor, definicao.casasSignificativas),
    ...(definicao.unidade === undefined ? {} : { unidade: definicao.unidade }),
    ...(definicao.selo === undefined ? {} : { selo: definicao.selo }),
    ...(medida.interpretacao === null ? {} : { interpretacao: medida.interpretacao }),
    ...(formula === undefined ? {} : { formula }),
  };
}

function medidaAusente(motivo: string): Medida {
  return { valor: null, aplicavel: false, motivo, calculo: null, interpretacao: null, formula: null };
}

function comInterpretacao(medida: Medida, padrao: string): Medida {
  return { ...medida, interpretacao: medida.interpretacao ?? padrao };
}

/** `Moda` não é uma `Medida`: várias modas viram um texto só. */
export function medidaDaModa(moda: Moda): Medida {
  const valor = moda.valores.length === 0 ? C.semModa : moda.valores.map((v) => formatarValorMedida(v)).join(' · ');
  return { valor, aplicavel: true, motivo: null, calculo: null, interpretacao: moda.interpretacao, formula: CHAVE_FORMULA_MODA };
}

function cartaoModaSimples(moda: Moda): DefinicaoCartao {
  return { id: 'moda', rotulo: C.moda, medida: medidaDaModa(moda), selo: C.seloModa[moda.classificacao] };
}

function cartaoCentro(analise: Analise): DefinicaoCartao {
  const { tendencia } = analise;
  return estaAplicavel(analise, 'proporcao')
    ? { id: 'proporcao', rotulo: C.proporcao, medida: tendencia.proporcao }
    : { id: 'media', rotulo: C.media, medida: tendencia.media };
}

/** Spec 05: o card mostra a moda bruta; na contínua, a de Czuber (pelas classes) vai como apoio no "Ver fórmula". */
function cartaoModa(analise: Analise): DefinicaoCartao {
  const cartao = cartaoModaSimples(analise.tendencia.moda);
  return estaAplicavel(analise, 'moda_czuber') ? { ...cartao, apoio: analise.tendencia.moda_czuber } : cartao;
}

export function cartoesTendencia(analise: Analise): DefinicaoCartao[] {
  const mediana = { id: 'mediana', rotulo: C.mediana, medida: analise.tendencia.mediana };
  return [cartaoCentro(analise), mediana, cartaoModa(analise)];
}

export function cartoesDispersao(dispersao: Dispersao): DefinicaoCartao[] {
  const { classificacao_cv: classificacao } = dispersao;
  return [
    { id: 'desvio_padrao', rotulo: C.desvioPadrao, medida: dispersao.desvio_padrao },
    {
      id: 'cv',
      rotulo: C.cv,
      medida: dispersao.cv,
      unidade: '%',
      casasSignificativas: 3,
      selo: classificacao === null ? undefined : C.seloCv[classificacao],
    },
    { id: 'iqr', rotulo: C.iqr, medida: dispersao.iqr },
    { id: 'amplitude', rotulo: C.amplitude, medida: dispersao.amplitude },
    { id: 'variancia', rotulo: C.variancia, medida: comInterpretacao(dispersao.variancia, C.notaVariancia) },
  ];
}

/** Linha de 4 cards da aba Frequências quando não há dispersão (nominal, design 4g). */
export function cartoesResumoCategorico(analise: Analise): DefinicaoCartao[] {
  const { tendencia } = analise;
  return [
    cartaoModaSimples(tendencia.moda),
    { id: 'media', rotulo: C.media, medida: tendencia.media },
    { id: 'mediana', rotulo: C.mediana, medida: tendencia.mediana },
    { id: 'desvio_padrao', rotulo: C.desvioPadrao, medida: medidaAusente(motivoNaoAplicavel(analise, 'dispersao')) },
  ];
}

export function notaPopulacional(dispersao: Dispersao): string | null {
  const { desvio_padrao_populacional: desvio, variancia_populacional: variancia } = dispersao;
  if (!desvio.aplicavel || !variancia.aplicavel) return null;
  return C.populacional(formatarValorMedida(desvio.valor), formatarValorMedida(variancia.valor));
}
```

`components/GradeCardsMetrica.tsx`:

```tsx
import CardMetrica from '../../../shared/ui/CardMetrica';
import { propsDoCartao, type DefinicaoCartao } from '../cartoes';
import type { Formula } from '../tipos';
import estilos from './GradeCardsMetrica.module.css';

interface Props {
  cartoes: readonly DefinicaoCartao[];
  formulas: readonly Formula[];
  colunas?: 3 | 4;
}

export default function GradeCardsMetrica({ cartoes, formulas, colunas = 3 }: Readonly<Props>) {
  return (
    <div className={estilos.grade} data-colunas={colunas}>
      {cartoes.map((cartao) => (
        <CardMetrica key={cartao.id} {...propsDoCartao(cartao, formulas)} />
      ))}
    </div>
  );
}
```

CSS (sempre tokens):

| Arquivo · seletor | Propriedades |
|---|---|
| `GradeCardsMetrica.module.css` `.grade` | `display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: var(--esp-16); align-items: start` |
| `.grade[data-colunas='4']` | `grid-template-columns: repeat(4, minmax(0, 1fr))` |
| `@media (max-width: 1279px)` `.grade` | `grid-template-columns: repeat(2, minmax(0, 1fr))` |
| `paineis.module.css` `.aba` | `display: flex; flex-direction: column; gap: var(--esp-20)` |
| `.nota` | `margin: 0; font-size: 13.5px; line-height: 1.5; color: var(--cor-texto-2)` |
| `.lista` | `display: flex; flex-direction: column; gap: var(--esp-12)` (banners de interpretação) |

**Passo 4: rodar e ver passar** — `npm run test -- cartoes` · `npm run lint`.

**Passo 5: commit**
```bash
git add frontend/src/features/analise
git commit -m "feat(analise): converte medidas da API em cards com fórmula, selo e motivo de não aplicável"
```

---

### Tarefa 5: Aba Frequências (4b, 4g)

**Arquivos:**
- Criar: `frontend/src/features/analise/frequencias.tsx` + `frequencias.module.css` · Teste: `frequencias.test.ts`
- Criar: `frontend/src/features/analise/components/ControleClasses.tsx` + `.module.css`
- Criar: `frontend/src/features/analise/components/TabelaFrequencias.tsx` · Teste: `TabelaFrequencias.test.tsx`
- Criar: `frontend/src/features/analise/components/CardGrafico.tsx` + `.module.css`
- Criar: `frontend/src/features/analise/components/AbaFrequencias.tsx` + `.module.css`

**Regras:**
- Colunas da tabela por **tabela de despacho** `Record<TipoVariavel, …>` (nada de `if` por tipo): contínua → Classe (mono, `rotulo` "60,0 ⊢ 65,5" já formatado pelo backend) + Ponto médio; discreta → valor (mono); ordinal/nominal/binária → categoria. Depois, sempre `fi` (600) e `fr%` (1 casa); por fim `Fi` e `Fr%` quando `acumulada_aplicavel`, senão uma coluna "Fr% acum." **esmaecida** com "—" e o motivo (`motivo_acumulada`) na nota abaixo.
- Linha "Total" (n e 100,0) no fim; a classe modal (`indice_modal`) usa o destaque de linha da `Tabela`.
- Controle "Número de classes" (− k +, 3..30) e "Sturges: {k_sturges}" só quando a tabela tem classes (`k` e `k_sturges` não nulos). O valor mostrado é o da URL (`classes`) quando houver, senão `tabela.k`: cliques rápidos não se perdem enquanto a nova tabela chega (`placeholderData`).
- Ao lado, o gráfico `principal` (`CardGrafico`: `Grafico` + resumo + "Por que este gráfico?").
- Coluna sem dispersão (`analise.dispersao === null`, nominal no 4g): linha de 4 cards abaixo (Moda + Média, Mediana, Desvio padrão não aplicáveis).

**Passo 1: testes (falham)**

`frequencias.test.ts`:

```ts
import { describe, expect, it } from 'vitest';
import { formatarNumero } from '../../shared/lib/formatar';
import { analiseContinua, analiseNominal } from '../../testes/fixturesAnalise';
import { colunasDaTabela, ehLinhaModal, linhasComTotal, notasDaTabela } from './frequencias';
import { TEXTOS_ANALISE } from './textos';

const T = TEXTOS_ANALISE.frequencias;
const continua = analiseContinua.frequencias;
const nominal = analiseNominal.frequencias;

describe('colunasDaTabela', () => {
  it('contínua: classe, ponto médio, fi, fr%, Fi e Fr%', () => {
    expect(colunasDaTabela(continua, 'peso_kg').map((c) => c.id)).toEqual([
      'rotulo', 'ponto_medio', 'fi', 'fr', 'fi_acumulada', 'fr_acumulada',
    ]);
    expect(colunasDaTabela(continua, 'peso_kg')[0]?.titulo).toBe(T.classe);
  });

  it('nominal: nome da coluna, fi, fr% e a acumulada esmaecida', () => {
    const colunas = colunasDaTabela(nominal, 'cidade');

    expect(colunas.map((c) => c.id)).toEqual(['rotulo', 'fi', 'fr', 'fr_acumulada']);
    expect(colunas[0]?.titulo).toBe('cidade');
  });

  it('discreta: valor em mono, sem ponto médio', () => {
    const discreta = { ...continua, tipo: 'discreta' as const, k: null, k_sturges: null, h: null };

    expect(colunasDaTabela(discreta, 'idade').map((c) => c.id)).toEqual([
      'rotulo', 'fi', 'fr', 'fi_acumulada', 'fr_acumulada',
    ]);
    expect(colunasDaTabela(discreta, 'idade')[0]?.mono).toBe(true);
  });
});

describe('linhasComTotal e ehLinhaModal', () => {
  it('acrescenta a linha Total no fim', () => {
    expect(linhasComTotal(continua).at(-1)).toEqual({ tipo: 'total', total: 227 });
  });

  it('destaca só a classe modal', () => {
    expect(linhasComTotal(continua).map(ehLinhaModal(continua))).toEqual([false, true, false, false]);
  });
});

describe('notasDaTabela', () => {
  it('contínua: explica ⊢ e a amplitude h e conta os faltantes', () => {
    expect(notasDaTabela(continua, 3)).toEqual([T.notaClasses(formatarNumero(16.5)), '3 faltantes ficaram de fora.']);
  });

  it('nominal: traz o motivo da acumulada vindo do backend', () => {
    expect(notasDaTabela(nominal, 0)).toEqual([nominal.motivo_acumulada]);
  });
});
```

`components/TabelaFrequencias.test.tsx`:

```tsx
import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import type { ComponentProps } from 'react';
import { describe, expect, it, vi } from 'vitest';
import { formatarNumero } from '../../../shared/lib/formatar';
import { analiseContinua, analiseNominal } from '../../../testes/fixturesAnalise';
import { renderizarComProvedores } from '../../../testes/renderizar';
import { TEXTOS_ANALISE } from '../textos';
import TabelaFrequencias from './TabelaFrequencias';

const T = TEXTOS_ANALISE.frequencias;

function renderizarTabela(props: Partial<ComponentProps<typeof TabelaFrequencias>> = {}) {
  const aoMudarClasses = vi.fn();
  renderizarComProvedores(
    <TabelaFrequencias
      tabela={analiseContinua.frequencias}
      coluna="peso_kg"
      nFaltantes={3}
      k={5}
      atualizando={false}
      aoMudarClasses={aoMudarClasses}
      {...props}
    />,
  );
  return aoMudarClasses;
}

describe('TabelaFrequencias', () => {
  it('mostra as classes com ⊢, a linha Total e a nota da amplitude', () => {
    renderizarTabela();

    expect(screen.getByText('60,0 ⊢ 76,5')).toBeInTheDocument();
    expect(screen.getByRole('row', { name: /Total/ })).toHaveTextContent('227');
    expect(screen.getByText(T.notaClasses(formatarNumero(16.5)))).toBeInTheDocument();
    expect(screen.getByText('Sturges: 9')).toBeInTheDocument();
  });

  it('o controle pede uma classe a mais ou a menos', async () => {
    const user = userEvent.setup();
    const aoMudarClasses = renderizarTabela();

    await user.click(screen.getByRole('button', { name: T.mais }));
    await user.click(screen.getByRole('button', { name: T.menos }));

    expect(aoMudarClasses.mock.calls).toEqual([[6], [4]]);
  });

  it('no mínimo de 3 classes, "menos" fica desabilitado', () => {
    renderizarTabela({ k: 3 });

    expect(screen.getByRole('button', { name: T.menos })).toBeDisabled();
  });

  it('nominal: sem controle de classes, com a acumulada esmaecida e o motivo', () => {
    renderizarTabela({ tabela: analiseNominal.frequencias, coluna: 'cidade', k: null, nFaltantes: 2 });

    expect(screen.queryByRole('group', { name: T.numeroClasses })).toBeNull();
    expect(screen.getByText(T.frAcumuladaNaoAplicavel)).toBeInTheDocument();
    expect(screen.getByText(analiseNominal.frequencias.motivo_acumulada as string)).toBeInTheDocument();
    expect(screen.getByText('2 faltantes ficaram de fora.')).toBeInTheDocument();
  });
});
```

**Passo 2: rodar e ver falhar** — `npm run test -- frequencias TabelaFrequencias` → FAIL.

**Passo 3: implementar**

`frequencias.tsx` (funções puras; `.tsx` porque as células devolvem JSX):

```tsx
import type { ReactNode } from 'react';
import { formatarDecimal, formatarInteiro, formatarNumero } from '../../shared/lib/formatar';
import type { ColunaTabela } from '../../shared/ui/Tabela';
import { formatarOpcional } from './formatacao';
import estilos from './frequencias.module.css';
import { TEXTOS_ANALISE } from './textos';
import type { LinhaFrequencia, TabelaFrequencia, TipoVariavel } from './tipos';

const T = TEXTOS_ANALISE.frequencias;

export type LinhaTabela = { tipo: 'linha'; indice: number; linha: LinhaFrequencia } | { tipo: 'total'; total: number };

type Coluna = ColunaTabela<LinhaTabela>;

export function linhasComTotal(tabela: TabelaFrequencia): LinhaTabela[] {
  const linhas: LinhaTabela[] = tabela.linhas.map((linha, indice) => ({ tipo: 'linha', indice, linha }));
  return [...linhas, { tipo: 'total', total: tabela.total }];
}

export function chaveDaLinha(linha: LinhaTabela): string {
  return linha.tipo === 'total' ? 'total' : String(linha.indice);
}

export function ehLinhaModal(tabela: TabelaFrequencia): (linha: LinhaTabela) => boolean {
  return (linha) => linha.tipo === 'linha' && linha.indice === tabela.indice_modal;
}

function colunaNumerica(id: string, titulo: ReactNode, daLinha: (linha: LinhaFrequencia) => ReactNode, doTotal: ReactNode = ''): Coluna {
  return {
    id,
    titulo,
    alinhamento: 'direita',
    mono: true,
    celula: (linha) => (linha.tipo === 'total' ? <strong>{doTotal}</strong> : daLinha(linha.linha)),
  };
}

function colunaRotulo(titulo: string, mono: boolean): Coluna {
  return {
    id: 'rotulo',
    titulo,
    mono,
    celula: (linha) => (linha.tipo === 'total' ? <strong>{T.total}</strong> : linha.linha.rotulo),
  };
}

const colunaPontoMedio = colunaNumerica('ponto_medio', T.pontoMedio, (linha) =>
  formatarOpcional(linha.ponto_medio, (valor) => formatarNumero(valor)),
);

const categorica = (nome: string): Coluna[] => [colunaRotulo(nome, false)];

const PRIMEIRAS_COLUNAS = {
  continua: () => [colunaRotulo(T.classe, true), colunaPontoMedio],
  discreta: (nome: string) => [colunaRotulo(nome, true)],
  ordinal: categorica,
  nominal: categorica,
  binaria: categorica,
  identificador: categorica,
} satisfies Record<TipoVariavel, (nome: string) => Coluna[]>;

function colunasBase(total: number): Coluna[] {
  return [
    colunaNumerica('fi', T.fi, (linha) => <span className={estilos.forte}>{formatarInteiro(linha.fi)}</span>, formatarInteiro(total)),
    colunaNumerica('fr', T.fr, (linha) => formatarDecimal(linha.fr_pct), formatarDecimal(100)),
  ];
}

const COLUNAS_ACUMULADAS: Coluna[] = [
  colunaNumerica('fi_acumulada', T.fiAcumulada, (linha) => formatarOpcional(linha.f_acum, formatarInteiro)),
  colunaNumerica('fr_acumulada', T.frAcumulada, (linha) =>
    formatarOpcional(linha.fr_acum_pct, (valor) => formatarDecimal(valor)),
  ),
];

const COLUNA_ACUMULADA_ESMAECIDA = colunaNumerica(
  'fr_acumulada',
  <span className={estilos.esmaecida}>{T.frAcumuladaNaoAplicavel}</span>,
  () => (
    <span className={estilos.esmaecida}>
      <span aria-hidden="true">—</span>
      <span className={estilos.somenteLeitor}>{T.naoSeAplica}</span>
    </span>
  ),
);

export function colunasDaTabela(tabela: TabelaFrequencia, nomeColuna: string): Coluna[] {
  const acumuladas = tabela.acumulada_aplicavel ? COLUNAS_ACUMULADAS : [COLUNA_ACUMULADA_ESMAECIDA];
  return [...PRIMEIRAS_COLUNAS[tabela.tipo](nomeColuna), ...colunasBase(tabela.total), ...acumuladas];
}

export function notasDaTabela(tabela: TabelaFrequencia, nFaltantes: number): string[] {
  const notas: string[] = [];
  if (tabela.h !== null) notas.push(T.notaClasses(formatarNumero(tabela.h)));
  if (tabela.motivo_acumulada !== null) notas.push(tabela.motivo_acumulada);
  if (nFaltantes > 0) notas.push(T.faltantes(nFaltantes));
  return notas;
}
```
(Se `formatarDecimal` vier com outro nome no M1.1, use o equivalente; `formatarInteiro` é do contrato.)

`components/ControleClasses.tsx`:

```tsx
import { useId } from 'react';
import Icone from '../../../shared/ui/Icone';
import { LIMITES_CLASSES } from '../parametros';
import { TEXTOS_ANALISE } from '../textos';
import estilos from './ControleClasses.module.css';

const T = TEXTOS_ANALISE.frequencias;

interface Props {
  k: number;
  kSturges: number;
  aoMudar: (k: number) => void;
}

export default function ControleClasses({ k, kSturges, aoMudar }: Readonly<Props>) {
  const idRotulo = useId();

  return (
    <div className={estilos.controle} role="group" aria-labelledby={idRotulo}>
      <span id={idRotulo} className={estilos.rotulo}>
        {T.numeroClasses}
      </span>
      <div className={estilos.passo}>
        <button
          type="button"
          className={estilos.botao}
          aria-label={T.menos}
          disabled={k <= LIMITES_CLASSES.minimo}
          onClick={() => {
            aoMudar(k - 1);
          }}
        >
          <Icone nome="remove" tamanho={18} />
        </button>
        <output className={estilos.valor} aria-live="polite">
          {k}
        </output>
        <button
          type="button"
          className={estilos.botao}
          aria-label={T.mais}
          disabled={k >= LIMITES_CLASSES.maximo}
          onClick={() => {
            aoMudar(k + 1);
          }}
        >
          <Icone nome="add" tamanho={18} />
        </button>
      </div>
      <span className={estilos.sturges}>{T.sturges(kSturges)}</span>
    </div>
  );
}
```

`components/TabelaFrequencias.tsx`:

```tsx
import Card from '../../../shared/ui/Card';
import Tabela from '../../../shared/ui/Tabela';
import { chaveDaLinha, colunasDaTabela, ehLinhaModal, linhasComTotal, notasDaTabela } from '../frequencias';
import { TEXTOS_ANALISE } from '../textos';
import type { TabelaFrequencia } from '../tipos';
import ControleClasses from './ControleClasses';
import paineis from './paineis.module.css';

const T = TEXTOS_ANALISE.frequencias;

interface Props {
  tabela: TabelaFrequencia;
  coluna: string;
  nFaltantes: number;
  /** Nº de classes mostrado no controle (URL ou o da tabela); null quando a tabela não tem classes. */
  k: number | null;
  atualizando: boolean;
  aoMudarClasses: (k: number) => void;
}

export default function TabelaFrequencias({ tabela, coluna, nFaltantes, k, atualizando, aoMudarClasses }: Readonly<Props>) {
  const controle =
    k !== null && tabela.k_sturges !== null ? (
      <ControleClasses k={k} kSturges={tabela.k_sturges} aoMudar={aoMudarClasses} />
    ) : null;

  return (
    <Card titulo={tabela.k === null ? T.titulo(coluna) : T.tituloClasses} acoes={controle}>
      <div aria-busy={atualizando}>
        <Tabela
          legenda={T.titulo(coluna)}
          colunas={colunasDaTabela(tabela, coluna)}
          linhas={linhasComTotal(tabela)}
          chave={chaveDaLinha}
          destacada={ehLinhaModal(tabela)}
        />
      </div>
      {notasDaTabela(tabela, nFaltantes).map((nota) => (
        <p key={nota} className={paineis.nota}>
          {nota}
        </p>
      ))}
    </Card>
  );
}
```

`components/CardGrafico.tsx`:

```tsx
import Grafico from '../../../shared/graficos/Grafico';
import Card from '../../../shared/ui/Card';
import { TEXTOS_ANALISE } from '../textos';
import type { Figura } from '../tipos';
import estilos from './CardGrafico.module.css';

const ALTURA_PADRAO = 300;

interface Props {
  figura: Figura;
  altura?: number;
}

export default function CardGrafico({ figura, altura = ALTURA_PADRAO }: Readonly<Props>) {
  return (
    <Card>
      <Grafico titulo={figura.titulo} resumo={figura.resumo} figura={figura.dados} altura={altura} />
      <p className={estilos.resumo}>{figura.resumo}</p>
      <p className={estilos.porque}>
        <strong>{TEXTOS_ANALISE.graficos.porque}</strong> {figura.porque}
      </p>
    </Card>
  );
}
```

`components/AbaFrequencias.tsx`:

```tsx
import { cartoesResumoCategorico } from '../cartoes';
import type { PropsPainel } from '../tipos';
import estilos from './AbaFrequencias.module.css';
import CardGrafico from './CardGrafico';
import GradeCardsMetrica from './GradeCardsMetrica';
import paineis from './paineis.module.css';
import TabelaFrequencias from './TabelaFrequencias';

export default function AbaFrequencias({ analise, atualizando, classes, aoMudarClasses }: Readonly<PropsPainel>) {
  const { frequencias } = analise;
  const principal = analise.figuras.find((figura) => figura.id === 'principal');

  return (
    <div className={paineis.aba}>
      <div className={estilos.grade}>
        <TabelaFrequencias
          tabela={frequencias}
          coluna={analise.coluna}
          nFaltantes={analise.n_faltantes}
          k={classes ?? frequencias.k}
          atualizando={atualizando}
          aoMudarClasses={aoMudarClasses}
        />
        {principal === undefined ? null : <CardGrafico figura={principal} />}
      </div>
      {analise.dispersao === null ? (
        <GradeCardsMetrica cartoes={cartoesResumoCategorico(analise)} formulas={analise.formulas} colunas={4} />
      ) : null}
    </div>
  );
}
```

CSS:

| Arquivo · seletor | Propriedades |
|---|---|
| `frequencias.module.css` `.forte` | `font-weight: 600` |
| `.esmaecida` | `color: var(--cor-texto-desab)` |
| `.somenteLeitor` | `position: absolute; width: 1px; height: 1px; overflow: hidden; clip-path: inset(50%); white-space: nowrap` |
| `ControleClasses.module.css` `.controle` | `display: flex; align-items: center; gap: var(--esp-16)` |
| `.rotulo` | `font-size: 13px; color: var(--cor-texto-2)` |
| `.passo` | `display: flex; align-items: center; height: 36px; border: 1px solid var(--cor-borda-forte); border-radius: var(--raio-md)` |
| `.botao` | `width: 32px; height: 100%; display: grid; place-items: center; border: 0; background: transparent; color: var(--cor-texto-2); cursor: pointer` · `:hover` `color: var(--cor-texto); background: var(--cor-superficie-2)` · `:disabled` `color: var(--cor-texto-desab); cursor: not-allowed` · `:focus-visible` `outline: 2px solid var(--cor-foco); outline-offset: 2px` |
| `.valor` | `width: 32px; text-align: center; font: 600 14px var(--fonte-mono)` |
| `.sturges` | `font: 500 12.5px var(--fonte-mono); color: var(--cor-texto-2)` |
| `CardGrafico.module.css` `.resumo` | `margin: var(--esp-12) 0 0; font-size: 15px; line-height: 1.55` |
| `.porque` | `margin: var(--esp-8) 0 0; font-size: 14px; line-height: 1.5; color: var(--cor-texto-2)` · `.porque strong` `color: var(--cor-texto); font-weight: 600` |
| `AbaFrequencias.module.css` `.grade` | `display: grid; grid-template-columns: minmax(0, 1.15fr) minmax(0, 1fr); gap: var(--esp-20); align-items: start` · `@media (max-width: 1279px)` `grid-template-columns: minmax(0, 1fr)` |

**Passo 4: rodar e ver passar** — `npm run test -- frequencias TabelaFrequencias` · `npm run lint`.

**Passo 5: commit**
```bash
git add frontend/src/features/analise
git commit -m "feat(analise): aba Frequências com tabela por tipo, controle de classes e gráfico principal"
```

---

### Tarefa 6: Abas Tendência central (4c) e Dispersão (4d)

**Arquivos:**
- Criar: `frontend/src/features/analise/components/AbaTendencia.tsx` · Teste: `AbaTendencia.test.tsx`
- Criar: `frontend/src/features/analise/components/AbaDispersao.tsx` · Teste: `AbaDispersao.test.tsx`

**Passo 1: testes (falham)**

`components/AbaTendencia.test.tsx`:

```tsx
import { screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { formatarNumero } from '../../../shared/lib/formatar';
import { analiseContinua, analiseNominal, propsPainel } from '../../../testes/fixturesAnalise';
import { renderizarComProvedores } from '../../../testes/renderizar';
import AbaTendencia from './AbaTendencia';

describe('AbaTendencia', () => {
  it('contínua: média, mediana e moda bruta, com a interpretação em banner', () => {
    renderizarComProvedores(<AbaTendencia {...propsPainel(analiseContinua)} />);

    expect(screen.getByText('Moda')).toBeInTheDocument();
    expect(screen.getByText(formatarNumero(72))).toBeInTheDocument();
    expect(screen.getByText(formatarNumero(70.3))).toBeInTheDocument();
    expect(screen.getByText(analiseContinua.interpretacoes[0] as string)).toBeInTheDocument();
  });

  it('nominal: média e mediana aparecem como não aplicáveis, com o motivo', () => {
    renderizarComProvedores(<AbaTendencia {...propsPainel(analiseNominal)} />);

    expect(screen.getByText(analiseNominal.tendencia.media.motivo as string)).toBeInTheDocument();
    expect(screen.getByText(analiseNominal.tendencia.mediana.motivo as string)).toBeInTheDocument();
    expect(screen.getByText('Goiânia')).toBeInTheDocument();
  });
});
```

`components/AbaDispersao.test.tsx`:

```tsx
import { screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { analiseContinua, propsPainel } from '../../../testes/fixturesAnalise';
import { renderizarComProvedores } from '../../../testes/renderizar';
import { notaPopulacional } from '../cartoes';
import { TEXTOS_ANALISE } from '../textos';
import type { Dispersao } from '../tipos';
import AbaDispersao from './AbaDispersao';

const C = TEXTOS_ANALISE.cartoes;

describe('AbaDispersao', () => {
  it('mostra os 5 cards, o selo do CV, a nota populacional e as faixas do CV', () => {
    renderizarComProvedores(<AbaDispersao {...propsPainel(analiseContinua)} />);

    for (const rotulo of [C.desvioPadrao, C.cv, C.iqr, C.amplitude, C.variancia]) {
      expect(screen.getByText(rotulo)).toBeInTheDocument();
    }
    expect(screen.getByText('Variação moderada')).toBeInTheDocument();
    expect(screen.getByText(C.notaVariancia)).toBeInTheDocument();
    expect(screen.getByText(notaPopulacional(analiseContinua.dispersao as Dispersao) as string)).toBeInTheDocument();
    expect(screen.getByText(C.faixasCv)).toBeInTheDocument();
  });
});
```

**Passo 2: rodar e ver falhar** — `npm run test -- AbaTendencia AbaDispersao` → FAIL.

**Passo 3: implementar**

`components/AbaTendencia.tsx`:

```tsx
import Banner from '../../../shared/ui/Banner';
import { cartoesTendencia } from '../cartoes';
import type { PropsPainel } from '../tipos';
import GradeCardsMetrica from './GradeCardsMetrica';
import paineis from './paineis.module.css';

export default function AbaTendencia({ analise }: Readonly<PropsPainel>) {
  return (
    <div className={paineis.aba}>
      <GradeCardsMetrica cartoes={cartoesTendencia(analise)} formulas={analise.formulas} />
      <div className={paineis.lista}>
        {analise.interpretacoes.map((texto) => (
          <Banner key={texto} variante="info">
            {texto}
          </Banner>
        ))}
      </div>
    </div>
  );
}
```

`components/AbaDispersao.tsx`:

```tsx
import Banner from '../../../shared/ui/Banner';
import { estaAplicavel } from '../abas';
import { cartoesDispersao, notaPopulacional } from '../cartoes';
import { TEXTOS_ANALISE } from '../textos';
import type { PropsPainel } from '../tipos';
import GradeCardsMetrica from './GradeCardsMetrica';
import paineis from './paineis.module.css';

export default function AbaDispersao({ analise }: Readonly<PropsPainel>) {
  const { dispersao } = analise;
  // A aba fica desabilitada quando não há dispersão (abasDaAnalise); a guarda só estreita o tipo.
  if (dispersao === null) return null;
  const nota = notaPopulacional(dispersao);

  return (
    <div className={paineis.aba}>
      <GradeCardsMetrica cartoes={cartoesDispersao(dispersao)} formulas={analise.formulas} />
      {nota === null ? null : <p className={paineis.nota}>{nota}</p>}
      {estaAplicavel(analise, 'cv') ? <Banner variante="info">{TEXTOS_ANALISE.cartoes.faixasCv}</Banner> : null}
    </div>
  );
}
```

**Passo 4: rodar e ver passar** — `npm run test -- AbaTendencia AbaDispersao` · `npm run lint`.

**Passo 5: commit**
```bash
git add frontend/src/features/analise
git commit -m "feat(analise): abas Tendência central e Dispersão com cards, interpretações e faixas do CV"
```

---

### Tarefa 7: Aba Separatrizes (4a) + "Onde está meu valor?" + `ReguaSeparatrizes`

**Arquivos:**
- Criar: `frontend/src/features/analise/separatrizes.ts` · Teste: `separatrizes.test.ts`
- Criar: `frontend/src/features/analise/hooks/useConsultaPosicao.ts`
- Criar: `frontend/src/features/analise/components/ListaSeparatrizes.tsx` + `.module.css`
- Criar: `frontend/src/features/analise/components/TabelaSeparatrizes.tsx` + `.module.css`
- Criar: `frontend/src/features/analise/components/ReguaSeparatrizes.tsx` + `.module.css`
- Criar: `frontend/src/features/analise/components/PainelPosicao.tsx` + `.module.css`
- Criar: `frontend/src/features/analise/components/AbaSeparatrizes.tsx` + `.module.css` · Teste: `AbaSeparatrizes.test.tsx`

**Regras:**
- Tabela em 3 grupos (Quartis · Decis · Percentis) lado a lado; cada grupo é um `<section>` com `<h3>` e uma `<dl>` (rótulo mono texto-2, valor mono). Percentis mostra os `destaques` (+ o percentil consultado, se houver); os 99 ficam num `<details>` "Ver os 99 percentis" (`content-visibility: auto`).
- Destaque da separatriz relevante = `{Q|D|P}{posicao.indice}` da última consulta (ex.: valor 75 em quartil → Q3). Nada é destacado fora da faixa.
- Painel "Onde está meu valor?" só quando `aplicavel.posicao` (ordinal: separatrizes como categoria, sem painel). Campo "Valor de {coluna}" (aceita vírgula) + Segmented Quartil/Decil/Percentil. A consulta sai **300 ms depois da última tecla** (`useValorAtrasado`) e só com número válido; texto inválido mostra o erro do campo.
- `ReguaSeparatrizes`: posição = (v − mín)/(máx − mín), limitada a 0–100%; faixa entre `limite_inferior` e `limite_superior` (nulos → mín/máx); marcas = `posicao.marcas` (o backend manda no máximo 9: 3 no quartil, 9 no decil, os 9 destaques no percentil), todas com rótulo; `role="img"` com `aria-label` equivalente.
- Frase `posicao.frase` num `<p aria-live="polite">` em bloco primaria-suave (o `<p>` existe desde o início com a dica, para o leitor de tela anunciar a primeira resposta). `fora_da_faixa` → `Banner` atenção "Fora da faixa observada." + "O valor está abaixo do menor/acima do maior dado observado ({mín}/{máx})."

**Passo 1: testes (falham)**

`separatrizes.test.ts`:

```ts
import { describe, expect, it } from 'vitest';
import { formatarNumero } from '../../shared/lib/formatar';
import { analiseContinua, posicaoAcima, posicaoQuartil } from '../../testes/fixturesAnalise';
import {
  descricaoDaRegua, montarRegua, percentisVisiveis, percentualNaRegua, rotuloDestacado, textoForaDaFaixa,
} from './separatrizes';
import { TEXTOS_ANALISE } from './textos';
import type { Separatrizes } from './tipos';

const separatrizes = analiseContinua.separatrizes as Separatrizes;
const P = TEXTOS_ANALISE.posicao;

describe('rotuloDestacado', () => {
  it('valor no 3º quartil destaca Q3', () => {
    expect(rotuloDestacado(posicaoQuartil)).toBe('Q3');
  });

  it('percentil usa o prefixo P', () => {
    expect(rotuloDestacado({ ...posicaoQuartil, tipo: 'percentil', indice: 66 })).toBe('P66');
  });

  it('fora da faixa ou sem consulta não destaca nada', () => {
    expect(rotuloDestacado(posicaoAcima)).toBeNull();
    expect(rotuloDestacado(undefined)).toBeNull();
  });
});

describe('percentisVisiveis', () => {
  it('mostra os 9 destaques', () => {
    expect(percentisVisiveis(separatrizes, null).map((p) => p.rotulo)).toEqual(separatrizes.destaques);
  });

  it('inclui o percentil consultado, na ordem', () => {
    expect(percentisVisiveis(separatrizes, 'P66').map((p) => p.rotulo)).toEqual([
      'P1', 'P5', 'P10', 'P25', 'P50', 'P66', 'P75', 'P90', 'P95', 'P99',
    ]);
  });
});

describe('percentualNaRegua', () => {
  it('posição = (v − mín) / (máx − mín)', () => {
    expect(percentualNaRegua(69.8, 43.8, 92.9)).toBeCloseTo(52.95, 2);
  });

  it('limita a 0–100% fora da faixa', () => {
    expect(percentualNaRegua(120, 43.8, 92.9)).toBe(100);
    expect(percentualNaRegua(10, 43.8, 92.9)).toBe(0);
  });

  it('com todos os valores iguais, fica no meio', () => {
    expect(percentualNaRegua(5, 5, 5)).toBe(50);
  });
});

describe('montarRegua', () => {
  it('pinta a faixa entre Q2 e Q3 e põe as marcas dos quartis', () => {
    const regua = montarRegua(posicaoQuartil);

    expect(regua.marcador).toBeCloseTo(63.54, 2);
    expect(regua.faixa.inicio).toBeCloseTo(52.95, 2);
    expect(regua.faixa.inicio + regua.faixa.largura).toBeCloseTo(69.45, 2);
    expect(regua.marcas.map((m) => m.rotulo)).toEqual(['Q1', 'Q2', 'Q3']);
  });

  it('acima do máximo: marcador e faixa vão até o fim', () => {
    const regua = montarRegua(posicaoAcima);

    expect(regua.marcador).toBe(100);
    expect(regua.faixa.inicio + regua.faixa.largura).toBe(100);
  });
});

describe('descricaoDaRegua e textoForaDaFaixa', () => {
  it('descreve a régua para leitor de tela', () => {
    expect(descricaoDaRegua(posicaoQuartil)).toBe(
      `Régua de ${formatarNumero(43.8)} a ${formatarNumero(92.9)} com Q1, Q2 e Q3; o valor ${formatarNumero(75)} fica no 3º quartil (entre Q2 e Q3).`,
    );
  });

  it('explica quando o valor passa do maior dado', () => {
    expect(textoForaDaFaixa(posicaoAcima)).toBe(P.acima(formatarNumero(92.9)));
    expect(textoForaDaFaixa(posicaoQuartil)).toBeNull();
  });
});
```

`components/AbaSeparatrizes.test.tsx`:

```tsx
import { screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it } from 'vitest';
import { formatarNumero } from '../../../shared/lib/formatar';
import { chamadasPara, type FetchFalso, simularApi } from '../../../testes/api';
import { ID_DATASET } from '../../../testes/fixtures/datasets';
import { analiseContinua, posicaoAcima, posicaoQuartil, propsPainel } from '../../../testes/fixturesAnalise';
import { renderizarComProvedores } from '../../../testes/renderizar';
import { TEXTOS_ANALISE } from '../textos';
import type { Posicao } from '../tipos';
import AbaSeparatrizes from './AbaSeparatrizes';

const P = TEXTOS_ANALISE.posicao;
const CAMINHO_POSICAO = `/datasets/${ID_DATASET}/colunas/peso_kg/posicao`;
const URL_POSICAO = `/api${CAMINHO_POSICAO}`;

function responderPosicao(posicao: Posicao) {
  return simularApi([{ caminho: CAMINHO_POSICAO, corpo: posicao }]);
}

function urlsChamadas(api: FetchFalso): string[] {
  return chamadasPara(api, 'GET', CAMINHO_POSICAO).map((chamada) => chamada.url);
}

async function digitarValor(texto: string) {
  const user = userEvent.setup();
  renderizarComProvedores(<AbaSeparatrizes {...propsPainel(analiseContinua)} />);
  await user.type(screen.getByLabelText('Valor de peso_kg'), texto);
  return user;
}

describe('AbaSeparatrizes', () => {
  it('mostra quartis, decis e os 9 percentis em destaque, com os 99 recolhidos', () => {
    responderPosicao(posicaoQuartil);
    renderizarComProvedores(<AbaSeparatrizes {...propsPainel(analiseContinua)} />);

    expect(within(screen.getByRole('region', { name: 'Quartis' })).getAllByRole('term')).toHaveLength(3);
    expect(within(screen.getByRole('region', { name: 'Decis' })).getAllByRole('term')).toHaveLength(9);
    expect(within(screen.getByRole('region', { name: 'Percentis' })).getAllByRole('term')).toHaveLength(9);
    expect(screen.getByText(TEXTOS_ANALISE.separatrizes.verTodos)).toBeInTheDocument();
  });

  it('consulta a posição depois da pausa na digitação e destaca a separatriz', async () => {
    const api = responderPosicao(posicaoQuartil);
    await digitarValor('75');

    expect(await screen.findByText(posicaoQuartil.frase)).toBeInTheDocument();
    expect(urlsChamadas(api)).toEqual([`${URL_POSICAO}?valor=75&tipo=quartil`]);
    const q3 = within(screen.getByRole('region', { name: 'Quartis' })).getByText('Q3').parentElement;
    expect(q3).toHaveAttribute('data-destaque', 'true');
    expect(screen.getByRole('img', { name: /fica no 3º quartil/ })).toBeInTheDocument();
  });

  it('trocar para Decil refaz a consulta com o novo tipo', async () => {
    const api = responderPosicao(posicaoQuartil);
    const user = await digitarValor('75');
    await screen.findByText(posicaoQuartil.frase);

    await user.click(screen.getByRole('radio', { name: 'Decil' }));

    await waitFor(() => {
      expect(urlsChamadas(api)).toContain(`${URL_POSICAO}?valor=75&tipo=decil`);
    });
  });

  it('texto que não é número mostra o erro do campo e não chama a API', async () => {
    const api = responderPosicao(posicaoQuartil);
    await digitarValor('abc');

    expect(screen.getByText(P.erroValor)).toBeInTheDocument();
    expect(urlsChamadas(api)).toEqual([]);
  });

  it('valor acima do maior dado mostra o aviso de fora da faixa', async () => {
    responderPosicao(posicaoAcima);
    await digitarValor('120');

    expect(await screen.findByText(P.foraTitulo)).toBeInTheDocument();
    expect(screen.getByText(P.acima(formatarNumero(92.9)))).toBeInTheDocument();
  });

  it('sem "posicao" aplicável (ordinal), o painel não aparece', () => {
    const ordinal = { ...analiseContinua, aplicavel: { ...analiseContinua.aplicavel, posicao: false } };
    renderizarComProvedores(<AbaSeparatrizes {...propsPainel(ordinal)} />);

    expect(screen.queryByText(P.titulo)).toBeNull();
  });
});
```

**Passo 2: rodar e ver falhar** — `npm run test -- separatrizes AbaSeparatrizes` → FAIL.

**Passo 3: implementar**

`separatrizes.ts`:

```ts
import { formatarNumero } from '../../shared/lib/formatar';
import { TEXTOS_ANALISE } from './textos';
import type { Posicao, Separatrizes, TipoSeparatriz, ValorSeparatriz } from './tipos';

const P = TEXTOS_ANALISE.posicao;
const PREFIXOS: Record<TipoSeparatriz, string> = { quartil: 'Q', decil: 'D', percentil: 'P' };
const LISTA_PT = new Intl.ListFormat('pt-BR', { style: 'long', type: 'conjunction' });

export interface MarcaRegua {
  rotulo: string;
  valor: string;
  percentual: number;
}

export interface Regua {
  marcador: number;
  faixa: { inicio: number; largura: number };
  marcas: MarcaRegua[];
  valor: string;
  minimo: string;
  maximo: string;
}

type MarcaNumerica = ValorSeparatriz & { valor: number };

function ehMarcaNumerica(marca: ValorSeparatriz): marca is MarcaNumerica {
  return typeof marca.valor === 'number';
}

/** Rótulo (Q3, D7, P66) da separatriz que contém o valor consultado. */
export function rotuloDestacado(posicao: Posicao | undefined): string | null {
  if (posicao === undefined || posicao.fora_da_faixa !== null) return null;
  return `${PREFIXOS[posicao.tipo]}${String(posicao.indice)}`;
}

export function percentisVisiveis(separatrizes: Separatrizes, destaque: string | null): ValorSeparatriz[] {
  const visiveis = new Set(separatrizes.destaques);
  if (destaque !== null) visiveis.add(destaque);
  return separatrizes.percentis.filter((percentil) => visiveis.has(percentil.rotulo));
}

/** Posição na régua: (v − mín) / (máx − mín), em % e limitada a 0–100. */
export function percentualNaRegua(valor: number, minimo: number, maximo: number): number {
  if (maximo <= minimo) return 50;
  const percentual = ((valor - minimo) / (maximo - minimo)) * 100;
  return Math.min(100, Math.max(0, percentual));
}

export function montarRegua(posicao: Posicao): Regua {
  const { minimo, maximo } = posicao;
  const emPercentual = (valor: number) => percentualNaRegua(valor, minimo, maximo);
  const inicio = emPercentual(posicao.limite_inferior ?? minimo);
  const fim = emPercentual(posicao.limite_superior ?? maximo);
  return {
    marcador: emPercentual(posicao.valor),
    faixa: { inicio, largura: fim - inicio },
    marcas: posicao.marcas.filter(ehMarcaNumerica).map((marca) => ({
      rotulo: marca.rotulo,
      valor: formatarNumero(marca.valor),
      percentual: emPercentual(marca.valor),
    })),
    valor: formatarNumero(posicao.valor),
    minimo: formatarNumero(minimo),
    maximo: formatarNumero(maximo),
  };
}

export function descricaoDaRegua(posicao: Posicao): string {
  const regua = montarRegua(posicao);
  return P.descricaoRegua({
    minimo: regua.minimo,
    maximo: regua.maximo,
    marcas: LISTA_PT.format(regua.marcas.map((marca) => marca.rotulo)),
    valor: regua.valor,
    regiao: posicao.regiao,
  });
}

export function textoForaDaFaixa(posicao: Posicao): string | null {
  if (posicao.fora_da_faixa === null) return null;
  return posicao.fora_da_faixa === 'abaixo'
    ? P.abaixo(formatarNumero(posicao.minimo))
    : P.acima(formatarNumero(posicao.maximo));
}
```

`hooks/useConsultaPosicao.ts`:

```ts
import { useState } from 'react';
import { lerNumeroPtBr } from '../../../shared/lib/formatar';
import { useValorAtrasado } from '../../../shared/lib/useValorAtrasado';
import { usePosicao } from '../api';
import type { TipoSeparatriz } from '../tipos';

export const ATRASO_DIGITACAO_MS = 300;

/** Estado do painel "Onde está meu valor?": texto digitado, tipo de separatriz e a consulta com debounce. */
export function useConsultaPosicao(datasetId: string, coluna: string, habilitada: boolean) {
  const [texto, setTexto] = useState('');
  const [tipo, setTipo] = useState<TipoSeparatriz>('quartil');
  const textoAtrasado = useValorAtrasado(texto, ATRASO_DIGITACAO_MS);
  const valor = habilitada ? lerNumeroPtBr(textoAtrasado) : null;
  const posicao = usePosicao({ datasetId, coluna, valor, tipo });

  return {
    texto,
    setTexto,
    tipo,
    setTipo,
    invalido: texto.trim() !== '' && lerNumeroPtBr(texto) === null,
    posicao,
    // Campo apagado: some o resultado anterior (o placeholderData o manteria).
    posicaoAtual: valor === null ? undefined : posicao.data,
  };
}

export type ConsultaPosicaoNaTela = ReturnType<typeof useConsultaPosicao>;
```

`components/ListaSeparatrizes.tsx`:

```tsx
import { useId } from 'react';
import { formatarValorMedida } from '../formatacao';
import type { ValorSeparatriz } from '../tipos';
import estilos from './ListaSeparatrizes.module.css';

interface Props {
  titulo: string;
  itens: readonly ValorSeparatriz[];
  destaque: string | null;
}

export default function ListaSeparatrizes({ titulo, itens, destaque }: Readonly<Props>) {
  const idTitulo = useId();

  return (
    <section className={estilos.lista} aria-labelledby={idTitulo}>
      <h3 id={idTitulo} className={estilos.titulo}>
        {titulo}
      </h3>
      <dl className={estilos.itens}>
        {itens.map((item) => (
          <div key={item.rotulo} className={estilos.item} data-destaque={item.rotulo === destaque}>
            <dt className={estilos.rotulo}>{item.rotulo}</dt>
            <dd className={estilos.valor}>{formatarValorMedida(item.valor)}</dd>
          </div>
        ))}
      </dl>
    </section>
  );
}
```

`components/TabelaSeparatrizes.tsx`:

```tsx
import Card from '../../../shared/ui/Card';
import { percentisVisiveis } from '../separatrizes';
import { TEXTOS_ANALISE } from '../textos';
import type { Separatrizes } from '../tipos';
import ListaSeparatrizes from './ListaSeparatrizes';
import estilos from './TabelaSeparatrizes.module.css';

const S = TEXTOS_ANALISE.separatrizes;

interface Props {
  coluna: string;
  separatrizes: Separatrizes;
  destaque: string | null;
}

export default function TabelaSeparatrizes({ coluna, separatrizes, destaque }: Readonly<Props>) {
  const grupos = [
    { titulo: S.quartis, itens: separatrizes.quartis },
    { titulo: S.decis, itens: separatrizes.decis },
    { titulo: S.percentis, itens: percentisVisiveis(separatrizes, destaque) },
  ];

  return (
    <Card titulo={S.titulo(coluna)}>
      <div className={estilos.grupos}>
        {grupos.map((grupo) => (
          <ListaSeparatrizes key={grupo.titulo} titulo={grupo.titulo} itens={grupo.itens} destaque={destaque} />
        ))}
      </div>
      <details className={estilos.todos}>
        <summary className={estilos.resumo}>{S.verTodos}</summary>
        <ListaSeparatrizes titulo={S.todosPercentis} itens={separatrizes.percentis} destaque={destaque} />
      </details>
    </Card>
  );
}
```

`components/ReguaSeparatrizes.tsx`:

```tsx
import { descricaoDaRegua, montarRegua } from '../separatrizes';
import { TEXTOS_ANALISE } from '../textos';
import type { Posicao } from '../tipos';
import estilos from './ReguaSeparatrizes.module.css';

const P = TEXTOS_ANALISE.posicao;

const emPorcentagem = (valor: number) => `${valor.toFixed(2)}%`;

interface Props {
  posicao: Posicao;
}

export default function ReguaSeparatrizes({ posicao }: Readonly<Props>) {
  const regua = montarRegua(posicao);

  return (
    <div className={estilos.regua} role="img" aria-label={descricaoDaRegua(posicao)}>
      <div className={estilos.area}>
        <div className={estilos.trilho} />
        <div className={estilos.faixa} style={{ left: emPorcentagem(regua.faixa.inicio), width: emPorcentagem(regua.faixa.largura) }} />
        {regua.marcas.map((marca) => (
          <div key={marca.rotulo} className={estilos.marca} style={{ left: emPorcentagem(marca.percentual) }} />
        ))}
        <div className={estilos.marcador} style={{ left: emPorcentagem(regua.marcador) }}>
          <span className={estilos.etiqueta}>{regua.valor}</span>
          <span className={estilos.ponto} />
        </div>
      </div>
      <div className={estilos.rotulos}>
        <span className={estilos.extremoEsquerdo}>
          {P.minimo}
          <br />
          {regua.minimo}
        </span>
        {regua.marcas.map((marca) => (
          <span key={marca.rotulo} className={estilos.rotulo} style={{ left: emPorcentagem(marca.percentual) }}>
            {marca.rotulo}
            <br />
            {marca.valor}
          </span>
        ))}
        <span className={estilos.extremoDireito}>
          {P.maximo}
          <br />
          {regua.maximo}
        </span>
      </div>
    </div>
  );
}
```
(As posições são estilo inline porque dependem do dado; cores e medidas ficam no CSS.)

`components/PainelPosicao.tsx`:

```tsx
import { textoDoErro } from '../../../shared/api/erros';
import Banner from '../../../shared/ui/Banner';
import CampoNumero from '../../../shared/ui/CampoNumero';
import Card from '../../../shared/ui/Card';
import Segmented from '../../../shared/ui/Segmented';
import type { ConsultaPosicaoNaTela } from '../hooks/useConsultaPosicao';
import { textoForaDaFaixa } from '../separatrizes';
import { TEXTOS_ANALISE } from '../textos';
import type { Posicao, TipoSeparatriz } from '../tipos';
import estilos from './PainelPosicao.module.css';
import ReguaSeparatrizes from './ReguaSeparatrizes';

const P = TEXTOS_ANALISE.posicao;
const TIPOS: readonly TipoSeparatriz[] = ['quartil', 'decil', 'percentil'];
const OPCOES_TIPO = TIPOS.map((valor) => ({ valor, rotulo: P.tipos[valor] }));

function ResultadoPosicao({ posicao }: Readonly<{ posicao: Posicao }>) {
  const fora = textoForaDaFaixa(posicao);
  return (
    <>
      {fora === null ? null : (
        <Banner variante="atencao" titulo={P.foraTitulo}>
          {fora}
        </Banner>
      )}
      <ReguaSeparatrizes posicao={posicao} />
    </>
  );
}

interface Props {
  coluna: string;
  consulta: ConsultaPosicaoNaTela;
}

export default function PainelPosicao({ coluna, consulta }: Readonly<Props>) {
  const { posicaoAtual, posicao } = consulta;

  return (
    <Card titulo={P.titulo}>
      <div className={estilos.corpo}>
        <div className={estilos.controles}>
          <CampoNumero
            rotulo={P.campo(coluna)}
            valor={consulta.texto}
            aoMudar={consulta.setTexto}
            {...(consulta.invalido ? { erro: P.erroValor } : {})}
          />
          <Segmented rotulo={P.comparar} opcoes={OPCOES_TIPO} valor={consulta.tipo} aoMudar={consulta.setTipo} />
        </div>
        {posicao.isError ? <Banner variante="erro">{textoDoErro(posicao.error).mensagem}</Banner> : null}
        {posicaoAtual === undefined ? null : <ResultadoPosicao posicao={posicaoAtual} />}
        <p aria-live="polite" className={posicaoAtual === undefined ? estilos.dica : estilos.frase}>
          {posicaoAtual?.frase ?? P.dica}
        </p>
      </div>
    </Card>
  );
}
```

`components/AbaSeparatrizes.tsx`:

```tsx
import { estaAplicavel } from '../abas';
import { useConsultaPosicao } from '../hooks/useConsultaPosicao';
import { rotuloDestacado } from '../separatrizes';
import type { PropsPainel } from '../tipos';
import estilos from './AbaSeparatrizes.module.css';
import PainelPosicao from './PainelPosicao';
import TabelaSeparatrizes from './TabelaSeparatrizes';

export default function AbaSeparatrizes({ analise, datasetId }: Readonly<PropsPainel>) {
  const comPainel = estaAplicavel(analise, 'posicao');
  const consulta = useConsultaPosicao(datasetId, analise.coluna, comPainel);
  // A aba fica desabilitada sem separatrizes (abasDaAnalise); a guarda só estreita o tipo.
  if (analise.separatrizes === null) return null;

  return (
    <div className={estilos.grade} data-com-painel={comPainel}>
      <TabelaSeparatrizes
        coluna={analise.coluna}
        separatrizes={analise.separatrizes}
        destaque={rotuloDestacado(consulta.posicaoAtual)}
      />
      {comPainel ? <PainelPosicao coluna={analise.coluna} consulta={consulta} /> : null}
    </div>
  );
}
```

CSS (medidas do `Tela 4 Univariada.dc.html` e de `componentes.md` › ReguaSeparatrizes):

| Arquivo · seletor | Propriedades |
|---|---|
| `AbaSeparatrizes.module.css` `.grade` | `display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1.35fr); gap: var(--esp-20); align-items: start` |
| `.grade[data-com-painel='false']` | `grid-template-columns: minmax(0, 1fr)` · `@media (max-width: 1279px)` `.grade` → 1 coluna |
| `TabelaSeparatrizes.module.css` `.grupos` | `display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); margin: 0 calc(-1 * var(--esp-20))` |
| `.grupos > *` | `border-right: 1px solid var(--cor-borda)` · `:last-child` `border-right: 0` |
| `.todos` | `margin-top: var(--esp-16); border-top: 1px solid var(--cor-borda); padding-top: var(--esp-12)` |
| `.todos > section` | `content-visibility: auto; contain-intrinsic-size: auto 600px` (99 itens) |
| `.resumo` | `cursor: pointer; font-size: 14px; font-weight: 500; color: var(--cor-primaria)` · `:focus-visible` anel `var(--cor-foco)` |
| `ListaSeparatrizes.module.css` `.titulo` | `margin: 0; padding: 8px 16px; background: var(--cor-superficie-2); font-size: 12.5px; font-weight: 600; color: var(--cor-texto-2); border-bottom: 1px solid var(--cor-borda-forte)` |
| `.itens` | `margin: 0` |
| `.item` | `display: flex; justify-content: space-between; padding: 7px 16px; font: 13.5px var(--fonte-mono); font-variant-numeric: tabular-nums` |
| `.item[data-destaque='true']` | `background: var(--cor-primaria-suave)` · `.item[data-destaque='true'] .valor` `font-weight: 600` |
| `.rotulo` | `color: var(--cor-texto-2)` · `.valor` `margin: 0` |
| `PainelPosicao.module.css` `.corpo` | `display: flex; flex-direction: column; gap: 18px` |
| `.controles` | `display: flex; gap: var(--esp-16); align-items: flex-end; flex-wrap: wrap` (campo com `width: 160px`) |
| `.frase` | `margin: 0; padding: 14px 16px; border-radius: var(--raio-md); background: var(--cor-primaria-suave); font-size: 15px; line-height: 1.55` |
| `.dica` | `margin: 0; font-size: 14px; color: var(--cor-texto-2)` |
| `ReguaSeparatrizes.module.css` `.regua` | `display: flex; flex-direction: column; gap: 6px; padding: 4px 4px 0` |
| `.area` | `position: relative; height: 60px` |
| `.trilho` | `position: absolute; inset: 30px 0 auto 0; height: 10px; border-radius: 5px; background: var(--cor-superficie-2); border: 1px solid var(--cor-borda-forte); box-sizing: border-box` |
| `.faixa` | `position: absolute; top: 30px; height: 10px; background: color-mix(in oklab, var(--cor-primaria) 32%, var(--cor-superficie))` |
| `.marca` | `position: absolute; top: 24px; width: 2px; height: 22px; background: var(--cor-texto-2); transform: translateX(-50%)` |
| `.marcador` | `position: absolute; top: 0; transform: translateX(-50%); display: flex; flex-direction: column; align-items: center` |
| `.etiqueta` | `font: 600 13px var(--fonte-mono); color: var(--cor-primaria); padding: 1px 6px; border-radius: var(--raio-xs); background: var(--cor-primaria-suave)` |
| `.ponto` | `width: 16px; height: 16px; margin-top: 5px; border-radius: 50%; background: var(--cor-primaria); border: 2px solid var(--cor-superficie); box-sizing: border-box; box-shadow: 0 0 0 1px var(--cor-primaria)` |
| `.rotulos` | `position: relative; height: 34px; font: 500 12.5px/1.35 var(--fonte-mono); color: var(--cor-texto-2)` |
| `.rotulo` | `position: absolute; transform: translateX(-50%); text-align: center` |
| `.extremoEsquerdo` | `position: absolute; left: 0` · `.extremoDireito` `position: absolute; right: 0; text-align: right` |

**Passo 4: rodar e ver passar** — `npm run test -- separatrizes AbaSeparatrizes` · `npm run lint`.

**Passo 5: commit**
```bash
git add frontend/src/features/analise
git commit -m "feat(analise): aba Separatrizes com tabela, régua e consulta \"Onde está meu valor?\""
```

---

### Tarefa 8: Aba Gráficos (4f)

**Arquivos:**
- Criar: `frontend/src/features/analise/figuras.ts` · Teste: `figuras.test.ts`
- Criar: `frontend/src/features/analise/components/AbaGraficos.tsx` + `.module.css` · Teste: `AbaGraficos.test.tsx`

**Regras:** Segmented com as figuras que vieram em `analise.figuras` (ordem do backend; selo "recomendado" na `recomendado`). Rótulo do segmento = `figura.rotulo`, que vem pronto do backend (M1.5: "Histograma", "Bastões", "Barras", "Boxplot", "Ogiva", "Acumulada", "Pizza"); ids possíveis: `principal` (sempre), `boxplot` (discreta, contínua), `ogiva` (contínua), `acumulada` (ordinal, discreta), `pizza` (nominal com ≤ 5 categorias). Nada de mapa de rótulos no frontend. A figura ativa começa na recomendada; se a escolhida não existir na nova coluna, volta à recomendada (derivado). Gráfico grande + os demais menores abaixo; à direita, cards "Por que este gráfico?" (`lightbulb`, `porque`) e "Resumo do gráfico" (`resumo`).

**Passo 1: testes (falham)**

`figuras.test.ts`:

```ts
import { describe, expect, it } from 'vitest';
import { analiseContinua, analiseNominal } from '../../testes/fixturesAnalise';
import { figuraAtiva, opcoesDeFiguras } from './figuras';
import type { Figura } from './tipos';

describe('opcoesDeFiguras', () => {
  it('contínua: Histograma recomendado, Boxplot e Ogiva', () => {
    expect(opcoesDeFiguras(analiseContinua.figuras)).toEqual([
      { valor: 'principal', rotulo: 'Histograma', selo: 'recomendado' },
      { valor: 'boxplot', rotulo: 'Boxplot' },
      { valor: 'ogiva', rotulo: 'Ogiva' },
    ]);
  });

  it('nominal: o gráfico principal se chama Barras', () => {
    expect(opcoesDeFiguras(analiseNominal.figuras)[0]?.rotulo).toBe('Barras');
  });

  it('usa o rótulo que vem do backend, também para ids novos', () => {
    const nova = { ...(analiseContinua.figuras[0] as Figura), id: 'qq', recomendado: false, rotulo: 'QQ-plot' };
    expect(opcoesDeFiguras([nova])[0]?.rotulo).toBe('QQ-plot');
  });
});

describe('figuraAtiva', () => {
  it('começa na recomendada', () => {
    expect(figuraAtiva(analiseContinua.figuras, null)?.id).toBe('principal');
  });

  it('usa a escolhida quando ela existe e volta à recomendada quando não existe', () => {
    expect(figuraAtiva(analiseContinua.figuras, 'ogiva')?.id).toBe('ogiva');
    expect(figuraAtiva(analiseNominal.figuras, 'ogiva')?.id).toBe('principal');
  });

  it('sem figuras devolve null', () => {
    expect(figuraAtiva([], null)).toBeNull();
  });
});
```

`components/AbaGraficos.test.tsx`:

```tsx
import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import { analiseContinua, propsPainel } from '../../../testes/fixturesAnalise';
import { renderizarComProvedores } from '../../../testes/renderizar';
import AbaGraficos from './AbaGraficos';

vi.mock('../../../shared/graficos/Grafico', () => import('../../../testes/graficoFalso'));

describe('AbaGraficos', () => {
  it('abre no gráfico recomendado e mostra os outros menores', () => {
    renderizarComProvedores(<AbaGraficos {...propsPainel(analiseContinua)} />);

    expect(screen.getByRole('radio', { name: /Histograma/ })).toHaveAttribute('aria-checked', 'true');
    expect(screen.getByText('recomendado')).toBeInTheDocument();
    expect(screen.getAllByRole('figure')).toHaveLength(3);
    expect(screen.getByText('Por que principal.')).toBeInTheDocument();
  });

  it('trocar o gráfico troca o "Por que" e o resumo', async () => {
    const user = userEvent.setup();
    renderizarComProvedores(<AbaGraficos {...propsPainel(analiseContinua)} />);

    await user.click(screen.getByRole('radio', { name: 'Boxplot' }));

    expect(screen.getByText('Por que boxplot.')).toBeInTheDocument();
    expect(screen.getByText('Resumo de boxplot.')).toBeInTheDocument();
  });
});
```

**Passo 2: rodar e ver falhar** — `npm run test -- figuras AbaGraficos` → FAIL.

**Passo 3: implementar**

`figuras.ts`:

```ts
import { TEXTOS_ANALISE } from './textos';
import type { Figura } from './tipos';

const G = TEXTOS_ANALISE.graficos;

export interface OpcaoFigura {
  valor: string;
  rotulo: string;
  selo?: string;
}

/** O rótulo do segmento vem pronto do backend (`Figura.rotulo`, M1.5). */
export function opcoesDeFiguras(figuras: readonly Figura[]): OpcaoFigura[] {
  return figuras.map((figura) => ({
    valor: figura.id,
    rotulo: figura.rotulo,
    ...(figura.recomendado ? { selo: G.recomendado } : {}),
  }));
}

export function figuraAtiva(figuras: readonly Figura[], escolhida: string | null): Figura | null {
  return (
    figuras.find((figura) => figura.id === escolhida) ?? figuras.find((figura) => figura.recomendado) ?? figuras[0] ?? null
  );
}
```

`components/AbaGraficos.tsx`:

```tsx
import { useState } from 'react';
import Grafico from '../../../shared/graficos/Grafico';
import Card from '../../../shared/ui/Card';
import EstadoVazio from '../../../shared/ui/EstadoVazio';
import Icone from '../../../shared/ui/Icone';
import Segmented from '../../../shared/ui/Segmented';
import { figuraAtiva, opcoesDeFiguras } from '../figuras';
import { TEXTOS_ANALISE } from '../textos';
import type { PropsPainel } from '../tipos';
import estilos from './AbaGraficos.module.css';

const G = TEXTOS_ANALISE.graficos;
const ALTURA_PRINCIPAL = 420;
const ALTURA_SECUNDARIA = 240;

const TITULO_PORQUE = (
  <span className={estilos.tituloPorque}>
    <Icone nome="lightbulb" />
    {G.porque}
  </span>
);

export default function AbaGraficos({ analise }: Readonly<PropsPainel>) {
  const [escolhida, setEscolhida] = useState<string | null>(null);
  const ativa = figuraAtiva(analise.figuras, escolhida);
  if (ativa === null) return <EstadoVazio icone="scatter_plot" titulo={G.semFiguras.titulo} descricao={G.semFiguras.descricao} />;
  const secundarias = analise.figuras.filter((figura) => figura.id !== ativa.id);

  return (
    <div className={estilos.grade}>
      <Card>
        <div className={estilos.principal}>
          <Segmented rotulo={G.tipoGrafico} opcoes={opcoesDeFiguras(analise.figuras)} valor={ativa.id} aoMudar={setEscolhida} />
          <Grafico titulo={ativa.titulo} resumo={ativa.resumo} figura={ativa.dados} altura={ALTURA_PRINCIPAL} />
          {secundarias.length === 0 ? null : (
            <div className={estilos.secundarias}>
              {secundarias.map((figura) => (
                <Grafico key={figura.id} titulo={figura.titulo} resumo={figura.resumo} figura={figura.dados} altura={ALTURA_SECUNDARIA} />
              ))}
            </div>
          )}
        </div>
      </Card>
      <aside className={estilos.lateral}>
        <Card titulo={TITULO_PORQUE}>
          <p className={estilos.texto}>{ativa.porque}</p>
        </Card>
        <Card titulo={G.resumo}>
          <p className={estilos.texto}>{ativa.resumo}</p>
        </Card>
      </aside>
    </div>
  );
}
```

CSS:

| Arquivo · seletor | Propriedades |
|---|---|
| `AbaGraficos.module.css` `.grade` | `display: grid; grid-template-columns: minmax(0, 1fr) 320px; gap: var(--esp-20); align-items: start` · `@media (max-width: 1279px)` 1 coluna |
| `.principal` | `display: flex; flex-direction: column; gap: var(--esp-16)` (Segmented com `align-self: flex-start`) |
| `.secundarias` | `display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: var(--esp-20); padding-top: var(--esp-16); border-top: 1px solid var(--cor-borda)` |
| `.lateral` | `display: flex; flex-direction: column; gap: var(--esp-16)` |
| `.tituloPorque` | `display: inline-flex; align-items: center; gap: var(--esp-8)` · `.tituloPorque > span:first-child` `color: var(--cor-primaria)` |
| `.texto` | `margin: 0; font-size: 14px; line-height: 1.55; color: var(--cor-texto-2)` |

**Passo 4: rodar e ver passar** — `npm run test -- figuras AbaGraficos` · `npm run lint`.

**Passo 5: commit**
```bash
git add frontend/src/features/analise
git commit -m "feat(analise): aba Gráficos com escolha da figura, recomendado e explicação"
```

---

### Tarefa 9: `PaginaAnalise` (seletor, abas, estados) + rota

**Arquivos:**
- Reutilizar (sem mudar): `shared/sessao/SemDataset.tsx` (**criado no M1.6**) e `shared/ui/EstadoCarregando.tsx`, que **já aceita lista de formas** desde o M1.1 (`forma={['cards', 'grafico']}`)
- Criar: `frontend/src/features/analise/components/SeletorColuna.tsx` + `.module.css`
- Criar: `frontend/src/features/analise/components/ConteudoAnalise.tsx`
- Criar: `frontend/src/features/analise/components/CorpoAnalise.tsx`
- Substituir: `frontend/src/features/analise/PaginaAnalise.tsx` (provisória do M1.1) · Teste: `PaginaAnalise.test.tsx`
- `app/rotas.ts` não muda: o M1.1 já carrega `features/analise/PaginaAnalise` com `lazy()` no mesmo caminho

**Regras:**
- `PaginaEtapa etapa={4}` (marca a etapa 4 como visitada) com o seletor de coluna em `acoesTopo`: `Select` 320×44, rótulo "Coluna", nome em mono, `ChipTipo curto` da coluna escolhida sobreposto à direita (antes da seta). Só colunas analisáveis (sem identificador).
- Estados (união discriminada `EstadoAnalise` + `switch`): carregando colunas → `EstadoCarregando forma="tabela"`; sem colunas → `EstadoVazio` com "Ir para Variáveis"; calculando → `EstadoCarregando` com cards + gráfico e "Calculando as estatísticas de {coluna}…" (4h); erro → `EstadoErro` (com "Tentar de novo" só se `podeTentarDeNovo`); pronta → `ConteudoAnalise`.
- Sem dataset na sessão → `SemDataset` do M1.6 ("Nenhum arquivo importado" + "Ir para Importar") com a descrição desta tela.
- `ConteudoAnalise`: `Abas` com `abasDaAnalise` e painel por **tabela de despacho** `Record<IdAba, ComponentType<PropsPainel>>`; o painel recebe `key={analise.coluna}` (zera o estado local da aba ao trocar de coluna).

**Passo 1: teste (falha)** — `PaginaAnalise.test.tsx`

```tsx
import { screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { chamadasPara, type FetchFalso, type RotaFalsa, simularApi } from '../../testes/api';
import { analiseContinua, analiseNominal, colunasPesquisa } from '../../testes/fixturesAnalise';
import { DATASET_TESTE, renderizarComProvedores } from '../../testes/renderizar';
import PaginaAnalise from './PaginaAnalise';
import { TEXTOS_ANALISE } from './textos';

vi.mock('../../shared/graficos/Grafico', () => import('../../testes/graficoFalso'));

const BASE = `/datasets/${DATASET_TESTE.id}`;
const ROTA_COLUNAS: RotaFalsa = { caminho: `${BASE}/colunas`, corpo: colunasPesquisa };
const ROTAS_PADRAO: RotaFalsa[] = [
  ROTA_COLUNAS,
  { caminho: `${BASE}/colunas/peso_kg/analise`, corpo: analiseContinua },
  { caminho: `${BASE}/colunas/cidade/analise`, corpo: analiseNominal },
];

/** Sessão real com o dataset de teste (entra depois da 1ª renderização: começar com findBy…). */
function renderizarPagina(rota = '/analise?coluna=peso_kg') {
  return renderizarComProvedores(<PaginaAnalise />, { rota, dataset: DATASET_TESTE });
}

describe('PaginaAnalise', () => {
  let api: FetchFalso;

  beforeEach(() => {
    api = simularApi(ROTAS_PADRAO);
  });

  it('mostra "Calculando…" e depois a tabela da coluna da URL', async () => {
    renderizarPagina();

    expect(await screen.findByText(TEXTOS_ANALISE.calculando('peso_kg'))).toBeInTheDocument();
    expect(await screen.findByText('60,0 ⊢ 76,5')).toBeInTheDocument();
    expect(screen.getByLabelText('Coluna')).toHaveValue('peso_kg');
  });

  it('o seletor lista só colunas analisáveis e escreve a escolha na URL', async () => {
    const { usuario, roteador } = renderizarPagina();
    await screen.findByText('60,0 ⊢ 76,5');

    expect(screen.queryByRole('option', { name: 'id' })).toBeNull();
    await usuario.selectOptions(screen.getByLabelText('Coluna'), 'cidade');

    await waitFor(() => {
      expect(roteador.state.location.search).toBe('?coluna=cidade');
    });
    expect(await screen.findByRole('tab', { name: /Separatrizes/ })).toHaveAttribute('aria-disabled', 'true');
  });

  it('mudar o número de classes pede de novo sem tirar a tabela da tela', async () => {
    const { usuario } = renderizarPagina();
    await screen.findByText('60,0 ⊢ 76,5');

    await usuario.click(screen.getByRole('button', { name: TEXTOS_ANALISE.frequencias.mais }));

    await waitFor(() => {
      expect(chamadasPara(api, 'GET', `${BASE}/colunas/peso_kg/analise`).map((c) => c.url)).toContain(
        `/api${BASE}/colunas/peso_kg/analise?classes=4`,
      );
    });
    expect(screen.getByText('60,0 ⊢ 76,5')).toBeInTheDocument();
  });

  it('COLUNA_VAZIA mostra a mensagem da API sem "Tentar de novo"', async () => {
    simularApi([
      ROTA_COLUNAS,
      {
        caminho: `${BASE}/colunas/peso_kg/analise`,
        status: 400,
        corpo: { codigo: 'COLUNA_VAZIA', mensagem: 'A coluna peso_kg não tem valores para analisar.', sugestao: 'Escolha outra coluna.' },
      },
    ]);
    renderizarPagina();

    expect(await screen.findByText('A coluna peso_kg não tem valores para analisar.')).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /Tentar de novo/ })).toBeNull();
  });

  it('sem colunas analisáveis orienta a corrigir os tipos', async () => {
    simularApi([{ ...ROTA_COLUNAS, corpo: colunasPesquisa.slice(0, 1) }]);
    renderizarPagina('/analise');

    expect(await screen.findByText(TEXTOS_ANALISE.semColunas.titulo)).toBeInTheDocument();
  });

  it('sem arquivo importado orienta a ir para Importar', () => {
    renderizarComProvedores(<PaginaAnalise />, { rota: '/analise' });

    expect(screen.getByText(TEXTOS_ANALISE.semDataset)).toBeInTheDocument();
  });
});
```

**Passo 2: rodar e ver falhar** — `npm run test -- PaginaAnalise` → FAIL.

**Passo 3: implementar**

`EstadoCarregando` (M1.1) e `SemDataset` (M1.6) já existem: nada a criar ou mudar neles.

`components/SeletorColuna.tsx`:

```tsx
import ChipTipo from '../../../shared/ui/ChipTipo';
import Select from '../../../shared/ui/Select';
import { TEXTOS_ANALISE } from '../textos';
import type { TipoColuna } from '../tipos';
import estilos from './SeletorColuna.module.css';

interface Props {
  colunas: readonly TipoColuna[];
  escolhida: TipoColuna;
  aoMudar: (coluna: string) => void;
}

export default function SeletorColuna({ colunas, escolhida, aoMudar }: Readonly<Props>) {
  const opcoes = colunas.map((coluna) => ({ valor: coluna.coluna, rotulo: coluna.coluna }));

  return (
    <div className={estilos.seletor}>
      <Select rotulo={TEXTOS_ANALISE.rotuloColuna} valor={escolhida.coluna} opcoes={opcoes} aoMudar={aoMudar} altura={44} />
      <span className={estilos.chip}>
        <ChipTipo tipo={escolhida.tipo} curto />
      </span>
    </div>
  );
}
```

`components/ConteudoAnalise.tsx`:

```tsx
import { useState, type ComponentType } from 'react';
import Abas from '../../../shared/ui/Abas';
import { abaEfetiva, abasDaAnalise } from '../abas';
import { TEXTOS_ANALISE } from '../textos';
import type { IdAba, PropsPainel } from '../tipos';
import AbaDispersao from './AbaDispersao';
import AbaFrequencias from './AbaFrequencias';
import AbaGraficos from './AbaGraficos';
import AbaSeparatrizes from './AbaSeparatrizes';
import AbaTendencia from './AbaTendencia';

const PAINEIS: Record<IdAba, ComponentType<PropsPainel>> = {
  frequencias: AbaFrequencias,
  tendencia: AbaTendencia,
  separatrizes: AbaSeparatrizes,
  dispersao: AbaDispersao,
  graficos: AbaGraficos,
};

export default function ConteudoAnalise(props: Readonly<PropsPainel>) {
  const [pedida, setPedida] = useState<IdAba>('frequencias');
  const abas = abasDaAnalise(props.analise);
  const ativa = abaEfetiva(pedida, abas);
  const Painel = PAINEIS[ativa];

  return (
    <Abas rotulo={TEXTOS_ANALISE.rotuloAbas} abas={abas} ativa={ativa} aoMudar={setPedida}>
      <Painel key={props.analise.coluna} {...props} />
    </Abas>
  );
}
```
(Se o lint do React Compiler reclamar de componente escolhido em render, troque por `switch (ativa)` que devolve o JSX de cada painel.)

`components/CorpoAnalise.tsx`:

```tsx
import { useNavigate } from 'react-router';
import { CAMINHOS } from '../../../shared/navegacao/caminhos';
import Botao from '../../../shared/ui/Botao';
import EstadoCarregando from '../../../shared/ui/EstadoCarregando';
import EstadoErro from '../../../shared/ui/EstadoErro';
import EstadoVazio from '../../../shared/ui/EstadoVazio';
import type { EstadoAnalise } from '../estadoAnalise';
import { TEXTOS_ANALISE } from '../textos';
import ConteudoAnalise from './ConteudoAnalise';

const T = TEXTOS_ANALISE;
const FORMAS_CALCULANDO = ['cards', 'grafico'] as const;

function SemColunas() {
  const navegar = useNavigate();
  const acao = (
    <Botao
      variante="secundario"
      onClick={() => {
        void navegar(CAMINHOS.variaveis);
      }}
    >
      {T.semColunas.acao}
    </Botao>
  );
  return <EstadoVazio icone="dataset" titulo={T.semColunas.titulo} descricao={T.semColunas.descricao} acao={acao} />;
}

interface Props {
  estado: EstadoAnalise;
  datasetId: string;
  classes: number | null;
  aoMudarClasses: (k: number) => void;
}

export default function CorpoAnalise({ estado, ...resto }: Readonly<Props>) {
  switch (estado.status) {
    case 'carregando-colunas':
      return <EstadoCarregando forma="tabela" mensagem={T.carregandoColunas} />;
    case 'sem-colunas':
      return <SemColunas />;
    case 'calculando':
      return <EstadoCarregando forma={FORMAS_CALCULANDO} mensagem={T.calculando(estado.coluna)} />;
    case 'erro':
      return (
        <EstadoErro erro={estado.erro} {...(estado.tentarDeNovo === null ? {} : { aoTentarDeNovo: estado.tentarDeNovo })} />
      );
    case 'pronta':
      return <ConteudoAnalise analise={estado.analise} atualizando={estado.atualizando} {...resto} />;
  }
}
```

`PaginaAnalise.tsx`:

```tsx
import { useColunasAnalisaveis } from '../../shared/api/colunas';
import SemDataset from '../../shared/sessao/SemDataset';
import { useSessao } from '../../shared/sessao/useSessao';
import PaginaEtapa from '../../shared/ui/PaginaEtapa';
import { useAnalise } from './api';
import CorpoAnalise from './components/CorpoAnalise';
import SeletorColuna from './components/SeletorColuna';
import { estadoDaAnalise } from './estadoAnalise';
import { useParametrosAnalise } from './hooks/useParametrosAnalise';
import { colunaEscolhida } from './parametros';
import { TEXTOS_ANALISE } from './textos';

const ETAPA_ANALISE = 4;
const T = TEXTOS_ANALISE;

function AnaliseDoDataset({ datasetId }: Readonly<{ datasetId: string }>) {
  const colunas = useColunasAnalisaveis(datasetId);
  const parametros = useParametrosAnalise();
  const escolhida = colunaEscolhida(parametros.coluna, colunas.data ?? []);
  const nomeColuna = escolhida?.coluna ?? null;
  const analise = useAnalise(datasetId, nomeColuna, parametros.classes);
  const seletor =
    colunas.data !== undefined && escolhida !== null ? (
      <SeletorColuna colunas={colunas.data} escolhida={escolhida} aoMudar={parametros.escolherColuna} />
    ) : null;

  return (
    <PaginaEtapa etapa={ETAPA_ANALISE} titulo={T.titulo} ajuda={T.ajuda} acoesTopo={seletor}>
      <CorpoAnalise
        estado={estadoDaAnalise(colunas, analise, nomeColuna)}
        datasetId={datasetId}
        classes={parametros.classes}
        aoMudarClasses={parametros.mudarClasses}
      />
    </PaginaEtapa>
  );
}

export default function PaginaAnalise() {
  const { dataset } = useSessao();
  return dataset === null ? (
    <PaginaEtapa etapa={ETAPA_ANALISE} titulo={T.titulo} ajuda={T.ajuda}>
      <SemDataset descricao={T.semDataset} />
    </PaginaEtapa>
  ) : (
    <AnaliseDoDataset datasetId={dataset.id} />
  );
}
```

Rota: o M1.1 já tem `lazy(() => import('../features/analise/PaginaAnalise'))` em `app/rotas.ts`; como a página foi substituída no mesmo caminho, nada muda (confira com `grep -n analise frontend/src/app/rotas.ts`).

CSS:

| Arquivo · seletor | Propriedades |
|---|---|
| `SeletorColuna.module.css` `.seletor` | `position: relative; width: 320px` |
| `.seletor :global(select)` | `font-family: var(--fonte-mono); padding-right: 150px` (espaço para o chip; se o `Select` ganhar `mono`/adorno no futuro, remover — anotar no PR) |
| `.chip` | `position: absolute; right: 40px; bottom: 9px; pointer-events: none` (o field tem 44 de altura e o chip 26) |

**Passo 4: rodar e ver passar** — `npm run test` (tudo) · `npm run lint` · `npm run build`.

**Passo 5: conferir no navegador** (preview `backend` + `frontend`, Importar `pesquisa_saude.txt`, ir para Análise): `peso_kg` mostra 4b; trocar para `cidade` mostra 4g com Separatrizes/Dispersão desabilitadas (tooltip com motivo); setas ←/→ andam pelas abas e pulam as desabilitadas; recarregar mantém a coluna.

**Passo 6: commit**
```bash
git add frontend/src
git commit -m "feat(analise): tela de análise univariada com seletor de coluna, abas e estados de carregando, vazio e erro"
```

---

### Tarefa 10: Base da feature `relatorio` (funções puras)

**Arquivos:**
- Criar: `frontend/src/features/relatorio/api.ts` · Teste: `api.test.ts`
- Criar: `frontend/src/features/relatorio/selecao.ts` · Teste: `selecao.test.ts`
- Substituir: `frontend/src/features/relatorio/textos.ts` (provisório do M1.1; `titulo` e `ajuda` continuam iguais)

**Decisões desta tarefa:**
- Seções do M1 = `leitura, tipos, limpeza, analises` (D57), sempre na ordem canônica, não na ordem dos cliques. Colunas na ordem do dataset e só quando "Análises por coluna" está marcada.
- "Análises por coluna" marcada sem nenhuma coluna não entra no pedido; sem nenhuma seção efetiva → estado vazio (prévia e botões desligados).
- **Prévia sempre com `offline=true`**: os gráficos aparecem mesmo sem internet e o "Imprimir / salvar PDF" (que imprime o `iframe`) sai igual ao arquivo. A caixa "Funciona sem internet" (marcada por padrão) vale **só para o arquivo baixado**: desmarcada, gera um HTML menor que carrega o Plotly da CDN.
- **"Baixar HTML" com `fetch` + `Blob`** (`requisitarBlob` + `baixarArquivo`) em vez de `<a download href=…>`: (1) erro da API (sessão expirada, coluna inválida) vira toast com a mensagem padronizada em vez de baixar um JSON de erro com nome de `.html`; (2) o nome `relatorio-{arquivo}.html` não depende do `Content-Disposition`; (3) o botão mostra "Gerando…" enquanto o backend monta o arquivo (com o Plotly embutido, ~3,5 MB). O custo (o arquivo passa pela memória da aba) é irrelevante para uso local.
- `SecaoRelatorio` é declarada no frontend porque o parâmetro de query não vira schema nomeado; **se o `schema.d.ts` gerar `SecaoRelatorio`**, troque a declaração por `components['schemas']['SecaoRelatorio']` e mantenha a lista com `satisfies readonly SecaoRelatorio[]`.

**Passo 1: testes (falham)**

`api.test.ts`:

```ts
import { describe, expect, it } from 'vitest';
import { caminhoRelatorio, nomeArquivoRelatorio, SECOES_RELATORIO } from './api';

describe('caminhoRelatorio', () => {
  it('repete secoes e colunas e manda offline', () => {
    const caminho = caminhoRelatorio('ds1', { secoes: SECOES_RELATORIO, colunas: ['sexo', 'peso_kg'], offline: true });

    expect(caminho).toBe(
      '/datasets/ds1/relatorio?secoes=leitura&secoes=tipos&secoes=limpeza&secoes=analises&colunas=sexo&colunas=peso_kg&offline=true',
    );
  });

  it('codifica nomes de coluna com espaço e acento', () => {
    expect(caminhoRelatorio('ds1', { secoes: ['analises'], colunas: ['renda média'], offline: false })).toBe(
      '/datasets/ds1/relatorio?secoes=analises&colunas=renda+m%C3%A9dia&offline=false',
    );
  });
});

describe('nomeArquivoRelatorio', () => {
  it.each([
    ['pesquisa_saude.txt', 'relatorio-pesquisa_saude.html'],
    ['notas.turma.csv', 'relatorio-notas.turma.html'],
    ['sem_extensao', 'relatorio-sem_extensao.html'],
  ])('%s → %s', (arquivo, esperado) => {
    expect(nomeArquivoRelatorio(arquivo)).toBe(esperado);
  });
});
```

`selecao.test.ts`:

```ts
import { describe, expect, it } from 'vitest';
import { alternar, selecaoEfetiva } from './selecao';

describe('alternar', () => {
  it('tira o item que está e põe o que não está, sem mudar o original', () => {
    const original = new Set(['a']);

    expect([...alternar(original, 'a')]).toEqual([]);
    expect([...alternar(original, 'b')]).toEqual(['a', 'b']);
    expect([...original]).toEqual(['a']);
  });
});

describe('selecaoEfetiva', () => {
  it('mantém seções e colunas quando há análises com colunas', () => {
    expect(selecaoEfetiva({ secoes: ['tipos', 'analises'], colunas: ['peso_kg'] })).toEqual({
      secoes: ['tipos', 'analises'],
      colunas: ['peso_kg'],
    });
  });

  it('sem colunas, "analises" sai do pedido', () => {
    expect(selecaoEfetiva({ secoes: ['leitura', 'analises'], colunas: [] })).toEqual({ secoes: ['leitura'], colunas: [] });
  });

  it('sem "analises", as colunas não vão no pedido', () => {
    expect(selecaoEfetiva({ secoes: ['leitura'], colunas: ['peso_kg'] })).toEqual({ secoes: ['leitura'], colunas: [] });
  });

  it('nada efetivo vira null (estado vazio)', () => {
    expect(selecaoEfetiva({ secoes: [], colunas: ['peso_kg'] })).toBeNull();
    expect(selecaoEfetiva({ secoes: ['analises'], colunas: [] })).toBeNull();
  });
});
```

**Passo 2: rodar e ver falhar** — `npm run test -- relatorio` → FAIL.

**Passo 3: implementar**

`api.ts`:

```ts
import { useMutation } from '@tanstack/react-query';
import { requisitarBlob } from '../../shared/api/cliente';
import { caminhoDataset } from '../../shared/api/dataset';
import { baixarArquivo } from '../../shared/lib/baixarArquivo';

/** Seções aceitas no M1 (D57), na ordem do relatório. */
export const SECOES_RELATORIO = ['leitura', 'tipos', 'limpeza', 'analises'] as const;
export type SecaoRelatorio = (typeof SECOES_RELATORIO)[number];

export interface SelecaoRelatorio {
  secoes: readonly SecaoRelatorio[];
  colunas: readonly string[];
}

export interface PedidoRelatorio extends SelecaoRelatorio {
  offline: boolean;
}

const EXTENSAO = /\.[^.]+$/u;

export function caminhoRelatorio(datasetId: string, pedido: PedidoRelatorio): string {
  const parametros = new URLSearchParams();
  for (const secao of pedido.secoes) parametros.append('secoes', secao);
  for (const coluna of pedido.colunas) parametros.append('colunas', coluna);
  parametros.set('offline', String(pedido.offline));
  return caminhoDataset(datasetId, `/relatorio?${parametros.toString()}`);
}

export function nomeArquivoRelatorio(nomeArquivo: string): string {
  return `relatorio-${nomeArquivo.replace(EXTENSAO, '')}.html`;
}

interface PedidoDownload {
  caminho: string;
  nomeArquivo: string;
}

export function useBaixarRelatorio() {
  return useMutation({
    mutationFn: async ({ caminho, nomeArquivo }: PedidoDownload) => {
      baixarArquivo(await requisitarBlob(caminho), nomeArquivo);
    },
  });
}
```

`selecao.ts`:

```ts
import type { SelecaoRelatorio } from './api';

export function alternar<T>(conjunto: ReadonlySet<T>, item: T): ReadonlySet<T> {
  const novo = new Set(conjunto);
  if (novo.has(item)) {
    novo.delete(item);
  } else {
    novo.add(item);
  }
  return novo;
}

/** O que de fato vai para o backend; null quando não há nada para mostrar. */
export function selecaoEfetiva(selecao: SelecaoRelatorio): SelecaoRelatorio | null {
  const semColunas = selecao.colunas.length === 0;
  const secoes = semColunas ? selecao.secoes.filter((secao) => secao !== 'analises') : selecao.secoes;
  if (secoes.length === 0) return null;
  return { secoes, colunas: secoes.includes('analises') ? selecao.colunas : [] };
}
```

`textos.ts`:

```ts
import type { SecaoRelatorio } from './api';

export const TEXTOS_RELATORIO = {
  titulo: 'Relatório',
  ajuda: 'Escolha o que entra. A prévia ao lado mostra exatamente como o relatório será impresso.',
  semDataset: 'Importe um arquivo para montar o relatório.',
  baixar: 'Baixar HTML',
  baixando: 'Gerando…',
  imprimir: 'Imprimir / salvar PDF',
  secoes: 'Seções',
  colunas: 'Colunas',
  rotulosSecoes: {
    leitura: 'Leitura',
    tipos: 'Tipos',
    limpeza: 'Limpeza',
    analises: 'Análises por coluna',
  } satisfies Record<SecaoRelatorio, string>,
  contador: (marcados: number, total: number) => `${String(marcados)} de ${String(total)}`,
  colunasSemAnalises: 'Marque "Análises por coluna" para escolher as colunas.',
  carregandoColunas: 'Carregando as colunas…',
  offline: 'Funciona sem internet',
  offlineAjuda: 'Embute o motor dos gráficos no arquivo (cerca de 3,5 MB). Sem isso, o arquivo fica menor, mas os gráficos só aparecem com internet.',
  previa: 'Prévia · A4 retrato',
  tituloPrevia: 'Prévia do relatório',
  montando: 'Montando a prévia do relatório…',
  vazio: { titulo: 'Nada para mostrar', descricao: 'Marque ao menos uma seção para ver a prévia do relatório.' },
  baixado: (nome: string) => `Relatório baixado: ${nome}.`,
};
```

**Passo 4: rodar e ver passar** — `npm run test -- relatorio` · `npm run lint`.

**Passo 5: commit**
```bash
git add frontend/src/features/relatorio
git commit -m "feat(relatorio): monta a URL do relatório, o nome do arquivo e a seleção de seções e colunas"
```

---

### Tarefa 11: `PaginaRelatorio` (8a) + rota

**Arquivos:**
- Criar: `frontend/src/features/relatorio/hooks/useSelecaoRelatorio.ts`, `usePreviaRelatorio.ts`, `useAcaoBaixar.ts`
- Criar: `frontend/src/features/relatorio/components/GrupoCaixas.tsx` + `.module.css`
- Criar: `frontend/src/features/relatorio/components/OpcoesRelatorio.tsx` + `.module.css`
- Criar: `frontend/src/features/relatorio/components/PreviaRelatorio.tsx` + `.module.css`
- Substituir: `frontend/src/features/relatorio/PaginaRelatorio.tsx` (provisória do M1.1) + criar `PaginaRelatorio.module.css` · Teste: `PaginaRelatorio.test.tsx`
- Reutilizar: `SemDataset` (M1.6) e `useValorAtrasado` (M1.6); `app/rotas.ts` não muda (o M1.1 já carrega a página com `lazy()` no mesmo caminho)

**Regras:**
- `PaginaEtapa etapa={8}` (marca a etapa 8 como visitada); topo: secundário lg "Baixar HTML" (`code`) e primário lg "Imprimir / salvar PDF" (`print`).
- Grid `300px 1fr`. Esquerda: fieldset "Seções" (4 caixas, contador "4 de 4"), fieldset "Colunas" (nome mono + `ChipTipo curto`, contador "{n} de {total}", desabilitado com nota quando "Análises por coluna" está desmarcada) e a caixa "Funciona sem internet" com a explicação. **Um só componente `GrupoCaixas`** serve aos dois fieldsets.
- Estado da seleção guarda os itens **desmarcados**: tudo começa marcado, inclusive as colunas que chegam depois da consulta (sem `useEffect`).
- Direita: área superficie-2 com "Prévia · A4 retrato" e o `<iframe title="Prévia do relatório">` 620×877 (proporção A4), `src` = `/api/...&offline=true`, trocado 400 ms depois da última mudança (`useValorAtrasado`). Enquanto o `iframe` carrega (`onLoad` ainda não veio para o `src` atual), um esqueleto cobre a página e "Imprimir" fica desligado. Prévia sempre clara (D47): o HTML traz o próprio CSS claro e o `iframe` usa `color-scheme: light`.
- "Imprimir / salvar PDF" → `iframe.contentWindow.print()` (mesma origem pelo proxy `/api`). "Baixar HTML" → `useBaixarRelatorio` com o `offline` da caixa; sucesso → toast "Relatório baixado: relatorio-pesquisa_saude.html."; erro → toast de erro com `textoDoErro`.

**Passo 1: teste (falha)** — `PaginaRelatorio.test.tsx`

```tsx
import { fireEvent, screen, waitFor, within } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { chamadasPara, type FetchFalso, simularApi } from '../../testes/api';
import { simularDownload } from '../../testes/downloadFalso';
import { colunasPesquisa } from '../../testes/fixturesAnalise';
import { DATASET_TESTE, renderizarComProvedores } from '../../testes/renderizar';
import PaginaRelatorio from './PaginaRelatorio';
import { TEXTOS_RELATORIO } from './textos';

const T = TEXTOS_RELATORIO;
const BASE = `/datasets/${DATASET_TESTE.id}`;

function previa(): HTMLIFrameElement {
  return screen.getByTitle(T.tituloPrevia);
}

/** Sessão real com o dataset de teste (entra depois da 1ª renderização: começar com findBy…). */
function renderizarPagina() {
  return renderizarComProvedores(<PaginaRelatorio />, { dataset: DATASET_TESTE });
}

describe('PaginaRelatorio', () => {
  let api: FetchFalso;

  beforeEach(() => {
    // O corpo do relatório não importa nos testes (o jsdom não carrega o iframe).
    api = simularApi([
      { caminho: `${BASE}/colunas`, corpo: colunasPesquisa },
      { caminho: `${BASE}/relatorio`, corpo: '<html></html>' },
    ]);
  });

  it('começa com as 4 seções do M1 e todas as colunas analisáveis marcadas', async () => {
    renderizarPagina();

    const secoes = await screen.findByRole('group', { name: /^Seções/ });
    expect(within(secoes).getAllByRole('checkbox', { checked: true })).toHaveLength(4);
    expect(within(secoes).getByText('4 de 4')).toBeInTheDocument();
    const colunas = await screen.findByRole('group', { name: /^Colunas/ });
    expect(within(colunas).getAllByRole('checkbox', { checked: true })).toHaveLength(3);
    expect(within(colunas).queryByText('id')).toBeNull();
  });

  it('a prévia usa a seleção e sempre funciona offline', async () => {
    renderizarPagina();

    await waitFor(() => {
      expect(previa().getAttribute('src')).toBe(
        `/api${BASE}/relatorio?secoes=leitura&secoes=tipos&secoes=limpeza&secoes=analises&colunas=sexo&colunas=peso_kg&colunas=cidade&offline=true`,
      );
    });
  });

  it('desmarcar uma coluna atualiza a prévia depois da pausa', async () => {
    const { usuario } = renderizarPagina();
    await usuario.click(await screen.findByRole('checkbox', { name: /peso_kg/ }));

    await waitFor(() => {
      expect(previa().getAttribute('src')).not.toContain('peso_kg');
    });
  });

  it('sem nenhuma seção, mostra o estado vazio e desliga os botões', async () => {
    const { usuario } = renderizarPagina();
    await screen.findByRole('group', { name: /^Seções/ });
    for (const rotulo of Object.values(T.rotulosSecoes)) {
      await usuario.click(screen.getByRole('checkbox', { name: rotulo }));
    }

    expect(screen.getByText(T.vazio.titulo)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: T.baixar })).toBeDisabled();
    expect(screen.getByRole('button', { name: T.imprimir })).toBeDisabled();
  });

  it('baixar usa a opção "Funciona sem internet" e o nome do arquivo', async () => {
    const { nomesBaixados } = simularDownload();
    const { usuario } = renderizarPagina();
    await screen.findByRole('checkbox', { name: /peso_kg/ });

    await usuario.click(screen.getByRole('checkbox', { name: new RegExp(T.offline) }));
    await usuario.click(screen.getByRole('button', { name: T.baixar }));

    expect(await screen.findByText(T.baixado('relatorio-pesquisa_saude.html'))).toBeInTheDocument();
    expect(nomesBaixados).toEqual(['relatorio-pesquisa_saude.html']);
    expect(chamadasPara(api, 'GET', `${BASE}/relatorio`).some((c) => c.url.endsWith('offline=false'))).toBe(true);
  });

  it('imprimir chama o print da prévia carregada', async () => {
    const { usuario } = renderizarPagina();
    await screen.findByRole('checkbox', { name: /peso_kg/ });
    await waitFor(() => {
      expect(previa().getAttribute('src')).toContain('colunas=cidade');
    });
    const janela = previa().contentWindow as Window;
    const imprimir = vi.spyOn(janela, 'print').mockImplementation(() => undefined);

    fireEvent.load(previa());
    await usuario.click(screen.getByRole('button', { name: T.imprimir }));

    expect(imprimir).toHaveBeenCalled();
  });

  it('sem arquivo importado orienta a ir para Importar', () => {
    renderizarComProvedores(<PaginaRelatorio />);

    expect(screen.getByText(T.semDataset)).toBeInTheDocument();
  });
});
```

**Passo 2: rodar e ver falhar** — `npm run test -- PaginaRelatorio` → FAIL.

**Passo 3: implementar**

`hooks/useSelecaoRelatorio.ts`:

```ts
import { useState } from 'react';
import { SECOES_RELATORIO, type SecaoRelatorio } from '../api';
import { alternar } from '../selecao';

/** Guarda o que foi desmarcado: tudo começa marcado, inclusive colunas que chegam depois. */
export function useSelecaoRelatorio(colunasDisponiveis: readonly string[]) {
  const [secoesFora, setSecoesFora] = useState<ReadonlySet<SecaoRelatorio>>(() => new Set());
  const [colunasFora, setColunasFora] = useState<ReadonlySet<string>>(() => new Set());

  return {
    secoes: SECOES_RELATORIO.filter((secao) => !secoesFora.has(secao)),
    colunas: colunasDisponiveis.filter((coluna) => !colunasFora.has(coluna)),
    alternarSecao: (secao: SecaoRelatorio) => {
      setSecoesFora((atual) => alternar(atual, secao));
    },
    alternarColuna: (coluna: string) => {
      setColunasFora((atual) => alternar(atual, coluna));
    },
  };
}

export type SelecaoNaTela = ReturnType<typeof useSelecaoRelatorio>;
```

`hooks/usePreviaRelatorio.ts`:

```ts
import { useRef, useState } from 'react';
import { urlDaApi } from '../../../shared/api/cliente';
import { useValorAtrasado } from '../../../shared/lib/useValorAtrasado';
import { caminhoRelatorio, type SelecaoRelatorio } from '../api';

export const ATRASO_PREVIA_MS = 400;

export function usePreviaRelatorio(datasetId: string, selecao: SelecaoRelatorio | null) {
  // Prévia sempre offline: gráficos sem internet e impressão igual ao arquivo (decisão da Tarefa 10).
  const caminho = selecao === null ? null : caminhoRelatorio(datasetId, { ...selecao, offline: true });
  const caminhoAtrasado = useValorAtrasado(caminho, ATRASO_PREVIA_MS);
  const src = caminho === null || caminhoAtrasado === null ? null : urlDaApi(caminhoAtrasado);
  const ref = useRef<HTMLIFrameElement>(null);
  const [srcCarregado, setSrcCarregado] = useState<string | null>(null);
  const carregando = src !== null && srcCarregado !== src;

  return {
    src,
    ref,
    carregando,
    pronta: src !== null && !carregando,
    aoCarregar: () => {
      setSrcCarregado(src);
    },
    imprimir: () => {
      ref.current?.contentWindow?.print();
    },
  };
}
```

`hooks/useAcaoBaixar.ts`:

```ts
import { textoDoErro } from '../../../shared/api/erros';
import { useToast } from '../../../shared/ui/useToast';
import { caminhoRelatorio, nomeArquivoRelatorio, useBaixarRelatorio, type SelecaoRelatorio } from '../api';
import { TEXTOS_RELATORIO } from '../textos';

export function useAcaoBaixar(datasetId: string, nomeArquivo: string) {
  const { mostrar } = useToast();
  const baixar = useBaixarRelatorio();

  return {
    baixando: baixar.isPending,
    baixar: (selecao: SelecaoRelatorio, offline: boolean) => {
      const nome = nomeArquivoRelatorio(nomeArquivo);
      baixar.mutate(
        { caminho: caminhoRelatorio(datasetId, { ...selecao, offline }), nomeArquivo: nome },
        {
          onSuccess: () => {
            mostrar({ tipo: 'sucesso', titulo: TEXTOS_RELATORIO.baixado(nome) });
          },
          onError: (erro) => {
            const { mensagem, sugestao } = textoDoErro(erro);
            mostrar({ tipo: 'erro', titulo: mensagem, descricao: sugestao });
          },
        },
      );
    },
  };
}
```

`components/GrupoCaixas.tsx`:

```tsx
import type { ReactNode } from 'react';
import CaixaSelecao from '../../../shared/ui/CaixaSelecao';
import { TEXTOS_RELATORIO } from '../textos';
import estilos from './GrupoCaixas.module.css';

export interface ItemCaixa<T extends string> {
  id: T;
  rotulo: ReactNode;
}

interface Props<T extends string> {
  legenda: string;
  itens: readonly ItemCaixa<T>[];
  marcados: readonly T[];
  aoAlternar: (id: T) => void;
  desabilitado?: boolean;
  nota?: ReactNode;
}

export default function GrupoCaixas<T extends string>({
  legenda, itens, marcados, aoAlternar, desabilitado = false, nota = null,
}: Readonly<Props<T>>) {
  const conjuntoMarcados = new Set(marcados);

  return (
    <fieldset className={estilos.grupo} disabled={desabilitado}>
      <legend className={estilos.legenda}>
        <span className={estilos.titulo}>{legenda}</span>
        <span className={estilos.contador}>{TEXTOS_RELATORIO.contador(marcados.length, itens.length)}</span>
      </legend>
      {itens.map((item) => (
        <CaixaSelecao
          key={item.id}
          rotulo={item.rotulo}
          marcada={conjuntoMarcados.has(item.id)}
          aoMudar={() => {
            aoAlternar(item.id);
          }}
        />
      ))}
      {nota}
    </fieldset>
  );
}
```

`components/OpcoesRelatorio.tsx`:

```tsx
import ChipTipo from '../../../shared/ui/ChipTipo';
import CaixaSelecao from '../../../shared/ui/CaixaSelecao';
import EstadoCarregando from '../../../shared/ui/EstadoCarregando';
import type { components } from '../../../shared/api/schema';
import { SECOES_RELATORIO } from '../api';
import type { SelecaoNaTela } from '../hooks/useSelecaoRelatorio';
import { TEXTOS_RELATORIO } from '../textos';
import GrupoCaixas from './GrupoCaixas';
import estilos from './OpcoesRelatorio.module.css';

type TipoColuna = components['schemas']['TipoColuna'];

const T = TEXTOS_RELATORIO;
const ITENS_SECOES = SECOES_RELATORIO.map((id) => ({ id, rotulo: T.rotulosSecoes[id] }));
const NOTA_SEM_ANALISES = <p className={estilos.nota}>{T.colunasSemAnalises}</p>;

interface Props {
  colunas: readonly TipoColuna[] | undefined;
  selecao: SelecaoNaTela;
  offline: boolean;
  aoMudarOffline: (offline: boolean) => void;
}

export default function OpcoesRelatorio({ colunas, selecao, offline, aoMudarOffline }: Readonly<Props>) {
  const semAnalises = !selecao.secoes.includes('analises');
  const itensColunas = (colunas ?? []).map((coluna) => ({
    id: coluna.coluna,
    rotulo: (
      <span className={estilos.coluna}>
        <span className={estilos.nome}>{coluna.coluna}</span>
        <ChipTipo tipo={coluna.tipo} curto />
      </span>
    ),
  }));

  return (
    <div className={estilos.opcoes}>
      <GrupoCaixas legenda={T.secoes} itens={ITENS_SECOES} marcados={selecao.secoes} aoAlternar={selecao.alternarSecao} />
      {colunas === undefined ? (
        <EstadoCarregando forma="tabela" mensagem={T.carregandoColunas} />
      ) : (
        <GrupoCaixas
          legenda={T.colunas}
          itens={itensColunas}
          marcados={selecao.colunas}
          aoAlternar={selecao.alternarColuna}
          desabilitado={semAnalises}
          nota={semAnalises ? NOTA_SEM_ANALISES : null}
        />
      )}
      <div className={estilos.offline}>
        <CaixaSelecao rotulo={T.offline} marcada={offline} aoMudar={aoMudarOffline} />
        <p className={estilos.nota}>{T.offlineAjuda}</p>
      </div>
    </div>
  );
}
```

`components/PreviaRelatorio.tsx`:

```tsx
import { useId, type Ref } from 'react';
import EstadoCarregando from '../../../shared/ui/EstadoCarregando';
import EstadoVazio from '../../../shared/ui/EstadoVazio';
import { TEXTOS_RELATORIO } from '../textos';
import estilos from './PreviaRelatorio.module.css';

const T = TEXTOS_RELATORIO;

interface PropsPagina {
  src: string;
  ref: Ref<HTMLIFrameElement>;
  carregando: boolean;
  aoCarregar: () => void;
}

function PaginaPrevia({ src, ref, carregando, aoCarregar }: Readonly<PropsPagina>) {
  return (
    <div className={estilos.pagina} aria-busy={carregando}>
      <iframe ref={ref} src={src} title={T.tituloPrevia} className={estilos.iframe} onLoad={aoCarregar} />
      {carregando ? (
        <div className={estilos.cobertura}>
          <EstadoCarregando forma="grafico" mensagem={T.montando} />
        </div>
      ) : null}
    </div>
  );
}

interface Props extends Omit<PropsPagina, 'src'> {
  src: string | null;
}

export default function PreviaRelatorio({ src, ...resto }: Readonly<Props>) {
  const idCabecalho = useId();

  return (
    <section className={estilos.area} aria-labelledby={idCabecalho}>
      <p id={idCabecalho} className={estilos.cabecalho}>
        {T.previa}
      </p>
      {src === null ? (
        <EstadoVazio icone="description" titulo={T.vazio.titulo} descricao={T.vazio.descricao} />
      ) : (
        <PaginaPrevia src={src} {...resto} />
      )}
    </section>
  );
}
```

`PaginaRelatorio.tsx`:

```tsx
import { useState } from 'react';
import { useColunasAnalisaveis } from '../../shared/api/colunas';
import SemDataset from '../../shared/sessao/SemDataset';
import { useSessao } from '../../shared/sessao/useSessao';
import Botao from '../../shared/ui/Botao';
import EstadoErro from '../../shared/ui/EstadoErro';
import PaginaEtapa from '../../shared/ui/PaginaEtapa';
import OpcoesRelatorio from './components/OpcoesRelatorio';
import PreviaRelatorio from './components/PreviaRelatorio';
import { useAcaoBaixar } from './hooks/useAcaoBaixar';
import { usePreviaRelatorio } from './hooks/usePreviaRelatorio';
import { useSelecaoRelatorio } from './hooks/useSelecaoRelatorio';
import estilos from './PaginaRelatorio.module.css';
import { selecaoEfetiva } from './selecao';
import { TEXTOS_RELATORIO } from './textos';

const ETAPA_RELATORIO = 8;
const T = TEXTOS_RELATORIO;

interface Props {
  datasetId: string;
  nomeArquivo: string;
}

function RelatorioDoDataset({ datasetId, nomeArquivo }: Readonly<Props>) {
  const colunas = useColunasAnalisaveis(datasetId);
  const selecao = useSelecaoRelatorio((colunas.data ?? []).map((coluna) => coluna.coluna));
  const [offline, setOffline] = useState(true);
  const efetiva = selecaoEfetiva(selecao);
  const previa = usePreviaRelatorio(datasetId, efetiva);
  const download = useAcaoBaixar(datasetId, nomeArquivo);

  const acoes = (
    <>
      <Botao
        variante="secundario"
        tamanho="lg"
        icone="code"
        carregando={download.baixando}
        textoCarregando={T.baixando}
        disabled={efetiva === null}
        onClick={() => {
          if (efetiva !== null) download.baixar(efetiva, offline);
        }}
      >
        {T.baixar}
      </Botao>
      <Botao tamanho="lg" icone="print" disabled={!previa.pronta} onClick={previa.imprimir}>
        {T.imprimir}
      </Botao>
    </>
  );

  return (
    <PaginaEtapa etapa={ETAPA_RELATORIO} titulo={T.titulo} ajuda={T.ajuda} acoesTopo={acoes}>
      {colunas.isError ? (
        <EstadoErro
          erro={colunas.error}
          aoTentarDeNovo={() => {
            void colunas.refetch();
          }}
        />
      ) : (
        <div className={estilos.grade}>
          <OpcoesRelatorio colunas={colunas.data} selecao={selecao} offline={offline} aoMudarOffline={setOffline} />
          <PreviaRelatorio src={previa.src} ref={previa.ref} carregando={previa.carregando} aoCarregar={previa.aoCarregar} />
        </div>
      )}
    </PaginaEtapa>
  );
}

export default function PaginaRelatorio() {
  const { dataset } = useSessao();
  return dataset === null ? (
    <PaginaEtapa etapa={ETAPA_RELATORIO} titulo={T.titulo} ajuda={T.ajuda}>
      <SemDataset descricao={T.semDataset} />
    </PaginaEtapa>
  ) : (
    <RelatorioDoDataset datasetId={dataset.id} nomeArquivo={dataset.nomeArquivo} />
  );
}
```
(Se `RelatorioDoDataset` passar de 50 linhas com a formatação do Prettier, extraia as ações para `components/AcoesRelatorio.tsx` recebendo `{ baixando, desabilitado, prontaParaImprimir, aoBaixar, aoImprimir }`.)

Rota: o M1.1 já carrega `features/relatorio/PaginaRelatorio` com `lazy()` em `app/rotas.ts`; nada muda.

CSS (medidas de `Tela 8 Relatorio.dc.html`):

| Arquivo · seletor | Propriedades |
|---|---|
| `PaginaRelatorio.module.css` `.grade` | `display: grid; grid-template-columns: 300px minmax(0, 1fr); gap: var(--esp-24); align-items: start` |
| `OpcoesRelatorio.module.css` `.opcoes` | `display: flex; flex-direction: column; gap: var(--esp-16)` |
| `.coluna` | `display: flex; align-items: center; justify-content: space-between; gap: var(--esp-8); width: 100%` |
| `.nome` | `font: 13.5px var(--fonte-mono)` |
| `.offline` | `background: var(--cor-superficie); border: 1px solid var(--cor-borda); border-radius: var(--raio-lg); padding: 16px 20px` |
| `.nota` | `margin: var(--esp-4) 0 0; font-size: 13px; line-height: 1.45; color: var(--cor-texto-2)` |
| `GrupoCaixas.module.css` `.grupo` | `margin: 0; min-width: 0; background: var(--cor-superficie); border: 1px solid var(--cor-borda); border-radius: var(--raio-lg); padding: 16px 20px; display: flex; flex-direction: column; gap: var(--esp-4)` |
| `.legenda` | `float: left; width: 100%; padding: 0; margin-bottom: var(--esp-8); display: flex; justify-content: space-between; align-items: baseline` |
| `.titulo` | `font-size: 15px; font-weight: 600` · `.contador` `font-size: 13px; color: var(--cor-texto-2); font-variant-numeric: tabular-nums` |
| `.grupo:disabled` | `opacity: 1` (o `CaixaSelecao` já mostra o estado desabilitado com `--cor-texto-desab`) |
| `PreviaRelatorio.module.css` `.area` | `background: var(--cor-superficie-2); border: 1px solid var(--cor-borda); border-radius: var(--raio-lg); padding: var(--esp-24); display: flex; flex-direction: column; align-items: center; gap: var(--esp-12)` |
| `.cabecalho` | `margin: 0; width: 620px; max-width: 100%; font-size: 13px; color: var(--cor-texto-2)` |
| `.pagina` | `position: relative; width: 620px; max-width: 100%; aspect-ratio: 1 / 1.414; box-shadow: var(--sombra-2)` |
| `.iframe` | `display: block; width: 100%; height: 100%; border: 0; color-scheme: light` |
| `.cobertura` | `position: absolute; inset: 0; background: var(--cor-superficie); padding: 48px 52px` |

**Passo 4: rodar e ver passar** — `npm run test` (tudo) · `npm run lint` · `npm run build`.

**Passo 5: conferir no navegador:** prévia aparece em ~1 s; desmarcar seções/colunas atualiza; tema escuro na tela mantém a prévia clara; "Imprimir / salvar PDF" abre o diálogo de impressão só com o relatório; "Baixar HTML" salva `relatorio-pesquisa_saude.html`.

**Passo 6: commit**
```bash
git add frontend/src
git commit -m "feat(relatorio): tela Relatório com seções, colunas, prévia em iframe, download e impressão"
```

---

### Tarefa 12: Documentação

**Arquivos:** `CHANGELOG.md`, `docs/decisions.md`, `docs/specs/15-frontend.md`, `docs/specs/13-relatorio.md`

**Passo 1: `CHANGELOG.md`** › *Não lançado* › *Adicionado*:

```markdown
- Tela Análise univariada (etapa 4): seletor de coluna (na URL), abas Frequências, Tendência central, Separatrizes, Dispersão e Gráficos; abas e medidas que não se aplicam aparecem desabilitadas ou esmaecidas com o motivo; número de classes ajustável (3 a 30); "Onde está meu valor?" com régua das separatrizes; estados de carregando, vazio e erro.
- Tela Relatório (etapa 8): escolha de seções (leitura, tipos, limpeza, análises) e colunas, prévia em iframe sempre clara, "Baixar HTML" (com opção "Funciona sem internet") e "Imprimir / salvar PDF".
- Utilitários do frontend: `urlDaApi`/`requisitarBlob`, colunas analisáveis compartilhadas, `baixarArquivo`, `formatarDecimal`.
```

**Passo 2: `docs/decisions.md`** — estas decisões **não têm número fixo** (os blocos entram em ordens diferentes): cada uma recebe **Dnn (próximo número livre em `docs/decisions.md` na hora do commit)**. Acrescentar, uma linha cada:

| Decisão | Alternativas | Motivo |
|---|---|---|
| Coluna escolhida e nº de classes da tela 4 ficam na URL (`?coluna=&classes=`); aba ativa em estado local, com volta para Frequências quando a aba não se aplica | Estado local; `localStorage` | Sobrevive ao recarregar e ao Voltar; sem `useEffect` |
| Na contínua, o card "Moda" da aba Tendência mostra a moda bruta (com a classificação) e a moda de Czuber entra como apoio no "Ver fórmula" do mesmo card (**desvio a confirmar com o usuário antes do PR**) | Card só com Czuber; quarto card | Spec 05 pede moda bruta + Czuber e o print 4c mostra a moda bruta; sem prop nova no `CardMetrica` |
| Valores populacionais (σ, σ²) numa nota abaixo dos cards da Dispersão | Prop nova no `CardMetrica`; 2 cards a mais | Cumpre D18 sem mudar o design system |
| Resumo de 4 cards (Moda + Média, Mediana, Desvio padrão não aplicáveis) na aba Frequências quando `dispersao` é nulo | Só na aba Tendência | Design 4g; mostra logo por que as outras abas estão desabilitadas |
| Prévia do relatório sempre com `offline=true`; a caixa "Funciona sem internet" (marcada por padrão) vale só para o arquivo baixado | Prévia seguindo a caixa | Gráficos aparecem sem internet e o PDF impresso sai igual ao arquivo |
| "Baixar HTML" com `fetch` + `Blob` | `<a download href>` direto | Erro da API vira toast; nome do arquivo controlado; botão com "Gerando…" |
| Colunas analisáveis em `shared/api/colunas.ts`, filtradas sobre `opcoesColunas` do M1.6 (mesma chave `['datasets', id, 'colunas']`); análise e posição sob `chavesDataset.analises(id)` | Hook e chaves próprios em cada feature | Análise e Relatório usam a mesma lista e o mesmo cache; invalidação do M1.6 cobre análise e posição |

**Passo 3: specs**
- `15-frontend.md`, linha da tela 4: "abas: Frequências · Tendência · Separatrizes · Dispersão · Gráficos (Forma e distribuição entra no M2, D60); coluna escolhida na URL". Linha da tela 8: "Checklist de seções (no M1: leitura, tipos, limpeza, análises — D57) e colunas; prévia em iframe sempre clara (D47); 'Funciona sem internet' para o arquivo baixado".
- `13-relatorio.md` › Requisitos: "A prévia da tela usa sempre `offline=true`; o arquivo baixado segue a opção 'Funciona sem internet'."

**Passo 4: commit**
```bash
git add CHANGELOG.md docs/decisions.md docs/specs/13-relatorio.md docs/specs/15-frontend.md
git commit -m "docs: registra decisões e atualiza specs das telas Análise univariada e Relatório"
```

---

### Tarefa 13: Verificação final e teste manual

**Passo 1: qualidade (tudo verde)**
```bash
cd frontend && npm run lint && npm run format && npm run test && npm run build
cd .. && npx --yes jscpd@4 backend/app backend/tests frontend/src
```
O backend não muda neste bloco, mas rode a suíte dele uma vez (`cd backend && ruff check . && ruff format --check . && mypy app && complexipy app --max-complexity-allowed 15 && pytest`) para garantir que `develop` continua verde com os tipos regenerados.

**Passo 2: tipos da API em dia** — `cd backend && python scripts/exportar_openapi.py && cd ../frontend && npm run gerar:tipos && git diff --exit-code src/shared/api/schema.d.ts` (sem diferença; se houver, o M1.4/M1.5 mudou algo — commit do `schema.d.ts` e ajuste das fixtures).

**Passo 3: teste manual no preview** (`.claude/launch.json`: iniciar `backend` e `frontend`). Importar `dados-exemplo/pesquisa_saude.txt`, aplicar a limpeza sugerida e conferir:

| Coluna (tipo) | O que conferir |
|---|---|
| `peso_kg` (contínua) | 4b: classes "a ⊢ b", Sturges, − / + muda a tabela sem piscar, nota de h; 4c com a moda bruta (72) e, em "Ver fórmula", a moda de Czuber; 4a: digitar `75` → régua, frase e Q3 destacado; `120` → aviso "Fora da faixa observada."; 4d com selo do CV e nota σ/σ²; 4f com Histograma (recomendado), Boxplot, Ogiva |
| `idade` (discreta ou contínua, conforme D19) | tabela por valor (discreta) ou por classes; gráfico em bastões se discreta |
| `satisfacao` (ordinal) | acumulada presente; mediana como categoria; Separatrizes sem o painel "Onde está meu valor?" |
| `cidade` (nominal) | 4g: Separatrizes e Dispersão desabilitadas com tooltip; "Fr% acum." esmaecida com o motivo; 4 cards de resumo |
| `sexo` (binária) | card "Proporção"; Separatrizes desabilitada |

Também: tema claro e escuro (4i) em todas as abas; teclado: Tab até as abas, ←/→ entre elas (pulando as desabilitadas), Tab até o controle de classes e o campo do valor; recarregar a página mantém a coluna; trocar de coluna mostra o 4h. Relatório: desmarcar/remarcar seções e colunas, prévia sempre clara no tema escuro, imprimir para PDF, baixar com "Funciona sem internet" marcado, **desligar a rede e abrir o arquivo baixado**: gráficos aparecem. Baixar com a caixa desmarcada: arquivo menor.

**Passo 4:** anotar o resultado no corpo do PR (checklist acima marcado).

---

### Tarefa 14: PR para `develop` (só depois do ok do usuário)

Mostrar ao usuário o resumo do que foi feito e o resultado da Tarefa 13 e **esperar a confirmação** antes de publicar.

```bash
git push -u origin feat/frontend-univariada-relatorio
gh pr create --base develop --title "feat: telas Análise univariada e Relatório (M1.7)" --body "<resumo; specs 04–08, 13, 15, 16; decisões novas; checklist do padroes-codigo.md §8; resultado do teste manual>"
```
Sem linhas de coautoria ou atribuição de IA no corpo nem nos commits. Aguardar o CI (`backend`, `frontend`, `duplicacao`) verde e o merge.

---

### Tarefa 15: Critérios de pronto do M1 + **proposta** do release `v0.1.0`

> **Só com autorização explícita do usuário.** Esta tarefa não executa nada sozinha: confere, relata e propõe.

**Passo 1: conferir o checklist do professor (itens do M1 em `docs/roadmap.md`) com `develop` atualizada:**

- [ ] Lê TXT e analisa ao menos um conjunto (`pesquisa_saude.txt` de ponta a ponta: Importar → Variáveis → Limpeza → Análise → Relatório)
- [ ] Classifica tipo por coluna (tela 2, com motivo e correção manual)
- [ ] Frequências, tendências, separatrizes e dispersão (tela 4, abas correspondentes, "Onde está meu valor?")
- [ ] Gráficos básicos (melhor gráfico por tipo, spec 08)
- [ ] Mini relatório (tela 8: HTML baixado e PDF impresso)

E os critérios da visão geral: cobertura ≥ 80% em `dominios/` e `compartilhado/`; CI verde em todos os PRs do M1; telas 1–4 e 8 conferidas com `docs/design/telas.md` nos temas claro e escuro, com os estados carregando, vazio e erro.

**Passo 2: propor o release** (descrever ao usuário e esperar o "pode fazer"; `padroes-codigo.md` §8):

1. Branch `chore/release-v0.1.0` saindo de `develop`:
   - `CHANGELOG.md`: mover o conteúdo de *Não lançado* para `## [0.1.0] - AAAA-MM-DD` (data do merge) e deixar *Não lançado* vazio.
   - Versão `0.1.0` em `backend/app/core/config.py` (`versao: str = "0.1.0"`), `backend/pyproject.toml` (`version = "0.1.0"`) e `frontend/package.json` (`"version": "0.1.0"`, e `npm install --package-lock-only` para atualizar o lock).
   - Commit: `chore: prepara a versão 0.1.0`.
2. PR para `develop` (CI verde, merge).
3. PR de release `develop → main`: `gh pr create --base main --head develop --title "release: v0.1.0 (M1 — prévia completa)"`.
4. Depois do merge na `main`: `git tag -a v0.1.0 -m "v0.1.0 — prévia completa (M1)"` na `main` e `git push origin v0.1.0` (opcional: `gh release create v0.1.0 --notes-from-tag`).

Nada disso é feito sem a autorização explícita do usuário em chat.

---

## Critérios de pronto do M1.7

- [ ] Tela 4 confere com os prints 4a, 4b, 4c, 4d, 4f, 4g, 4h e 4i (sem a aba "Forma e distribuição", D60), nos temas claro e escuro
- [ ] Abas Separatrizes/Dispersão desabilitadas pelo `aplicavel` da API, com o motivo de `nao_aplicavel`; nenhuma regra de aplicabilidade no frontend
- [ ] Itens não aplicáveis esmaecidos com o motivo vindo do backend (D46)
- [ ] Nº de classes 3–30 com Sturges visível e tabela mantida durante o recálculo; coluna na URL
- [ ] "Onde está meu valor?" com debounce, régua acessível (`role="img"` + `aria-label`), frase em `aria-live`, aviso fora da faixa
- [ ] Tela 8 confere com o print 8a (seções do M1, D57): prévia em `iframe`, sempre clara, imprimir e baixar funcionando; arquivo baixado abre sem internet
- [ ] Estados carregando, vazio e erro nas duas telas; etapas 4 e 8 marcadas como visitadas
- [ ] Funções puras com testes (abas, colunas da tabela, cartões, régua, URL do relatório, seleção, estado da tela); componentes testados com a API simulada e fixtures tipadas pelo schema
- [ ] `npm run lint && npm run format && npm run test && npm run build` e `jscpd` verdes; nenhum `eslint-disable`
- [ ] CHANGELOG, `decisions.md` e specs 13/15 atualizados; PR mergeado em `develop`
