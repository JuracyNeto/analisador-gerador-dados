/** X e Y da tela 5 na URL (`?x=&y=`), como coluna e classes na tela 4 (D78, D105). */
import type { Par, TipoColuna } from './tipos';

export interface ParPedido {
  x: string | null;
  y: string | null;
}

export function lerPar(busca: URLSearchParams): ParPedido {
  return { x: busca.get('x'), y: busca.get('y') };
}

/** O par da URL se as duas colunas ainda forem numéricas e diferentes; senão as duas primeiras. */
export function parEscolhido(pedido: ParPedido, colunas: readonly TipoColuna[]): Par | null {
  const nomes = colunas.map((coluna) => coluna.coluna);
  const [primeira, segunda] = nomes;
  if (primeira === undefined || segunda === undefined) return null;
  const { x, y } = pedido;
  const valido = x !== null && y !== null && x !== y && nomes.includes(x) && nomes.includes(y);
  return valido ? { x, y } : { x: primeira, y: segunda };
}

export function comPar(busca: URLSearchParams, par: Par): URLSearchParams {
  const nova = new URLSearchParams(busca);
  nova.set('x', par.x);
  nova.set('y', par.y);
  return nova;
}

export function trocado(par: Par): Par {
  return { x: par.y, y: par.x };
}
