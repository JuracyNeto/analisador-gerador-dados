import { keepPreviousData, useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { requisitar } from '../../shared/api/cliente';
import { corpoJson } from '../../shared/api/corpoJson';
import { caminhoDataset, chavesDataset } from '../../shared/api/dataset';
import { useAvisarErro } from '../../shared/ui/useAvisarErro';
import type { Diagnostico, PedidoLimpeza, ResultadoLimpeza } from './tipos';

/** Dnn-limites: o diagnóstico com limites novos espera 600 ms sem digitação. */
export const ATRASO_LIMITES_MS = 600;

export const chavesLimpeza = {
  diagnostico: (id: string, limitesJson: string) =>
    [...chavesDataset.diagnostico(id), limitesJson] as const,
};

export function caminhoDiagnostico(id: string, limitesJson: string): string {
  const consulta = limitesJson === '' ? '' : `?limites=${encodeURIComponent(limitesJson)}`;
  return caminhoDataset(id, `/diagnostico${consulta}`);
}

export function useDiagnostico(datasetId: string, limitesJson: string) {
  return useQuery({
    queryKey: chavesLimpeza.diagnostico(datasetId, limitesJson),
    queryFn: () => requisitar<Diagnostico>(caminhoDiagnostico(datasetId, limitesJson)),
    placeholderData: keepPreviousData,
  });
}

/** Limpeza muda linhas, tipos, log, diagnóstico e análises: invalida o prefixo do dataset (Dnn-chaves). */
function useAoConcluirLimpeza(datasetId: string) {
  const cliente = useQueryClient();
  const avisarErro = useAvisarErro();
  return {
    onSuccess: () => cliente.invalidateQueries({ queryKey: chavesDataset.todas(datasetId) }),
    onError: avisarErro,
  };
}

export function useAplicarLimpeza(datasetId: string) {
  const callbacks = useAoConcluirLimpeza(datasetId);
  return useMutation({
    mutationFn: (pedido: PedidoLimpeza) =>
      requisitar<ResultadoLimpeza>(
        caminhoDataset(datasetId, '/limpeza'),
        corpoJson('POST', pedido),
      ),
    ...callbacks,
  });
}

export function useDesfazerLimpeza(datasetId: string) {
  const callbacks = useAoConcluirLimpeza(datasetId);
  return useMutation({
    mutationFn: () =>
      requisitar<ResultadoLimpeza>(caminhoDataset(datasetId, '/limpeza/desfazer'), {
        method: 'POST',
      }),
    ...callbacks,
  });
}
