# M1.1 — Base visual do frontend: plano de implementação

> **Para o agente:** use a skill `executing-plans` (ou `subagent-driven-development`) para executar tarefa por tarefa. Antes de escrever código, leia `CLAUDE.md`, `docs/padroes-codigo.md` e a seção "Contratos do frontend" de `docs/plans/2026-10-03-m1-visao-geral.md`.

**Objetivo:** entregar a base visual que as telas do M1 (blocos M1.6 e M1.7) vão usar: fontes e ícones locais, tokens completos, tema claro/escuro, sessão do dataset, formatadores pt-BR, tratamento de erro da API, os componentes de `shared/ui` do contrato, o wrapper Plotly com tema e o layout (barra de etapas + cabeçalho + rotas com páginas provisórias).

**Arquitetura:** tudo em `frontend/src`. `shared/` ganha `lib/` (funções puras e hooks utilitários), `tema/`, `sessao/`, `ui/` (componentes com CSS Module cada um, sempre `var(--token)`) e `graficos/` (Plotly carregado com `React.lazy`). `app/` ganha `etapas.ts`, `textos.ts`, `layout/` e `paginas/`; as rotas saem de `ETAPAS`. Cada feature (`importar`, `variaveis`, `limpeza`, `analise`, `relatorio`) recebe só uma página provisória e seu `textos.ts`; M1.6 e M1.7 substituem as páginas. Nenhuma chamada nova à API neste bloco.

**Stack:** React 19, Vite 8, TypeScript ~5.9 strict, react-router 7, react-query 5, Vitest 5 + jsdom 29 + Testing Library, ESLint 9 (typescript-eslint strict-type-checked, sonarjs, jsx-a11y, react-hooks 7), Prettier, `react-plotly.js` 4 + `plotly.js-dist-min` 4, `@fontsource`.

**Branch:** `chore/frontend-base-visual` (sai de `develop`) → PR para `develop`.

**Prazo:** 10/10/2026 (o M1.6 depende deste bloco).

**Referências:** `docs/design/handoff.md`, `README.md`, `tokens.md`, `componentes.md`, `graficos-plotly.md`, ADR 0008, prints `docs/design/telas/prints/1a`, `1b`, `4h`, `4i`, `docs/specs/15-frontend.md`, `docs/specs/16-ux-writing.md`.

---

## Convenções deste plano (valem para todas as tarefas)

- Comandos rodam em `frontend/` (Git Bash). Um teste só: `npx vitest run src/caminho/arquivo.test.tsx`.
- **Antes de cada commit:** `npm run lint && npm run format && npm run test && npm run build` (se o Prettier reclamar, `npm run format:fix` e confira o diff).
- **Cores sempre por token** (`var(--cor-…)`, `var(--graf-…)`). Medidas usam token quando estão na grade (`--esp-4…64`, `--raio-*`); valores fora da grade (6, 10, 14, 18 px) vêm literais de `componentes.md`.
- **Props:** `interface` + `Readonly<Props…>` no parâmetro (regra `sonarjs/prefer-read-only-props`). Callbacks como **propriedade** (`aoMudar: (v: T) => void`), não como método, para não cair em `@typescript-eslint/unbound-method` ao desestruturar. É o mesmo contrato da visão geral, só com a sintaxe que o lint aceita.
- **`exactOptionalPropertyTypes`:** prop opcional que recebe valor possivelmente `undefined` de outro componente é declarada `prop?: T | undefined`.
- **Arrow functions que chamam algo `void`** usam chaves: `onClick={() => { aoMudar(v); }}` (`no-confusing-void-expression`). Promises ignoradas com `void` dentro de chaves.
- **Template strings com número:** `String(n)` (`restrict-template-expressions` do strict não aceita número).
- **Sem `&&` em JSX** (ternário com `null`), sem `as` fora de testes, sem `any`, sem `eslint-disable`, sem barrel files, 1 componente exportado por arquivo (subcomponentes internos não exportados podem ficar no mesmo arquivo).
- **Textos de interface** só em módulos de textos: `shared/ui/textos.ts` (genéricos), `app/textos.ts` (layout), `features/<etapa>/textos.ts`.
- **Testes** por papel e rótulo (Testing Library), nunca por classe CSS.
- **Commits** em Conventional Commits, português, **sem** `Co-Authored-By` nem qualquer atribuição de IA.
- Se uma regra de lint não prevista aqui reclamar (ex.: `sonarjs/function-return-type`, `sonarjs/slow-regex`), refatore seguindo `padroes-codigo.md` §1 e anote no PR; não silencie.

## Visão geral das tarefas

| # | Tarefa | Principais arquivos | Commit |
|---|---|---|---|
| 1 | Dependências e ambiente de teste (jsdom) | `package.json`, `vite.config.ts`, `eslint.config.js`, `src/testes/` | `chore(frontend)` |
| 2 | Fontes locais, tokens e estilos base | `shared/ui/tokens.css`, `base.css`, `main.tsx` | `feat(frontend)` |
| 3 | Utilitários: formatadores pt-BR, classes, consulta de mídia, tecla Esc | `shared/lib/` | `feat(frontend)` |
| 4 | Tema claro/escuro | `shared/tema/` | `feat(frontend)` |
| 5 | Sessão do dataset | `shared/sessao/` | `feat(frontend)` |
| 6 | Erros da API e textos fixos | `shared/api/erros.ts`, `shared/ui/textos.ts` | `feat(frontend)` |
| 7 | Ícone e Botão | `shared/ui/Icone`, `Botao` | `feat(frontend)` |
| 8 | Card, Banner e estados | `Card`, `Banner`, `EstadoCarregando`, `EstadoVazio`, `EstadoErro` | `feat(frontend)` |
| 9 | Tooltip | `Tooltip` | `feat(frontend)` |
| 10 | Toast | `ToastProvider`, `ItemToast`, `useToast` | `feat(frontend)` |
| 11 | Campos | `Select`, `CampoNumero`, `CaixaSelecao`, `MensagemCampo` | `feat(frontend)` |
| 12 | Navegação por setas | `useNavegacaoPorSetas`, `Segmented`, `Abas` | `feat(frontend)` |
| 13 | Dados | `CardMetrica`, `Tabela` | `feat(frontend)` |
| 14 | Wrapper Plotly | `shared/graficos/` | `feat(frontend)` |
| 15 | Etapas, PaginaEtapa e páginas provisórias | `app/etapas.ts`, `app/textos.ts`, `PaginaEtapa`, `features/*/Pagina*.tsx` | `feat(frontend)` |
| 16 | Barra de etapas | `app/layout/estadoEtapa.ts`, `ItemEtapa`, `BarraEtapas` | `feat(frontend)` |
| 17 | Cabeçalho e alternância de tema | `app/layout/Cabecalho`, `AlternanciaTema` | `feat(frontend)` |
| 18 | LayoutApp, sessão expirada, rotas e providers | `LayoutApp`, `useSessaoExpirada`, `rotas.ts`, `App.tsx`; remove `features/inicio` | `feat(frontend)` |
| 19 | Docs, verificação final, teste manual e PR | `CHANGELOG.md`, `docs/decisions.md`, `docs/specs/15-frontend.md` | `docs` |

Estrutura final de `frontend/src`:
```
app/        App.tsx · etapas.ts · textos.ts · rotas.ts · roteador.ts · layout/ · paginas/
features/   importar · variaveis · limpeza · analise · relatorio   (Pagina*.tsx provisória + textos.ts)
shared/api/ cliente.ts · erros.ts · schema.d.ts
shared/lib/ formatar.ts · classes.ts · useConsultaMidia.ts · useTeclaEsc.ts
shared/tema/ · shared/sessao/ · shared/ui/ · shared/graficos/
testes/     configuracao.ts · matchMedia.ts · renderizar.tsx
```

---

### Tarefa 1: Dependências e ambiente de teste

**Arquivos:**
- Modificar: `frontend/package.json`, `frontend/package-lock.json` (via npm)
- Modificar: `frontend/vite.config.ts`, `frontend/eslint.config.js`
- Criar: `frontend/src/testes/configuracao.ts`, `frontend/src/testes/matchMedia.ts`

**Passo 1: instalar**
```bash
cd frontend
npm install @fontsource/inter@^5 @fontsource/jetbrains-mono@^5 @fontsource-variable/material-symbols-rounded@^5 react-plotly.js@^4 plotly.js-dist-min@^4
npm install -D jsdom@^29 @testing-library/react@^16 @testing-library/user-event@^14 @testing-library/jest-dom@^7
```
- **jsdom 29, não 30:** o jsdom 30 exige Node ≥ 22.22.2; a máquina local tem 22.14 e o 29 aceita `^22.13`.
- **Não** atualizar `typescript` (~5.9) nem `eslint` (^9) (D41). Confira com `git diff package.json`: só entradas novas.
- `@types/plotly.js-dist-min` **não** é necessário: `plotly.js-dist-min` 4 traz `lib/index.d.ts` e `react-plotly.js` 4 tipa `data`/`layout`/`config` como `unknown`.

**Passo 2: conferir dependências de par (peer)**
```bash
npm ls @testing-library/dom plotly.js
```
Esperado:
- `@testing-library/dom@10.x` instalado automaticamente pelo npm (é peer obrigatório de `@testing-library/react`, `user-event` e `jest-dom`). Se aparecer `UNMET PEER`, rode `npm install -D @testing-library/dom@^10` e registre no PR.
- `plotly.js` instalado como peer de `react-plotly.js` (o npm ≥ 7 instala peers). Ele **não entra no bundle**: só importamos `react-plotly.js/factory` e `plotly.js-dist-min` (confira na Tarefa 19). Não use `--legacy-peer-deps`.

**Passo 3: `vite.config.ts`**
```ts
import react from '@vitejs/plugin-react';
import { defineConfig } from 'vitest/config';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: { '/api': 'http://localhost:8000' },
  },
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/testes/configuracao.ts'],
    restoreMocks: true,
  },
});
```

**Passo 4: `src/testes/matchMedia.ts`** (o jsdom não implementa `matchMedia`)
```ts
import { vi } from 'vitest';

/** Simula window.matchMedia: só as consultas listadas correspondem. */
export function simularMatchMedia(consultasVerdadeiras: readonly string[] = []): void {
  vi.stubGlobal('matchMedia', (consulta: string) => ({
    matches: consultasVerdadeiras.includes(consulta),
    media: consulta,
    onchange: null,
    addEventListener: () => undefined,
    removeEventListener: () => undefined,
    addListener: () => undefined,
    removeListener: () => undefined,
    dispatchEvent: () => false,
  }));
}
```

**Passo 5: `src/testes/configuracao.ts`**
```ts
import '@testing-library/jest-dom/vitest';
import { cleanup } from '@testing-library/react';
import { afterEach, beforeEach, vi } from 'vitest';
import { simularMatchMedia } from './matchMedia';

beforeEach(() => {
  simularMatchMedia();
});

afterEach(() => {
  // Sem `globals: true` o Testing Library não limpa sozinho.
  cleanup();
  vi.unstubAllGlobals();
  vi.useRealTimers();
  localStorage.clear();
  document.documentElement.removeAttribute('data-tema');
  document.title = '';
});
```

**Passo 6: `eslint.config.js`** — trocar o bloco de override dos testes por:
```js
  {
    files: ['**/*.test.{ts,tsx}', 'src/testes/**'],
    rules: {
      'max-lines-per-function': 'off',
      'react-refresh/only-export-components': 'off',
    },
  },
```

**Passo 7: conferir**
```bash
npm run test
```
Esperado: `5 passed` (os testes de `shared/api/cliente.test.ts` continuam passando no jsdom: `fetch` e `Response` do Node seguem disponíveis porque o jsdom não os define).
`npm run lint && npm run format && npm run build` → verdes.

**Passo 8: commit**
```bash
git add frontend/package.json frontend/package-lock.json frontend/vite.config.ts frontend/eslint.config.js frontend/src/testes
git commit -m "chore(frontend): adiciona fontes locais, Plotly e Testing Library com jsdom"
```

---

### Tarefa 2: Fontes locais, tokens e estilos base

Sem teste unitário útil para CSS: a verificação é por build e preview.

**Arquivos:**
- Modificar: `frontend/src/shared/ui/tokens.css`
- Criar: `frontend/src/shared/ui/base.css`
- Modificar: `frontend/src/main.tsx`

**Passo 1: `tokens.css`**
1. Apagar as duas linhas `@import url('https://fonts.googleapis.com/…')` do topo.
2. Logo abaixo do comentário de cabeçalho, acrescentar um bloco `:root` com os tokens que não mudam com o tema:
```css
:root {
  --fonte-texto: 'Inter', system-ui, sans-serif;
  --fonte-mono: 'JetBrains Mono', ui-monospace, monospace;
  --fonte-icones: 'Material Symbols Rounded Variable';

  --esp-4: 4px;
  --esp-8: 8px;
  --esp-12: 12px;
  --esp-16: 16px;
  --esp-20: 20px;
  --esp-24: 24px;
  --esp-32: 32px;
  --esp-48: 48px;
  --esp-64: 64px;

  --raio-xs: 4px;
  --raio-sm: 6px;
  --raio-md: 8px;
  --raio-lg: 12px;
  --raio-pilula: 999px;

  --transicao: 120ms ease;

  --largura-barra: 264px;
  --largura-barra-recolhida: 72px;
  --altura-cabecalho: 64px;
  --largura-conteudo: 1176px;
}
```
3. No bloco `:root, [data-tema='claro']` acrescentar `color-scheme: light;` e no bloco `[data-tema='escuro']` acrescentar `color-scheme: dark;` (controles nativos, como a lista do `<select>`, seguem o tema).

Confira o nome da família do Material Symbols em `node_modules/@fontsource-variable/material-symbols-rounded/full.css` (`font-family: 'Material Symbols Rounded Variable'`). Se for outro, ajuste `--fonte-icones`.

**Passo 2: `shared/ui/base.css`**
```css
/* Reset mínimo e estilos globais. Componentes usam CSS Modules. */
*,
*::before,
*::after {
  box-sizing: border-box;
}

html {
  -webkit-text-size-adjust: 100%;
}

body {
  margin: 0;
  min-height: 100vh;
  background: var(--cor-fundo);
  color: var(--cor-texto);
  font-family: var(--fonte-texto);
  font-size: 15px;
  line-height: 1.55;
  -webkit-font-smoothing: antialiased;
}

h1,
h2,
h3,
h4,
p,
figure {
  margin: 0;
}

ol,
ul {
  margin: 0;
  padding: 0;
}

button,
input,
select,
textarea {
  font: inherit;
  color: inherit;
}

a {
  color: var(--cor-primaria);
}

code,
kbd,
samp {
  font-family: var(--fonte-mono);
}

:focus-visible {
  outline: 2px solid var(--cor-foco);
  outline-offset: 2px;
}

.visualmente-oculto {
  position: absolute;
  width: 1px;
  height: 1px;
  margin: -1px;
  padding: 0;
  overflow: hidden;
  clip: rect(0 0 0 0);
  white-space: nowrap;
  border: 0;
}

@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```
A classe do ícone (com `font-variation-settings`) fica em `Icone.module.css` (Tarefa 7), seguindo o ADR 0008 (CSS Module por componente).

**Passo 3: `main.tsx`** — acrescentar no topo, antes dos imports de React:
```tsx
import '@fontsource/inter/400.css';
import '@fontsource/inter/500.css';
import '@fontsource/inter/600.css';
import '@fontsource/inter/700.css';
import '@fontsource/jetbrains-mono/400.css';
import '@fontsource/jetbrains-mono/500.css';
import '@fontsource/jetbrains-mono/600.css';
import '@fontsource-variable/material-symbols-rounded/full.css';
import './shared/ui/tokens.css';
import './shared/ui/base.css';
```
`full.css` traz todos os eixos variáveis (FILL, wght, GRAD, opsz): o eixo FILL é necessário para os ícones preenchidos (toast, banner, severidade).

**Passo 4: conferir**
```bash
npm run build
ls dist/assets | grep -c woff2      # > 0: fontes empacotadas localmente
grep -rl "fonts.googleapis" dist || echo "sem Google Fonts"
```
Esperado: contagem maior que zero e "sem Google Fonts".

**Passo 5: commit**
```bash
git add frontend/src/shared/ui/tokens.css frontend/src/shared/ui/base.css frontend/src/main.tsx
git commit -m "feat(frontend): serve fontes e ícones localmente e completa os tokens de espaço e raio"
```

---

### Tarefa 3: Utilitários — formatadores pt-BR, classes, consulta de mídia, tecla Esc

**Arquivos:**
- Criar: `frontend/src/shared/lib/formatar.ts` + `formatar.test.ts`
- Criar: `frontend/src/shared/lib/classes.ts` + `classes.test.ts`
- Criar: `frontend/src/shared/lib/useConsultaMidia.ts` + `useConsultaMidia.test.ts`
- Criar: `frontend/src/shared/lib/useTeclaEsc.ts` + `useTeclaEsc.test.ts`

**Passo 1: escrever os testes (falham)**

`formatar.test.ts`
```ts
import { describe, expect, it } from 'vitest';
import { formatarInteiro, formatarNumero, formatarPercentual, lerNumeroPtBr } from './formatar';

describe('formatarNumero', () => {
  it.each([
    [70.314, '70,31'],
    [12345.6, '12.346'],
    [0.0012346, '0,001235'],
    [0, '0'],
    [-3.14159, '-3,142'],
    [69.8, '69,8'],
    [1.72, '1,72'],
    [999.95, '1.000'],
  ])('formata %s como %s', (valor, esperado) => {
    expect(formatarNumero(valor)).toBe(esperado);
  });

  it('aceita outro número de casas significativas', () => {
    expect(formatarNumero(70.314, 2)).toBe('70');
  });

  it('usa travessão para valores não finitos', () => {
    expect(formatarNumero(Number.NaN)).toBe('—');
    expect(formatarNumero(Number.POSITIVE_INFINITY)).toBe('—');
  });
});

describe('formatarInteiro', () => {
  it.each([
    [1234, '1.234'],
    [1234567, '1.234.567'],
    [12.6, '13'],
  ])('formata %s como %s', (valor, esperado) => {
    expect(formatarInteiro(valor)).toBe(esperado);
  });
});

describe('formatarPercentual', () => {
  it.each([
    [21.6, 1, '21,6%'],
    [21.66, 1, '21,7%'],
    [100, 1, '100%'],
    [33.333, 2, '33,33%'],
    [-0.04, 1, '0%'],
  ])('formata %s com %s casas como %s', (valor, casas, esperado) => {
    expect(formatarPercentual(valor, casas)).toBe(esperado);
  });
});

describe('lerNumeroPtBr', () => {
  it.each([
    ['1,72', 1.72],
    ['1.234,5', 1234.5],
    ['1.234.567,89', 1234567.89],
    ['-3', -3],
    [' 7 ', 7],
    ['+2,5', 2.5],
    ['1.234', 1234],
    ['1.72', 1.72],
  ])('lê "%s" como %s', (texto, esperado) => {
    expect(lerNumeroPtBr(texto)).toBe(esperado);
  });

  it.each(['', '   ', 'abc', '1,2,3', '1.23.4', '12a', ',5'])('devolve null para "%s"', (texto) => {
    expect(lerNumeroPtBr(texto)).toBeNull();
  });
});
```

`classes.test.ts`
```ts
import { expect, it } from 'vitest';
import { juntarClasses } from './classes';

it('junta só as classes preenchidas', () => {
  expect(juntarClasses('a', false, undefined, null, '', 'b')).toBe('a b');
});
```

`useConsultaMidia.test.ts`
```ts
import { renderHook } from '@testing-library/react';
import { expect, it } from 'vitest';
import { simularMatchMedia } from '../../testes/matchMedia';
import { useConsultaMidia } from './useConsultaMidia';

it('diz se a consulta de mídia corresponde', () => {
  simularMatchMedia(['(min-width: 1280px)']);

  expect(renderHook(() => useConsultaMidia('(min-width: 1280px)')).result.current).toBe(true);
  expect(renderHook(() => useConsultaMidia('(max-width: 600px)')).result.current).toBe(false);
});
```

`useTeclaEsc.test.ts`
```ts
import { renderHook } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { expect, it, vi } from 'vitest';
import { useTeclaEsc } from './useTeclaEsc';

it('chama o callback no Esc só quando está ativo', async () => {
  const aoPressionar = vi.fn();
  const { rerender } = renderHook(({ ativo }) => { useTeclaEsc(ativo, aoPressionar); }, {
    initialProps: { ativo: false },
  });

  await userEvent.keyboard('{Escape}');
  expect(aoPressionar).not.toHaveBeenCalled();

  rerender({ ativo: true });
  await userEvent.keyboard('{Escape}');
  expect(aoPressionar).toHaveBeenCalledOnce();
});
```

**Passo 2: rodar e ver falhar**
`npx vitest run src/shared/lib` → FAIL (`Failed to resolve import "./formatar"` etc.)

**Passo 3: implementar**

`formatar.ts`
```ts
/**
 * Formatadores pt-BR. A regra de casas decimais é a mesma de
 * backend/app/compartilhado/numeros.py (M1.2): mesmos números na tela e no relatório.
 */

const LOCALE = 'pt-BR';
const VALOR_AUSENTE = '—';
const PADRAO_PT_BR = /^[+-]?(?:\d{1,3}(?:\.\d{3})+|\d+)(?:,\d+)?$/;
const PADRAO_PONTO_DECIMAL = /^[+-]?\d+\.\d+$/;

function formatador(casas: number): Intl.NumberFormat {
  // signDisplay 'negative' evita "-0" quando o arredondamento zera um negativo.
  return new Intl.NumberFormat(LOCALE, { maximumFractionDigits: casas, signDisplay: 'negative' });
}

/** Casas decimais para mostrar `casasSignificativas` algarismos: max(0, cs − 1 − ⌊log10 |v|⌋). */
export function casasDecimais(valor: number, casasSignificativas: number): number {
  if (valor === 0) return 0;
  return Math.max(0, casasSignificativas - 1 - Math.floor(Math.log10(Math.abs(valor))));
}

/** 70.314 → "70,31"; 12345.6 → "12.346"; 0.0012346 → "0,001235" (sem zeros à direita). */
export function formatarNumero(valor: number, casasSignificativas = 4): string {
  if (!Number.isFinite(valor)) return VALOR_AUSENTE;
  return formatador(casasDecimais(valor, casasSignificativas)).format(valor);
}

/** 1234 → "1.234". */
export function formatarInteiro(valor: number): string {
  return Number.isFinite(valor) ? formatador(0).format(valor) : VALOR_AUSENTE;
}

/** Recebe o percentual já em 0–100: 21.6 → "21,6%". */
export function formatarPercentual(valor: number, casas = 1): string {
  return Number.isFinite(valor) ? `${formatador(casas).format(valor)}%` : VALOR_AUSENTE;
}

/**
 * Lê um número digitado em pt-BR ("1.234,5", "1,72", "-3").
 * Sem vírgula e com ponto fora do padrão de milhar ("1.72"), o ponto vale como decimal.
 */
export function lerNumeroPtBr(texto: string): number | null {
  const limpo = texto.trim();
  if (PADRAO_PT_BR.test(limpo)) return Number(limpo.replaceAll('.', '').replace(',', '.'));
  return PADRAO_PONTO_DECIMAL.test(limpo) ? Number(limpo) : null;
}
```

`classes.ts`
```ts
export type ClasseOpcional = string | false | null | undefined;

/** Classe global de base.css: esconde da tela e mantém para leitores de tela. */
export const VISUALMENTE_OCULTO = 'visualmente-oculto';

export function juntarClasses(...classes: readonly ClasseOpcional[]): string {
  return classes.filter((classe): classe is string => typeof classe === 'string' && classe !== '').join(' ');
}
```

`useConsultaMidia.ts`
```ts
import { useCallback, useSyncExternalStore } from 'react';

/** Acompanha uma media query (ex.: '(min-width: 1280px)'). */
export function useConsultaMidia(consulta: string): boolean {
  const assinar = useCallback(
    (aoMudar: () => void) => {
      const lista = window.matchMedia(consulta);
      lista.addEventListener('change', aoMudar);
      return () => {
        lista.removeEventListener('change', aoMudar);
      };
    },
    [consulta],
  );
  return useSyncExternalStore(assinar, () => window.matchMedia(consulta).matches);
}
```

`useTeclaEsc.ts`
```ts
import { useEffect } from 'react';

/** Escuta Esc no documento enquanto `ativo`. `aoPressionar` deve ser estável (useCallback). */
export function useTeclaEsc(ativo: boolean, aoPressionar: () => void): void {
  useEffect(() => {
    if (!ativo) return undefined;
    const aoTeclar = (evento: KeyboardEvent): void => {
      if (evento.key === 'Escape') aoPressionar();
    };
    document.addEventListener('keydown', aoTeclar);
    return () => {
      document.removeEventListener('keydown', aoTeclar);
    };
  }, [ativo, aoPressionar]);
}
```

**Passo 4: rodar e ver passar**
`npx vitest run src/shared/lib` → todos passam. `npm run lint` → sem erros.

**Passo 5: commit**
```bash
git add frontend/src/shared/lib
git commit -m "feat(frontend): adiciona formatadores pt-BR e utilitários de classe, mídia e Esc"
```

---

### Tarefa 4: Tema claro/escuro

**Arquivos:**
- Criar: `frontend/src/shared/tema/tipos.ts`, `preferencia.ts` (+ `preferencia.test.ts`), `contextoTema.ts`, `TemaProvider.tsx` (+ `TemaProvider.test.tsx`), `useTema.ts`
- Modificar: `frontend/src/main.tsx`

**Passo 1: escrever os testes (falham)**

`preferencia.test.ts`
```ts
import { describe, expect, it, vi } from 'vitest';
import { simularMatchMedia } from '../../testes/matchMedia';
import { aplicarTemaInicial, salvarTema } from './preferencia';

describe('aplicarTemaInicial', () => {
  it('usa o tema salvo e marca o <html>', () => {
    localStorage.setItem('tema', 'escuro');

    expect(aplicarTemaInicial()).toBe('escuro');
    expect(document.documentElement).toHaveAttribute('data-tema', 'escuro');
  });

  it('segue o sistema quando não há tema salvo', () => {
    simularMatchMedia(['(prefers-color-scheme: dark)']);

    expect(aplicarTemaInicial()).toBe('escuro');
  });

  it('ignora valor inválido salvo', () => {
    localStorage.setItem('tema', 'roxo');

    expect(aplicarTemaInicial()).toBe('claro');
  });

  it('funciona com o localStorage bloqueado', () => {
    vi.spyOn(Storage.prototype, 'getItem').mockImplementation(() => {
      throw new Error('bloqueado');
    });

    expect(aplicarTemaInicial()).toBe('claro');
  });
});

describe('salvarTema', () => {
  it('salva e devolve true', () => {
    expect(salvarTema('escuro')).toBe(true);
    expect(localStorage.getItem('tema')).toBe('escuro');
  });

  it('devolve false quando não consegue salvar', () => {
    vi.spyOn(Storage.prototype, 'setItem').mockImplementation(() => {
      throw new Error('cheio');
    });

    expect(salvarTema('escuro')).toBe(false);
  });
});
```

`TemaProvider.test.tsx`
```tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { expect, it } from 'vitest';
import TemaProvider from './TemaProvider';
import { useTema } from './useTema';

function Alternador() {
  const { tema, definirTema } = useTema();
  return (
    <button
      type="button"
      onClick={() => {
        definirTema(tema === 'claro' ? 'escuro' : 'claro');
      }}
    >
      {tema}
    </button>
  );
}

it('começa no tema já aplicado ao documento', () => {
  document.documentElement.dataset.tema = 'escuro';

  render(
    <TemaProvider>
      <Alternador />
    </TemaProvider>,
  );

  expect(screen.getByRole('button')).toHaveTextContent('escuro');
});

it('troca o tema, aplica no <html> e salva a escolha', async () => {
  render(
    <TemaProvider>
      <Alternador />
    </TemaProvider>,
  );

  await userEvent.click(screen.getByRole('button', { name: 'claro' }));

  expect(screen.getByRole('button')).toHaveTextContent('escuro');
  expect(document.documentElement).toHaveAttribute('data-tema', 'escuro');
  expect(localStorage.getItem('tema')).toBe('escuro');
});
```

**Passo 2: rodar e ver falhar**
`npx vitest run src/shared/tema` → FAIL (módulos não existem)

**Passo 3: implementar**

`tipos.ts`
```ts
export type Tema = 'claro' | 'escuro';

export interface ValorTema {
  tema: Tema;
  definirTema: (tema: Tema) => void;
}
```

`preferencia.ts`
```ts
import type { Tema } from './tipos';

const CHAVE_TEMA = 'tema';
const CONSULTA_ESCURO = '(prefers-color-scheme: dark)';

export function ehTema(valor: unknown): valor is Tema {
  return valor === 'claro' || valor === 'escuro';
}

export function lerTemaSalvo(): Tema | null {
  try {
    const salvo = localStorage.getItem(CHAVE_TEMA);
    return ehTema(salvo) ? salvo : null;
  } catch {
    // Armazenamento bloqueado (modo privado, política do navegador): segue o sistema.
    return null;
  }
}

/** Devolve false se o navegador não deixou salvar; a escolha vale só nesta visita. */
export function salvarTema(tema: Tema): boolean {
  try {
    localStorage.setItem(CHAVE_TEMA, tema);
    return true;
  } catch {
    return false;
  }
}

export function temaDoSistema(): Tema {
  return window.matchMedia(CONSULTA_ESCURO).matches ? 'escuro' : 'claro';
}

export function temaDoDocumento(): Tema | null {
  const atual = document.documentElement.dataset.tema;
  return ehTema(atual) ? atual : null;
}

export function aplicarTema(tema: Tema): void {
  document.documentElement.dataset.tema = tema;
}

/** Chamado em main.tsx antes do render: a primeira pintura já sai no tema certo. */
export function aplicarTemaInicial(): Tema {
  const tema = lerTemaSalvo() ?? temaDoSistema();
  aplicarTema(tema);
  return tema;
}
```

`contextoTema.ts`
```ts
import { createContext } from 'react';
import type { ValorTema } from './tipos';

export const ContextoTema = createContext<ValorTema | null>(null);
```

`useTema.ts`
```ts
import { useContext } from 'react';
import { ContextoTema } from './contextoTema';
import type { ValorTema } from './tipos';

export function useTema(): ValorTema {
  const valor = useContext(ContextoTema);
  if (valor === null) throw new Error('useTema precisa estar dentro de <TemaProvider>.');
  return valor;
}
```

`TemaProvider.tsx`
```tsx
import { type ReactNode, useCallback, useMemo, useState } from 'react';
import { ContextoTema } from './contextoTema';
import { aplicarTema, aplicarTemaInicial, salvarTema, temaDoDocumento } from './preferencia';
import type { Tema } from './tipos';

interface PropsTemaProvider {
  children: ReactNode;
}

export default function TemaProvider({ children }: Readonly<PropsTemaProvider>) {
  const [tema, setTema] = useState<Tema>(() => temaDoDocumento() ?? aplicarTemaInicial());

  const definirTema = useCallback((novo: Tema) => {
    // Aplica no <html> antes do render: quem lê tokens (Grafico) já vê o tema novo.
    aplicarTema(novo);
    salvarTema(novo);
    setTema(novo);
  }, []);

  const valor = useMemo(() => ({ tema, definirTema }), [tema, definirTema]);

  return <ContextoTema value={valor}>{children}</ContextoTema>;
}
```

`main.tsx` — acrescentar o import e a chamada antes de `createRoot`:
```tsx
import { aplicarTemaInicial } from './shared/tema/preferencia';

aplicarTemaInicial();
```

**Passo 4: rodar e ver passar**
`npx vitest run src/shared/tema` → 8 passed. `npm run lint` → sem erros.

**Passo 5: commit**
```bash
git add frontend/src/shared/tema frontend/src/main.tsx
git commit -m "feat(frontend): adiciona tema claro/escuro com preferência salva e padrão do sistema"
```

---

### Tarefa 5: Sessão do dataset (D61)

**Arquivos:**
- Criar: `frontend/src/shared/sessao/tipos.ts`, `persistencia.ts` (+ `persistencia.test.ts`), `contextoSessao.ts`, `SessaoProvider.tsx` (+ `SessaoProvider.test.tsx`), `useSessao.ts`

Regras: a sessão guarda `{ dataset: { id, nomeArquivo } | null, etapasVisitadas: number[] }` em `localStorage('sessao')`. O JSON lido é validado por narrowing (sem `as`); qualquer coisa fora do formato vira sessão vazia. Trocar de dataset zera as etapas visitadas (a `PaginaEtapa` remarca a etapa atual, Tarefa 15).

**Passo 1: escrever os testes (falham)**

`persistencia.test.ts`
```ts
import { describe, expect, it, vi } from 'vitest';
import { SESSAO_VAZIA, carregarSessao, comEtapaVisitada, interpretarSessao } from './persistencia';

const DATASET = { id: 'd1', nomeArquivo: 'pesquisa_saude.txt' };

describe('interpretarSessao', () => {
  it.each([null, 'não é json', '[]', '{"dataset":{"id":"d1"}}', '{"dataset":null}'])(
    'devolve sessão vazia para %s',
    (texto) => {
      expect(interpretarSessao(texto)).toEqual(SESSAO_VAZIA);
    },
  );

  it('lê o dataset e só as etapas inteiras', () => {
    const texto = JSON.stringify({ dataset: DATASET, etapasVisitadas: [1, '2', 3.5, 4] });

    expect(interpretarSessao(texto)).toEqual({ dataset: DATASET, etapasVisitadas: [1, 4] });
  });

  it('descarta campos extras do dataset', () => {
    const texto = JSON.stringify({ dataset: { ...DATASET, senha: 'x' }, etapasVisitadas: 'x' });

    expect(interpretarSessao(texto)).toEqual({ dataset: DATASET, etapasVisitadas: [] });
  });
});

describe('comEtapaVisitada', () => {
  it('acrescenta sem repetir', () => {
    const uma = comEtapaVisitada({ dataset: DATASET, etapasVisitadas: [] }, 2);

    expect(comEtapaVisitada(uma, 2)).toBe(uma);
    expect(uma.etapasVisitadas).toEqual([2]);
  });
});

describe('carregarSessao', () => {
  it('devolve sessão vazia com o localStorage bloqueado', () => {
    vi.spyOn(Storage.prototype, 'getItem').mockImplementation(() => {
      throw new Error('bloqueado');
    });

    expect(carregarSessao()).toEqual(SESSAO_VAZIA);
  });
});
```

`SessaoProvider.test.tsx`
```tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { expect, it } from 'vitest';
import SessaoProvider from './SessaoProvider';
import { useSessao } from './useSessao';

function Painel() {
  const { dataset, definirDataset, encerrar, etapasVisitadas, marcarVisitada } = useSessao();
  return (
    <div>
      <p>{dataset ? dataset.nomeArquivo : 'sem arquivo'}</p>
      <p>visitadas: {[...etapasVisitadas].join(',')}</p>
      <button
        type="button"
        onClick={() => {
          definirDataset({ id: 'd2', nomeArquivo: 'notas_turma.csv' });
        }}
      >
        importar
      </button>
      <button
        type="button"
        onClick={() => {
          marcarVisitada(3);
        }}
      >
        visitar 3
      </button>
      <button type="button" onClick={encerrar}>
        encerrar
      </button>
    </div>
  );
}

function renderizar() {
  render(
    <SessaoProvider>
      <Painel />
    </SessaoProvider>,
  );
}

function sessaoSalva(): unknown {
  return JSON.parse(localStorage.getItem('sessao') ?? 'null');
}

it('começa vazia', () => {
  renderizar();

  expect(screen.getByText('sem arquivo')).toBeInTheDocument();
});

it('restaura a sessão salva', () => {
  localStorage.setItem(
    'sessao',
    JSON.stringify({ dataset: { id: 'd1', nomeArquivo: 'pesquisa_saude.txt' }, etapasVisitadas: [1, 2] }),
  );

  renderizar();

  expect(screen.getByText('pesquisa_saude.txt')).toBeInTheDocument();
  expect(screen.getByText('visitadas: 1,2')).toBeInTheDocument();
});

it('trocar de dataset zera as etapas visitadas e salva', async () => {
  localStorage.setItem(
    'sessao',
    JSON.stringify({ dataset: { id: 'd1', nomeArquivo: 'pesquisa_saude.txt' }, etapasVisitadas: [1, 2] }),
  );
  renderizar();

  await userEvent.click(screen.getByRole('button', { name: 'importar' }));
  await userEvent.click(screen.getByRole('button', { name: 'visitar 3' }));

  expect(screen.getByText('notas_turma.csv')).toBeInTheDocument();
  expect(sessaoSalva()).toEqual({
    dataset: { id: 'd2', nomeArquivo: 'notas_turma.csv' },
    etapasVisitadas: [3],
  });
});

it('encerrar limpa a sessão', async () => {
  renderizar();
  await userEvent.click(screen.getByRole('button', { name: 'importar' }));

  await userEvent.click(screen.getByRole('button', { name: 'encerrar' }));

  expect(screen.getByText('sem arquivo')).toBeInTheDocument();
  expect(sessaoSalva()).toEqual({ dataset: null, etapasVisitadas: [] });
});
```

**Passo 2: rodar e ver falhar**
`npx vitest run src/shared/sessao` → FAIL

**Passo 3: implementar**

`tipos.ts`
```ts
export interface DatasetSessao {
  id: string;
  nomeArquivo: string;
}

export interface ValorSessao {
  dataset: DatasetSessao | null;
  definirDataset: (dataset: DatasetSessao) => void;
  encerrar: () => void;
  etapasVisitadas: ReadonlySet<number>;
  marcarVisitada: (etapa: number) => void;
}
```

`persistencia.ts`
```ts
import type { DatasetSessao } from './tipos';

const CHAVE_SESSAO = 'sessao';

export interface EstadoSessao {
  readonly dataset: DatasetSessao | null;
  readonly etapasVisitadas: readonly number[];
}

export const SESSAO_VAZIA: EstadoSessao = { dataset: null, etapasVisitadas: [] };

function ehRegistro(valor: unknown): valor is Record<string, unknown> {
  return typeof valor === 'object' && valor !== null && !Array.isArray(valor);
}

function lerJson(texto: string): unknown {
  try {
    return JSON.parse(texto);
  } catch {
    return null;
  }
}

function lerDataset(valor: unknown): DatasetSessao | null {
  if (!ehRegistro(valor)) return null;
  const { id, nomeArquivo } = valor;
  return typeof id === 'string' && typeof nomeArquivo === 'string' ? { id, nomeArquivo } : null;
}

function lerEtapas(valor: unknown): number[] {
  return Array.isArray(valor) ? valor.filter((item: unknown): item is number => Number.isInteger(item)) : [];
}

/** Valida o JSON salvo; qualquer coisa fora do formato vira sessão vazia. */
export function interpretarSessao(texto: string | null): EstadoSessao {
  if (texto === null) return SESSAO_VAZIA;
  const bruto = lerJson(texto);
  if (!ehRegistro(bruto)) return SESSAO_VAZIA;
  const dataset = lerDataset(bruto.dataset);
  return dataset === null ? SESSAO_VAZIA : { dataset, etapasVisitadas: lerEtapas(bruto.etapasVisitadas) };
}

export function comEtapaVisitada(estado: EstadoSessao, etapa: number): EstadoSessao {
  if (estado.etapasVisitadas.includes(etapa)) return estado;
  return { ...estado, etapasVisitadas: [...estado.etapasVisitadas, etapa] };
}

export function carregarSessao(): EstadoSessao {
  try {
    return interpretarSessao(localStorage.getItem(CHAVE_SESSAO));
  } catch {
    return SESSAO_VAZIA;
  }
}

/** Devolve false se o navegador não deixou salvar; a sessão vale só até recarregar. */
export function salvarSessao(estado: EstadoSessao): boolean {
  try {
    localStorage.setItem(CHAVE_SESSAO, JSON.stringify(estado));
    return true;
  } catch {
    return false;
  }
}
```

`contextoSessao.ts`
```ts
import { createContext } from 'react';
import type { ValorSessao } from './tipos';

export const ContextoSessao = createContext<ValorSessao | null>(null);
```

`useSessao.ts`
```ts
import { useContext } from 'react';
import { ContextoSessao } from './contextoSessao';
import type { ValorSessao } from './tipos';

export function useSessao(): ValorSessao {
  const valor = useContext(ContextoSessao);
  if (valor === null) throw new Error('useSessao precisa estar dentro de <SessaoProvider>.');
  return valor;
}
```

`SessaoProvider.tsx`
```tsx
import { type ReactNode, useCallback, useEffect, useMemo, useState } from 'react';
import { ContextoSessao } from './contextoSessao';
import { SESSAO_VAZIA, carregarSessao, comEtapaVisitada, salvarSessao } from './persistencia';
import type { DatasetSessao, ValorSessao } from './tipos';

interface PropsSessaoProvider {
  children: ReactNode;
}

export default function SessaoProvider({ children }: Readonly<PropsSessaoProvider>) {
  const [estado, setEstado] = useState(carregarSessao);

  useEffect(() => {
    salvarSessao(estado);
  }, [estado]);

  const definirDataset = useCallback((dataset: DatasetSessao) => {
    setEstado({ dataset, etapasVisitadas: [] });
  }, []);
  const encerrar = useCallback(() => {
    setEstado(SESSAO_VAZIA);
  }, []);
  const marcarVisitada = useCallback((etapa: number) => {
    setEstado((anterior) => comEtapaVisitada(anterior, etapa));
  }, []);

  const etapasVisitadas = useMemo(() => new Set(estado.etapasVisitadas), [estado.etapasVisitadas]);
  const valor = useMemo<ValorSessao>(
    () => ({ dataset: estado.dataset, definirDataset, encerrar, etapasVisitadas, marcarVisitada }),
    [estado.dataset, definirDataset, encerrar, etapasVisitadas, marcarVisitada],
  );

  return <ContextoSessao value={valor}>{children}</ContextoSessao>;
}
```

**Passo 4: rodar e ver passar**
`npx vitest run src/shared/sessao` → todos passam. `npm run lint` → sem erros.

**Passo 5: commit**
```bash
git add frontend/src/shared/sessao
git commit -m "feat(frontend): adiciona sessão do dataset persistida e validada no localStorage"
```

---

### Tarefa 6: Erros da API e textos fixos de interface

**Arquivos:**
- Criar: `frontend/src/shared/api/erros.ts` + `erros.test.ts`
- Criar: `frontend/src/shared/ui/textos.ts`

**Passo 1: escrever o teste (falha)** — `erros.test.ts`
```ts
import { describe, expect, it } from 'vitest';
import { ErroApi } from './cliente';
import { ehDatasetNaoEncontrado, textoDoErro } from './erros';

const SESSAO_EXPIRADA = new ErroApi(404, {
  codigo: 'DATASET_NAO_ENCONTRADO',
  mensagem: 'Sua sessão expirou.',
  sugestao: 'Envie o arquivo novamente.',
});

describe('ehDatasetNaoEncontrado', () => {
  it('reconhece o código DATASET_NAO_ENCONTRADO', () => {
    expect(ehDatasetNaoEncontrado(SESSAO_EXPIRADA)).toBe(true);
  });

  it.each([
    new ErroApi(404, { codigo: 'COLUNA_NAO_ENCONTRADA', mensagem: 'x', sugestao: 'y' }),
    new Error('Sua sessão expirou.'),
    'DATASET_NAO_ENCONTRADO',
    null,
  ])('ignora %s', (erro) => {
    expect(ehDatasetNaoEncontrado(erro)).toBe(false);
  });
});

describe('textoDoErro', () => {
  it('usa mensagem e sugestão da API', () => {
    expect(textoDoErro(SESSAO_EXPIRADA)).toEqual({
      mensagem: 'Sua sessão expirou.',
      sugestao: 'Envie o arquivo novamente.',
    });
  });

  it('completa a sugestão vazia com o texto genérico', () => {
    const erro = new ErroApi(400, { codigo: 'X', mensagem: 'O arquivo está vazio.', sugestao: '' });

    expect(textoDoErro(erro)).toEqual({
      mensagem: 'O arquivo está vazio.',
      sugestao: 'Tente de novo. Se continuar, recarregue a página.',
    });
  });

  it.each([new Error('TypeError interno'), 'texto', undefined])('usa texto genérico para %s', (erro) => {
    expect(textoDoErro(erro)).toEqual({
      mensagem: 'Algo deu errado do nosso lado.',
      sugestao: 'Tente de novo. Se continuar, recarregue a página.',
    });
  });
});
```

**Passo 2: rodar e ver falhar**
`npx vitest run src/shared/api/erros.test.ts` → FAIL

**Passo 3: implementar**

`shared/api/erros.ts`
```ts
import { ErroApi } from './cliente';

export interface TextoErro {
  mensagem: string;
  sugestao: string;
}

const CODIGO_DATASET_NAO_ENCONTRADO = 'DATASET_NAO_ENCONTRADO';

/** Erro que não veio da API (falha inesperada no navegador). Spec 16: o que houve + o que fazer. */
const ERRO_GENERICO: TextoErro = {
  mensagem: 'Algo deu errado do nosso lado.',
  sugestao: 'Tente de novo. Se continuar, recarregue a página.',
};

/** A API perdeu o dataset (expirou ou o servidor reiniciou): a sessão do frontend acabou (D61). */
export function ehDatasetNaoEncontrado(erro: unknown): boolean {
  return erro instanceof ErroApi && erro.codigo === CODIGO_DATASET_NAO_ENCONTRADO;
}

/** Texto para EstadoErro e toasts: a mensagem da API ou um texto genérico amigável. */
export function textoDoErro(erro: unknown): TextoErro {
  if (!(erro instanceof ErroApi)) return ERRO_GENERICO;
  return {
    mensagem: erro.message,
    sugestao: erro.sugestao === '' ? ERRO_GENERICO.sugestao : erro.sugestao,
  };
}
```

`shared/ui/textos.ts` (textos fixos usados por mais de um componente; spec 16)
```ts
export const TEXTOS_UI = {
  nomeApp: 'Analisador e Gerador de Dados',
  etapaDeTotal: (etapa: number): string => `Etapa ${String(etapa)} de 8`,
  verFormula: 'Ver fórmula',
  ocultarFormula: 'Ocultar fórmula',
  naoSeAplica: 'Não se aplica',
  valorAusente: '—',
  tentarDeNovo: 'Tentar de novo',
  fecharAviso: 'Fechar aviso',
  carregandoGrafico: 'Carregando o gráfico…',
  etapaEmBreve: 'Esta etapa ainda não está pronta',
  telaEmConstrucao: 'Estamos construindo esta tela. Ela fica pronta ainda nesta versão.',
} as const;
```

**Passo 4: rodar e ver passar**
`npx vitest run src/shared/api` → todos passam (inclusive `cliente.test.ts`).

**Passo 5: commit**
```bash
git add frontend/src/shared/api/erros.ts frontend/src/shared/api/erros.test.ts frontend/src/shared/ui/textos.ts
git commit -m "feat(frontend): traduz erros da API em textos de tela e reúne textos fixos da interface"
```

---

### Tarefa 7: Ícone e Botão

**Arquivos:**
- Criar: `frontend/src/shared/ui/Icone.tsx`, `Icone.module.css`, `Icone.test.tsx`
- Criar: `frontend/src/shared/ui/Botao.tsx`, `Botao.module.css`, `Botao.test.tsx`

Extensão do contrato: `Botao` ganha `tamanho: 'sm'` (36 px), usado no Cabeçalho ("Trocar arquivo"), em `EstadoErro` e no `CardMetrica`; `Icone` aceita `className` para receber cor do componente pai.

**Passo 1: escrever os testes (falham)**

`Icone.test.tsx`
```tsx
import { render, screen } from '@testing-library/react';
import { expect, it } from 'vitest';
import Icone from './Icone';

it('é decorativo quando não tem rótulo', () => {
  const { container } = render(<Icone nome="check" />);

  expect(container.firstElementChild).toHaveAttribute('aria-hidden', 'true');
  expect(screen.queryByRole('img')).not.toBeInTheDocument();
});

it('vira imagem com nome acessível quando recebe rótulo', () => {
  render(<Icone nome="lock" rotulo="Bloqueada" />);

  expect(screen.getByRole('img', { name: 'Bloqueada' })).toHaveTextContent('lock');
});
```

`Botao.test.tsx`
```tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { expect, it, vi } from 'vitest';
import Botao from './Botao';

it('é um botão type="button" e o ícone não entra no nome', async () => {
  const aoClicar = vi.fn();
  render(
    <Botao iconeFinal="arrow_forward" onClick={aoClicar}>
      Continuar para Variáveis
    </Botao>,
  );

  const botao = screen.getByRole('button', { name: 'Continuar para Variáveis' });
  expect(botao).toHaveAttribute('type', 'button');
  await userEvent.click(botao);
  expect(aoClicar).toHaveBeenCalledOnce();
});

it('aceita type submit', () => {
  render(<Botao type="submit">Enviar</Botao>);

  expect(screen.getByRole('button', { name: 'Enviar' })).toHaveAttribute('type', 'submit');
});

it('carregando: desabilita, marca aria-busy e mostra o verbo no gerúndio', async () => {
  const aoClicar = vi.fn();
  render(
    <Botao carregando textoCarregando="Calculando…" onClick={aoClicar}>
      Calcular
    </Botao>,
  );

  const botao = screen.getByRole('button', { name: 'Calculando…' });
  expect(botao).toBeDisabled();
  expect(botao).toHaveAttribute('aria-busy', 'true');
  await userEvent.click(botao);
  expect(aoClicar).not.toHaveBeenCalled();
});
```

**Passo 2: rodar e ver falhar**
`npx vitest run src/shared/ui/Icone.test.tsx src/shared/ui/Botao.test.tsx` → FAIL

**Passo 3: implementar**

`Icone.tsx`
```tsx
import type { CSSProperties } from 'react';
import { juntarClasses } from '../lib/classes';
import estilos from './Icone.module.css';

interface PropsIcone {
  nome: string;
  preenchido?: boolean;
  tamanho?: number;
  /** Sem rótulo o ícone é decorativo (aria-hidden); com rótulo vira role="img". */
  rotulo?: string | undefined;
  className?: string | undefined;
}

export default function Icone({ nome, preenchido = false, tamanho = 20, rotulo, className }: Readonly<PropsIcone>) {
  const classes = juntarClasses(estilos.icone, preenchido && estilos.preenchido, className);
  const estilo: CSSProperties = { fontSize: tamanho };
  if (rotulo === undefined) {
    return (
      <span className={classes} style={estilo} aria-hidden="true">
        {nome}
      </span>
    );
  }
  return (
    <span className={classes} style={estilo} role="img" aria-label={rotulo}>
      {nome}
    </span>
  );
}
```

`Icone.module.css`
```css
.icone {
  display: inline-block;
  flex: none;
  width: 1em;
  height: 1em;
  overflow: hidden;
  font-family: var(--fonte-icones);
  font-weight: normal;
  font-style: normal;
  line-height: 1;
  letter-spacing: normal;
  text-transform: none;
  white-space: nowrap;
  direction: ltr;
  user-select: none;
  font-feature-settings: 'liga';
  -webkit-font-smoothing: antialiased;
  font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
}

.preenchido {
  font-variation-settings: 'FILL' 1, 'wght' 400, 'GRAD' 0, 'opsz' 24;
}
```

`Botao.tsx`
```tsx
import type { ButtonHTMLAttributes, ReactNode } from 'react';
import { juntarClasses } from '../lib/classes';
import estilos from './Botao.module.css';
import Icone from './Icone';

type VarianteBotao = 'primario' | 'secundario' | 'fantasma' | 'perigo';
type TamanhoBotao = 'sm' | 'md' | 'lg';

const TAMANHO_ICONE = { sm: 18, md: 18, lg: 20 } as const satisfies Record<TamanhoBotao, number>;

interface PropsBotao extends ButtonHTMLAttributes<HTMLButtonElement> {
  variante?: VarianteBotao;
  tamanho?: TamanhoBotao;
  icone?: string | undefined;
  iconeFinal?: string | undefined;
  carregando?: boolean;
  textoCarregando?: string | undefined;
}

export default function Botao({
  variante = 'primario',
  tamanho = 'md',
  icone,
  iconeFinal,
  carregando = false,
  textoCarregando,
  className,
  disabled,
  children,
  ...resto
}: Readonly<PropsBotao>) {
  return (
    <button
      type="button"
      {...resto}
      className={juntarClasses(estilos.botao, estilos[tamanho], estilos[variante], className)}
      disabled={disabled === true || carregando}
      aria-busy={carregando}
    >
      <ConteudoBotao
        carregando={carregando}
        textoCarregando={textoCarregando}
        icone={icone}
        iconeFinal={iconeFinal}
        tamanhoIcone={TAMANHO_ICONE[tamanho]}
      >
        {children}
      </ConteudoBotao>
    </button>
  );
}

interface PropsConteudoBotao {
  carregando: boolean;
  textoCarregando: string | undefined;
  icone: string | undefined;
  iconeFinal: string | undefined;
  tamanhoIcone: number;
  children: ReactNode;
}

function ConteudoBotao({ carregando, textoCarregando, icone, iconeFinal, tamanhoIcone, children }: Readonly<PropsConteudoBotao>) {
  if (carregando) {
    return (
      <>
        <span className={estilos.spinner} aria-hidden="true" />
        {textoCarregando ?? children}
      </>
    );
  }
  return (
    <>
      {icone ? <Icone nome={icone} tamanho={tamanhoIcone} /> : null}
      {children}
      {iconeFinal ? <Icone nome={iconeFinal} tamanho={tamanhoIcone} /> : null}
    </>
  );
}
```
`type="button"` vem antes do spread para quem precisar passar `type="submit"`.

`Botao.module.css` (ordem importa: tamanho antes da variante, para o padding do fantasma vencer)
```css
.botao {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--esp-8);
  height: 40px;
  padding: 0 var(--esp-16);
  border: 1px solid transparent;
  border-radius: var(--raio-md);
  background: transparent;
  font-size: 14px;
  font-weight: 500;
  line-height: 1;
  white-space: nowrap;
  cursor: pointer;
  transition:
    background-color var(--transicao),
    border-color var(--transicao),
    box-shadow var(--transicao),
    color var(--transicao);
}
.botao:disabled { cursor: not-allowed; }
.botao[aria-busy='true'] { cursor: progress; }

.sm { height: 36px; padding: 0 14px; }
.md { height: 40px; }
.lg { height: 44px; padding: 0 18px; font-size: 15px; }

.primario { background: var(--cor-primaria); color: var(--cor-sobre-primaria); font-weight: 600; }
.primario:hover:not(:disabled) { background: var(--cor-primaria-hover); }
.primario:active:not(:disabled) { background: var(--cor-primaria-ativa); }
.primario:disabled { background: var(--cor-superficie-2); color: var(--cor-texto-desab); }
.primario[aria-busy='true'] { background: var(--cor-primaria); color: var(--cor-sobre-primaria); }

.secundario { border-color: var(--cor-borda-forte); background: var(--cor-superficie); color: var(--cor-texto); }
.secundario:hover:not(:disabled) { background: var(--cor-superficie-2); }
.secundario:active:not(:disabled) { border-color: var(--cor-texto-2); background: var(--cor-borda); }
.secundario:disabled { border-color: var(--cor-borda); color: var(--cor-texto-desab); }

.fantasma { padding: 0 var(--esp-12); color: var(--cor-primaria); }
.fantasma:hover:not(:disabled) { background: var(--cor-primaria-suave); }
.fantasma:active:not(:disabled) { background: color-mix(in oklab, var(--cor-primaria) 18%, transparent); }
.fantasma:disabled { color: var(--cor-texto-desab); }

.perigo { border-color: var(--cor-erro); background: var(--cor-superficie); color: var(--cor-erro); font-weight: 600; }
.perigo:hover:not(:disabled) { background: var(--cor-erro-suave); }
.perigo:active:not(:disabled) { background: var(--cor-erro); color: var(--cor-superficie); }
.perigo:disabled { border-color: var(--cor-borda); color: var(--cor-texto-desab); }

.spinner {
  width: 14px;
  height: 14px;
  border: 2px solid currentColor;
  border-right-color: transparent;
  border-radius: 50%;
  animation: girar 0.8s linear infinite;
}

@keyframes girar {
  to { transform: rotate(360deg); }
}
```
As regras de uma linha são só para o plano ficar curto: rode `npm run format:fix` e aceite o CSS expandido pelo Prettier.

**Passo 4: rodar e ver passar**
`npx vitest run src/shared/ui` → 5 passed. `npm run lint` → sem erros.

**Passo 5: commit**
```bash
git add frontend/src/shared/ui/Icone.* frontend/src/shared/ui/Botao.*
git commit -m "feat(frontend): adiciona componentes Icone e Botao com variantes e estado carregando"
```

---

### Tarefa 8: Card, Banner e estados (carregando, vazio, erro)

**Arquivos:**
- Criar em `frontend/src/shared/ui/`: `Card.tsx`, `Card.module.css`, `Card.test.tsx`; `Banner.tsx`, `Banner.module.css`, `Banner.test.tsx`; `EstadoCarregando.tsx`, `EstadoCarregando.module.css`, `EstadoCarregando.test.tsx`; `EstadoVazio.tsx`, `EstadoVazio.module.css`, `EstadoVazio.test.tsx`; `EstadoErro.tsx`, `EstadoErro.test.tsx`

Extensão do contrato: `Card` ganha `preenchimento?: 'normal' | 'nenhum'` (tabela de prévia encostada nas bordas, como no print 1a). `EstadoCarregando` aceita `forma?: FormaCarregando | readonly FormaCarregando[]` (várias formas em sequência, um só `role="status"`; a tela 4h do M1.7 usa cards + gráfico) e exporta o tipo `FormaCarregando`. `EstadoErro` reaproveita o `Banner` variante `erro` (sem CSS próprio, sem duplicação).

**Passo 1: escrever os testes (falham)**

`Card.test.tsx`
```tsx
import { render, screen } from '@testing-library/react';
import { expect, it } from 'vitest';
import Botao from './Botao';
import Card from './Card';

it('mostra título como h2, subtítulo e ações', () => {
  render(
    <Card titulo="Prévia" subtitulo="20 primeiras linhas de 230" acoes={<Botao variante="secundario">Ler de novo</Botao>}>
      <p>conteúdo</p>
    </Card>,
  );

  expect(screen.getByRole('heading', { level: 2, name: 'Prévia' })).toBeInTheDocument();
  expect(screen.getByText('20 primeiras linhas de 230')).toBeInTheDocument();
  expect(screen.getByRole('button', { name: 'Ler de novo' })).toBeInTheDocument();
  expect(screen.getByText('conteúdo')).toBeInTheDocument();
});

it('sem título não cria cabeçalho', () => {
  render(
    <Card>
      <p>só conteúdo</p>
    </Card>,
  );

  expect(screen.queryByRole('heading')).not.toBeInTheDocument();
});
```

`Banner.test.tsx`
```tsx
import { render, screen } from '@testing-library/react';
import { expect, it } from 'vitest';
import Banner from './Banner';

it('erro é anunciado como alerta', () => {
  render(
    <Banner variante="erro" titulo="Não conseguimos ler este arquivo: relatorio_final.pdf">
      PDF não é um formato de tabela.
    </Banner>,
  );

  const alerta = screen.getByRole('alert');
  expect(alerta).toHaveTextContent('Não conseguimos ler este arquivo: relatorio_final.pdf');
  expect(alerta).toHaveTextContent('PDF não é um formato de tabela.');
});

it('info é uma nota e mostra as ações', () => {
  render(
    <Banner variante="info" acoes={<a href="#ajuda">Saiba mais</a>}>
      Média e mediana estão próximas.
    </Banner>,
  );

  expect(screen.getByRole('note')).toHaveTextContent('Média e mediana estão próximas.');
  expect(screen.getByRole('link', { name: 'Saiba mais' })).toBeInTheDocument();
});
```

`EstadoCarregando.test.tsx`
```tsx
import { render, screen } from '@testing-library/react';
import { expect, it } from 'vitest';
import EstadoCarregando from './EstadoCarregando';

it.each(['cards', 'tabela', 'grafico'] as const)('forma %s: anuncia a mensagem e marca aria-busy', (forma) => {
  const { container } = render(<EstadoCarregando forma={forma} mensagem="Calculando as estatísticas de peso_kg…" />);

  expect(screen.getByRole('status')).toHaveTextContent('Calculando as estatísticas de peso_kg…');
  expect(container.firstElementChild).toHaveAttribute('aria-busy', 'true');
});

it('várias formas: desenha os esqueletos em sequência com um só status (print 4h)', () => {
  const { container } = render(
    <EstadoCarregando forma={['cards', 'grafico']} mensagem="Calculando as estatísticas de peso_kg…" />,
  );

  expect(screen.getAllByRole('status')).toHaveLength(1);
  expect(container.querySelector('[aria-hidden="true"]')?.childElementCount).toBe(2);
});
```

`EstadoVazio.test.tsx`
```tsx
import { render, screen } from '@testing-library/react';
import { expect, it } from 'vitest';
import Botao from './Botao';
import EstadoVazio from './EstadoVazio';

it('mostra título, próximo passo e ação', () => {
  render(
    <EstadoVazio
      icone="upload_file"
      titulo="Nenhum arquivo importado"
      descricao="Importe um arquivo para ver as variáveis."
      acao={<Botao>Importar arquivo</Botao>}
    />,
  );

  expect(screen.getByRole('heading', { name: 'Nenhum arquivo importado' })).toBeInTheDocument();
  expect(screen.getByText('Importe um arquivo para ver as variáveis.')).toBeInTheDocument();
  expect(screen.getByRole('button', { name: 'Importar arquivo' })).toBeInTheDocument();
});
```

`EstadoErro.test.tsx`
```tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { expect, it, vi } from 'vitest';
import { ErroApi } from '../api/cliente';
import EstadoErro from './EstadoErro';

it('mostra mensagem e sugestão da API e permite tentar de novo', async () => {
  const aoTentarDeNovo = vi.fn();
  const erro = new ErroApi(0, {
    codigo: 'SEM_CONEXAO',
    mensagem: 'Não conseguimos falar com o servidor.',
    sugestao: 'Verifique se o backend está rodando e tente novamente.',
  });
  render(<EstadoErro erro={erro} aoTentarDeNovo={aoTentarDeNovo} />);

  const alerta = screen.getByRole('alert');
  expect(alerta).toHaveTextContent('Não conseguimos falar com o servidor.');
  expect(alerta).toHaveTextContent('Verifique se o backend está rodando e tente novamente.');
  await userEvent.click(screen.getByRole('button', { name: 'Tentar de novo' }));
  expect(aoTentarDeNovo).toHaveBeenCalledOnce();
});

it('usa texto genérico para erro que não veio da API e não mostra botão sem callback', () => {
  render(<EstadoErro erro={new Error('falha interna')} />);

  expect(screen.getByRole('alert')).toHaveTextContent('Algo deu errado do nosso lado.');
  expect(screen.queryByRole('button')).not.toBeInTheDocument();
});
```

**Passo 2: rodar e ver falhar**
`npx vitest run src/shared/ui` → FAIL nos 5 arquivos novos

**Passo 3: implementar**

`Card.tsx`
```tsx
import type { ReactNode } from 'react';
import { juntarClasses } from '../lib/classes';
import estilos from './Card.module.css';

type Preenchimento = 'normal' | 'nenhum';

interface PropsCard {
  titulo?: ReactNode;
  subtitulo?: ReactNode;
  acoes?: ReactNode;
  preenchimento?: Preenchimento;
  children: ReactNode;
}

export default function Card({ titulo, subtitulo, acoes, preenchimento = 'normal', children }: Readonly<PropsCard>) {
  const temCabecalho = titulo !== undefined || acoes !== undefined;
  return (
    <section className={estilos.card}>
      {temCabecalho ? <CabecalhoCard titulo={titulo} subtitulo={subtitulo} acoes={acoes} /> : null}
      <div className={juntarClasses(estilos.corpo, preenchimento === 'nenhum' && estilos.semEspaco)}>{children}</div>
    </section>
  );
}

interface PropsCabecalhoCard {
  titulo: ReactNode;
  subtitulo: ReactNode;
  acoes: ReactNode;
}

function CabecalhoCard({ titulo, subtitulo, acoes }: Readonly<PropsCabecalhoCard>) {
  return (
    <header className={estilos.cabecalho}>
      <div className={estilos.textos}>
        {titulo === undefined ? null : <h2 className={estilos.titulo}>{titulo}</h2>}
        {subtitulo === undefined ? null : <p className={estilos.subtitulo}>{subtitulo}</p>}
      </div>
      {acoes === undefined ? null : <div className={estilos.acoes}>{acoes}</div>}
    </header>
  );
}
```

`Card.module.css`
```css
.card {
  background: var(--cor-superficie);
  border: 1px solid var(--cor-borda);
  border-radius: var(--raio-lg);
  box-shadow: var(--sombra-1);
}
.cabecalho {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--esp-16);
  padding: var(--esp-20) var(--esp-24) var(--esp-16);
}
.textos { display: flex; flex-wrap: wrap; align-items: baseline; gap: var(--esp-4) var(--esp-12); min-width: 0; }
.titulo { font-size: 17px; font-weight: 600; line-height: 1.35; }
.subtitulo { font-size: 14px; color: var(--cor-texto-2); }
.acoes { display: flex; flex: none; gap: var(--esp-8); }
.corpo { padding: var(--esp-24); }
.cabecalho + .corpo { padding-top: 0; }
.semEspaco,
.cabecalho + .semEspaco {
  padding: 0;
  overflow: hidden;
  border-bottom-left-radius: inherit;
  border-bottom-right-radius: inherit;
}
```
O card **não** usa `overflow: hidden` (cortaria tooltips); só o corpo sem espaço recorta os cantos da tabela.

`Banner.tsx`
```tsx
import type { ReactNode } from 'react';
import { juntarClasses } from '../lib/classes';
import estilos from './Banner.module.css';
import Icone from './Icone';

type VarianteBanner = 'info' | 'atencao' | 'erro' | 'sucesso';

const ICONES = { info: 'info', atencao: 'warning', erro: 'error', sucesso: 'check_circle' } as const satisfies Record<
  VarianteBanner,
  string
>;
const PAPEIS = { info: 'note', atencao: 'note', erro: 'alert', sucesso: 'status' } as const satisfies Record<
  VarianteBanner,
  string
>;

interface PropsBanner {
  variante: VarianteBanner;
  titulo?: string | undefined;
  acoes?: ReactNode;
  children: ReactNode;
}

export default function Banner({ variante, titulo, acoes, children }: Readonly<PropsBanner>) {
  return (
    <div role={PAPEIS[variante]} className={juntarClasses(estilos.banner, estilos[variante])}>
      <Icone nome={ICONES[variante]} preenchido tamanho={variante === 'erro' ? 24 : 20} className={estilos.icone} />
      <div className={estilos.conteudo}>
        {titulo ? <p className={estilos.titulo}>{titulo}</p> : null}
        <div className={estilos.texto}>{children}</div>
        {acoes === undefined ? null : <div className={estilos.acoes}>{acoes}</div>}
      </div>
    </div>
  );
}
```

`Banner.module.css`
```css
.banner {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: var(--esp-12) var(--esp-16);
  border: 1px solid transparent;
  border-radius: 10px;
  font-size: 14px;
  line-height: 1.5;
}
.info { border-color: color-mix(in oklab, var(--sev-info) 30%, transparent); background: var(--sev-info-suave); }
.info .icone { color: var(--sev-info); }
.atencao { border-color: var(--sev-atencao-borda); background: var(--sev-atencao-suave); }
.atencao .icone { color: var(--sev-atencao); }
.erro { border-color: var(--cor-erro); background: var(--cor-erro-suave); }
.erro .icone { color: var(--cor-erro); }
.sucesso { border-color: color-mix(in oklab, var(--cor-sucesso) 30%, transparent); background: var(--cor-sucesso-suave); }
.sucesso .icone { color: var(--cor-sucesso); }
.conteudo { display: flex; flex: 1; flex-direction: column; gap: var(--esp-4); min-width: 0; }
.titulo { font-weight: 600; }
.erro .titulo { font-size: 15px; }
.acoes { display: flex; flex-wrap: wrap; gap: var(--esp-8); margin-top: var(--esp-4); }
```

`EstadoCarregando.tsx` (skeletons içados para fora do componente). Extensão compatível do contrato: `forma` aceita também uma lista, desenhada em sequência com **um** `role="status"` (a tela 4h do M1.7 usa `['cards', 'grafico']`).
```tsx
import { Fragment } from 'react';
import { juntarClasses } from '../lib/classes';
import estilos from './EstadoCarregando.module.css';

export type FormaCarregando = 'cards' | 'tabela' | 'grafico';

/** Alturas (%) das barras do histograma de mentira (print 4h); valores únicos servem de key. */
const ALTURAS_BARRAS = [12, 30, 48, 70, 84, 77, 56, 34, 20] as const;
const CARTOES = [1, 2, 3] as const;
const LINHAS_TABELA = [1, 2, 3, 4, 5, 6] as const;

const ESQUELETO_CARDS = (
  <div className={estilos.cartoes}>
    {CARTOES.map((n) => (
      <div key={n} className={estilos.cartao}>
        <span className={juntarClasses(estilos.bloco, estilos.rotulo)} />
        <span className={juntarClasses(estilos.bloco, estilos.valor)} />
        <span className={juntarClasses(estilos.bloco, estilos.linha)} />
        <span className={juntarClasses(estilos.bloco, estilos.linhaCurta)} />
      </div>
    ))}
  </div>
);

const ESQUELETO_TABELA = (
  <div className={estilos.tabela}>
    {LINHAS_TABELA.map((n) => (
      <span key={n} className={juntarClasses(estilos.bloco, estilos.linhaTabela)} />
    ))}
  </div>
);

const ESQUELETO_GRAFICO = (
  <div className={estilos.grafico}>
    <div className={estilos.area}>
      {ALTURAS_BARRAS.map((altura) => (
        <span key={altura} className={estilos.barra} style={{ height: `${String(altura)}%` }} />
      ))}
    </div>
    <div className={estilos.textos}>
      <span className={juntarClasses(estilos.bloco, estilos.rotulo)} />
      <span className={juntarClasses(estilos.bloco, estilos.linha)} />
      <span className={juntarClasses(estilos.bloco, estilos.linhaCurta)} />
    </div>
  </div>
);

const ESQUELETOS = { cards: ESQUELETO_CARDS, tabela: ESQUELETO_TABELA, grafico: ESQUELETO_GRAFICO } as const satisfies Record<
  FormaCarregando,
  unknown
>;

interface PropsEstadoCarregando {
  mensagem: string;
  /** Uma forma ou várias em sequência (ex.: `['cards', 'grafico']`). */
  forma?: FormaCarregando | readonly FormaCarregando[];
}

export default function EstadoCarregando({ mensagem, forma = 'cards' }: Readonly<PropsEstadoCarregando>) {
  const formas: readonly FormaCarregando[] = typeof forma === 'string' ? [forma] : forma;
  return (
    <div className={estilos.estado} aria-busy="true">
      <div className={estilos.esqueletos} aria-hidden="true">
        {formas.map((cada) => (
          <Fragment key={cada}>{ESQUELETOS[cada]}</Fragment>
        ))}
      </div>
      <p role="status" className={estilos.mensagem}>
        {mensagem}
      </p>
    </div>
  );
}
```

`EstadoCarregando.module.css`
```css
.estado { display: flex; flex-direction: column; gap: var(--esp-16); }
.esqueletos { display: flex; flex-direction: column; gap: var(--esp-16); }
.bloco {
  display: block;
  border-radius: var(--raio-sm);
  background: var(--cor-superficie-2);
  animation: pulsar 1.2s ease-in-out infinite alternate;
}
.cartoes { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: var(--esp-16); }
.cartao,
.tabela,
.grafico {
  padding: var(--esp-20);
  border: 1px solid var(--cor-borda);
  border-radius: var(--raio-lg);
  background: var(--cor-superficie);
}
.cartao { display: flex; flex-direction: column; gap: var(--esp-12); }
.rotulo { width: 40%; height: 12px; }
.valor { width: 55%; height: 30px; }
.linha { width: 85%; height: 12px; }
.linhaCurta { width: 65%; height: 12px; }
.tabela { display: flex; flex-direction: column; gap: var(--esp-8); }
.linhaTabela { width: 100%; height: 28px; }
.grafico { display: grid; grid-template-columns: minmax(0, 2fr) minmax(0, 1fr); gap: var(--esp-24); }
.area {
  display: flex;
  align-items: flex-end;
  gap: var(--esp-12);
  height: 320px;
  padding: var(--esp-20);
  border-radius: var(--raio-md);
  background: var(--cor-superficie-2);
}
.barra {
  flex: 1;
  border-radius: var(--raio-xs) var(--raio-xs) 0 0;
  background: var(--cor-borda);
  animation: pulsar 1.2s ease-in-out infinite alternate;
}
.textos { display: flex; flex-direction: column; gap: var(--esp-12); }
.mensagem { font-size: 14px; color: var(--cor-texto-2); }

@keyframes pulsar {
  from { opacity: 1; }
  to { opacity: 0.55; }
}

@media (max-width: 1279px) {
  .cartoes { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .grafico { grid-template-columns: 1fr; }
}
```

`EstadoVazio.tsx`
```tsx
import type { ReactNode } from 'react';
import estilos from './EstadoVazio.module.css';
import Icone from './Icone';

interface PropsEstadoVazio {
  icone: string;
  titulo: string;
  /** Frase com o próximo passo (spec 15). */
  descricao: string;
  acao?: ReactNode;
}

export default function EstadoVazio({ icone, titulo, descricao, acao }: Readonly<PropsEstadoVazio>) {
  return (
    <div className={estilos.vazio}>
      <span className={estilos.circulo}>
        <Icone nome={icone} tamanho={28} />
      </span>
      <h2 className={estilos.titulo}>{titulo}</h2>
      <p className={estilos.descricao}>{descricao}</p>
      {acao === undefined ? null : <div className={estilos.acao}>{acao}</div>}
    </div>
  );
}
```

`EstadoVazio.module.css`
```css
.vazio {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--esp-12);
  padding: var(--esp-48) var(--esp-24);
  border: 1px dashed var(--cor-borda-forte);
  border-radius: var(--raio-lg);
  text-align: center;
}
.circulo {
  display: grid;
  place-items: center;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: var(--cor-primaria-suave);
  color: var(--cor-primaria);
}
.titulo { font-size: 17px; font-weight: 600; }
.descricao { max-width: 52ch; font-size: 14px; color: var(--cor-texto-2); }
.acao { margin-top: var(--esp-4); }
```

`EstadoErro.tsx`
```tsx
import type { ReactNode } from 'react';
import { textoDoErro } from '../api/erros';
import Banner from './Banner';
import Botao from './Botao';
import { TEXTOS_UI } from './textos';

interface PropsEstadoErro {
  erro: unknown;
  aoTentarDeNovo?: (() => void) | undefined;
  acoes?: ReactNode;
}

export default function EstadoErro({ erro, aoTentarDeNovo, acoes }: Readonly<PropsEstadoErro>) {
  const { mensagem, sugestao } = textoDoErro(erro);
  const temAcoes = aoTentarDeNovo !== undefined || acoes !== undefined;
  const botaoTentar = aoTentarDeNovo ? (
    <Botao variante="secundario" tamanho="sm" icone="refresh" onClick={aoTentarDeNovo}>
      {TEXTOS_UI.tentarDeNovo}
    </Botao>
  ) : null;
  return (
    <Banner
      variante="erro"
      titulo={mensagem}
      acoes={
        temAcoes ? (
          <>
            {botaoTentar}
            {acoes}
          </>
        ) : undefined
      }
    >
      {sugestao}
    </Banner>
  );
}
```

**Passo 4: rodar e ver passar**
`npx vitest run src/shared/ui` → todos passam. `npm run lint` → sem erros.

**Passo 5: commit**
```bash
git add frontend/src/shared/ui
git commit -m "feat(frontend): adiciona Card, Banner e estados de carregando, vazio e erro"
```

---

### Tarefa 9: Tooltip

**Arquivos:**
- Criar: `frontend/src/shared/ui/Tooltip.tsx`, `Tooltip.module.css`, `Tooltip.test.tsx`

Comportamento (`componentes.md` §Tooltip): abre em hover e foco, fecha com Esc; o texto fica sempre no DOM (com `hidden` quando fechado) e é ligado ao alvo por `aria-describedby`. Extensão do contrato: `posicao?: 'acima' | 'direita'` (a barra recolhida mostra o nome da etapa à direita).

**Passo 1: escrever o teste (falha)** — `Tooltip.test.tsx`
```tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { expect, it } from 'vitest';
import Tooltip from './Tooltip';

function renderizar() {
  render(
    <Tooltip texto="Disponível na versão v0.2.">
      <button type="button" aria-disabled="true">
        Bivariada
      </button>
    </Tooltip>,
  );
  return {
    alvo: screen.getByRole('button', { name: 'Bivariada' }),
    dica: screen.getByRole('tooltip', { hidden: true }),
  };
}

it('liga o texto ao alvo e abre com o mouse', async () => {
  const { alvo, dica } = renderizar();

  expect(alvo).toHaveAttribute('aria-describedby', dica.id);
  expect(dica).not.toBeVisible();
  await userEvent.hover(alvo);
  expect(dica).toBeVisible();
  expect(dica).toHaveTextContent('Disponível na versão v0.2.');
  await userEvent.unhover(alvo);
  expect(dica).not.toBeVisible();
});

it('abre com o foco do teclado e fecha com Esc', async () => {
  const { dica } = renderizar();

  await userEvent.tab();
  expect(dica).toBeVisible();
  await userEvent.keyboard('{Escape}');
  expect(dica).not.toBeVisible();
});
```

**Passo 2: rodar e ver falhar**
`npx vitest run src/shared/ui/Tooltip.test.tsx` → FAIL

**Passo 3: implementar**

`Tooltip.tsx`
```tsx
import { type ReactElement, cloneElement, useCallback, useId, useState } from 'react';
import { juntarClasses } from '../lib/classes';
import { useTeclaEsc } from '../lib/useTeclaEsc';
import estilos from './Tooltip.module.css';

type PosicaoTooltip = 'acima' | 'direita';

/** O alvo precisa repassar aria-describedby para o elemento focável. */
interface AtributosAlvo {
  'aria-describedby'?: string | undefined;
}

interface PropsTooltip {
  texto: string;
  posicao?: PosicaoTooltip;
  children: ReactElement<AtributosAlvo>;
}

export default function Tooltip({ texto, posicao = 'acima', children }: Readonly<PropsTooltip>) {
  const id = useId();
  const [aberto, setAberto] = useState(false);
  const abrir = useCallback(() => {
    setAberto(true);
  }, []);
  const fechar = useCallback(() => {
    setAberto(false);
  }, []);
  useTeclaEsc(aberto, fechar);

  return (
    <span className={estilos.ancora} onMouseEnter={abrir} onMouseLeave={fechar} onFocus={abrir} onBlur={fechar}>
      {cloneElement(children, { 'aria-describedby': id })}
      <span
        role="tooltip"
        id={id}
        hidden={!aberto}
        className={juntarClasses(estilos.balao, posicao === 'direita' && estilos.direita)}
      >
        {texto}
      </span>
    </span>
  );
}
```

`Tooltip.module.css`
```css
.ancora { position: relative; display: inline-flex; }
.balao {
  position: absolute;
  z-index: 40;
  bottom: calc(100% + 8px);
  left: 50%;
  width: max-content;
  max-width: 260px;
  padding: var(--esp-8) var(--esp-12);
  border-radius: var(--raio-sm);
  background: var(--cor-texto);
  color: var(--cor-superficie);
  font-size: 13px;
  font-weight: 400;
  line-height: 1.45;
  text-align: left;
  white-space: normal;
  pointer-events: none;
  transform: translateX(-50%);
}
.balao::after {
  content: '';
  position: absolute;
  top: 100%;
  left: 50%;
  margin-left: -6px;
  border: 6px solid transparent;
  border-top-color: var(--cor-texto);
}
.direita { top: 50%; bottom: auto; left: calc(100% + 8px); transform: translateY(-50%); }
.direita::after {
  top: 50%;
  right: 100%;
  left: auto;
  margin: -6px 0 0;
  border-color: transparent;
  border-right-color: var(--cor-texto);
}
```
O balão não define `display`, então o atributo `hidden` continua escondendo.

**Passo 4: rodar e ver passar**
`npx vitest run src/shared/ui/Tooltip.test.tsx` → 2 passed.

**Passo 5: commit**
```bash
git add frontend/src/shared/ui/Tooltip.*
git commit -m "feat(frontend): adiciona Tooltip acessível por mouse, foco e Esc"
```

---

### Tarefa 10: Toast

**Arquivos:**
- Criar em `frontend/src/shared/ui/`: `contextoToast.ts`, `useToast.ts`, `ToastProvider.tsx`, `ItemToast.tsx`, `Toast.module.css`, `ToastProvider.test.tsx`

Comportamento (`componentes.md` §Toast, handoff): canto superior direito abaixo do cabeçalho; some em 6 s; hover ou foco pausam (ao sair, a contagem recomeça dos 6 s — mais simples e dá tempo de ler); sucesso `role="status"`, erro `role="alert"` com ação opcional; botão "Fechar aviso". A região que recebe os toasts é fixa e tem `aria-live="polite"`, para o anúncio funcionar quando o toast entra.

**Passo 1: escrever o teste (falha)** — `ToastProvider.test.tsx`
```tsx
import { act, fireEvent, render, screen, within } from '@testing-library/react';
import { beforeEach, expect, it, vi } from 'vitest';
import type { PedidoToast } from './contextoToast';
import ToastProvider from './ToastProvider';
import { useToast } from './useToast';

function Disparador({ pedido }: Readonly<{ pedido: PedidoToast }>) {
  const { mostrar } = useToast();
  return (
    <button
      type="button"
      onClick={() => {
        mostrar(pedido);
      }}
    >
      mostrar
    </button>
  );
}

function mostrarToast(pedido: PedidoToast) {
  render(
    <ToastProvider>
      <Disparador pedido={pedido} />
    </ToastProvider>,
  );
  fireEvent.click(screen.getByRole('button', { name: 'mostrar' }));
}

function avancar(ms: number) {
  act(() => {
    vi.advanceTimersByTime(ms);
  });
}

beforeEach(() => {
  vi.useFakeTimers();
});

it('sucesso aparece como status e some depois de 6 s', () => {
  mostrarToast({
    tipo: 'sucesso',
    titulo: 'Arquivo lido: 230 linhas e 8 colunas.',
    descricao: 'As etapas 2 a 8 foram liberadas.',
  });

  expect(screen.getByRole('status')).toHaveTextContent('Arquivo lido: 230 linhas e 8 colunas.');
  avancar(5999);
  expect(screen.getByRole('status')).toBeInTheDocument();
  avancar(1);
  expect(screen.queryByRole('status')).not.toBeInTheDocument();
});

it('erro aparece como alerta; a ação roda e fecha o aviso', () => {
  const aoClicar = vi.fn();
  mostrarToast({ tipo: 'erro', titulo: 'Não conseguimos aplicar a limpeza.', acao: { rotulo: 'Tentar de novo', aoClicar } });

  fireEvent.click(within(screen.getByRole('alert')).getByRole('button', { name: 'Tentar de novo' }));

  expect(aoClicar).toHaveBeenCalledOnce();
  expect(screen.queryByRole('alert')).not.toBeInTheDocument();
});

it('pausa enquanto o mouse está em cima', () => {
  mostrarToast({ tipo: 'sucesso', titulo: 'Limpeza aplicada: 3 linhas removidas.' });

  fireEvent.mouseEnter(screen.getByRole('status'));
  avancar(10000);
  expect(screen.getByRole('status')).toBeInTheDocument();
  fireEvent.mouseLeave(screen.getByRole('status'));
  avancar(6000);
  expect(screen.queryByRole('status')).not.toBeInTheDocument();
});

it('o botão Fechar aviso remove na hora', () => {
  mostrarToast({ tipo: 'sucesso', titulo: 'Tipo alterado.' });

  fireEvent.click(screen.getByRole('button', { name: 'Fechar aviso' }));

  expect(screen.queryByRole('status')).not.toBeInTheDocument();
});
```

**Passo 2: rodar e ver falhar**
`npx vitest run src/shared/ui/ToastProvider.test.tsx` → FAIL

**Passo 3: implementar**

`contextoToast.ts`
```ts
import { createContext } from 'react';

export type TipoToast = 'sucesso' | 'erro';

export interface AcaoToast {
  rotulo: string;
  aoClicar: () => void;
}

export interface PedidoToast {
  tipo: TipoToast;
  /** Verbo no passado + quantidade (spec 16): "Limpeza aplicada: 12 linhas removidas." */
  titulo: string;
  descricao?: string | undefined;
  acao?: AcaoToast | undefined;
}

export interface ToastAtivo extends PedidoToast {
  id: number;
}

export interface ValorToast {
  mostrar: (pedido: PedidoToast) => void;
}

export const ContextoToast = createContext<ValorToast | null>(null);
```

`useToast.ts`
```ts
import { useContext } from 'react';
import { ContextoToast, type ValorToast } from './contextoToast';

export function useToast(): ValorToast {
  const valor = useContext(ContextoToast);
  if (valor === null) throw new Error('useToast precisa estar dentro de <ToastProvider>.');
  return valor;
}
```

`ToastProvider.tsx`
```tsx
import { type ReactNode, useCallback, useMemo, useRef, useState } from 'react';
import { ContextoToast, type PedidoToast, type ToastAtivo } from './contextoToast';
import ItemToast from './ItemToast';
import estilos from './Toast.module.css';

interface PropsToastProvider {
  children: ReactNode;
}

export default function ToastProvider({ children }: Readonly<PropsToastProvider>) {
  const [toasts, setToasts] = useState<readonly ToastAtivo[]>([]);
  const proximoId = useRef(0);

  const mostrar = useCallback((pedido: PedidoToast) => {
    proximoId.current += 1;
    const id = proximoId.current;
    setToasts((atuais) => [...atuais, { ...pedido, id }]);
  }, []);
  const remover = useCallback((id: number) => {
    setToasts((atuais) => atuais.filter((toast) => toast.id !== id));
  }, []);
  const valor = useMemo(() => ({ mostrar }), [mostrar]);

  return (
    <ContextoToast value={valor}>
      {children}
      <div className={estilos.regiao} aria-live="polite">
        {toasts.map((toast) => (
          <ItemToast key={toast.id} toast={toast} aoRemover={remover} />
        ))}
      </div>
    </ContextoToast>
  );
}
```

`ItemToast.tsx`
```tsx
import { useCallback, useEffect, useState } from 'react';
import { juntarClasses } from '../lib/classes';
import Botao from './Botao';
import type { ToastAtivo } from './contextoToast';
import Icone from './Icone';
import { TEXTOS_UI } from './textos';
import estilos from './Toast.module.css';

const DURACAO_MS = 6000;

function useTemporizador(duracaoMs: number, aoTerminar: () => void) {
  const [pausado, setPausado] = useState(false);
  useEffect(() => {
    if (pausado) return undefined;
    const temporizador = window.setTimeout(aoTerminar, duracaoMs);
    return () => {
      window.clearTimeout(temporizador);
    };
  }, [pausado, duracaoMs, aoTerminar]);
  const pausar = useCallback(() => {
    setPausado(true);
  }, []);
  const retomar = useCallback(() => {
    setPausado(false);
  }, []);
  return { pausar, retomar };
}

interface PropsItemToast {
  toast: ToastAtivo;
  aoRemover: (id: number) => void;
}

export default function ItemToast({ toast, aoRemover }: Readonly<PropsItemToast>) {
  const { id, tipo, titulo, descricao, acao } = toast;
  const fechar = useCallback(() => {
    aoRemover(id);
  }, [aoRemover, id]);
  const { pausar, retomar } = useTemporizador(DURACAO_MS, fechar);

  return (
    <div
      role={tipo === 'erro' ? 'alert' : 'status'}
      className={juntarClasses(estilos.toast, estilos[tipo])}
      onMouseEnter={pausar}
      onMouseLeave={retomar}
      onFocus={pausar}
      onBlur={retomar}
    >
      <Icone nome={tipo === 'erro' ? 'error' : 'check_circle'} preenchido tamanho={22} className={estilos.icone} />
      <div className={estilos.texto}>
        <p className={estilos.titulo}>{titulo}</p>
        {descricao ? <p className={estilos.descricao}>{descricao}</p> : null}
        {acao ? (
          <Botao
            variante="fantasma"
            tamanho="sm"
            className={estilos.acao}
            onClick={() => {
              acao.aoClicar();
              fechar();
            }}
          >
            {acao.rotulo}
          </Botao>
        ) : null}
      </div>
      <button type="button" className={estilos.fechar} aria-label={TEXTOS_UI.fecharAviso} onClick={fechar}>
        <Icone nome="close" tamanho={20} />
      </button>
    </div>
  );
}
```

`Toast.module.css`
```css
.regiao {
  position: fixed;
  top: 80px;
  right: var(--esp-32);
  z-index: 50;
  display: flex;
  flex-direction: column;
  gap: var(--esp-12);
  width: min(380px, calc(100vw - 2 * var(--esp-16)));
  pointer-events: none;
}
.toast {
  display: flex;
  align-items: flex-start;
  gap: var(--esp-12);
  padding: 14px var(--esp-16);
  border: 1px solid var(--cor-borda);
  border-radius: 10px;
  background: var(--cor-superficie-elevada);
  box-shadow: var(--sombra-2);
  pointer-events: auto;
}
.sucesso .icone { color: var(--cor-sucesso); }
.erro .icone { color: var(--cor-erro); }
.texto { display: flex; flex: 1; flex-direction: column; gap: 2px; min-width: 0; }
.titulo { font-size: 14px; font-weight: 600; line-height: 1.4; }
.descricao { font-size: 13px; line-height: 1.45; color: var(--cor-texto-2); }
.acao { align-self: flex-start; margin: var(--esp-4) 0 0 calc(-1 * var(--esp-12)); }
.fechar {
  display: grid;
  place-items: center;
  width: 28px;
  height: 28px;
  border: 0;
  border-radius: var(--raio-sm);
  background: transparent;
  color: var(--cor-texto-2);
  cursor: pointer;
}
.fechar:hover { background: var(--cor-superficie-2); color: var(--cor-texto); }
```

**Passo 4: rodar e ver passar**
`npx vitest run src/shared/ui/ToastProvider.test.tsx` → 4 passed.

**Passo 5: commit**
```bash
git add frontend/src/shared/ui/contextoToast.ts frontend/src/shared/ui/useToast.ts frontend/src/shared/ui/ToastProvider.* frontend/src/shared/ui/ItemToast.tsx frontend/src/shared/ui/Toast.module.css
git commit -m "feat(frontend): adiciona toasts com aria-live, 6 s de duração e pausa no hover/foco"
```

---

### Tarefa 11: Campos — Select, CampoNumero, CaixaSelecao

**Arquivos:**
- Criar em `frontend/src/shared/ui/`: `Campo.module.css` (compartilhado por Select e CampoNumero), `MensagemCampo.tsx`, `Select.tsx` (+ `Select.test.tsx`), `CampoNumero.tsx` (+ `CampoNumero.test.tsx`), `CaixaSelecao.tsx`, `CaixaSelecao.module.css` (+ `CaixaSelecao.test.tsx`)

Decisões: `Select` é o `<select>` nativo estilizado (`componentes.md` permite; acessível sem biblioteca). `CampoNumero` é `type="text"` com `inputMode="decimal"` (aceita vírgula; quem usa valida com `lerNumeroPtBr`). Ajuda e erro saem de um só componente (`MensagemCampo`) para não duplicar JSX.

**Passo 1: escrever os testes (falham)**

`Select.test.tsx`
```tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { expect, it, vi } from 'vitest';
import Select from './Select';

type Decimal = 'virgula' | 'ponto' | 'outro';

const OPCOES = [
  { valor: 'virgula', rotulo: 'Vírgula ( , )' },
  { valor: 'ponto', rotulo: 'Ponto ( . )' },
  { valor: 'outro', rotulo: 'Outro', desabilitada: true },
] as const;

it('associa rótulo e ajuda e devolve o valor escolhido', async () => {
  const aoMudar = vi.fn();
  render(
    <Select<Decimal> rotulo="Decimal" valor="virgula" opcoes={OPCOES} aoMudar={aoMudar} ajuda="Valores como 1,72 e 68,4." />,
  );

  const campo = screen.getByRole('combobox', { name: 'Decimal' });
  expect(campo).toHaveValue('virgula');
  expect(campo).toHaveAccessibleDescription('Valores como 1,72 e 68,4.');
  await userEvent.selectOptions(campo, 'ponto');
  expect(aoMudar).toHaveBeenCalledWith('ponto');
  expect(screen.getByRole('option', { name: 'Outro' })).toBeDisabled();
});

it('rótulo oculto continua dando nome ao campo', () => {
  render(<Select<Decimal> rotulo="Coluna" rotuloOculto valor="ponto" opcoes={OPCOES} aoMudar={vi.fn()} />);

  expect(screen.getByRole('combobox', { name: 'Coluna' })).toBeInTheDocument();
});
```

`CampoNumero.test.tsx`
```tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { useState } from 'react';
import { expect, it } from 'vitest';
import CampoNumero from './CampoNumero';

function CampoControlado({ erro, ajuda }: Readonly<{ erro?: string; ajuda?: string }>) {
  const [valor, setValor] = useState('');
  return <CampoNumero rotulo="Valor de peso_kg" valor={valor} aoMudar={setValor} erro={erro} ajuda={ajuda} />;
}

it('aceita vírgula decimal e abre o teclado numérico', async () => {
  render(<CampoControlado ajuda="Use vírgula para decimais." />);

  const campo = screen.getByRole('textbox', { name: 'Valor de peso_kg' });
  await userEvent.type(campo, '1,72');
  expect(campo).toHaveValue('1,72');
  expect(campo).toHaveAttribute('inputmode', 'decimal');
  expect(campo).toHaveAccessibleDescription('Use vírgula para decimais.');
  expect(campo).not.toHaveAttribute('aria-invalid');
});

it('mostra o erro ligado ao campo', () => {
  render(<CampoControlado erro="Digite um número. Use vírgula para decimais, como 1,72." />);

  const campo = screen.getByRole('textbox', { name: 'Valor de peso_kg' });
  expect(campo).toHaveAttribute('aria-invalid', 'true');
  expect(campo).toHaveAccessibleDescription('Digite um número. Use vírgula para decimais, como 1,72.');
});
```

`CaixaSelecao.test.tsx`
```tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { expect, it, vi } from 'vitest';
import CaixaSelecao from './CaixaSelecao';

it('alterna pelo rótulo', async () => {
  const aoMudar = vi.fn();
  render(<CaixaSelecao rotulo="Leitura do arquivo" marcada={false} aoMudar={aoMudar} />);

  await userEvent.click(screen.getByText('Leitura do arquivo'));

  expect(aoMudar).toHaveBeenCalledWith(true);
  expect(screen.getByRole('checkbox', { name: 'Leitura do arquivo' })).not.toBeChecked();
});

it('desabilitada não muda', async () => {
  const aoMudar = vi.fn();
  render(<CaixaSelecao rotulo="Forma e distribuição" marcada desabilitada aoMudar={aoMudar} />);

  const caixa = screen.getByRole('checkbox', { name: 'Forma e distribuição' });
  await userEvent.click(caixa);

  expect(caixa).toBeDisabled();
  expect(caixa).toBeChecked();
  expect(aoMudar).not.toHaveBeenCalled();
});
```

**Passo 2: rodar e ver falhar**
`npx vitest run src/shared/ui/Select.test.tsx src/shared/ui/CampoNumero.test.tsx src/shared/ui/CaixaSelecao.test.tsx` → FAIL

**Passo 3: implementar**

`MensagemCampo.tsx`
```tsx
import campo from './Campo.module.css';
import Icone from './Icone';

interface PropsMensagemCampo {
  id: string;
  erro?: string | undefined;
  ajuda?: string | undefined;
}

/** Erro tem prioridade sobre a ajuda; formato do erro: "{o que}. {como resolver}." (spec 16). */
export default function MensagemCampo({ id, erro, ajuda }: Readonly<PropsMensagemCampo>) {
  if (erro) {
    return (
      <p id={id} className={campo.erro}>
        <Icone nome="error" tamanho={16} />
        {erro}
      </p>
    );
  }
  return ajuda ? (
    <p id={id} className={campo.ajuda}>
      {ajuda}
    </p>
  ) : null;
}
```

`Select.tsx`
```tsx
import { type ChangeEvent, useId } from 'react';
import { VISUALMENTE_OCULTO, juntarClasses } from '../lib/classes';
import campo from './Campo.module.css';
import Icone from './Icone';
import MensagemCampo from './MensagemCampo';

interface OpcaoSelect<T extends string> {
  valor: T;
  rotulo: string;
  desabilitada?: boolean | undefined;
}

interface PropsSelect<T extends string> {
  rotulo: string;
  valor: T;
  opcoes: readonly OpcaoSelect<T>[];
  aoMudar: (valor: T) => void;
  ajuda?: string | undefined;
  rotuloOculto?: boolean;
  altura?: 36 | 40 | 44;
}

const CLASSE_ALTURA = { 36: campo.altura36, 40: undefined, 44: campo.altura44 } as const;

export default function Select<T extends string>({
  rotulo,
  valor,
  opcoes,
  aoMudar,
  ajuda,
  rotuloOculto = false,
  altura = 40,
}: Readonly<PropsSelect<T>>) {
  const id = useId();
  const idAjuda = `${id}-ajuda`;
  // Recupera o valor tipado T a partir da string do DOM, sem `as`.
  const aoAlterar = (evento: ChangeEvent<HTMLSelectElement>): void => {
    const escolhida = opcoes.find((opcao) => opcao.valor === evento.target.value);
    if (escolhida) aoMudar(escolhida.valor);
  };
  return (
    <div className={campo.campo}>
      <label htmlFor={id} className={rotuloOculto ? VISUALMENTE_OCULTO : campo.rotulo}>
        {rotulo}
      </label>
      <div className={campo.caixa}>
        <select
          id={id}
          value={valor}
          onChange={aoAlterar}
          aria-describedby={ajuda ? idAjuda : undefined}
          className={juntarClasses(campo.entrada, campo.select, CLASSE_ALTURA[altura])}
        >
          {opcoes.map((opcao) => (
            <option key={opcao.valor} value={opcao.valor} disabled={opcao.desabilitada}>
              {opcao.rotulo}
            </option>
          ))}
        </select>
        <Icone nome="expand_more" tamanho={20} className={campo.seta} />
      </div>
      <MensagemCampo id={idAjuda} ajuda={ajuda} />
    </div>
  );
}
```

`CampoNumero.tsx`
```tsx
import { useId } from 'react';
import { juntarClasses } from '../lib/classes';
import campo from './Campo.module.css';
import MensagemCampo from './MensagemCampo';

interface PropsCampoNumero {
  rotulo: string;
  /** Texto digitado; quem usa converte com lerNumeroPtBr (shared/lib/formatar). */
  valor: string;
  aoMudar: (texto: string) => void;
  erro?: string | undefined;
  ajuda?: string | undefined;
}

export default function CampoNumero({ rotulo, valor, aoMudar, erro, ajuda }: Readonly<PropsCampoNumero>) {
  const id = useId();
  const idMensagem = `${id}-mensagem`;
  const temMensagem = Boolean(erro ?? ajuda);
  return (
    <div className={campo.campo}>
      <label htmlFor={id} className={campo.rotulo}>
        {rotulo}
      </label>
      <input
        id={id}
        type="text"
        inputMode="decimal"
        autoComplete="off"
        value={valor}
        onChange={(evento) => {
          aoMudar(evento.target.value);
        }}
        aria-invalid={erro ? true : undefined}
        aria-describedby={temMensagem ? idMensagem : undefined}
        className={juntarClasses(campo.entrada, campo.mono, erro ? campo.comErro : undefined)}
      />
      <MensagemCampo id={idMensagem} erro={erro} ajuda={ajuda} />
    </div>
  );
}
```

`CaixaSelecao.tsx`
```tsx
import type { ReactNode } from 'react';
import { juntarClasses } from '../lib/classes';
import estilos from './CaixaSelecao.module.css';
import Icone from './Icone';

interface PropsCaixaSelecao {
  rotulo: ReactNode;
  marcada: boolean;
  aoMudar: (marcada: boolean) => void;
  desabilitada?: boolean;
}

export default function CaixaSelecao({ rotulo, marcada, aoMudar, desabilitada = false }: Readonly<PropsCaixaSelecao>) {
  return (
    <label className={juntarClasses(estilos.caixa, desabilitada && estilos.desabilitada)}>
      <input
        type="checkbox"
        className={estilos.entrada}
        checked={marcada}
        disabled={desabilitada}
        onChange={(evento) => {
          aoMudar(evento.target.checked);
        }}
      />
      <span className={estilos.marca} aria-hidden="true">
        <Icone nome="check" tamanho={16} />
      </span>
      <span>{rotulo}</span>
    </label>
  );
}
```

`Campo.module.css` (medidas de `componentes.md` §CampoTexto/§Select)
```css
.campo { display: flex; flex-direction: column; gap: 6px; min-width: 0; }
.rotulo { font-size: 13px; font-weight: 500; color: var(--cor-texto); }
.caixa { position: relative; display: flex; align-items: center; }
.entrada {
  width: 100%;
  height: 40px;
  padding: 0 var(--esp-12);
  border: 1px solid var(--cor-borda-forte);
  border-radius: var(--raio-md);
  background: var(--cor-superficie);
  color: var(--cor-texto);
  font-size: 14px;
  transition: border-color var(--transicao), box-shadow var(--transicao);
}
.entrada:hover:not(:disabled) { border-color: var(--cor-texto-2); }
.entrada:focus-visible { border-color: var(--cor-foco); outline: 2px solid var(--cor-foco); outline-offset: 1px; }
.entrada:disabled { border-color: var(--cor-borda); background: var(--cor-superficie-2); color: var(--cor-texto-desab); cursor: not-allowed; }
.mono { font-family: var(--fonte-mono); font-size: 15px; }
.comErro,
.comErro:hover:not(:disabled) { padding: 0 11px; border: 2px solid var(--cor-erro); }
.select { padding-right: 40px; appearance: none; cursor: pointer; }
.altura36 { height: 36px; }
.altura44 { height: 44px; }
.seta { position: absolute; right: var(--esp-12); color: var(--cor-texto-2); pointer-events: none; }
.ajuda { font-size: 12.5px; line-height: 1.45; color: var(--cor-texto-2); }
.erro { display: flex; align-items: flex-start; gap: var(--esp-4); font-size: 13px; line-height: 1.45; color: var(--cor-erro); }
```

`CaixaSelecao.module.css` (não há medidas em `componentes.md`; segue os campos: borda forte, raio xs, alvo ≥ 24 px)
```css
.caixa { position: relative; display: inline-flex; align-items: center; gap: var(--esp-8); min-height: 24px; font-size: 14px; cursor: pointer; }
.entrada { position: absolute; width: 1px; height: 1px; margin: 0; opacity: 0; }
.marca {
  display: grid;
  flex: none;
  place-items: center;
  width: 18px;
  height: 18px;
  border: 1.5px solid var(--cor-borda-forte);
  border-radius: var(--raio-xs);
  background: var(--cor-superficie);
  color: transparent;
  transition: background-color var(--transicao), border-color var(--transicao);
}
.entrada:checked + .marca { border-color: var(--cor-primaria); background: var(--cor-primaria); color: var(--cor-sobre-primaria); }
.entrada:focus-visible + .marca { outline: 2px solid var(--cor-foco); outline-offset: 2px; }
.desabilitada { color: var(--cor-texto-desab); cursor: not-allowed; }
.desabilitada .marca { border-color: var(--cor-borda); background: var(--cor-superficie-2); }
.entrada:checked:disabled + .marca { border-color: var(--cor-texto-desab); background: var(--cor-texto-desab); }
```

**Passo 4: rodar e ver passar**
`npx vitest run src/shared/ui` → todos passam. `npm run lint` → sem erros.

**Passo 5: commit**
```bash
git add frontend/src/shared/ui/Campo.module.css frontend/src/shared/ui/MensagemCampo.tsx frontend/src/shared/ui/Select.* frontend/src/shared/ui/CampoNumero.* frontend/src/shared/ui/CaixaSelecao.*
git commit -m "feat(frontend): adiciona Select nativo, CampoNumero com vírgula e CaixaSelecao"
```

---

### Tarefa 12: Navegação por setas — Segmented e Abas

**Arquivos:**
- Criar em `frontend/src/shared/ui/`: `useNavegacaoPorSetas.ts` (+ `useNavegacaoPorSetas.test.ts`), `Segmented.tsx`, `Segmented.module.css` (+ `Segmented.test.tsx`), `Abas.tsx`, `Abas.module.css` (+ `Abas.test.tsx`)

`Segmented`, `Abas` e a alternância de tema (Tarefa 17) usam o mesmo hook de *roving tabindex* (WAI-ARIA): só o item ativo entra no Tab; ←/→ (e ↑/↓) andam em círculo; Home/End vão às pontas. O foco passa por itens desabilitados (para o leitor de tela ouvir o motivo no tooltip), mas só itens habilitados são selecionados.

**Passo 1: escrever os testes (falham)**

`useNavegacaoPorSetas.test.ts`
```ts
import { describe, expect, it } from 'vitest';
import { idDestino } from './useNavegacaoPorSetas';

const IDS = ['a', 'b', 'c'] as const;

describe('idDestino', () => {
  it.each([
    ['a', 'ArrowRight', 'b'],
    ['c', 'ArrowRight', 'a'],
    ['a', 'ArrowLeft', 'c'],
    ['b', 'ArrowDown', 'c'],
    ['b', 'ArrowUp', 'a'],
    ['b', 'Home', 'a'],
    ['a', 'End', 'c'],
  ])('de %s com %s vai para %s', (atual, tecla, esperado) => {
    expect(idDestino(IDS, atual, tecla)).toBe(esperado);
  });

  it('ignora outras teclas', () => {
    expect(idDestino(IDS, 'a', 'Enter')).toBeUndefined();
  });
});
```

`Segmented.test.tsx`
```tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { useState } from 'react';
import { expect, it } from 'vitest';
import Segmented from './Segmented';

type Separatriz = 'quartil' | 'decil' | 'percentil';

const OPCOES = [
  { valor: 'quartil', rotulo: 'Quartil' },
  { valor: 'decil', rotulo: 'Decil' },
  { valor: 'percentil', rotulo: 'Percentil' },
] as const;

function SegmentedControlado() {
  const [valor, setValor] = useState<Separatriz>('quartil');
  return <Segmented rotulo="Tipo de separatriz" opcoes={OPCOES} valor={valor} aoMudar={setValor} />;
}

it('é um grupo de rádios com a opção atual marcada', async () => {
  render(<SegmentedControlado />);

  expect(screen.getByRole('radiogroup', { name: 'Tipo de separatriz' })).toBeInTheDocument();
  expect(screen.getByRole('radio', { name: 'Quartil' })).toHaveAttribute('aria-checked', 'true');
  await userEvent.click(screen.getByRole('radio', { name: 'Decil' }));
  expect(screen.getByRole('radio', { name: 'Decil' })).toHaveAttribute('aria-checked', 'true');
});

it('setas mudam a opção e o foco, em círculo; só a marcada entra no Tab', async () => {
  render(<SegmentedControlado />);

  await userEvent.tab();
  expect(screen.getByRole('radio', { name: 'Quartil' })).toHaveFocus();
  await userEvent.keyboard('{ArrowLeft}');
  const percentil = screen.getByRole('radio', { name: 'Percentil' });
  expect(percentil).toHaveFocus();
  expect(percentil).toHaveAttribute('aria-checked', 'true');
  expect(screen.getByRole('radio', { name: 'Quartil' })).toHaveAttribute('tabindex', '-1');
});
```

`Abas.test.tsx`
```tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { useState } from 'react';
import { expect, it } from 'vitest';
import Abas from './Abas';

const ABAS = [
  { id: 'frequencias', rotulo: 'Frequências' },
  { id: 'tendencia', rotulo: 'Tendência central' },
  {
    id: 'separatrizes',
    rotulo: 'Separatrizes',
    desabilitada: true,
    motivo: 'Separatrizes não se aplicam a Qualitativa nominal: as categorias não têm ordem.',
  },
  { id: 'dispersao', rotulo: 'Dispersão' },
] as const;

type IdAba = (typeof ABAS)[number]['id'];

function AbasControladas() {
  const [ativa, setAtiva] = useState<IdAba>('frequencias');
  return (
    <Abas rotulo="Análises da coluna" abas={ABAS} ativa={ativa} aoMudar={setAtiva}>
      <p>Conteúdo de {ativa}</p>
    </Abas>
  );
}

it('liga a aba ativa ao painel', async () => {
  render(<AbasControladas />);

  expect(screen.getByRole('tablist', { name: 'Análises da coluna' })).toBeInTheDocument();
  expect(screen.getByRole('tab', { name: 'Frequências' })).toHaveAttribute('aria-selected', 'true');
  expect(screen.getByRole('tabpanel', { name: 'Frequências' })).toHaveTextContent('Conteúdo de frequencias');
  await userEvent.click(screen.getByRole('tab', { name: 'Tendência central' }));
  expect(screen.getByRole('tabpanel', { name: 'Tendência central' })).toHaveTextContent('Conteúdo de tendencia');
});

it('setas passam pela aba desabilitada sem selecioná-la', async () => {
  render(<AbasControladas />);
  await userEvent.click(screen.getByRole('tab', { name: 'Tendência central' }));

  await userEvent.keyboard('{ArrowRight}');
  expect(screen.getByRole('tab', { name: 'Separatrizes' })).toHaveFocus();
  expect(screen.getByRole('tab', { name: 'Tendência central' })).toHaveAttribute('aria-selected', 'true');

  await userEvent.keyboard('{ArrowRight}');
  expect(screen.getByRole('tab', { name: 'Dispersão' })).toHaveAttribute('aria-selected', 'true');

  await userEvent.keyboard('{Home}');
  expect(screen.getByRole('tab', { name: 'Frequências' })).toHaveAttribute('aria-selected', 'true');
});

it('aba desabilitada não abre e explica o motivo no tooltip', async () => {
  render(<AbasControladas />);
  const desabilitada = screen.getByRole('tab', { name: 'Separatrizes' });

  await userEvent.click(desabilitada);
  await userEvent.hover(desabilitada);

  expect(desabilitada).toHaveAttribute('aria-disabled', 'true');
  expect(screen.getByRole('tab', { name: 'Frequências' })).toHaveAttribute('aria-selected', 'true');
  expect(screen.getByRole('tooltip')).toHaveTextContent('as categorias não têm ordem.');
});
```

**Passo 2: rodar e ver falhar**
`npx vitest run src/shared/ui/useNavegacaoPorSetas.test.ts src/shared/ui/Segmented.test.tsx src/shared/ui/Abas.test.tsx` → FAIL

**Passo 3: implementar**

`useNavegacaoPorSetas.ts`
```ts
import { type KeyboardEvent, useRef } from 'react';

const PASSO_POR_TECLA: Readonly<Partial<Record<string, number>>> = {
  ArrowRight: 1,
  ArrowDown: 1,
  ArrowLeft: -1,
  ArrowUp: -1,
};

export interface PropsItemNavegavel {
  ref: (elemento: HTMLElement | null) => void;
  tabIndex: 0 | -1;
  onKeyDown: (evento: KeyboardEvent<HTMLElement>) => void;
}

interface OpcoesNavegacao<T extends string> {
  ids: readonly T[];
  ativo: T;
  aoMudar: (id: T) => void;
  habilitado?: (id: T) => boolean;
}

/** Destino da tecla: setas andam em círculo; Home/End vão às pontas; outras teclas → undefined. */
export function idDestino<T>(ids: readonly T[], atual: T, tecla: string): T | undefined {
  if (tecla === 'Home') return ids[0];
  if (tecla === 'End') return ids.at(-1);
  const passo = PASSO_POR_TECLA[tecla];
  const indice = ids.indexOf(atual);
  if (passo === undefined || indice < 0) return undefined;
  return ids[(indice + passo + ids.length) % ids.length];
}

const sempreHabilitado = (): boolean => true;

/** Roving tabindex (WAI-ARIA). Devolve as props de cada item: `<button {...propsItem(id)} />`. */
export function useNavegacaoPorSetas<T extends string>({
  ids,
  ativo,
  aoMudar,
  habilitado = sempreHabilitado,
}: OpcoesNavegacao<T>): (id: T) => PropsItemNavegavel {
  const elementos = useRef(new Map<T, HTMLElement>());
  return (id: T) => ({
    ref: (elemento) => {
      if (elemento) {
        elementos.current.set(id, elemento);
      } else {
        elementos.current.delete(id);
      }
    },
    tabIndex: id === ativo ? 0 : -1,
    onKeyDown: (evento) => {
      const destino = idDestino(ids, id, evento.key);
      if (destino === undefined) return;
      evento.preventDefault();
      elementos.current.get(destino)?.focus();
      if (habilitado(destino)) aoMudar(destino);
    },
  });
}
```

`Segmented.tsx`
```tsx
import { juntarClasses } from '../lib/classes';
import estilos from './Segmented.module.css';
import { useNavegacaoPorSetas } from './useNavegacaoPorSetas';

interface OpcaoSegmented<T extends string> {
  valor: T;
  rotulo: string;
  selo?: string | undefined;
}

interface PropsSegmented<T extends string> {
  rotulo: string;
  opcoes: readonly OpcaoSegmented<T>[];
  valor: T;
  aoMudar: (valor: T) => void;
}

export default function Segmented<T extends string>({ rotulo, opcoes, valor, aoMudar }: Readonly<PropsSegmented<T>>) {
  const propsItem = useNavegacaoPorSetas({ ids: opcoes.map((opcao) => opcao.valor), ativo: valor, aoMudar });
  return (
    <div role="radiogroup" aria-label={rotulo} className={estilos.grupo}>
      {opcoes.map((opcao) => (
        <button
          key={opcao.valor}
          {...propsItem(opcao.valor)}
          type="button"
          role="radio"
          aria-checked={opcao.valor === valor}
          className={juntarClasses(estilos.opcao, opcao.valor === valor && estilos.selecionada)}
          onClick={() => {
            aoMudar(opcao.valor);
          }}
        >
          {opcao.rotulo}
          {opcao.selo ? <span className={estilos.selo}>{opcao.selo}</span> : null}
        </button>
      ))}
    </div>
  );
}
```

`Abas.tsx`
```tsx
import { type ReactNode, useId } from 'react';
import { juntarClasses } from '../lib/classes';
import estilos from './Abas.module.css';
import Icone from './Icone';
import Tooltip from './Tooltip';
import { type PropsItemNavegavel, useNavegacaoPorSetas } from './useNavegacaoPorSetas';

export interface DefinicaoAba<T extends string> {
  id: T;
  rotulo: string;
  desabilitada?: boolean | undefined;
  /** Texto do tooltip da aba desabilitada (D46): "{medida} não se aplica a {tipo}: {motivo}." */
  motivo?: string | undefined;
}

interface PropsAbas<T extends string> {
  rotulo: string;
  abas: readonly DefinicaoAba<T>[];
  ativa: T;
  aoMudar: (id: T) => void;
  children: ReactNode;
}

export default function Abas<T extends string>({ rotulo, abas, ativa, aoMudar, children }: Readonly<PropsAbas<T>>) {
  const prefixo = useId();
  const propsItem = useNavegacaoPorSetas({
    ids: abas.map((aba) => aba.id),
    ativo: ativa,
    aoMudar,
    habilitado: (id) => abas.find((aba) => aba.id === id)?.desabilitada !== true,
  });
  return (
    <div>
      <div role="tablist" aria-label={rotulo} className={estilos.lista}>
        {abas.map((aba) => (
          <ItemAba
            key={aba.id}
            aba={aba}
            ativa={aba.id === ativa}
            prefixo={prefixo}
            propsNavegacao={propsItem(aba.id)}
            aoAtivar={aoMudar}
          />
        ))}
      </div>
      <div
        role="tabpanel"
        id={`${prefixo}painel`}
        aria-labelledby={`${prefixo}${ativa}`}
        tabIndex={0}
        className={estilos.painel}
      >
        {children}
      </div>
    </div>
  );
}

interface PropsItemAba<T extends string> {
  aba: DefinicaoAba<T>;
  ativa: boolean;
  prefixo: string;
  propsNavegacao: PropsItemNavegavel;
  aoAtivar: (id: T) => void;
}

function ItemAba<T extends string>({ aba, ativa, prefixo, propsNavegacao, aoAtivar }: Readonly<PropsItemAba<T>>) {
  const desabilitada = aba.desabilitada === true;
  const botao = (
    <button
      {...propsNavegacao}
      type="button"
      role="tab"
      id={`${prefixo}${aba.id}`}
      aria-selected={ativa}
      aria-controls={ativa ? `${prefixo}painel` : undefined}
      aria-disabled={desabilitada}
      className={juntarClasses(estilos.aba, ativa && estilos.ativa, desabilitada && estilos.desabilitada)}
      onClick={() => {
        if (!desabilitada) aoAtivar(aba.id);
      }}
    >
      {desabilitada ? <Icone nome="block" tamanho={16} /> : null}
      {aba.rotulo}
    </button>
  );
  return desabilitada && aba.motivo ? <Tooltip texto={aba.motivo}>{botao}</Tooltip> : botao;
}
```

`Segmented.module.css`
```css
.grupo { display: inline-flex; gap: 2px; padding: 3px; border: 1px solid var(--cor-borda); border-radius: var(--raio-md); background: var(--cor-superficie-2); }
.opcao {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  height: 32px;
  padding: 0 14px;
  border: 0;
  border-radius: var(--raio-sm);
  background: transparent;
  color: var(--cor-texto-2);
  font-size: 14px;
  cursor: pointer;
  transition: background-color var(--transicao), color var(--transicao);
}
.opcao:hover { color: var(--cor-texto); }
.selecionada { background: var(--cor-superficie); box-shadow: var(--sombra-1); color: var(--cor-texto); font-weight: 600; }
.selo { padding: 1px 6px; border-radius: var(--raio-xs); background: var(--cor-primaria-suave); color: var(--cor-primaria); font-size: 11.5px; font-weight: 600; }
```

`Abas.module.css` (sem `overflow` na lista: cortaria o tooltip; em telas estreitas as abas quebram linha)
```css
.lista { display: flex; flex-wrap: wrap; gap: var(--esp-4); border-bottom: 1px solid var(--cor-borda); }
.aba {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  height: 44px;
  padding: 0 14px;
  border: 0;
  background: transparent;
  color: var(--cor-texto-2);
  font-size: 14px;
  white-space: nowrap;
  cursor: pointer;
  transition: color var(--transicao), box-shadow var(--transicao);
}
.aba:hover { color: var(--cor-texto); }
.ativa,
.ativa:hover { box-shadow: inset 0 -2px 0 var(--cor-primaria); color: var(--cor-primaria); font-weight: 600; }
.desabilitada,
.desabilitada:hover { color: var(--cor-texto-desab); cursor: not-allowed; }
.painel { padding-top: var(--esp-20); }
.painel:focus-visible { outline-offset: 4px; }
```

**Passo 4: rodar e ver passar**
`npx vitest run src/shared/ui` → todos passam. `npm run lint` → sem erros. Rode também `npx --yes jscpd@4 frontend/src` na raiz: Segmented e Abas não podem ter clones.

**Passo 5: commit**
```bash
git add frontend/src/shared/ui/useNavegacaoPorSetas.* frontend/src/shared/ui/Segmented.* frontend/src/shared/ui/Abas.*
git commit -m "feat(frontend): adiciona Segmented e Abas com navegação por setas e aba desabilitada com motivo"
```

---

### Tarefa 13: Dados — CardMetrica e Tabela

**Arquivos:**
- Criar em `frontend/src/shared/ui/`: `CardMetrica.tsx`, `CardMetrica.module.css` (+ `CardMetrica.test.tsx`), `Tabela.tsx`, `Tabela.module.css` (+ `Tabela.test.tsx`)

Extensão do contrato: `ColunaTabela` ganha `cabecalhoLinha?: boolean` (a célula vira `<th scope="row">`, ex.: "Q1", classe de frequência). A linha destacada recebe `data-destacada="true"` (o CSS usa o atributo; o teste também).

**Passo 1: escrever os testes (falham)**

`CardMetrica.test.tsx`
```tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { expect, it } from 'vitest';
import CardMetrica from './CardMetrica';

it('mostra rótulo, valor com unidade, selo e interpretação', () => {
  render(
    <CardMetrica
      rotulo="Coeficiente de variação"
      valor="14,2"
      unidade="%"
      selo="Variação moderada"
      interpretacao="Os pesos variam cerca de 14% em torno da média."
    />,
  );

  const card = screen.getByRole('article');
  expect(screen.getByRole('heading', { name: 'Coeficiente de variação' })).toBeInTheDocument();
  expect(card).toHaveTextContent('14,2%');
  expect(card).toHaveTextContent('Variação moderada');
  expect(card).toHaveTextContent('Os pesos variam cerca de 14% em torno da média.');
});

it('abre e fecha a fórmula', async () => {
  render(
    <CardMetrica
      rotulo="Média"
      valor="70,3"
      unidade="kg"
      formula={{ expressao: 'x̄ = Σxᵢ / n', calculo: '16.150,1 / 227 = 70,3' }}
    />,
  );

  await userEvent.click(screen.getByRole('button', { name: 'Ver fórmula' }));
  expect(screen.getByRole('button', { name: 'Ocultar fórmula' })).toHaveAttribute('aria-expanded', 'true');
  expect(screen.getByText('x̄ = Σxᵢ / n')).toBeVisible();
  expect(screen.getByText('16.150,1 / 227 = 70,3')).toBeVisible();

  await userEvent.click(screen.getByRole('button', { name: 'Ocultar fórmula' }));
  expect(screen.getByText('x̄ = Σxᵢ / n')).not.toBeVisible();
});

it('não aplicável fica esmaecido com motivo e sem fórmula', () => {
  render(
    <CardMetrica
      rotulo="Média"
      valor="70,3"
      formula={{ expressao: 'x̄ = Σxᵢ / n' }}
      naoAplicavel={{ motivo: 'Média não se aplica a Qualitativa nominal: as categorias não são números.' }}
    />,
  );

  const card = screen.getByRole('article');
  expect(card).toHaveTextContent('Não se aplica');
  expect(card).toHaveTextContent('as categorias não são números.');
  expect(card).not.toHaveTextContent('70,3');
  expect(screen.queryByRole('button', { name: 'Ver fórmula' })).not.toBeInTheDocument();
});
```

`Tabela.test.tsx`
```tsx
import { render, screen, within } from '@testing-library/react';
import { expect, it } from 'vitest';
import Tabela, { type ColunaTabela } from './Tabela';

interface Linha {
  classe: string;
  fi: number;
}

const COLUNAS: readonly ColunaTabela<Linha>[] = [
  { id: 'classe', titulo: 'Classe (kg)', celula: (linha) => linha.classe, mono: true, cabecalhoLinha: true },
  { id: 'fi', titulo: 'fi', celula: (linha) => linha.fi, alinhamento: 'direita' },
];

const LINHAS: readonly Linha[] = [
  { classe: '60,0 ⊢ 65,5', fi: 12 },
  { classe: '65,5 ⊢ 71,0', fi: 30 },
];

it('monta a tabela com legenda, cabeçalhos com scope e linha destacada', () => {
  render(
    <Tabela
      legenda="Frequências de peso_kg"
      colunas={COLUNAS}
      linhas={LINHAS}
      chave={(linha) => linha.classe}
      destacada={(linha) => linha.fi === 30}
      rodape="Total: 42"
    />,
  );

  const tabela = screen.getByRole('table', { name: 'Frequências de peso_kg' });
  expect(within(tabela).getByRole('columnheader', { name: 'Classe (kg)' })).toHaveAttribute('scope', 'col');
  expect(within(tabela).getByRole('rowheader', { name: '65,5 ⊢ 71,0' })).toHaveAttribute('scope', 'row');
  expect(within(tabela).getByRole('cell', { name: '30' })).toBeInTheDocument();
  const linhas = within(tabela).getAllByRole('row');
  expect(linhas[2]).toHaveAttribute('data-destacada', 'true');
  expect(linhas[1]).not.toHaveAttribute('data-destacada');
  expect(screen.getByText('Total: 42')).toBeInTheDocument();
});

it('com altura máxima a rolagem vira região focável', () => {
  render(
    <Tabela legenda="Prévia" colunas={COLUNAS} linhas={LINHAS} chave={(linha) => linha.classe} alturaMaxima={520} />,
  );

  expect(screen.getByRole('region', { name: 'Prévia' })).toHaveAttribute('tabindex', '0');
});
```

**Passo 2: rodar e ver falhar**
`npx vitest run src/shared/ui/CardMetrica.test.tsx src/shared/ui/Tabela.test.tsx` → FAIL

**Passo 3: implementar**

`CardMetrica.tsx`
```tsx
import { useId, useState } from 'react';
import { juntarClasses } from '../lib/classes';
import Botao from './Botao';
import estilos from './CardMetrica.module.css';
import { TEXTOS_UI } from './textos';

interface FormulaMetrica {
  expressao: string;
  calculo?: string | undefined;
}

interface PropsCardMetrica {
  rotulo: string;
  valor: string;
  unidade?: string | undefined;
  interpretacao?: string | undefined;
  selo?: string | undefined;
  formula?: FormulaMetrica | undefined;
  /** Motivo já no formato da spec 16: "{medida} não se aplica a {tipo}: {motivo}." */
  naoAplicavel?: { motivo: string } | undefined;
}

export default function CardMetrica({ naoAplicavel, ...props }: Readonly<PropsCardMetrica>) {
  if (naoAplicavel) return <CardNaoAplicavel rotulo={props.rotulo} motivo={naoAplicavel.motivo} />;
  return <CardAplicavel {...props} />;
}

function CardAplicavel({ rotulo, valor, unidade, interpretacao, selo, formula }: Readonly<Omit<PropsCardMetrica, 'naoAplicavel'>>) {
  return (
    <article className={estilos.card}>
      <h3 className={estilos.rotulo}>{rotulo}</h3>
      <p className={estilos.valor}>
        {valor}
        {unidade ? <span className={estilos.unidade}>{unidade}</span> : null}
      </p>
      {selo ? <span className={estilos.selo}>{selo}</span> : null}
      {interpretacao ? <p className={estilos.interpretacao}>{interpretacao}</p> : null}
      {formula ? <FormulaRecolhivel formula={formula} /> : null}
    </article>
  );
}

function FormulaRecolhivel({ formula }: Readonly<{ formula: FormulaMetrica }>) {
  const [aberta, setAberta] = useState(false);
  const id = useId();
  return (
    <>
      <Botao
        variante="fantasma"
        tamanho="sm"
        className={estilos.botaoFormula}
        iconeFinal={aberta ? 'expand_less' : 'expand_more'}
        aria-expanded={aberta}
        aria-controls={id}
        onClick={() => {
          setAberta((atual) => !atual);
        }}
      >
        {aberta ? TEXTOS_UI.ocultarFormula : TEXTOS_UI.verFormula}
      </Botao>
      <div id={id} className={estilos.formula} hidden={!aberta}>
        <p className={estilos.expressao}>{formula.expressao}</p>
        {formula.calculo ? <p className={estilos.calculo}>{formula.calculo}</p> : null}
      </div>
    </>
  );
}

function CardNaoAplicavel({ rotulo, motivo }: Readonly<{ rotulo: string; motivo: string }>) {
  return (
    <article className={juntarClasses(estilos.card, estilos.naoAplicavel)}>
      <div className={estilos.topo}>
        <h3 className={estilos.rotulo}>{rotulo}</h3>
        <span className={estilos.seloNaoAplica}>{TEXTOS_UI.naoSeAplica}</span>
      </div>
      <p className={juntarClasses(estilos.valor, estilos.ausente)} aria-hidden="true">
        {TEXTOS_UI.valorAusente}
      </p>
      <p className={estilos.motivo}>{motivo}</p>
    </article>
  );
}
```

`CardMetrica.module.css`
```css
.card {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 18px var(--esp-20);
  border: 1px solid var(--cor-borda);
  border-radius: var(--raio-lg);
  background: var(--cor-superficie);
  box-shadow: var(--sombra-1);
}
.topo { display: flex; align-items: center; justify-content: space-between; gap: var(--esp-8); }
.rotulo { font-size: 13px; font-weight: 500; color: var(--cor-texto-2); }
.valor { font: 600 32px/1.1 var(--fonte-mono); letter-spacing: -0.02em; font-variant-numeric: tabular-nums; }
.unidade { margin-left: 6px; font: 500 16px var(--fonte-texto); letter-spacing: 0; color: var(--cor-texto-2); }
.selo { align-self: flex-start; padding: 2px var(--esp-8); border-radius: var(--raio-sm); background: var(--cor-primaria-suave); color: var(--cor-primaria); font-size: 12.5px; font-weight: 600; }
.interpretacao { font-size: 14px; line-height: 1.5; }
.botaoFormula { align-self: flex-start; margin-left: calc(-1 * var(--esp-12)); }
.formula { display: flex; flex-direction: column; gap: var(--esp-4); padding: var(--esp-12) 14px; border-radius: var(--raio-md); background: var(--cor-superficie-2); }
.formula[hidden] { display: none; }
.expressao { font: 500 16px/1.5 var(--fonte-mono); text-align: center; }
.calculo { font: 400 12.5px/1.5 var(--fonte-mono); color: var(--cor-texto-2); text-align: center; }
.naoAplicavel { border-style: dashed; border-color: var(--cor-borda-forte); background: var(--cor-superficie-2); box-shadow: none; }
.seloNaoAplica { padding: 1px 6px; border: 1px solid var(--cor-borda-forte); border-radius: var(--raio-xs); color: var(--cor-texto-2); font-size: 11.5px; font-weight: 600; }
.ausente { color: var(--cor-texto-desab); }
.motivo { font-size: 14px; color: var(--cor-texto-2); }
```
Atenção: `.formula[hidden]` é obrigatório, porque `.formula` define `display: flex` e venceria o atributo `hidden`.

`Tabela.tsx`
```tsx
import type { ReactNode } from 'react';
import { VISUALMENTE_OCULTO, juntarClasses } from '../lib/classes';
import estilos from './Tabela.module.css';

export interface ColunaTabela<L> {
  id: string;
  titulo: ReactNode;
  celula: (linha: L) => ReactNode;
  alinhamento?: 'esquerda' | 'direita';
  mono?: boolean;
  /** A célula vira <th scope="row"> (rótulo da linha). */
  cabecalhoLinha?: boolean;
}

interface PropsTabela<L> {
  legenda: string;
  colunas: readonly ColunaTabela<L>[];
  linhas: readonly L[];
  chave: (linha: L) => string;
  alturaMaxima?: number | undefined;
  destacada?: ((linha: L) => boolean) | undefined;
  rodape?: ReactNode;
}

function classeAlinhamento<L>(coluna: ColunaTabela<L>): string | undefined {
  return coluna.alinhamento === 'direita' ? estilos.direita : undefined;
}

function classesDaCelula<L>(coluna: ColunaTabela<L>): string {
  return juntarClasses(classeAlinhamento(coluna), coluna.mono === true && estilos.mono);
}

export default function Tabela<L>({ legenda, colunas, linhas, chave, alturaMaxima, destacada, rodape }: Readonly<PropsTabela<L>>) {
  const rolavel = alturaMaxima !== undefined;
  return (
    <div className={estilos.moldura}>
      <div
        className={estilos.rolagem}
        style={rolavel ? { maxHeight: alturaMaxima } : undefined}
        role={rolavel ? 'region' : undefined}
        aria-label={rolavel ? legenda : undefined}
        tabIndex={rolavel ? 0 : undefined}
      >
        <table className={estilos.tabela}>
          <caption className={VISUALMENTE_OCULTO}>{legenda}</caption>
          <thead>
            <tr>
              {colunas.map((coluna) => (
                <th key={coluna.id} scope="col" className={classeAlinhamento(coluna)}>
                  {coluna.titulo}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {linhas.map((linha) => (
              <LinhaTabela key={chave(linha)} linha={linha} colunas={colunas} destacada={destacada?.(linha) === true} />
            ))}
          </tbody>
        </table>
      </div>
      {rodape === undefined ? null : <div className={estilos.rodape}>{rodape}</div>}
    </div>
  );
}

interface PropsLinhaTabela<L> {
  linha: L;
  colunas: readonly ColunaTabela<L>[];
  destacada: boolean;
}

function LinhaTabela<L>({ linha, colunas, destacada }: Readonly<PropsLinhaTabela<L>>) {
  return (
    <tr data-destacada={destacada || undefined}>
      {colunas.map((coluna) =>
        coluna.cabecalhoLinha === true ? (
          <th key={coluna.id} scope="row" className={classesDaCelula(coluna)}>
            {coluna.celula(linha)}
          </th>
        ) : (
          <td key={coluna.id} className={classesDaCelula(coluna)}>
            {coluna.celula(linha)}
          </td>
        ),
      )}
    </tr>
  );
}
```
Mais de 200 linhas → virtualizar (`componentes.md`); não é o caso no M1 (prévia de 20 linhas, páginas de 20). Fica para quando uma tela precisar.

`Tabela.module.css`
```css
.moldura { overflow: hidden; border: 1px solid var(--cor-borda); border-radius: var(--raio-lg); background: var(--cor-superficie); }
.rolagem { overflow: auto; }
.tabela { width: 100%; border-collapse: separate; border-spacing: 0; font-size: 14px; font-variant-numeric: tabular-nums; }
.tabela thead th {
  position: sticky;
  top: 0;
  z-index: 1;
  padding: 10px var(--esp-16);
  border-bottom: 1px solid var(--cor-borda-forte);
  background: var(--cor-superficie-2);
  font-size: 12.5px;
  font-weight: 600;
  text-align: left;
  white-space: nowrap;
}
.tabela td,
.tabela tbody th { padding: var(--esp-8) var(--esp-16); font-weight: 400; text-align: left; }
.tabela tbody tr:nth-child(even) { background: var(--cor-zebra); }
.tabela tbody tr[data-destacada='true'] { background: var(--cor-destaque-linha); font-weight: 600; }
.tabela tbody tr[data-destacada='true'] > :first-child { box-shadow: inset 3px 0 0 var(--sev-atencao); }
.tabela .direita { text-align: right; }
.tabela .mono { font-family: var(--fonte-mono); font-size: 13.5px; }
.rodape { display: flex; align-items: center; justify-content: space-between; gap: var(--esp-16); padding: 10px var(--esp-16); border-top: 1px solid var(--cor-borda); color: var(--cor-texto-2); font-size: 13px; }
```

**Passo 4: rodar e ver passar**
`npx vitest run src/shared/ui` → todos passam. `npm run lint` → sem erros.

**Passo 5: commit**
```bash
git add frontend/src/shared/ui/CardMetrica.* frontend/src/shared/ui/Tabela.*
git commit -m "feat(frontend): adiciona CardMetrica com fórmula recolhível e Tabela acessível com cabeçalho fixo"
```

---

### Tarefa 14: Wrapper Plotly (D63)

**Arquivos:**
- Criar em `frontend/src/shared/graficos/`: `temaPlotly.ts` (+ `temaPlotly.test.ts`), `GraficoPlotly.tsx`, `Grafico.tsx`, `Grafico.module.css` (+ `Grafico.test.tsx`)

Como funciona (`docs/design/graficos-plotly.md`, ADR 0003/0008):
- A figura vem do backend como `Record<string, unknown>` (`{data, layout}`, sem template). `extrairFigura` tira `data`/`layout` por narrowing e **copia** `data` com `structuredClone` (o Plotly escreve nos traces e não pode mexer no cache do react-query).
- `layoutTema(tokens)` é função pura; `mesclarLayout(figuraLayout, tema)` faz mescla profunda em que **a figura vence** (títulos de eixo, `barmode`) e o tema completa cores e fontes. Arrays não são mesclados (a figura troca o do tema).
- `GraficoPlotly` (carregado com `React.lazy`) lê os tokens com `getComputedStyle` na montagem. `Grafico` passa `key={tema}`: trocar o tema remonta o gráfico e relê os tokens. Remontar é mais caro que `Plotly.react`, mas acontece só quando o usuário troca o tema, e evita lógica de diff (o `TemaProvider` aplica `data-tema` antes do render, Tarefa 4).
- Título fora do Plotly (`<figcaption>`), resumo abaixo, `aria-label` e `aria-describedby` no `<figure>`.

**Passo 1: escrever os testes (falham)**

`temaPlotly.test.ts`
```ts
import { describe, expect, it, vi } from 'vitest';
import { type TokensGrafico, extrairFigura, layoutTema, lerTokensGrafico, mesclarLayout } from './temaPlotly';

const TOKENS: TokensGrafico = {
  texto: '#161a20',
  texto2: '#4b5462',
  fundo: '#ffffff',
  grade: '#e6e9ee',
  eixo: '#868f9c',
  series: ['#0b6aa8', '#c4520a'],
  fonte: 'Inter, system-ui, sans-serif',
};

describe('layoutTema', () => {
  it('aplica cores, separadores pt-BR e paleta', () => {
    const layout = layoutTema(TOKENS);

    expect(layout).toMatchObject({
      paper_bgcolor: '#ffffff',
      plot_bgcolor: '#ffffff',
      separators: ',.',
      colorway: ['#0b6aa8', '#c4520a'],
      font: { family: 'Inter, system-ui, sans-serif', size: 12, color: '#4b5462' },
      xaxis: { gridcolor: '#e6e9ee', linecolor: '#868f9c', zeroline: false },
    });
  });

  it('não compartilha objetos entre os eixos', () => {
    const layout = layoutTema(TOKENS);

    expect(layout.xaxis).not.toBe(layout.yaxis);
  });
});

describe('mesclarLayout', () => {
  it('mantém o que a figura define e completa com o tema', () => {
    const figura = { xaxis: { title: { text: 'peso_kg' } }, barmode: 'overlay', colorway: ['#000000'] };

    const layout = mesclarLayout(figura, layoutTema(TOKENS));

    expect(layout).toMatchObject({
      barmode: 'overlay',
      colorway: ['#000000'],
      xaxis: { gridcolor: '#e6e9ee', title: { text: 'peso_kg', font: { size: 13, color: '#161a20' } } },
    });
  });
});

describe('extrairFigura', () => {
  it('extrai data e layout e copia os traces', () => {
    const traces = [{ type: 'bar', x: [1, 2], y: [3, 4] }];
    const figura = { data: traces, layout: { title: 'x' } };

    const extraida = extrairFigura(figura);

    expect(extraida).toEqual({ data: traces, layout: { title: 'x' } });
    expect(extraida.data).not.toBe(traces);
  });

  it('usa vazios quando o formato não confere', () => {
    expect(extrairFigura({ data: 'x', layout: [1] })).toEqual({ data: [], layout: {} });
  });
});

describe('lerTokensGrafico', () => {
  it('lê as variáveis CSS do documento', () => {
    vi.spyOn(window, 'getComputedStyle').mockReturnValue({
      getPropertyValue: (nome: string) => ` valor${nome} `,
    } as CSSStyleDeclaration);

    const tokens = lerTokensGrafico();

    expect(tokens.fundo).toBe('valor--graf-fundo');
    expect(tokens.series).toHaveLength(8);
    expect(tokens.series[0]).toBe('valor--graf-1');
  });
});
```

`Grafico.test.tsx`
```tsx
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { expect, it, vi } from 'vitest';
import TemaProvider from '../tema/TemaProvider';
import { useTema } from '../tema/useTema';
import Grafico from './Grafico';

const { montagens } = vi.hoisted(() => ({ montagens: vi.fn() }));

// Sem JSX no factory: o vi.mock é içado antes dos imports.
vi.mock('./GraficoPlotly', async () => {
  const { createElement, useEffect } = await import('react');
  function GraficoPlotlyFalso() {
    useEffect(() => {
      montagens();
    }, []);
    return createElement('div', { 'data-testid': 'grafico-plotly' });
  }
  return { default: GraficoPlotlyFalso };
});

function BotaoEscuro() {
  const { definirTema } = useTema();
  return (
    <button
      type="button"
      onClick={() => {
        definirTema('escuro');
      }}
    >
      escuro
    </button>
  );
}

function renderizar() {
  render(
    <TemaProvider>
      <BotaoEscuro />
      <Grafico
        titulo="Distribuição de peso_kg (n = 227)"
        resumo="A maior parte das pessoas pesa entre 60 e 80 kg."
        figura={{ data: [], layout: {} }}
      />
    </TemaProvider>,
  );
}

it('tem título, resumo e carrega o Plotly sob demanda', async () => {
  renderizar();

  const figura = screen.getByRole('figure', { name: 'Distribuição de peso_kg (n = 227)' });
  expect(figura).toHaveAccessibleDescription('A maior parte das pessoas pesa entre 60 e 80 kg.');
  expect(await screen.findByTestId('grafico-plotly')).toBeInTheDocument();
});

it('remonta o gráfico quando o tema muda', async () => {
  montagens.mockClear();
  renderizar();
  await screen.findByTestId('grafico-plotly');
  expect(montagens).toHaveBeenCalledTimes(1);

  await userEvent.click(screen.getByRole('button', { name: 'escuro' }));

  await waitFor(() => {
    expect(montagens).toHaveBeenCalledTimes(2);
  });
});
```

**Passo 2: rodar e ver falhar**
`npx vitest run src/shared/graficos` → FAIL

**Passo 3: implementar**

`temaPlotly.ts`
```ts
/** Tema Plotly a partir dos tokens CSS (docs/design/graficos-plotly.md). Funções puras, exceto lerTokensGrafico. */

type Objeto = Record<string, unknown>;

export interface TokensGrafico {
  texto: string;
  texto2: string;
  fundo: string;
  grade: string;
  eixo: string;
  series: readonly string[];
  fonte: string;
}

export interface FiguraPlotly {
  data: unknown[];
  layout: Objeto;
}

const VARIAVEIS_SERIES = ['--graf-1', '--graf-2', '--graf-3', '--graf-4', '--graf-5', '--graf-6', '--graf-7', '--graf-8'] as const;

export const CONFIG_PLOTLY = {
  displaylogo: false,
  responsive: true,
  locale: 'pt-BR',
  modeBarButtonsToRemove: ['lasso2d', 'select2d'],
} as const;

export function lerTokensGrafico(raiz: Element = document.documentElement): TokensGrafico {
  const estilo = window.getComputedStyle(raiz);
  const ler = (variavel: string): string => estilo.getPropertyValue(variavel).trim();
  return {
    texto: ler('--cor-texto'),
    texto2: ler('--cor-texto-2'),
    fundo: ler('--graf-fundo'),
    grade: ler('--graf-grade'),
    eixo: ler('--graf-eixo'),
    series: VARIAVEIS_SERIES.map((variavel) => ler(variavel)),
    fonte: ler('--fonte-texto'),
  };
}

function criarEixo(tokens: TokensGrafico): Objeto {
  return {
    gridcolor: tokens.grade,
    linecolor: tokens.eixo,
    zeroline: false,
    ticks: '',
    title: { font: { size: 13, color: tokens.texto } },
  };
}

export function layoutTema(tokens: TokensGrafico): Objeto {
  return {
    font: { family: tokens.fonte, size: 12, color: tokens.texto2 },
    paper_bgcolor: tokens.fundo,
    plot_bgcolor: tokens.fundo,
    colorway: [...tokens.series],
    separators: ',.',
    margin: { l: 60, r: 16, t: 32, b: 48 },
    xaxis: criarEixo(tokens),
    yaxis: criarEixo(tokens),
    legend: { orientation: 'h', x: 0, y: 1.12, font: { size: 12, color: tokens.texto } },
    bargap: 0.04,
    hoverlabel: { font: { family: tokens.fonte } },
    autosize: true,
  };
}

function ehObjetoSimples(valor: unknown): valor is Objeto {
  return typeof valor === 'object' && valor !== null && !Array.isArray(valor);
}

function mesclarValor(daBase: unknown, daPrioridade: unknown): unknown {
  return ehObjetoSimples(daBase) && ehObjetoSimples(daPrioridade) ? mesclarProfundo(daBase, daPrioridade) : daPrioridade;
}

/** Mescla profunda; `prioridade` vence. Usa fromEntries (não atribuição) para não herdar __proto__ do JSON. */
export function mesclarProfundo(base: Objeto, prioridade: Objeto): Objeto {
  const chaves = new Set([...Object.keys(base), ...Object.keys(prioridade)]);
  return Object.fromEntries(
    [...chaves].map((chave) => [
      chave,
      Object.hasOwn(prioridade, chave) ? mesclarValor(base[chave], prioridade[chave]) : base[chave],
    ]),
  );
}

/** A figura do backend vence (títulos, barmode); o tema completa cores e fontes. */
export function mesclarLayout(figuraLayout: Objeto, tema: Objeto): Objeto {
  return mesclarProfundo(tema, figuraLayout);
}

export function extrairFigura(figura: Readonly<Objeto>): FiguraPlotly {
  const { data, layout } = figura;
  const traces: unknown[] = Array.isArray(data) ? structuredClone(data) : [];
  return { data: traces, layout: ehObjetoSimples(layout) ? layout : {} };
}

export function montarFigura(figura: Readonly<Objeto>, tokens: TokensGrafico): FiguraPlotly {
  const { data, layout } = extrairFigura(figura);
  return { data, layout: mesclarLayout(layout, layoutTema(tokens)) };
}
```
`mesclarValor` e `mesclarProfundo` são mutuamente recursivas; se o lint reclamar de uso antes da definição (`no-use-before-define` não está ativo hoje), mova `mesclarProfundo` para cima.

`GraficoPlotly.tsx` (confira em `node_modules/react-plotly.js/dist/factory.d.mts` que o export padrão é `createPlotlyComponent`)
```tsx
import Plotly from 'plotly.js-dist-min';
import { useMemo } from 'react';
import criarComponentePlotly from 'react-plotly.js/factory';
import { CONFIG_PLOTLY, lerTokensGrafico, montarFigura } from './temaPlotly';

/** Bundle mínimo do Plotly (D63). Este módulo só é carregado por React.lazy em Grafico.tsx. */
const Plot = criarComponentePlotly(Plotly);

interface PropsGraficoPlotly {
  figura: Readonly<Record<string, unknown>>;
  altura: number;
}

export default function GraficoPlotly({ figura, altura }: Readonly<PropsGraficoPlotly>) {
  // Tokens lidos na montagem; Grafico remonta este componente (key = tema) quando o tema muda.
  const { data, layout } = useMemo(() => montarFigura(figura, lerTokensGrafico()), [figura]);
  return (
    <Plot data={data} layout={layout} config={CONFIG_PLOTLY} useResizeHandler style={{ width: '100%', height: altura }} />
  );
}
```

`Grafico.tsx`
```tsx
import { Suspense, lazy, useId } from 'react';
import { useTema } from '../tema/useTema';
import EstadoCarregando from '../ui/EstadoCarregando';
import { TEXTOS_UI } from '../ui/textos';
import estilos from './Grafico.module.css';

const GraficoPlotly = lazy(() => import('./GraficoPlotly'));

const ALTURA_PADRAO = 360;

interface PropsGrafico {
  /** Descritivo: "Distribuição de peso_kg (n = 227)". */
  titulo: string;
  /** Resumo textual do que o gráfico mostra (acessibilidade e leitura rápida). */
  resumo: string;
  /** JSON do Plotly vindo do backend ({data, layout}), sem template. */
  figura: Readonly<Record<string, unknown>>;
  altura?: number;
}

export default function Grafico({ titulo, resumo, figura, altura = ALTURA_PADRAO }: Readonly<PropsGrafico>) {
  const { tema } = useTema();
  const idResumo = useId();
  return (
    <figure className={estilos.figura} aria-label={titulo} aria-describedby={idResumo}>
      <figcaption className={estilos.titulo}>{titulo}</figcaption>
      <Suspense fallback={<EstadoCarregando forma="grafico" mensagem={TEXTOS_UI.carregandoGrafico} />}>
        <GraficoPlotly key={tema} figura={figura} altura={altura} />
      </Suspense>
      <p id={idResumo} className={estilos.resumo}>
        {resumo}
      </p>
    </figure>
  );
}
```

`Grafico.module.css`
```css
.figura { display: flex; flex-direction: column; gap: var(--esp-12); min-width: 0; }
.titulo { font-size: 14px; font-weight: 600; }
.resumo { font-size: 13.5px; line-height: 1.5; color: var(--cor-texto-2); }
```

**Passo 4: rodar e ver passar**
`npx vitest run src/shared/graficos` → todos passam. `npm run lint && npm run build` → verdes (o `tsc -b` confere os tipos do `react-plotly.js/factory` e do `plotly.js-dist-min`).

Nenhuma rota usa `Grafico` neste bloco, então o Plotly ainda não aparece no build; a separação em chunk próprio é conferida no M1.7. Aqui basta: `grep -l "plotly" dist/assets/*.js || echo "Plotly fora do bundle"` → "Plotly fora do bundle".

**Passo 5: commit**
```bash
git add frontend/src/shared/graficos
git commit -m "feat(frontend): adiciona wrapper Plotly com tema dos tokens e carregamento sob demanda"
```

---

### Tarefa 15: Etapas, PaginaEtapa e páginas provisórias

**Arquivos:**
- Criar: `frontend/src/app/etapas.ts` (+ `etapas.test.ts`), `frontend/src/app/textos.ts`
- Criar: `frontend/src/testes/renderizar.tsx`
- Criar: `frontend/src/shared/ui/PaginaEtapa.tsx`, `PaginaEtapa.module.css` (+ `PaginaEtapa.test.tsx`), `frontend/src/shared/ui/EtapaEmBreve.tsx`
- Criar: `frontend/src/features/{importar,variaveis,limpeza,analise,relatorio}/textos.ts` e `Pagina{Importar,Variaveis,Limpeza,Analise,Relatorio}.tsx`
- Criar: `frontend/src/app/paginas/PaginaIndisponivel.tsx`

As páginas das features são **provisórias**: `PaginaEtapa` + `EstadoVazio` "Esta etapa ainda não está pronta". M1.6 e M1.7 reescrevem os arquivos `Pagina*.tsx` e reaproveitam os `textos.ts` (título e ajuda já são os do design). `PaginaIndisponivel` atende as etapas 5–7, bloqueadas no M1 (D60), e continua até cada uma ser liberada.

**Passo 1: escrever os testes (falham)**

`app/etapas.test.ts`
```ts
import { describe, expect, it } from 'vitest';
import { ETAPAS, ehEtapaFutura, etapaDoCaminho } from './etapas';

describe('ETAPAS', () => {
  it('tem as 8 etapas em ordem', () => {
    expect(ETAPAS.map((etapa) => etapa.numero)).toEqual([1, 2, 3, 4, 5, 6, 7, 8]);
  });

  it('só 5, 6 e 7 são futuras no M1', () => {
    expect(ETAPAS.filter(ehEtapaFutura).map((etapa) => etapa.numero)).toEqual([5, 6, 7]);
  });
});

describe('etapaDoCaminho', () => {
  it.each([
    ['/analise', 4],
    ['/analise/peso_kg', 4],
    ['/importar', 1],
  ])('%s é a etapa %s', (caminho, numero) => {
    expect(etapaDoCaminho(caminho)?.numero).toBe(numero);
  });

  it.each(['/', '/importarx', '/outra'])('%s não é etapa', (caminho) => {
    expect(etapaDoCaminho(caminho)).toBeUndefined();
  });
});
```

`shared/ui/PaginaEtapa.test.tsx`
```tsx
import { screen, waitFor } from '@testing-library/react';
import { expect, it } from 'vitest';
import { renderizarComProvedores } from '../../testes/renderizar';
import PaginaEtapa from './PaginaEtapa';

function pagina() {
  return (
    <PaginaEtapa etapa={2} titulo="Variáveis" ajuda="Classificamos cada coluna pelo que ela contém.">
      <p>conteúdo da etapa</p>
    </PaginaEtapa>
  );
}

it('mostra "Etapa N de 8", o título como h1, a ajuda e o conteúdo', async () => {
  renderizarComProvedores(pagina());

  expect(await screen.findByRole('heading', { level: 1, name: 'Variáveis' })).toBeInTheDocument();
  expect(screen.getByText('Etapa 2 de 8')).toBeInTheDocument();
  expect(screen.getByText('Classificamos cada coluna pelo que ela contém.')).toBeInTheDocument();
  expect(screen.getByText('conteúdo da etapa')).toBeInTheDocument();
  expect(document.title).toBe('Variáveis · Analisador e Gerador de Dados');
});

it('marca a etapa como visitada na sessão', async () => {
  localStorage.setItem('sessao', JSON.stringify({ dataset: { id: 'd1', nomeArquivo: 'a.csv' }, etapasVisitadas: [1] }));

  renderizarComProvedores(pagina());

  await waitFor(() => {
    expect(localStorage.getItem('sessao')).toContain('"etapasVisitadas":[1,2]');
  });
});
```

**Passo 2: rodar e ver falhar**
`npx vitest run src/app/etapas.test.ts src/shared/ui/PaginaEtapa.test.tsx` → FAIL

**Passo 3: implementar**

`app/etapas.ts` (contrato da visão geral, sem mudanças na lista)
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

export type Etapa = (typeof ETAPAS)[number];

/** Etapa que ainda não existe nesta versão (D60). */
export type EtapaFutura = Extract<Etapa, { disponivelEm: string }>;

export function ehEtapaFutura(etapa: Etapa): etapa is EtapaFutura {
  return 'disponivelEm' in etapa;
}

export function etapaDoCaminho(caminho: string): Etapa | undefined {
  return ETAPAS.find((etapa) => caminho === etapa.caminho || caminho.startsWith(`${etapa.caminho}/`));
}
```

`app/textos.ts` (textos do layout e das páginas indisponíveis; spec 16)
```ts
import { formatarInteiro } from '../shared/lib/formatar';
import type { EtapaFutura } from './etapas';

function quantidade(n: number, singular: string, plural: string): string {
  return `${formatarInteiro(n)} ${n === 1 ? singular : plural}`;
}

export const TEXTOS_APP = {
  marcaLinha1: 'Analisador e Gerador',
  marcaLinha2: 'de Dados',
  simboloMarca: 'x̄',
  etapasDaAnalise: 'Etapas da análise',
  etapasBloqueadas: 'As etapas 2 a 8 ficam disponíveis depois que você importar um arquivo.',
  concluida: 'Concluída',
  bloqueada: 'Bloqueada',
  recolherBarra: 'Recolher barra',
  expandirBarra: 'Expandir barra',
  fecharBarra: 'Fechar a barra de etapas',
  disponivelNaVersao: (versao: string): string => `Disponível na versão ${versao}.`,
  nenhumArquivo: 'Nenhum arquivo importado',
  trocarArquivo: 'Trocar arquivo',
  dimensoes: (linhas: number, colunas: number): string =>
    `${quantidade(linhas, 'linha', 'linhas')} × ${quantidade(colunas, 'coluna', 'colunas')}`,
  tema: 'Tema',
  temaClaro: 'Tema claro',
  temaEscuro: 'Tema escuro',
  pularParaConteudo: 'Pular para o conteúdo',
  abrindoEtapa: 'Abrindo a etapa…',
  ajudaFutura: 'Esta etapa faz parte do roteiro do projeto e ainda não foi liberada.',
  titulosFuturos: {
    5: 'Análise bivariada',
    6: 'Gerador de dados',
    7: 'Detector de dados artificiais',
  } satisfies Record<EtapaFutura['numero'], string>,
} as const;
```

`testes/renderizar.tsx` (provedores reais + roteador em memória, para testes de páginas e layout; o M1.6 amplia este mesmo arquivo com `opcoes` opcionais — `rota`, `dataset`, `cliente` —, `renderizarHook` e `DATASET_TESTE`, sem mudar as chamadas abaixo)
```tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { render } from '@testing-library/react';
import type { ReactElement } from 'react';
import { type RouteObject, RouterProvider, createMemoryRouter } from 'react-router';
import SessaoProvider from '../shared/sessao/SessaoProvider';
import TemaProvider from '../shared/tema/TemaProvider';
import ToastProvider from '../shared/ui/ToastProvider';

export function renderizarComRotas(rotas: RouteObject[], rotaInicial = '/') {
  const roteador = createMemoryRouter(rotas, { initialEntries: [rotaInicial] });
  const clienteConsultas = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
  const resultado = render(
    <QueryClientProvider client={clienteConsultas}>
      <TemaProvider>
        <SessaoProvider>
          <ToastProvider>
            <RouterProvider router={roteador} />
          </ToastProvider>
        </SessaoProvider>
      </TemaProvider>
    </QueryClientProvider>,
  );
  return { ...resultado, roteador, clienteConsultas };
}

export function renderizarComProvedores(elemento: ReactElement) {
  return renderizarComRotas([{ path: '*', element: elemento }]);
}
```

`shared/ui/PaginaEtapa.tsx`
```tsx
import { type ReactNode, useEffect } from 'react';
import { useSessao } from '../sessao/useSessao';
import estilos from './PaginaEtapa.module.css';
import { TEXTOS_UI } from './textos';

interface PropsPaginaEtapa {
  etapa: number;
  titulo: string;
  ajuda: string;
  acoesTopo?: ReactNode;
  children: ReactNode;
}

export default function PaginaEtapa({ etapa, titulo, ajuda, acoesTopo, children }: Readonly<PropsPaginaEtapa>) {
  const { dataset, marcarVisitada } = useSessao();
  const idDataset = dataset?.id;

  useEffect(() => {
    // idDataset entra nas dependências de propósito: trocar de arquivo zera as visitadas e a etapa atual é remarcada.
    marcarVisitada(etapa);
  }, [etapa, idDataset, marcarVisitada]);

  useEffect(() => {
    document.title = `${titulo} · ${TEXTOS_UI.nomeApp}`;
  }, [titulo]);

  return (
    <div className={estilos.pagina}>
      <header className={estilos.topo}>
        <div className={estilos.textos}>
          <p className={estilos.sobrelinha}>{TEXTOS_UI.etapaDeTotal(etapa)}</p>
          <h1 className={estilos.titulo}>{titulo}</h1>
          <p className={estilos.ajuda}>{ajuda}</p>
        </div>
        {acoesTopo === undefined ? null : <div className={estilos.acoesTopo}>{acoesTopo}</div>}
      </header>
      {children}
    </div>
  );
}
```

`shared/ui/PaginaEtapa.module.css` (README §Layout geral)
```css
.pagina { display: flex; flex-direction: column; gap: var(--esp-24); }
.topo { display: flex; flex-wrap: wrap; align-items: flex-end; justify-content: space-between; gap: var(--esp-16) var(--esp-24); }
.textos { display: flex; flex-direction: column; gap: var(--esp-4); min-width: 0; }
.sobrelinha { font-size: 13px; font-weight: 500; line-height: 1.4; color: var(--cor-texto-2); }
.titulo { font-size: 28px; font-weight: 700; line-height: 1.25; letter-spacing: -0.015em; }
.ajuda { font-size: 15px; color: var(--cor-texto-2); }
.acoesTopo { display: flex; flex: none; align-items: flex-end; gap: var(--esp-12); }
```

`shared/ui/EtapaEmBreve.tsx`
```tsx
import EstadoVazio from './EstadoVazio';
import PaginaEtapa from './PaginaEtapa';
import { TEXTOS_UI } from './textos';

interface PropsEtapaEmBreve {
  etapa: number;
  titulo: string;
  ajuda: string;
  descricao?: string;
}

/** Página de etapa sem conteúdo ainda (provisórias do M1 e etapas futuras, D60). */
export default function EtapaEmBreve({ etapa, titulo, ajuda, descricao = TEXTOS_UI.telaEmConstrucao }: Readonly<PropsEtapaEmBreve>) {
  return (
    <PaginaEtapa etapa={etapa} titulo={titulo} ajuda={ajuda}>
      <EstadoVazio icone="construction" titulo={TEXTOS_UI.etapaEmBreve} descricao={descricao} />
    </PaginaEtapa>
  );
}
```

**Páginas provisórias das features.** Cada feature recebe dois arquivos com o mesmo formato. Exemplo completo para `importar`:

`features/importar/textos.ts`
```ts
export const TEXTOS_IMPORTAR = {
  titulo: 'Importar arquivo',
  ajuda: 'Envie sua tabela de dados. Nós descobrimos sozinhos como ela foi escrita, e você confere antes de seguir.',
} as const;
```

`features/importar/PaginaImportar.tsx`
```tsx
import EtapaEmBreve from '../../shared/ui/EtapaEmBreve';
import { TEXTOS_IMPORTAR } from './textos';

export default function PaginaImportar() {
  return <EtapaEmBreve etapa={1} titulo={TEXTOS_IMPORTAR.titulo} ajuda={TEXTOS_IMPORTAR.ajuda} />;
}
```

Os outros quatro seguem exatamente o mesmo modelo, trocando nomes, número e textos (títulos e ajudas copiados dos protótipos `docs/design/telas/Tela N *.dc.html`):

| Pasta | Constante | Componente | `etapa` | `titulo` | `ajuda` |
|---|---|---|---|---|---|
| `features/variaveis` | `TEXTOS_VARIAVEIS` | `PaginaVariaveis` | 2 | `Variáveis` | `Classificamos cada coluna pelo que ela contém. Confira o motivo e corrija o tipo se não concordar.` |
| `features/limpeza` | `TEXTOS_LIMPEZA` | `PaginaLimpeza` | 3 | `Limpeza` | `Encontramos alguns problemas comuns. Escolha o que fazer com cada um; nada muda até você clicar em "Aplicar limpeza".` |
| `features/analise` | `TEXTOS_ANALISE` | `PaginaAnalise` | 4 | `Análise univariada` | `Uma coluna por vez: como os valores se distribuem, onde fica o centro e quanto eles variam.` |
| `features/relatorio` | `TEXTOS_RELATORIO` | `PaginaRelatorio` | 8 | `Relatório` | `Escolha o que entra. A prévia ao lado mostra exatamente como o relatório será impresso.` |

`app/paginas/PaginaIndisponivel.tsx` (rotas `/bivariada`, `/gerador`, `/detector`)
```tsx
import { Navigate, useLocation } from 'react-router';
import EtapaEmBreve from '../../shared/ui/EtapaEmBreve';
import { ETAPAS, ehEtapaFutura, etapaDoCaminho } from '../etapas';
import { TEXTOS_APP } from '../textos';

export default function PaginaIndisponivel() {
  const etapa = etapaDoCaminho(useLocation().pathname);
  if (etapa === undefined || !ehEtapaFutura(etapa)) return <Navigate to={ETAPAS[0].caminho} replace />;
  return (
    <EtapaEmBreve
      etapa={etapa.numero}
      titulo={TEXTOS_APP.titulosFuturos[etapa.numero]}
      ajuda={TEXTOS_APP.ajudaFutura}
      descricao={TEXTOS_APP.disponivelNaVersao(etapa.disponivelEm)}
    />
  );
}
```

**Passo 4: rodar e ver passar**
`npx vitest run src/app src/shared/ui/PaginaEtapa.test.tsx` → todos passam. `npm run lint` → sem erros. Na raiz, `npx --yes jscpd@4 frontend/src` → 0 clones (as páginas provisórias são curtas o bastante para não formar clone de 50 tokens; se o jscpd acusar, reduza o JSX repetido, nunca o ignore).

**Passo 5: commit**
```bash
git add frontend/src/app/etapas.ts frontend/src/app/etapas.test.ts frontend/src/app/textos.ts frontend/src/app/paginas frontend/src/testes/renderizar.tsx frontend/src/shared/ui/PaginaEtapa.* frontend/src/shared/ui/EtapaEmBreve.tsx frontend/src/features/importar frontend/src/features/variaveis frontend/src/features/limpeza frontend/src/features/analise frontend/src/features/relatorio
git commit -m "feat(frontend): adiciona etapas, PaginaEtapa e páginas provisórias das etapas"
```

---

### Tarefa 16: Barra de etapas

**Arquivos:**
- Criar em `frontend/src/app/layout/`: `estadoEtapa.ts` (+ `estadoEtapa.test.ts`), `ItemEtapa.tsx`, `ItemEtapa.module.css`, `BarraEtapas.tsx`, `BarraEtapas.module.css` (+ `BarraEtapas.test.tsx`)

Regras (`componentes.md` §BarraEtapas, handoff, D60):
- Futuras (`disponivelEm`) sempre **bloqueadas**, com tooltip "Disponível na versão {v}.".
- Etapa da rota atual: **atual** (`aria-current="step"`).
- Sem dataset: só a etapa 1 abre; 2–8 **bloqueadas** e aparece a frase "As etapas 2 a 8 ficam disponíveis depois que você importar um arquivo.".
- Com dataset: visitada → **concluída** (`check` + "Concluída"); senão **disponível**.
- Bloqueada é `<button aria-disabled="true">` (focável, para ouvir o motivo; não navega). As demais são `<Link>`.
- Recolhida (72 px): só o marcador; nome e estado ficam em texto visualmente oculto (continuam acessíveis) e o nome aparece num tooltip à direita.

**Passo 1: escrever os testes (falham)**

`estadoEtapa.test.ts`
```ts
import { describe, expect, it } from 'vitest';
import { ETAPAS } from '../etapas';
import { type ContextoEtapas, dicaDaEtapa, estadoDaEtapa } from './estadoEtapa';

const [IMPORTAR, VARIAVEIS, LIMPEZA] = ETAPAS;
const BIVARIADA = ETAPAS[4];

function contexto(parcial: Partial<ContextoEtapas>): ContextoEtapas {
  return { atual: null, temDataset: false, visitadas: new Set(), ...parcial };
}

describe('estadoDaEtapa', () => {
  it('sem dataset só Importar abre', () => {
    expect(estadoDaEtapa(IMPORTAR, contexto({}))).toBe('disponivel');
    expect(estadoDaEtapa(IMPORTAR, contexto({ atual: 1 }))).toBe('atual');
    expect(estadoDaEtapa(VARIAVEIS, contexto({ atual: 1 }))).toBe('bloqueada');
  });

  it('com dataset: visitada vira concluída, a atual vence', () => {
    const comDados = contexto({ atual: 3, temDataset: true, visitadas: new Set([1, 3]) });

    expect(estadoDaEtapa(IMPORTAR, comDados)).toBe('concluida');
    expect(estadoDaEtapa(VARIAVEIS, comDados)).toBe('disponivel');
    expect(estadoDaEtapa(LIMPEZA, comDados)).toBe('atual');
  });

  it('etapa futura fica bloqueada mesmo com dataset e na própria rota', () => {
    expect(estadoDaEtapa(BIVARIADA, contexto({ atual: 5, temDataset: true, visitadas: new Set([5]) }))).toBe(
      'bloqueada',
    );
  });
});

describe('dicaDaEtapa', () => {
  it.each([
    [IMPORTAR, false, null],
    [BIVARIADA, false, 'Disponível na versão v0.2.'],
    [IMPORTAR, true, 'Importar'],
    [BIVARIADA, true, 'Bivariada. Disponível na versão v0.2.'],
  ] as const)('%o recolhida=%s → %s', (etapa, recolhida, esperado) => {
    expect(dicaDaEtapa(etapa, recolhida)).toBe(esperado);
  });
});
```

`BarraEtapas.test.tsx`
```tsx
import { screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { expect, it, vi } from 'vitest';
import { renderizarComRotas } from '../../testes/renderizar';
import BarraEtapas from './BarraEtapas';

function renderizarBarra(caminho: string, recolhida = false) {
  const aoAlternar = vi.fn();
  renderizarComRotas(
    [{ path: '*', element: <BarraEtapas recolhida={recolhida} sobreposta={false} aoAlternar={aoAlternar} /> }],
    caminho,
  );
  return { aoAlternar };
}

function salvarSessao(etapasVisitadas: number[]) {
  localStorage.setItem(
    'sessao',
    JSON.stringify({ dataset: { id: 'd1', nomeArquivo: 'pesquisa_saude.txt' }, etapasVisitadas }),
  );
}

it('sem arquivo: só Importar abre e a frase explica o bloqueio', () => {
  renderizarBarra('/importar');

  const nav = screen.getByRole('navigation', { name: 'Etapas da análise' });
  expect(within(nav).getByRole('link', { name: 'Importar' })).toHaveAttribute('aria-current', 'step');
  expect(within(nav).getByRole('button', { name: 'Variáveis Bloqueada' })).toHaveAttribute('aria-disabled', 'true');
  expect(within(nav).getAllByRole('img', { name: 'Bloqueada' })).toHaveLength(7);
  expect(screen.getByText('As etapas 2 a 8 ficam disponíveis depois que você importar um arquivo.')).toBeInTheDocument();
});

it('com arquivo: visitadas aparecem concluídas e a atual fica marcada', () => {
  salvarSessao([1, 2]);

  renderizarBarra('/limpeza');

  expect(screen.getByRole('link', { name: 'Importar Concluída' })).toBeInTheDocument();
  expect(screen.getByRole('link', { name: 'Variáveis Concluída' })).toBeInTheDocument();
  expect(screen.getByRole('link', { name: 'Limpeza' })).toHaveAttribute('aria-current', 'step');
  expect(screen.getByRole('link', { name: 'Análise univariada' })).not.toHaveAttribute('aria-current');
  expect(screen.queryByText(/ficam disponíveis depois/)).not.toBeInTheDocument();
});

it('etapas futuras ficam bloqueadas mesmo com arquivo e dizem a versão', async () => {
  salvarSessao([1]);
  renderizarBarra('/importar');

  const bivariada = screen.getByRole('button', { name: 'Bivariada Bloqueada' });
  await userEvent.hover(bivariada);

  expect(bivariada).toHaveAttribute('aria-disabled', 'true');
  expect(screen.getByRole('tooltip')).toHaveTextContent('Disponível na versão v0.2.');
});

it('recolhida: nomes seguem acessíveis e o botão pede para expandir', async () => {
  const { aoAlternar } = renderizarBarra('/importar', true);

  expect(screen.getByRole('link', { name: 'Importar' })).toBeInTheDocument();
  expect(screen.queryByText(/ficam disponíveis depois/)).not.toBeInTheDocument();
  await userEvent.click(screen.getByRole('button', { name: 'Expandir barra' }));
  expect(aoAlternar).toHaveBeenCalledOnce();
});
```

**Passo 2: rodar e ver falhar**
`npx vitest run src/app/layout` → FAIL

**Passo 3: implementar**

`estadoEtapa.ts`
```ts
import { type Etapa, ehEtapaFutura } from '../etapas';
import { TEXTOS_APP } from '../textos';

export type EstadoEtapa = 'concluida' | 'atual' | 'disponivel' | 'bloqueada';

export interface ContextoEtapas {
  atual: number | null;
  temDataset: boolean;
  visitadas: ReadonlySet<number>;
}

const ETAPA_IMPORTAR = 1;

/** componentes.md §BarraEtapas + D60: futuras sempre bloqueadas; sem dataset só a etapa 1 abre. */
export function estadoDaEtapa(etapa: Etapa, contexto: ContextoEtapas): EstadoEtapa {
  if (ehEtapaFutura(etapa)) return 'bloqueada';
  if (etapa.numero === contexto.atual) return 'atual';
  if (!contexto.temDataset) return etapa.numero === ETAPA_IMPORTAR ? 'disponivel' : 'bloqueada';
  return contexto.visitadas.has(etapa.numero) ? 'concluida' : 'disponivel';
}

/** Texto do tooltip: motivo das futuras; na barra recolhida, o nome (+ motivo). */
export function dicaDaEtapa(etapa: Etapa, recolhida: boolean): string | null {
  const motivo = ehEtapaFutura(etapa) ? TEXTOS_APP.disponivelNaVersao(etapa.disponivelEm) : null;
  if (!recolhida) return motivo;
  return motivo === null ? etapa.nome : `${etapa.nome}. ${motivo}`;
}
```

`ItemEtapa.tsx`
```tsx
import { Link } from 'react-router';
import { VISUALMENTE_OCULTO, juntarClasses } from '../../shared/lib/classes';
import Icone from '../../shared/ui/Icone';
import Tooltip from '../../shared/ui/Tooltip';
import type { Etapa } from '../etapas';
import { TEXTOS_APP } from '../textos';
import { type EstadoEtapa, dicaDaEtapa } from './estadoEtapa';
import estilos from './ItemEtapa.module.css';

const CLASSE_MARCADOR = {
  concluida: estilos.marcadorConcluida,
  atual: estilos.marcadorAtual,
  disponivel: estilos.marcadorDisponivel,
  bloqueada: estilos.marcadorBloqueada,
} satisfies Record<EstadoEtapa, string | undefined>;

const SUFIXOS = {
  concluida: TEXTOS_APP.concluida,
  bloqueada: TEXTOS_APP.bloqueada,
  atual: null,
  disponivel: null,
} as const satisfies Record<EstadoEtapa, string | null>;

interface PropsConteudo {
  etapa: Etapa;
  estado: EstadoEtapa;
  recolhida: boolean;
}

interface PropsAlvo extends PropsConteudo {
  /** Repassado pelo Tooltip (cloneElement). */
  'aria-describedby'?: string | undefined;
}

export default function ItemEtapa({ etapa, estado, recolhida }: Readonly<PropsConteudo>) {
  const dica = dicaDaEtapa(etapa, recolhida);
  const alvo =
    estado === 'bloqueada' ? (
      <EtapaBloqueada etapa={etapa} estado={estado} recolhida={recolhida} />
    ) : (
      <EtapaNavegavel etapa={etapa} estado={estado} recolhida={recolhida} />
    );
  return (
    <li className={estilos.linha}>
      {dica === null ? (
        alvo
      ) : (
        <Tooltip texto={dica} posicao="direita">
          {alvo}
        </Tooltip>
      )}
    </li>
  );
}

function EtapaNavegavel({ etapa, estado, recolhida, 'aria-describedby': descritaPor }: Readonly<PropsAlvo>) {
  const atual = estado === 'atual';
  return (
    <Link
      to={etapa.caminho}
      aria-current={atual ? 'step' : undefined}
      aria-describedby={descritaPor}
      className={juntarClasses(estilos.item, atual && estilos.atual, recolhida && estilos.recolhida)}
    >
      <ConteudoEtapa etapa={etapa} estado={estado} recolhida={recolhida} />
    </Link>
  );
}

function EtapaBloqueada({ etapa, estado, recolhida, 'aria-describedby': descritaPor }: Readonly<PropsAlvo>) {
  return (
    <button
      type="button"
      aria-disabled="true"
      aria-describedby={descritaPor}
      className={juntarClasses(estilos.item, estilos.bloqueada, recolhida && estilos.recolhida)}
    >
      <ConteudoEtapa etapa={etapa} estado={estado} recolhida={recolhida} />
    </button>
  );
}

function ConteudoEtapa({ etapa, estado, recolhida }: Readonly<PropsConteudo>) {
  return (
    <>
      <span className={juntarClasses(estilos.marcador, CLASSE_MARCADOR[estado])} aria-hidden="true">
        {estado === 'concluida' ? <Icone nome="check" tamanho={18} /> : etapa.numero}
      </span>
      <span className={recolhida ? VISUALMENTE_OCULTO : estilos.nome}>{etapa.nome}</span>{' '}
      <SufixoEtapa estado={estado} recolhida={recolhida} />
    </>
  );
}

function SufixoEtapa({ estado, recolhida }: Readonly<Omit<PropsConteudo, 'etapa'>>) {
  const texto = SUFIXOS[estado];
  if (texto === null) return null;
  if (recolhida) return <span className={VISUALMENTE_OCULTO}>{texto}</span>;
  return estado === 'bloqueada' ? (
    <Icone nome="lock" tamanho={18} rotulo={texto} className={estilos.cadeado} />
  ) : (
    <span className={estilos.concluida}>{texto}</span>
  );
}
```
O `{' '}` entre nome e sufixo garante o espaço no nome acessível ("Importar Concluída"); num contêiner flex ele não aparece na tela.

`ItemEtapa.module.css` (medidas de `telas/Barra Lateral.dc.html`)
```css
.linha > * { display: flex; width: 100%; }
.item {
  display: flex;
  align-items: center;
  gap: var(--esp-12);
  width: 100%;
  min-height: 44px;
  padding: 0 var(--esp-12);
  border: 0;
  border-radius: var(--raio-md);
  background: transparent;
  color: var(--cor-texto);
  font-size: 14px;
  text-align: left;
  text-decoration: none;
  cursor: pointer;
  transition: background-color var(--transicao);
}
.item:hover { background: var(--cor-superficie-2); }
.atual,
.atual:hover { background: var(--cor-primaria-suave); color: var(--cor-primaria); font-weight: 600; }
.bloqueada,
.bloqueada:hover { background: transparent; color: var(--cor-texto-desab); cursor: not-allowed; }
.recolhida { justify-content: center; padding: 0; }
.nome { flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.concluida { color: var(--cor-sucesso); font-size: 12px; font-weight: 500; }
.cadeado { color: var(--cor-texto-desab); }
.marcador { display: grid; flex: none; place-items: center; width: 26px; height: 26px; border-radius: 50%; font: 500 12px var(--fonte-mono); }
.marcadorConcluida { background: var(--cor-sucesso-suave); color: var(--cor-sucesso); }
.marcadorAtual { background: var(--cor-primaria); color: var(--cor-sobre-primaria); font-weight: 600; }
.marcadorDisponivel { border: 1.5px solid var(--cor-borda-forte); color: var(--cor-texto-2); }
.marcadorBloqueada { border: 1.5px dashed var(--cor-borda); }
```

`BarraEtapas.tsx`
```tsx
import { useLocation } from 'react-router';
import { VISUALMENTE_OCULTO, juntarClasses } from '../../shared/lib/classes';
import { useSessao } from '../../shared/sessao/useSessao';
import Icone from '../../shared/ui/Icone';
import { ETAPAS, etapaDoCaminho } from '../etapas';
import { TEXTOS_APP } from '../textos';
import estilos from './BarraEtapas.module.css';
import { type ContextoEtapas, estadoDaEtapa } from './estadoEtapa';
import ItemEtapa from './ItemEtapa';

interface PropsBarraEtapas {
  recolhida: boolean;
  /** Aberta por cima do conteúdo em telas de 768 a 1279 px. */
  sobreposta: boolean;
  aoAlternar: () => void;
}

export default function BarraEtapas({ recolhida, sobreposta, aoAlternar }: Readonly<PropsBarraEtapas>) {
  const { dataset, etapasVisitadas } = useSessao();
  const { pathname } = useLocation();
  const contexto: ContextoEtapas = {
    atual: etapaDoCaminho(pathname)?.numero ?? null,
    temDataset: dataset !== null,
    visitadas: etapasVisitadas,
  };
  return (
    <aside className={juntarClasses(estilos.barra, recolhida && estilos.recolhida, sobreposta && estilos.sobreposta)}>
      <Marca recolhida={recolhida} />
      <nav aria-label={TEXTOS_APP.etapasDaAnalise} className={estilos.nav}>
        <ol className={estilos.lista}>
          {ETAPAS.map((etapa) => (
            <ItemEtapa key={etapa.numero} etapa={etapa} estado={estadoDaEtapa(etapa, contexto)} recolhida={recolhida} />
          ))}
        </ol>
      </nav>
      {contexto.temDataset || recolhida ? null : <p className={estilos.aviso}>{TEXTOS_APP.etapasBloqueadas}</p>}
      <BotaoRecolher recolhida={recolhida} aoAlternar={aoAlternar} />
    </aside>
  );
}

function Marca({ recolhida }: Readonly<{ recolhida: boolean }>) {
  return (
    <div className={estilos.marca}>
      <span className={estilos.simbolo} aria-hidden="true">
        {TEXTOS_APP.simboloMarca}
      </span>
      <span className={recolhida ? VISUALMENTE_OCULTO : estilos.nomeApp}>
        {TEXTOS_APP.marcaLinha1} <small className={estilos.nomeApp2}>{TEXTOS_APP.marcaLinha2}</small>
      </span>
    </div>
  );
}

function BotaoRecolher({ recolhida, aoAlternar }: Readonly<{ recolhida: boolean; aoAlternar: () => void }>) {
  return (
    <div className={estilos.rodape}>
      <button type="button" className={estilos.recolher} aria-expanded={!recolhida} onClick={aoAlternar}>
        <Icone nome={recolhida ? 'left_panel_open' : 'left_panel_close'} tamanho={20} />
        <span className={recolhida ? VISUALMENTE_OCULTO : undefined}>
          {recolhida ? TEXTOS_APP.expandirBarra : TEXTOS_APP.recolherBarra}
        </span>
      </button>
    </div>
  );
}
```

`BarraEtapas.module.css` (sem `overflow` na barra nem na lista: cortaria o tooltip à direita)
```css
.barra {
  position: sticky;
  top: 0;
  display: flex;
  flex-direction: column;
  width: var(--largura-barra);
  height: 100vh;
  border-right: 1px solid var(--cor-borda);
  background: var(--cor-superficie);
}
.recolhida { width: var(--largura-barra-recolhida); }
.sobreposta { position: fixed; left: 0; z-index: 30; box-shadow: var(--sombra-3); }
.marca { display: flex; align-items: center; gap: 10px; height: var(--altura-cabecalho); padding: 0 var(--esp-20); border-bottom: 1px solid var(--cor-borda); }
.recolhida .marca { justify-content: center; padding: 0; }
.simbolo { display: grid; flex: none; place-items: center; width: 28px; height: 28px; border-radius: var(--raio-md); background: var(--cor-primaria); color: var(--cor-sobre-primaria); font: 600 13px var(--fonte-mono); }
.nomeApp { display: flex; flex-direction: column; font-size: 14px; font-weight: 600; line-height: 1.25; white-space: nowrap; }
.nomeApp2 { color: var(--cor-texto-2); font-size: 12px; font-weight: 400; }
.nav { flex: 1; }
.lista { display: flex; flex-direction: column; gap: 2px; padding: var(--esp-12); list-style: none; }
.aviso { margin: 0 var(--esp-20) var(--esp-16); color: var(--cor-texto-2); font-size: 12px; line-height: 1.5; }
.rodape { padding: var(--esp-12); border-top: 1px solid var(--cor-borda); }
.recolher {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  min-height: 40px;
  padding: 0 var(--esp-12);
  border: 0;
  border-radius: var(--raio-md);
  background: transparent;
  color: var(--cor-texto-2);
  font-size: 13px;
  cursor: pointer;
  transition: background-color var(--transicao);
}
.recolher:hover { background: var(--cor-superficie-2); }
.recolhida .recolher { justify-content: center; padding: 0; }
```

**Passo 4: rodar e ver passar**
`npx vitest run src/app/layout` → todos passam. `npm run lint` → sem erros.

**Passo 5: commit**
```bash
git add frontend/src/app/layout
git commit -m "feat(frontend): adiciona barra de etapas com estados concluída, atual, disponível e bloqueada"
```

---

### Tarefa 17: Cabeçalho e alternância de tema

**Arquivos:**
- Criar em `frontend/src/app/layout/`: `AlternanciaTema.tsx`, `AlternanciaTema.module.css`, `Cabecalho.tsx`, `Cabecalho.module.css` (+ `Cabecalho.test.tsx`)

O Cabeçalho **não busca dados** neste bloco: recebe `nomeArquivo`, `nLinhas`, `nColunas` por props (todos opcionais). Neste bloco o `LayoutApp` passa só o nome que está na sessão. **Ponto de integração do M1.6:** criar o hook do resumo do dataset (react-query, `GET /datasets/{id}`) e passar `nLinhas`/`nColunas` do `resumo` no `LayoutApp`.

**Passo 1: escrever o teste (falha)** — `Cabecalho.test.tsx`
```tsx
import { screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import type { ReactElement } from 'react';
import { expect, it } from 'vitest';
import { renderizarComRotas } from '../../testes/renderizar';
import Cabecalho from './Cabecalho';

function renderizar(cabecalho: ReactElement) {
  renderizarComRotas([
    { path: '/', element: cabecalho },
    { path: '/importar', element: <p>Tela de importar</p> },
  ]);
}

it('sem arquivo mostra o aviso e não oferece troca', () => {
  renderizar(<Cabecalho />);

  expect(screen.getByText('Nenhum arquivo importado')).toBeInTheDocument();
  expect(screen.queryByRole('button', { name: 'Trocar arquivo' })).not.toBeInTheDocument();
});

it('com arquivo mostra nome e tamanho; "Trocar arquivo" leva para Importar', async () => {
  renderizar(<Cabecalho nomeArquivo="pesquisa_saude.txt" nLinhas={230} nColunas={8} />);

  expect(screen.getByText('pesquisa_saude.txt')).toBeInTheDocument();
  expect(screen.getByText('230 linhas × 8 colunas')).toBeInTheDocument();
  await userEvent.click(screen.getByRole('button', { name: 'Trocar arquivo' }));
  expect(await screen.findByText('Tela de importar')).toBeInTheDocument();
});

it('usa singular e separador de milhar', () => {
  renderizar(<Cabecalho nomeArquivo="grande.csv" nLinhas={1234} nColunas={1} />);

  expect(screen.getByText('1.234 linhas × 1 coluna')).toBeInTheDocument();
});

it('alterna o tema por clique e por setas', async () => {
  renderizar(<Cabecalho />);
  const grupo = screen.getByRole('radiogroup', { name: 'Tema' });

  await userEvent.click(within(grupo).getByRole('radio', { name: 'Tema escuro' }));
  expect(document.documentElement).toHaveAttribute('data-tema', 'escuro');
  expect(within(grupo).getByRole('radio', { name: 'Tema escuro' })).toHaveAttribute('aria-checked', 'true');

  await userEvent.keyboard('{ArrowLeft}');
  expect(document.documentElement).toHaveAttribute('data-tema', 'claro');
  expect(within(grupo).getByRole('radio', { name: 'Tema claro' })).toHaveFocus();
});
```

**Passo 2: rodar e ver falhar**
`npx vitest run src/app/layout/Cabecalho.test.tsx` → FAIL

**Passo 3: implementar**

`AlternanciaTema.tsx`
```tsx
import { juntarClasses } from '../../shared/lib/classes';
import type { Tema } from '../../shared/tema/tipos';
import { useTema } from '../../shared/tema/useTema';
import Icone from '../../shared/ui/Icone';
import { useNavegacaoPorSetas } from '../../shared/ui/useNavegacaoPorSetas';
import { TEXTOS_APP } from '../textos';
import estilos from './AlternanciaTema.module.css';

const OPCOES = [
  { valor: 'claro', icone: 'light_mode', rotulo: TEXTOS_APP.temaClaro },
  { valor: 'escuro', icone: 'dark_mode', rotulo: TEXTOS_APP.temaEscuro },
] as const satisfies readonly { valor: Tema; icone: string; rotulo: string }[];

const IDS: readonly Tema[] = OPCOES.map((opcao) => opcao.valor);

export default function AlternanciaTema() {
  const { tema, definirTema } = useTema();
  const propsItem = useNavegacaoPorSetas({ ids: IDS, ativo: tema, aoMudar: definirTema });
  return (
    <div role="radiogroup" aria-label={TEXTOS_APP.tema} className={estilos.grupo}>
      {OPCOES.map((opcao) => {
        const selecionada = opcao.valor === tema;
        return (
          <button
            key={opcao.valor}
            {...propsItem(opcao.valor)}
            type="button"
            role="radio"
            aria-checked={selecionada}
            aria-label={opcao.rotulo}
            className={juntarClasses(estilos.opcao, selecionada && estilos.selecionada)}
            onClick={() => {
              definirTema(opcao.valor);
            }}
          >
            <Icone nome={opcao.icone} tamanho={18} />
          </button>
        );
      })}
    </div>
  );
}
```

`AlternanciaTema.module.css`
```css
.grupo { display: flex; gap: 2px; padding: 3px; border: 1px solid var(--cor-borda); border-radius: var(--raio-pilula); background: var(--cor-superficie-2); }
.opcao {
  display: grid;
  place-items: center;
  width: 30px;
  height: 30px;
  border: 0;
  border-radius: 50%;
  background: transparent;
  color: var(--cor-texto-2);
  cursor: pointer;
  transition: background-color var(--transicao), color var(--transicao);
}
.opcao:hover { color: var(--cor-texto); }
.selecionada { background: var(--cor-superficie-elevada); box-shadow: var(--sombra-1); color: var(--cor-texto); }
```
(`--cor-superficie-elevada` é branco no claro e #1d222a no escuro, como em `Cabecalho.dc.html`.)

`Cabecalho.tsx`
```tsx
import { useNavigate } from 'react-router';
import Botao from '../../shared/ui/Botao';
import Icone from '../../shared/ui/Icone';
import { ETAPAS } from '../etapas';
import { TEXTOS_APP } from '../textos';
import AlternanciaTema from './AlternanciaTema';
import estilos from './Cabecalho.module.css';

const CAMINHO_IMPORTAR = ETAPAS[0].caminho;

interface PropsCabecalho {
  nomeArquivo?: string | undefined;
  nLinhas?: number | undefined;
  nColunas?: number | undefined;
}

export default function Cabecalho({ nomeArquivo, nLinhas, nColunas }: Readonly<PropsCabecalho>) {
  const navegar = useNavigate();
  return (
    <header className={estilos.cabecalho}>
      {nomeArquivo === undefined ? (
        <span className={estilos.vazio}>{TEXTOS_APP.nenhumArquivo}</span>
      ) : (
        <ArquivoAtual nomeArquivo={nomeArquivo} nLinhas={nLinhas} nColunas={nColunas} />
      )}
      {nomeArquivo === undefined ? null : (
        <Botao
          variante="secundario"
          tamanho="sm"
          icone="swap_horiz"
          onClick={() => {
            void navegar(CAMINHO_IMPORTAR);
          }}
        >
          {TEXTOS_APP.trocarArquivo}
        </Botao>
      )}
      <AlternanciaTema />
    </header>
  );
}

interface PropsArquivoAtual {
  nomeArquivo: string;
  nLinhas: number | undefined;
  nColunas: number | undefined;
}

function ArquivoAtual({ nomeArquivo, nLinhas, nColunas }: Readonly<PropsArquivoAtual>) {
  return (
    <div className={estilos.arquivo}>
      <Icone nome="description" tamanho={22} className={estilos.icone} />
      <div className={estilos.textos}>
        <span className={estilos.nome}>{nomeArquivo}</span>
        {nLinhas === undefined || nColunas === undefined ? null : (
          <span className={estilos.dimensoes}>{TEXTOS_APP.dimensoes(nLinhas, nColunas)}</span>
        )}
      </div>
    </div>
  );
}
```

`Cabecalho.module.css`
```css
.cabecalho { display: flex; align-items: center; gap: var(--esp-16); height: var(--altura-cabecalho); padding: 0 var(--esp-32); border-bottom: 1px solid var(--cor-borda); background: var(--cor-superficie); }
.arquivo { display: flex; flex: 1; align-items: center; gap: var(--esp-12); min-width: 0; }
.icone { color: var(--cor-texto-2); }
.textos { display: flex; align-items: baseline; gap: var(--esp-12); min-width: 0; }
.nome { overflow: hidden; font: 600 14px var(--fonte-mono); text-overflow: ellipsis; white-space: nowrap; }
.dimensoes { color: var(--cor-texto-2); font-size: 13px; font-variant-numeric: tabular-nums; white-space: nowrap; }
.vazio { flex: 1; color: var(--cor-texto-2); font-size: 14px; }

@media (max-width: 767px) {
  .cabecalho { padding: 0 var(--esp-16); }
  .dimensoes { display: none; }
}
```

**Passo 4: rodar e ver passar**
`npx vitest run src/app/layout` → todos passam. `npm run lint` → sem erros.

**Passo 5: commit**
```bash
git add frontend/src/app/layout/AlternanciaTema.* frontend/src/app/layout/Cabecalho.*
git commit -m "feat(frontend): adiciona cabeçalho com arquivo atual, troca de arquivo e alternância de tema"
```

---

### Tarefa 18: LayoutApp, sessão expirada, rotas e providers

**Arquivos:**
- Criar em `frontend/src/app/layout/`: `useBarraRecolhivel.ts`, `useSessaoExpirada.ts` (+ `useSessaoExpirada.test.tsx`), `LayoutApp.tsx`, `LayoutApp.module.css` (+ `LayoutApp.test.tsx`)
- Substituir: `frontend/src/app/rotas.ts` (passa a exportar `ROTAS`); criar `frontend/src/app/roteador.ts` (+ `frontend/src/app/rotas.test.tsx`)
- Modificar: `frontend/src/app/App.tsx`
- Remover: `frontend/src/features/inicio/` (`PaginaInicio.tsx`, `api.ts`)

**Decisão sobre o status da API (Dnn-status — Dnn = próximo número livre em `docs/decisions.md` na hora do commit, Tarefa 19):** a página inicial do M0 sai e o status **não** vai para o cabeçalho. O cliente HTTP já transforma backend parado em `SEM_CONEXAO` com mensagem amigável, que cada tela mostra no `EstadoErro` com "Tentar de novo"; uma consulta extra a `/api/saude` em toda tela só repetiria isso. O endpoint continua no backend (CI e diagnóstico).

**Rotas:** continuam em `.ts` (não `.tsx` como diz o contrato): não há JSX, porque o redirecionamento é feito por `loader` + `redirect`, e as páginas futuras descobrem a etapa pela URL. O roteador do navegador fica em `roteador.ts`, para os testes importarem `ROTAS` sem criar um `BrowserRouter`.

**Responsivo (README §Responsivo):** ≥ 1280 px a barra começa expandida; abaixo disso começa recolhida (72 px). "Expandir barra" em tela média abre a barra **sobreposta** (sombra 3 + fundo `--cor-overlay`); Esc, clique no fundo ou "Recolher barra" fecham. A escolha do usuário vale até recarregar.

**Passo 1: escrever os testes (falham)**

`useSessaoExpirada.test.tsx`
```tsx
import { useQuery } from '@tanstack/react-query';
import { screen, waitFor } from '@testing-library/react';
import { Outlet } from 'react-router';
import { expect, it } from 'vitest';
import { ErroApi } from '../../shared/api/cliente';
import { renderizarComRotas } from '../../testes/renderizar';
import { useSessaoExpirada } from './useSessaoExpirada';

function PaginaQueFalha({ codigo }: Readonly<{ codigo: string }>) {
  useQuery({
    queryKey: ['teste', codigo],
    queryFn: () => Promise.reject(new ErroApi(404, { codigo, mensagem: 'Sua sessão expirou.', sugestao: 'Envie o arquivo novamente.' })),
  });
  return <p>Análise</p>;
}

function Vigia() {
  useSessaoExpirada();
  return <Outlet />;
}

function renderizar(codigo: string) {
  localStorage.setItem(
    'sessao',
    JSON.stringify({ dataset: { id: 'd1', nomeArquivo: 'pesquisa_saude.txt' }, etapasVisitadas: [1, 2] }),
  );
  return renderizarComRotas(
    [
      {
        path: '/',
        element: <Vigia />,
        children: [
          { path: 'analise', element: <PaginaQueFalha codigo={codigo} /> },
          { path: 'importar', element: <p>Importar</p> },
        ],
      },
    ],
    '/analise',
  );
}

it('DATASET_NAO_ENCONTRADO encerra a sessão, avisa e volta para Importar', async () => {
  renderizar('DATASET_NAO_ENCONTRADO');

  expect(await screen.findByText('Importar')).toBeInTheDocument();
  expect(screen.getByRole('alert')).toHaveTextContent('Sua sessão expirou.');
  const salvo: unknown = JSON.parse(localStorage.getItem('sessao') ?? 'null');
  expect(salvo).toEqual({ dataset: null, etapasVisitadas: [] });
});

it('outros erros não mexem na sessão', async () => {
  const { clienteConsultas } = renderizar('COLUNA_NAO_ENCONTRADA');

  await waitFor(() => {
    expect(clienteConsultas.getQueryState(['teste', 'COLUNA_NAO_ENCONTRADA'])?.status).toBe('error');
  });
  expect(screen.getByText('Análise')).toBeInTheDocument();
  expect(localStorage.getItem('sessao')).toContain('pesquisa_saude.txt');
});
```

`LayoutApp.test.tsx`
```tsx
import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { expect, it } from 'vitest';
import { simularMatchMedia } from '../../testes/matchMedia';
import { renderizarComRotas } from '../../testes/renderizar';
import LayoutApp from './LayoutApp';

const ROTAS_TESTE = [
  { path: '/', element: <LayoutApp />, children: [{ path: 'importar', element: <p>Página de importar</p> }] },
];

it('monta barra, cabeçalho e conteúdo no <main>', async () => {
  simularMatchMedia(['(min-width: 1280px)']);

  renderizarComRotas(ROTAS_TESTE, '/importar');

  expect(await screen.findByText('Página de importar')).toBeInTheDocument();
  expect(screen.getByRole('main')).toContainElement(screen.getByText('Página de importar'));
  expect(screen.getByRole('navigation', { name: 'Etapas da análise' })).toBeInTheDocument();
  expect(screen.getByText('Nenhum arquivo importado')).toBeInTheDocument();
  expect(screen.getByRole('link', { name: 'Pular para o conteúdo' })).toHaveAttribute('href', '#conteudo');
  expect(screen.getByRole('button', { name: 'Recolher barra' })).toHaveAttribute('aria-expanded', 'true');
});

it('mostra o nome do arquivo da sessão no cabeçalho', async () => {
  localStorage.setItem('sessao', JSON.stringify({ dataset: { id: 'd1', nomeArquivo: 'pesquisa_saude.txt' }, etapasVisitadas: [] }));

  renderizarComRotas(ROTAS_TESTE, '/importar');

  expect(await screen.findByText('pesquisa_saude.txt')).toBeInTheDocument();
});

it('em tela média a barra começa recolhida, abre sobreposta e fecha com Esc', async () => {
  renderizarComRotas(ROTAS_TESTE, '/importar');

  await userEvent.click(await screen.findByRole('button', { name: 'Expandir barra' }));
  expect(screen.getByRole('button', { name: 'Fechar a barra de etapas' })).toBeInTheDocument();

  await userEvent.keyboard('{Escape}');
  expect(screen.getByRole('button', { name: 'Expandir barra' })).toBeInTheDocument();
  expect(screen.queryByRole('button', { name: 'Fechar a barra de etapas' })).not.toBeInTheDocument();
});
```
(O `beforeEach` do setup simula `matchMedia` sem correspondências, ou seja, tela menor que 1280 px.)

`app/rotas.test.tsx`
```tsx
import { screen, within } from '@testing-library/react';
import { expect, it } from 'vitest';
import { renderizarComRotas } from '../testes/renderizar';
import { ROTAS } from './rotas';

it.each(['/', '/caminho-que-nao-existe'])('%s leva para Importar', async (caminho) => {
  renderizarComRotas(ROTAS, caminho);

  expect(await screen.findByRole('heading', { level: 1, name: 'Importar arquivo' })).toBeInTheDocument();
});

it('etapa futura abre a página que diz quando ela chega', async () => {
  renderizarComRotas(ROTAS, '/bivariada');

  expect(await screen.findByRole('heading', { level: 1, name: 'Análise bivariada' })).toBeInTheDocument();
  expect(within(screen.getByRole('main')).getByText('Disponível na versão v0.2.')).toBeInTheDocument();
});
```
(O texto também existe no tooltip da barra, por isso a busca é dentro do `<main>`.)

**Passo 2: rodar e ver falhar**
`npx vitest run src/app` → FAIL

**Passo 3: implementar**

`useBarraRecolhivel.ts`
```ts
import { useCallback, useState } from 'react';
import { useConsultaMidia } from '../../shared/lib/useConsultaMidia';
import { useTeclaEsc } from '../../shared/lib/useTeclaEsc';

const CONSULTA_TELA_LARGA = '(min-width: 1280px)';

export interface EstadoBarra {
  recolhida: boolean;
  sobreposta: boolean;
  alternar: () => void;
  recolher: () => void;
}

/** ≥ 1280 px começa expandida; abaixo, recolhida. Expandir em tela média abre por cima do conteúdo. */
export function useBarraRecolhivel(): EstadoBarra {
  const telaLarga = useConsultaMidia(CONSULTA_TELA_LARGA);
  // null = o usuário ainda não escolheu; segue a largura da tela.
  const [escolha, setEscolha] = useState<boolean | null>(null);
  const expandida = escolha ?? telaLarga;
  const sobreposta = expandida && !telaLarga;

  const alternar = useCallback(() => {
    setEscolha(!expandida);
  }, [expandida]);
  const recolher = useCallback(() => {
    setEscolha(false);
  }, []);
  useTeclaEsc(sobreposta, recolher);

  return { recolhida: !expandida, sobreposta, alternar, recolher };
}
```

`useSessaoExpirada.ts`
```ts
import { useQueryClient } from '@tanstack/react-query';
import { useEffect } from 'react';
import { useNavigate } from 'react-router';
import { ehDatasetNaoEncontrado, textoDoErro } from '../../shared/api/erros';
import { useSessao } from '../../shared/sessao/useSessao';
import { useToast } from '../../shared/ui/useToast';
import { ETAPAS } from '../etapas';

/** D61: DATASET_NAO_ENCONTRADO em qualquer consulta ou mutação encerra a sessão, avisa e leva para Importar. */
export function useSessaoExpirada(): void {
  const clienteConsultas = useQueryClient();
  const { encerrar } = useSessao();
  const { mostrar } = useToast();
  const navegar = useNavigate();

  useEffect(() => {
    const aoFalhar = (erro: unknown): void => {
      if (!ehDatasetNaoEncontrado(erro)) return;
      const { mensagem, sugestao } = textoDoErro(erro);
      encerrar();
      mostrar({ tipo: 'erro', titulo: mensagem, descricao: sugestao });
      void navegar(ETAPAS[0].caminho);
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
  }, [clienteConsultas, encerrar, mostrar, navegar]);
}
```

`LayoutApp.tsx`
```tsx
import { Suspense } from 'react';
import { Outlet } from 'react-router';
import { juntarClasses } from '../../shared/lib/classes';
import { useSessao } from '../../shared/sessao/useSessao';
import EstadoCarregando from '../../shared/ui/EstadoCarregando';
import { TEXTOS_APP } from '../textos';
import BarraEtapas from './BarraEtapas';
import Cabecalho from './Cabecalho';
import estilos from './LayoutApp.module.css';
import { useBarraRecolhivel } from './useBarraRecolhivel';
import { useSessaoExpirada } from './useSessaoExpirada';

export default function LayoutApp() {
  const { dataset } = useSessao();
  const barra = useBarraRecolhivel();
  useSessaoExpirada();

  return (
    <div className={juntarClasses(estilos.app, (barra.recolhida || barra.sobreposta) && estilos.estreita)}>
      <a href="#conteudo" className={estilos.pular}>
        {TEXTOS_APP.pularParaConteudo}
      </a>
      <BarraEtapas recolhida={barra.recolhida} sobreposta={barra.sobreposta} aoAlternar={barra.alternar} />
      {barra.sobreposta ? (
        <button
          type="button"
          tabIndex={-1}
          className={estilos.fundo}
          aria-label={TEXTOS_APP.fecharBarra}
          onClick={barra.recolher}
        />
      ) : null}
      <div className={estilos.coluna}>
        {/* M1.6: passar nLinhas/nColunas do resumo do dataset (react-query). */}
        <Cabecalho nomeArquivo={dataset?.nomeArquivo} />
        <main id="conteudo" className={estilos.principal}>
          <Suspense fallback={<EstadoCarregando mensagem={TEXTOS_APP.abrindoEtapa} />}>
            <Outlet />
          </Suspense>
        </main>
      </div>
    </div>
  );
}
```

`LayoutApp.module.css`
```css
.app { display: grid; grid-template-columns: var(--largura-barra) minmax(0, 1fr); min-height: 100vh; background: var(--cor-fundo); }
.estreita { grid-template-columns: var(--largura-barra-recolhida) minmax(0, 1fr); }
/* Coluna fixa: a barra sobreposta sai do fluxo e o conteúdo não pode pular para a 1ª coluna. */
.coluna { display: flex; flex-direction: column; grid-column: 2; min-width: 0; }
.principal { flex: 1; width: 100%; max-width: calc(var(--largura-conteudo) + 2 * var(--esp-32)); padding: var(--esp-32); }
.pular {
  position: absolute;
  top: var(--esp-16);
  left: var(--esp-16);
  z-index: 60;
  padding: var(--esp-8) var(--esp-12);
  border-radius: var(--raio-md);
  background: var(--cor-superficie-elevada);
  box-shadow: var(--sombra-2);
  transform: translateY(-200%);
}
.pular:focus { transform: none; }
.fundo { position: fixed; inset: 0; z-index: 20; border: 0; background: var(--cor-overlay); cursor: pointer; }

@media (max-width: 767px) {
  .principal { padding: var(--esp-16); }
}
```

`app/rotas.ts` (substitui o arquivo atual)
```ts
import { type ComponentType, lazy } from 'react';
import { type RouteObject, redirect } from 'react-router';
import { ETAPAS, type Etapa } from './etapas';
import LayoutApp from './layout/LayoutApp';

const PaginaImportar = lazy(() => import('../features/importar/PaginaImportar'));
const PaginaVariaveis = lazy(() => import('../features/variaveis/PaginaVariaveis'));
const PaginaLimpeza = lazy(() => import('../features/limpeza/PaginaLimpeza'));
const PaginaAnalise = lazy(() => import('../features/analise/PaginaAnalise'));
const PaginaRelatorio = lazy(() => import('../features/relatorio/PaginaRelatorio'));
const PaginaIndisponivel = lazy(() => import('./paginas/PaginaIndisponivel'));

/** Uma página por etapa; as futuras (D60) usam PaginaIndisponivel. */
const PAGINAS = {
  1: PaginaImportar,
  2: PaginaVariaveis,
  3: PaginaLimpeza,
  4: PaginaAnalise,
  5: PaginaIndisponivel,
  6: PaginaIndisponivel,
  7: PaginaIndisponivel,
  8: PaginaRelatorio,
} as const satisfies Record<Etapa['numero'], ComponentType>;

const irParaInicio = () => redirect(ETAPAS[0].caminho);

export const ROTAS: RouteObject[] = [
  {
    path: '/',
    Component: LayoutApp,
    children: [
      { index: true, loader: irParaInicio },
      ...ETAPAS.map((etapa) => ({ path: etapa.caminho, Component: PAGINAS[etapa.numero] })),
      { path: '*', loader: irParaInicio },
    ],
  },
];
```

`app/roteador.ts`
```ts
import { createBrowserRouter } from 'react-router';
import { ROTAS } from './rotas';

export const roteador = createBrowserRouter(ROTAS);
```

`app/App.tsx`
```tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useState } from 'react';
import { RouterProvider } from 'react-router';
import SessaoProvider from '../shared/sessao/SessaoProvider';
import TemaProvider from '../shared/tema/TemaProvider';
import ToastProvider from '../shared/ui/ToastProvider';
import { roteador } from './roteador';

export default function App() {
  const [clienteConsultas] = useState(() => new QueryClient());

  return (
    <QueryClientProvider client={clienteConsultas}>
      <TemaProvider>
        <SessaoProvider>
          <ToastProvider>
            <RouterProvider router={roteador} />
          </ToastProvider>
        </SessaoProvider>
      </TemaProvider>
    </QueryClientProvider>
  );
}
```
O `Suspense` que envolvia o `RouterProvider` sai: o `LayoutApp` não é lazy e já envolve o `<Outlet/>` num `Suspense` com skeleton.

Remover a página inicial:
```bash
git rm -r frontend/src/features/inicio
```
`main.tsx` não muda nesta tarefa (já importa fontes, estilos e chama `aplicarTemaInicial()`).

**Passo 4: rodar e ver passar**
`npm run test` → todos passam. `npm run lint && npm run format && npm run build` → verdes. `grep -rn "inicio\|useSaude" src` → nada.

**Passo 5: commit**
```bash
git add frontend/src/app frontend/src/features
git commit -m "feat(frontend): monta layout com barra recolhível, rotas das 8 etapas e sessão expirada"
```

---

### Tarefa 19: Docs, verificação final, teste manual e PR

**Arquivos:**
- Modificar: `CHANGELOG.md`, `docs/decisions.md`, `docs/specs/15-frontend.md`

**Passo 1: `CHANGELOG.md`** — em *Não lançado › Adicionado*:
```
- Base visual do frontend (M1.1): fontes e ícones locais (@fontsource), tokens de espaço e raio, tema claro/escuro salvo no navegador.
- Componentes de `shared/ui`: Icone, Botao, Card, Banner, estados de carregando/vazio/erro, Toast, Tooltip, Select, CampoNumero, CaixaSelecao, Segmented, Abas, CardMetrica, Tabela e PaginaEtapa.
- Layout com barra de etapas (concluída, atual, disponível, bloqueada; recolhível), cabeçalho com arquivo atual e rotas das 8 etapas (5–7 bloqueadas até a versão em que entram).
- Sessão do dataset no navegador; sessão expirada na API leva de volta para Importar com aviso.
- Formatadores pt-BR (`shared/lib/formatar.ts`) e wrapper Plotly com o tema dos tokens, carregado sob demanda.
- Testes de componentes com Vitest + jsdom + Testing Library.
```
E criar *Não lançado › Removido* (se não existir):
```
- Página inicial com o status da API (as telas mostram a falta de conexão no próprio estado de erro).
```

**Passo 2: `docs/decisions.md`** — acrescentar ao fim da tabela. D58–D61 e D63 são os números reservados na visão geral. A decisão do status da API **não tem número fixo** (os blocos entram em ordens diferentes): use **Dnn (próximo número livre em `docs/decisions.md` na hora do commit)** e troque o rótulo `Dnn-status` da Tarefa 18 por esse número:
```
| D58 | 03/10/2026 | Testes de componentes com Vitest + jsdom 29 + Testing Library (`jest-dom`, `user-event`); setup em `src/testes/configuracao.ts` | happy-dom; só testes de funções puras | API de DOM mais completa; testa papéis, rótulos e teclado. jsdom 30 exige Node ≥ 22.22 | — |
| D59 | 03/10/2026 | Ícones Material Symbols Rounded locais via `@fontsource-variable/material-symbols-rounded` (`full.css`, com eixo FILL); Inter e JetBrains Mono via `@fontsource`; sem Google Fonts | `@material-symbols/font-400`; SVGs | Uso offline; eixo FILL para ícones preenchidos | — |
| D60 | 03/10/2026 | No M1, etapas 5–7 aparecem bloqueadas na barra com "Disponível na versão {v}." (tooltip) e têm página própria com o mesmo aviso; a aba "Forma e distribuição" fica oculta até o M2 (M1.7) | Esconder as etapas | Mostra o roteiro sem prometer o que ainda não existe | — |
| D61 | 03/10/2026 | Sessão do frontend (id e nome do dataset, etapas visitadas) no `localStorage('sessao')`, validada na leitura; trocar de dataset zera as visitadas; `DATASET_NAO_ENCONTRADO` em qualquer consulta ou mutação encerra a sessão, mostra toast e leva para Importar | Só em memória; `sessionStorage` | Sobrevive a recarregar a página; o backend guarda datasets em memória e pode reiniciar | — |
| D63 | 03/10/2026 | Gráficos com `react-plotly.js/factory` + `plotly.js-dist-min`, carregados com `React.lazy`; o tema é aplicado mesclando o layout e o gráfico remonta ao trocar o tema | `plotly.js` completo; `Plotly.react` manual | Bundle menor; troca de tema sem lógica de diff | [0008](adr/0008-design-system-tokens-css.md) |
| Dnn | 03/10/2026 | Removida a página inicial com status da API; falta de conexão aparece no `EstadoErro` de cada tela (`SEM_CONEXAO`) | Indicador no cabeçalho | Evita consulta extra e código fora do fluxo das 8 etapas | — |
```

**Passo 3: `docs/specs/15-frontend.md`** — na seção "Layout geral":
- Linha da barra lateral: acrescentar "Etapas que entram em versões futuras (5–7 no M1) ficam bloqueadas com 'Disponível na versão {v}.' (D60)."
- Nova linha: "**Sessão:** o arquivo ativo e as etapas visitadas ficam salvos no navegador; se a API avisar que a sessão expirou, o app volta para Importar com um aviso (D61)."
- Linha do responsivo: "768–1279 px barra lateral recolhida (72 px), abre por cima do conteúdo".

**Passo 4: verificação final** (tudo verde)
```bash
cd frontend
npm run lint && npm run format && npm run test && npm run build
cd ..
npx --yes jscpd@4 backend/app backend/tests frontend/src
cd frontend
ls dist/assets | grep -c woff2                      # > 0
grep -l "plotly" dist/assets/*.js || echo "Plotly fora do bundle principal"
ls dist/assets/*.js                                  # um chunk por página (PaginaImportar-*.js, ...)
```
Se o backend estiver configurado, rode também a verificação do backend de `CLAUDE.md` (nada muda nele, mas o CI roda os três jobs).

**Passo 5: teste manual pelo preview** (`.claude/launch.json` → `frontend`; o backend não é necessário neste bloco)
- [ ] `/` abre `/importar`; barra com 2–8 bloqueadas (cadeado), frase de bloqueio, cabeçalho "Nenhum arquivo importado" (compare com o print `1b`).
- [ ] Tema: alternar claro/escuro no cabeçalho; recarregar mantém a escolha; sem escolha salva, segue o sistema. Compare cores com `4i` (escuro).
- [ ] Teclado: Tab mostra "Pular para o conteúdo"; foco visível (anel azul) em links, botões e alternância de tema; ←/→ trocam o tema; Esc fecha tooltip.
- [ ] Hover/foco em "Bivariada" mostra "Disponível na versão v0.2."; `/bivariada` abre a página com o mesmo aviso.
- [ ] Simular sessão no console do navegador e recarregar:
  `localStorage.setItem('sessao', JSON.stringify({dataset:{id:'x',nomeArquivo:'pesquisa_saude.txt'},etapasVisitadas:[1,2,3]}))`
  → cabeçalho com `pesquisa_saude.txt` e "Trocar arquivo"; Importar/Variáveis/Limpeza "Concluída"; Análise e Relatório disponíveis; 5–7 bloqueadas (compare com `4h`).
- [ ] Responsivo: em 1024 px a barra fica com 72 px (só marcadores; nome no tooltip à direita); "Expandir barra" abre por cima com fundo escurecido; Esc fecha. Em 1440 px a barra volta a 264 px.
- [ ] Ícones aparecem como símbolos (não como palavras) e o DevTools › Network não mostra requisições a `fonts.googleapis.com`.

**Passo 6: commit**
```bash
git add CHANGELOG.md docs/decisions.md docs/specs/15-frontend.md
git commit -m "docs: registra decisões do M1.1 e atualiza changelog e spec do frontend"
```

**Passo 7: PR** — **só depois do ok do usuário**
```bash
git push -u origin chore/frontend-base-visual
gh pr create --base develop --title "chore(frontend): base visual do M1 (M1.1)" --body "<resumo por tarefa; specs 15 e 16; docs/design; checklist de padroes-codigo.md §8; prints claro/escuro e 1024 px>"
```
Sem linhas de coautoria ou atribuição de IA no corpo. Esperar o CI (`backend`, `frontend`, `duplicacao`) verde antes do merge.

---

## Critérios de pronto do M1.1
- [ ] Fontes e ícones servidos localmente; nenhum acesso a Google Fonts.
- [ ] `tokens.css` com `--esp-*`, `--raio-*`, famílias de fonte e `color-scheme`; `base.css` com foco visível, `.visualmente-oculto` e `prefers-reduced-motion`.
- [ ] Tema claro/escuro: `data-tema` no `<html>`, `localStorage('tema')`, padrão do sistema, aplicado antes do primeiro render.
- [ ] Sessão em `localStorage('sessao')` validada na leitura; `DATASET_NAO_ENCONTRADO` encerra a sessão e leva para Importar com toast.
- [ ] `formatarNumero`/`formatarInteiro`/`formatarPercentual`/`lerNumeroPtBr` com a regra de casas igual à do backend.
- [ ] Todos os componentes do contrato (exceto `ChipTipo`, M1.6) com CSS Module, `var(--token)` e teste de papel/rótulo/teclado.
- [ ] `Grafico` com tema dos tokens, Plotly via `React.lazy`, remonta ao trocar o tema.
- [ ] Layout: barra com os 4 estados, frase de bloqueio, etapas 5–7 bloqueadas com versão, recolhível (72 px em 768–1279 px); cabeçalho com arquivo, "Trocar arquivo" e alternância de tema; rotas das 8 etapas; `features/inicio` removida.
- [ ] Lint, Prettier, Vitest, build e jscpd verdes; CI verde no PR; teste manual do Passo 5 feito.
- [ ] `CHANGELOG.md`, `docs/decisions.md` (D58–D61, D63 e a decisão do status da API com o próximo número livre) e `docs/specs/15-frontend.md` atualizados.
