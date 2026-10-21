import axe from 'axe-core';
import { expect } from 'vitest';

/** Limite dos testes que rodam o axe em telas inteiras (vários segundos com a suíte toda). */
export const TEMPO_AXE = 20_000;

/** WCAG 2.0 e 2.1, níveis A e AA, e as boas práticas do axe (D153). */
const ETIQUETAS = ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'best-practice'];

/** O jsdom não calcula cores: o contraste fica com o teste dos tokens. */
const SO_COR = ['color-contrast'];

/**
 * Num componente ou numa tela isolada, também ficam de fora as regras da página inteira: o `main`,
 * o h1 e o link de pular são do layout (o teste do layout cobre essas).
 */
const DESLIGADAS = [...SO_COR, 'region', 'landmark-one-main', 'page-has-heading-one', 'bypass'];

/** Violações do axe no elemento, como "button-name (critical): button". */
export async function violacoesAxe(
  alvo: Element = document.body,
  desligadas: readonly string[] = DESLIGADAS,
): Promise<string[]> {
  const resultado = await axe.run(alvo, {
    runOnly: { type: 'tag', values: ETIQUETAS },
    rules: Object.fromEntries(desligadas.map((regra) => [regra, { enabled: false }])),
    // O jsdom não carrega iframes (a prévia do relatório é outro documento).
    iframes: false,
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

/** A página montada com o layout: só a regra de cor fica de fora. */
export async function esperarPaginaSemViolacoes(): Promise<void> {
  expect(await violacoesAxe(document.body, SO_COR)).toEqual([]);
}
