import type { components } from '../api/schema';

export type Celula = components['schemas']['LinhaDados']['valores'][string];

const NUMERO_CELULA = new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 10 });
const VAZIO = '—';

/** Valor bruto de uma célula para exibir em tabela (sem arredondar casas significativas). */
export function formatarCelula(valor: Celula | undefined): string {
  if (valor === null || valor === undefined) return VAZIO;
  if (typeof valor === 'number') return NUMERO_CELULA.format(valor);
  if (typeof valor === 'boolean') return valor ? 'Sim' : 'Não';
  return valor;
}
