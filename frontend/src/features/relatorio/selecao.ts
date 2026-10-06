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
  const secoes = semColunas
    ? selecao.secoes.filter((secao) => secao !== 'analises')
    : selecao.secoes;
  if (secoes.length === 0) return null;
  return { secoes, colunas: secoes.includes('analises') ? selecao.colunas : [] };
}
