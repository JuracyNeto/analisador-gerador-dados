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
  // Sem consulta ou fora da faixa observada: nada é destacado.
  if (posicao?.fora_da_faixa !== null) return null;
  return `${PREFIXOS[posicao.tipo]}${String(posicao.indice)}`;
}

export function percentisVisiveis(
  separatrizes: Separatrizes,
  destaque: string | null,
): ValorSeparatriz[] {
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
