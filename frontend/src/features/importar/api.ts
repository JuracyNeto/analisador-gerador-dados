import { useMutation, useQueryClient } from '@tanstack/react-query';
import { requisitar } from '../../shared/api/cliente';
import { chavesDataset } from '../../shared/api/dataset';
import type { components } from '../../shared/api/schema';
import { useSessao } from '../../shared/sessao/useSessao';
import { useToast } from '../../shared/ui/useToast';
import { montarFormulario, type OpcoesLeitura } from './opcoesLeitura';
import { TEXTOS_IMPORTAR as T } from './textos';

export type DatasetCriado = components['schemas']['DatasetCriado'];

export interface PedidoImportacao {
  arquivo: File;
  opcoes: OpcoesLeitura;
}

/** Leituras em fila: trocar dois Selects rápido não deixa a resposta antiga vencer a nova. */
const ESCOPO_IMPORTACAO = { id: 'importacao' };

function enviarArquivo({ arquivo, opcoes }: PedidoImportacao): Promise<DatasetCriado> {
  return requisitar<DatasetCriado>('/datasets', {
    method: 'POST',
    body: montarFormulario(arquivo, opcoes),
  });
}

function abrirExemplo(): Promise<DatasetCriado> {
  return requisitar<DatasetCriado>('/datasets/exemplo', { method: 'POST' });
}

/** Sucesso de qualquer leitura: sessão nova, etapa 1 visitada, colunas no cache e toast. */
function useConcluirImportacao(): (criado: DatasetCriado) => void {
  const cliente = useQueryClient();
  const sessao = useSessao();
  const toast = useToast();
  return (criado) => {
    cliente.setQueryData(chavesDataset.colunas(criado.dataset_id), criado.colunas);
    sessao.definirDataset({ id: criado.dataset_id, nomeArquivo: criado.nome_arquivo });
    sessao.marcarVisitada(1);
    toast.mostrar({
      tipo: 'sucesso',
      titulo: T.toast.titulo(criado.metadados.n_linhas, criado.metadados.n_colunas),
      descricao: T.toast.descricao,
    });
  };
}

export function useImportarArquivo() {
  const concluir = useConcluirImportacao();
  return useMutation({ mutationFn: enviarArquivo, onSuccess: concluir, scope: ESCOPO_IMPORTACAO });
}

export function useAbrirExemplo() {
  const concluir = useConcluirImportacao();
  return useMutation({ mutationFn: abrirExemplo, onSuccess: concluir, scope: ESCOPO_IMPORTACAO });
}
