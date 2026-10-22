import { startTransition } from 'react';
import { useSearchParams } from 'react-router';
import {
  comAba,
  comClasses,
  comColuna,
  comTentativas,
  lerParametros,
  semTentativas,
  type ParametrosAnalise,
} from '../parametros';
import type { IdAba } from '../tipos';

export interface ParametrosAnaliseNaUrl extends ParametrosAnalise {
  escolherColuna: (coluna: string) => void;
  mudarClasses: (k: number) => void;
  mudarTentativas: (n: number) => void;
  usarTentativasPadrao: () => void;
  mudarAba: (aba: IdAba) => void;
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
    mudarTentativas: (n) => {
      definirBusca((atual) => comTentativas(atual, n), { replace: true });
    },
    usarTentativasPadrao: () => {
      definirBusca((atual) => semTentativas(atual), { replace: true });
    },
    mudarAba: (aba) => {
      definirBusca((atual) => comAba(atual, aba), { replace: true });
    },
  };
}
