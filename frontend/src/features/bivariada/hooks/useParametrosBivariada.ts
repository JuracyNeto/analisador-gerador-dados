import { startTransition } from 'react';
import { useSearchParams } from 'react-router';
import { comPar, lerPar, type ParPedido } from '../parametros';
import type { Par } from '../tipos';

export interface ParNaUrl {
  pedido: ParPedido;
  escolher: (par: Par) => void;
}

export function useParametrosBivariada(): ParNaUrl {
  const [busca, definirBusca] = useSearchParams();
  return {
    pedido: lerPar(busca),
    escolher: (par) => {
      // Trocar o par não é urgente: os selects respondem na hora e o cálculo vem depois.
      startTransition(() => {
        definirBusca((atual) => comPar(atual, par));
      });
    },
  };
}
