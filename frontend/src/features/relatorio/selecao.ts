import type { SecaoRelatorio, SelecaoRelatorio } from './api';

/** Seções que mostram as colunas escolhidas (D106). */
const SECOES_POR_COLUNA: ReadonlySet<SecaoRelatorio> = new Set(['analises', 'distribuicoes']);

export function usaColunas(secoes: readonly SecaoRelatorio[]): boolean {
  return secoes.some((secao) => SECOES_POR_COLUNA.has(secao));
}

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
  const secoes = semColunas
    ? selecao.secoes.filter((secao) => !SECOES_POR_COLUNA.has(secao))
    : selecao.secoes;
  if (secoes.length === 0) return null;
  return { secoes, colunas: usaColunas(secoes) ? selecao.colunas : [] };
}
