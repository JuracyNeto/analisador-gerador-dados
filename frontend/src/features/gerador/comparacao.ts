/** Textos da tabela Original × Gerado (puro). Diferença absoluta com sinal (D110). */
import { formatarInteiro, formatarNumero, formatarPercentual } from '../../shared/lib/formatar';
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

/** "+0,3", "−0,27", "0"; nas frequências, em pontos percentuais ("+2,2 p.p."). */
export function formatarDiferenca(linha: LinhaComparacao): string {
  const { diferenca } = linha;
  if (diferenca === null) return VAZIO;
  const texto = formatarNumero(diferenca, ehFrequencia(linha) ? 2 : 4);
  const comSinal = diferenca > 0 ? `+${texto}` : texto;
  return ehFrequencia(linha) ? `${comSinal} p.p.` : comSinal;
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
