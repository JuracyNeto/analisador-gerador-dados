/** Textos da tabela Original × Gerado (puro). Diferença absoluta com sinal (D110). */
import {
  formatarDecimal,
  formatarInteiro,
  formatarNumero,
  formatarPercentual,
} from '../../shared/lib/formatar';
import { TEXTOS_GERADOR } from './textos';
import type { Gerado, LinhaComparacao } from './tipos';

const VAZIO = '—';
const PREFIXO_FREQUENCIA = 'fr% · ';
const ESTATISTICA_N = 'n';

function ehFrequencia(linha: LinhaComparacao): boolean {
  return linha.estatistica.startsWith(PREFIXO_FREQUENCIA);
}

export function formatarValor(linha: LinhaComparacao, valor: number | null): string {
  if (valor === null) return VAZIO;
  if (linha.estatistica === ESTATISTICA_N) return formatarInteiro(valor);
  return ehFrequencia(linha) ? formatarPercentual(valor) : formatarNumero(valor);
}

const MENOS = '−';
const DECIMAIS = /,(\d+)/u;

function casasDe(texto: string): number {
  return DECIMAIS.exec(texto)?.[1]?.length ?? 0;
}

function sinal(valor: number): string {
  if (valor > 0) return '+';
  return valor < 0 ? MENOS : '';
}

/**
 * Na precisão dos valores mostrados (print 6a: "0,0", "+0,3", "−0,27"): o resto de
 * arredondamento da reescala não aparece. Frequências em pontos percentuais.
 */
export function formatarDiferenca(linha: LinhaComparacao): string {
  const { diferenca } = linha;
  if (diferenca === null) return VAZIO;
  const casas = Math.max(
    casasDe(formatarValor(linha, linha.original)),
    casasDe(formatarValor(linha, linha.gerado)),
  );
  const arredondada = Number(diferenca.toFixed(casas));
  const absoluta =
    arredondada === 0 ? formatarDecimal(0, casas) : formatarNumero(Math.abs(arredondada));
  const texto = `${sinal(arredondada)}${absoluta}`;
  return ehFrequencia(linha) ? `${texto} p.p.` : texto;
}

/** "Semente 42 · preservar estatísticas" (o modo vem dos parâmetros da geração). */
export function subtituloResultado(gerado: Gerado): string {
  const modo = gerado.parametros.find((parametro) => parametro.nome === 'Modo')?.valor;
  const textoModo = modo?.toLowerCase() ?? TEXTOS_GERADOR.modoNoSubtitulo.bivariado;
  return TEXTOS_GERADOR.resultado.subtitulo(gerado.semente, textoModo);
}

export function quantidadeGerada(gerado: Gerado): string {
  return formatarInteiro(gerado.n);
}
