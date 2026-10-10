import { useState } from 'react';
import type { UseQueryResult } from '@tanstack/react-query';
import { lerNumeroPtBr } from '../../../shared/lib/formatar';
import { usePrevisaoNaApi } from '../api';
import { TEXTOS_BIVARIADA } from '../textos';
import type { Par, Previsao } from '../tipos';

export interface PrevisaoNaTela {
  texto: string;
  mudarTexto: (texto: string) => void;
  erro: string | undefined;
  prever: () => void;
  consulta: UseQueryResult<Previsao>;
}

/** O texto digitado só vira consulta ao clicar em "Prever" (D105); número inválido não consulta. */
export function usePrevisao(datasetId: string, par: Par): PrevisaoNaTela {
  const [texto, setTexto] = useState('');
  const [valor, setValor] = useState<number | null>(null);
  const [erro, setErro] = useState<string | undefined>(undefined);
  const consulta = usePrevisaoNaApi(datasetId, par, valor);

  return {
    texto,
    mudarTexto: setTexto,
    erro,
    consulta,
    prever: () => {
      const numero = lerNumeroPtBr(texto);
      setErro(numero === null ? TEXTOS_BIVARIADA.previsao.erroValor : undefined);
      if (numero !== null) setValor(numero);
    },
  };
}
