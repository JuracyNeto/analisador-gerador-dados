/** X e Y da tela 5 na URL (`?x=&y=`), como coluna e classes na tela 4 (D78, D105). */
import type { MatrizCorrelacao, Par, TipoColuna } from './tipos';

export interface ParPedido {
  x: string | null;
  y: string | null;
}

export function lerPar(busca: URLSearchParams): ParPedido {
  return { x: busca.get('x'), y: busca.get('y') };
}

function parDaUrl(pedido: ParPedido, nomes: readonly string[]): Par | null {
  const { x, y } = pedido;
  const valido = x !== null && y !== null && x !== y && nomes.includes(x) && nomes.includes(y);
  return valido ? { x, y } : null;
}

/** O par com o maior |r| da matriz (empate: o primeiro na ordem das colunas). */
export function parMaisForte(matriz: MatrizCorrelacao): Par | null {
  const candidatos = matriz.colunas.flatMap((x, i) =>
    matriz.colunas.slice(i + 1).map((y, deslocamento) => ({
      par: { x, y },
      r: Math.abs(matriz.valores[i]?.[i + 1 + deslocamento] ?? Number.NaN),
    })),
  );
  const validos = candidatos.filter((candidato) => Number.isFinite(candidato.r));
  const melhor = validos.reduce<(typeof validos)[number] | null>(
    (atual, candidato) => (atual === null || candidato.r > atual.r ? candidato : atual),
    null,
  );
  return melhor?.par ?? null;
}

/**
 * O par da URL se as duas colunas ainda forem numéricas e diferentes; sem ele, o par mais
 * forte da matriz (a que o heatmap aponta) e, sem matriz, as duas primeiras numéricas.
 */
export function parEscolhido(
  pedido: ParPedido,
  colunas: readonly TipoColuna[],
  matriz: MatrizCorrelacao | null,
): Par | null {
  const nomes = colunas.map((coluna) => coluna.coluna);
  const [primeira, segunda] = nomes;
  if (primeira === undefined || segunda === undefined) return null;
  const forte = matriz === null ? null : parMaisForte(matriz);
  const forteValido = forte !== null && nomes.includes(forte.x) && nomes.includes(forte.y);
  return parDaUrl(pedido, nomes) ?? (forteValido ? forte : { x: primeira, y: segunda });
}

/** Sem par na URL, a tela espera a matriz para abrir no par mais forte (só quando há ≥ 2). */
export function esperaAMatriz(
  pedido: ParPedido,
  colunas: readonly TipoColuna[],
  matrizPendente: boolean,
): boolean {
  const nomes = colunas.map((coluna) => coluna.coluna);
  return matrizPendente && nomes.length >= 2 && parDaUrl(pedido, nomes) === null;
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
