import { useState } from 'react';
import type { ResumoDataset } from '../../../shared/api/dataset';
import { useReler } from '../api';
import { aplicarCorrecao, type CampoDeteccao, type OpcoesLeitura } from '../opcoesLeitura';

export interface Releitura {
  lendo: boolean;
  corrigir: (campo: CampoDeteccao, valor: string) => void;
  /** Detecta tudo de novo (sem as correções). */
  lerDeNovo: () => void;
  aguardandoConfirmacao: boolean;
  confirmar: () => void;
  cancelar: () => void;
}

/**
 * Corrigir a leitura relê no servidor o arquivo guardado (D88), mesmo depois de avançar.
 * Com tipos corrigidos ou limpeza aplicada, pede confirmação antes, porque eles se perdem.
 */
export function useReleitura(resumo: ResumoDataset): Releitura {
  const reler = useReler(resumo.dataset_id);
  const [pendente, setPendente] = useState<OpcoesLeitura | null>(null);

  function pedir(opcoes: OpcoesLeitura): void {
    if (resumo.tem_ajustes) setPendente(opcoes);
    else reler.mutate(opcoes);
  }

  return {
    lendo: reler.isPending,
    corrigir: (campo, valor) => {
      pedir(aplicarCorrecao(resumo.opcoes_leitura, campo, valor));
    },
    lerDeNovo: () => {
      pedir({});
    },
    aguardandoConfirmacao: pendente !== null,
    confirmar: () => {
      if (pendente !== null) reler.mutate(pendente);
      setPendente(null);
    },
    cancelar: () => {
      setPendente(null);
    },
  };
}
