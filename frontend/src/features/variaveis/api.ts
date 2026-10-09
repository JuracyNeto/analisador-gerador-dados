import { type QueryClient, useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { requisitar } from '../../shared/api/cliente';
import { corpoJson } from '../../shared/api/corpoJson';
import {
  caminhoDataset,
  chavesDataset,
  opcoesColunas,
  type TipoColuna,
} from '../../shared/api/dataset';
import { useAvisarErro } from '../../shared/ui/useAvisarErro';
import { type AlteracaoTipo, aplicarAlteracao } from './regras';

export interface PedidoAlteracao {
  coluna: string;
  alteracao: AlteracaoTipo;
}

export const chavesVariaveis = {
  alterarTipo: (id: string) => [...chavesDataset.colunas(id), 'alterar'] as const,
};

export function useColunas(datasetId: string | null) {
  return useQuery(opcoesColunas(datasetId));
}

function alterarTipo(
  datasetId: string,
  { coluna, alteracao }: PedidoAlteracao,
): Promise<TipoColuna> {
  const caminho = caminhoDataset(datasetId, `/colunas/${encodeURIComponent(coluna)}`);
  return requisitar<TipoColuna>(caminho, corpoJson('PATCH', alteracao));
}

/** Tipo e ordem das categorias mudam análises, diagnóstico e relatório (tabela de invalidação, D68). */
function invalidarDerivados(cliente: QueryClient, id: string): Promise<unknown> {
  const chaves = [
    chavesDataset.colunas(id),
    chavesDataset.diagnostico(id),
    chavesDataset.analises(id),
    chavesDataset.bivariada(id),
    chavesDataset.relatorio(id),
  ];
  return Promise.all(chaves.map((queryKey) => cliente.invalidateQueries({ queryKey })));
}

/**
 * PATCH otimista em fila (scope): reordenar várias vezes seguidas manda os pedidos em ordem
 * e só a última resposta dispara a invalidação.
 */
export function useAlterarTipo(datasetId: string) {
  const cliente = useQueryClient();
  const avisarErro = useAvisarErro();
  const chave = chavesDataset.colunas(datasetId);
  const chaveMutacao = chavesVariaveis.alterarTipo(datasetId);
  return useMutation({
    mutationKey: chaveMutacao,
    scope: { id: chaveMutacao.join('/') },
    mutationFn: (pedido: PedidoAlteracao) => alterarTipo(datasetId, pedido),
    onMutate: async ({ coluna, alteracao }) => {
      await cliente.cancelQueries({ queryKey: chave });
      const anteriores = cliente.getQueryData<TipoColuna[]>(chave);
      cliente.setQueryData<TipoColuna[]>(chave, (atuais) =>
        aplicarAlteracao(atuais, coluna, alteracao),
      );
      return { anteriores };
    },
    onError: (erro, _pedido, contexto) => {
      cliente.setQueryData(chave, contexto?.anteriores);
      avisarErro(erro);
    },
    onSettled: () =>
      cliente.isMutating({ mutationKey: chaveMutacao }) > 1
        ? undefined
        : invalidarDerivados(cliente, datasetId),
  });
}
