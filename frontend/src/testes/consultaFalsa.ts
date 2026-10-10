import { vi } from 'vitest';
import type { ConsultaSimples } from '../shared/api/consulta';

/** Consulta para testar os estados de tela; começa pendente, sem dados. */
export function consultaFalsa<T>(parcial: Partial<ConsultaSimples<T>> = {}): ConsultaSimples<T> {
  return {
    status: 'pending',
    data: undefined,
    error: null,
    isPlaceholderData: false,
    refetch: vi.fn(),
    ...parcial,
  };
}
