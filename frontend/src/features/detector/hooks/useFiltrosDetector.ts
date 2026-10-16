import { startTransition } from 'react';
import { useSearchParams } from 'react-router';
import { escreverParametros, lerParametros } from '../parametros';
import type { Agrupamento, FiltrosDetector, Severidade } from '../tipos';

export interface FiltrosNaUrl extends FiltrosDetector {
  alternarSeveridade: (severidade: Severidade) => void;
  mudarAgrupamento: (agrupar: Agrupamento) => void;
}

function alternada(filtros: FiltrosDetector, severidade: Severidade): FiltrosDetector {
  const severidades = new Set(filtros.severidades);
  if (!severidades.delete(severidade)) severidades.add(severidade);
  return { ...filtros, severidades };
}

/** Filtros e agrupamento na URL (D140): recarregar ou voltar mantém a escolha. */
export function useFiltrosDetector(): FiltrosNaUrl {
  const [busca, definirBusca] = useSearchParams();
  const mudar = (transformar: (atuais: FiltrosDetector) => FiltrosDetector) => {
    // Filtrar não é urgente: o chip responde na hora e a lista vem depois (§6).
    startTransition(() => {
      definirBusca((atual) => escreverParametros(atual, transformar(lerParametros(atual))));
    });
  };
  return {
    ...lerParametros(busca),
    alternarSeveridade: (severidade) => {
      mudar((atuais) => alternada(atuais, severidade));
    },
    mudarAgrupamento: (agrupar) => {
      mudar((atuais) => ({ ...atuais, agrupar }));
    },
  };
}
