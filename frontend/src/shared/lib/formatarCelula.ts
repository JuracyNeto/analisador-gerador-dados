import type { components } from '../api/schema';
import { TEXTOS_UI } from '../ui/textos';

export type Celula = components['schemas']['LinhaDados']['valores'][string];

const NUMERO_CELULA = new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 10 });
const INTEIRO_CELULA = new Intl.NumberFormat('pt-BR', { useGrouping: false });
const MENOS = '−';

/** Como o backend (`texto_do_numero`): inteiros sem ponto de milhar (códigos, anos), sinal "−". */
function formatarNumeroCelula(valor: number): string {
  const formato = Number.isInteger(valor) ? INTEIRO_CELULA : NUMERO_CELULA;
  const texto = formato.format(valor);
  return texto.startsWith('-') ? `${MENOS}${texto.slice(1)}` : texto;
}

/** Valor bruto de uma célula para exibir em tabela (sem arredondar casas significativas). */
export function formatarCelula(valor: Celula | undefined): string {
  if (valor === null || valor === undefined) return TEXTOS_UI.valorAusente;
  if (typeof valor === 'number') return formatarNumeroCelula(valor);
  if (typeof valor === 'boolean') return valor ? TEXTOS_UI.sim : TEXTOS_UI.nao;
  return valor;
}
