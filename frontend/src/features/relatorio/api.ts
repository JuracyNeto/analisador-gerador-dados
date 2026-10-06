import { useMutation } from '@tanstack/react-query';
import { requisitarBlob } from '../../shared/api/cliente';
import { caminhoDataset } from '../../shared/api/dataset';
import type { components } from '../../shared/api/schema';
import { baixarArquivo } from '../../shared/lib/baixarArquivo';

export type SecaoRelatorio = components['schemas']['Secao'];

/** Seções aceitas no M1 (D57), na ordem do relatório. */
export const SECOES_RELATORIO = [
  'leitura',
  'tipos',
  'limpeza',
  'analises',
] as const satisfies readonly SecaoRelatorio[];

export interface SelecaoRelatorio {
  secoes: readonly SecaoRelatorio[];
  colunas: readonly string[];
}

export interface PedidoRelatorio extends SelecaoRelatorio {
  offline: boolean;
}

const EXTENSAO = /\.[^.]+$/u;

export function caminhoRelatorio(datasetId: string, pedido: PedidoRelatorio): string {
  const parametros = new URLSearchParams();
  for (const secao of pedido.secoes) parametros.append('secoes', secao);
  for (const coluna of pedido.colunas) parametros.append('colunas', coluna);
  parametros.set('offline', String(pedido.offline));
  return caminhoDataset(datasetId, `/relatorio?${parametros.toString()}`);
}

export function nomeArquivoRelatorio(nomeArquivo: string): string {
  return `relatorio-${nomeArquivo.replace(EXTENSAO, '')}.html`;
}

interface PedidoDownload {
  caminho: string;
  nomeArquivo: string;
}

export function useBaixarRelatorio() {
  return useMutation({
    mutationFn: async ({ caminho, nomeArquivo }: PedidoDownload) => {
      baixarArquivo(await requisitarBlob(caminho), nomeArquivo);
    },
  });
}
