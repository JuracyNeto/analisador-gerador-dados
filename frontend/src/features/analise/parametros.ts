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
export function colunaEscolhida(
  pedida: string | null,
  colunas: readonly TipoColuna[],
): TipoColuna | null {
  return colunas.find((coluna) => coluna.coluna === pedida) ?? colunas[0] ?? null;
}
