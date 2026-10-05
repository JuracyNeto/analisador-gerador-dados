import { createContext } from 'react';

export type TipoToast = 'sucesso' | 'erro';

export interface AcaoToast {
  rotulo: string;
  aoClicar: () => void;
}

export interface PedidoToast {
  tipo: TipoToast;
  /** Verbo no passado + quantidade (spec 16): "Limpeza aplicada: 12 linhas removidas." */
  titulo: string;
  descricao?: string | undefined;
  acao?: AcaoToast | undefined;
}

export interface ToastAtivo extends PedidoToast {
  id: number;
}

export interface ValorToast {
  mostrar: (pedido: PedidoToast) => void;
}

export const ContextoToast = createContext<ValorToast | null>(null);
