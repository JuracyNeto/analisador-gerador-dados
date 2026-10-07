import { formatarNumero } from '../../shared/lib/formatar';
import type { Medida } from './tipos';

/** Número em pt-BR; texto (categoria) como veio; ausente vira travessão. */
export function formatarValorMedida(valor: Medida['valor'], casasSignificativas?: number): string {
  if (valor === null) return '—';
  return typeof valor === 'number' ? formatarNumero(valor, casasSignificativas) : valor;
}

export function formatarOpcional(valor: number | null, formatar: (v: number) => string): string {
  return valor === null ? '—' : formatar(valor);
}
