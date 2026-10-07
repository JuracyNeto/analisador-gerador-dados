import { startTransition } from 'react';
import { useSearchParams } from 'react-router';
import { comClasses, comColuna, lerParametros, type ParametrosAnalise } from '../parametros';

export interface ParametrosAnaliseNaUrl extends ParametrosAnalise {
  escolherColuna: (coluna: string) => void;
  mudarClasses: (k: number) => void;
}

export function useParametrosAnalise(): ParametrosAnaliseNaUrl {
  const [busca, definirBusca] = useSearchParams();

  return {
    ...lerParametros(busca),
    escolherColuna: (coluna) => {
      // Trocar de coluna não é urgente: o select responde na hora e o recálculo vem depois.
      startTransition(() => {
        definirBusca((atual) => comColuna(atual, coluna));
      });
    },
    mudarClasses: (k) => {
      definirBusca((atual) => comClasses(atual, k), { replace: true });
    },
  };
}
