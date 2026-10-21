import axe from 'axe-core';
import { expect } from 'vitest';

/** WCAG 2.0 e 2.1, níveis A e AA, e as boas práticas do axe (D153). */
const ETIQUETAS = ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'best-practice'];

/**
 * Regras desligadas nos testes: o jsdom não calcula cores (o contraste fica com o teste dos
 * tokens) e um componente ou uma tela isolada não tem o `main`, o h1 nem o link de pular do layout
 * (o teste do layout cobre isso).
 */
const DESLIGADAS = [
  'color-contrast',
  'region',
  'landmark-one-main',
  'page-has-heading-one',
  'bypass',
];

/** Violações do axe no elemento, como "button-name (critical): button". */
export async function violacoesAxe(alvo: Element = document.body): Promise<string[]> {
  const resultado = await axe.run(alvo, {
    runOnly: { type: 'tag', values: ETIQUETAS },
    rules: Object.fromEntries(DESLIGADAS.map((regra) => [regra, { enabled: false }])),
  });
  return resultado.violations.map(
    (violacao) =>
      `${violacao.id} (${violacao.impact ?? 'sem impacto'}): ${violacao.nodes
        .map((no) => no.target.join(' '))
        .join(' | ')}`,
  );
}

export async function esperarSemViolacoes(alvo: Element = document.body): Promise<void> {
  expect(await violacoesAxe(alvo)).toEqual([]);
}
