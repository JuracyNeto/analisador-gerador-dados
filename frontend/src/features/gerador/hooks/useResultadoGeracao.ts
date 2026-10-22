import { useState } from 'react';
import { useSessao } from '../../../shared/sessao/useSessao';
import { useGeracaoGuardada } from '../api';
import type { Gerado, IdAba } from '../tipos';
import type { useGeracao } from './useGeracao';

export interface ResultadoDaAba {
  gerado: Gerado | undefined;
  gerando: boolean;
  expirar: () => void;
  gerarDeNovo: (() => void) | null;
}

/** A última geração da sessão, se for do tipo da aba e ainda estiver no servidor. */
function useUltimaGeracao(aba: IdAba) {
  const { ultimoGerado } = useSessao();
  const [descartada, definirDescartada] = useState<string | null>(null);
  const id = ultimoGerado?.id ?? null;
  const consulta = useGeracaoGuardada(id === descartada ? null : id);
  const gerado = consulta.data?.tipo === aba ? consulta.data : undefined;
  return { gerado, descartar: definirDescartada };
}

/**
 * O resultado mostrado na aba: a geração feita agora ou, ao voltar à etapa (ou recarregar),
 * a última da sessão — o relatório já a usa. Se ela saiu da memória do servidor, a aba fica vazia.
 */
export function useResultadoGeracao(
  aba: IdAba,
  geracao: ReturnType<typeof useGeracao>,
): ResultadoDaAba {
  const mutacao = aba === 'univariado' ? geracao.univariado : geracao.bivariado;
  const ultima = useUltimaGeracao(aba);
  const gerado = mutacao.data ?? ultima.gerado;
  return {
    gerado,
    gerando: mutacao.isPending,
    expirar: () => {
      mutacao.reset();
      if (gerado !== undefined) ultima.descartar(gerado.gerado_id);
    },
    gerarDeNovo: mutacao.data === undefined ? null : geracao.refazer(mutacao.data),
  };
}
