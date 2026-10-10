import { formatarNumero } from '../lib/formatar';
import type { components } from '../api/schema';

type ValorMedida = components['schemas']['Medida']['valor'];

/** Número em pt-BR; texto (categoria, equação) como veio; ausente vira travessão. */
export function formatarValorMedida(valor: ValorMedida, casasSignificativas?: number): string {
  if (valor === null) return '—';
  return typeof valor === 'number' ? formatarNumero(valor, casasSignificativas) : valor;
}
