import { useMutation, useQuery, type UseQueryResult } from '@tanstack/react-query';
import { requisitar, requisitarBlob } from '../../shared/api/cliente';
import { filtrarAnalisaveis } from '../../shared/api/colunas';
import { corpoJson } from '../../shared/api/corpoJson';
import { chavesDataset, opcoesColunas, type TipoColuna } from '../../shared/api/dataset';
import { baixarArquivo } from '../../shared/lib/baixarArquivo';
import type {
  Adotado,
  Gerado,
  PedidoBivariado,
  PedidoUnivariado,
  ResumoOrigem,
  ResumoOrigemPar,
} from './tipos';

/** Sob `chavesDataset.todas(id)`: anexar, limpar ou trocar o tipo refazem as medidas da origem. */
export const chavesGerador = {
  origem: (id: string, coluna: string) =>
    [...chavesDataset.todas(id), 'gerador', 'origem', coluna] as const,
  origemPar: (id: string, x: string, y: string) =>
    [...chavesDataset.todas(id), 'gerador', 'origem-par', x, y] as const,
};

export function caminhoOrigem(id: string, coluna: string): string {
  return `/gerador/origem?${new URLSearchParams({ dataset_id: id, coluna }).toString()}`;
}

export function caminhoOrigemPar(id: string, x: string, y: string): string {
  return `/gerador/origem-par?${new URLSearchParams({ dataset_id: id, x, y }).toString()}`;
}

export function caminhoCsv(geradoId: string): string {
  return `/gerador/${encodeURIComponent(geradoId)}/csv`;
}

export function nomeCsv(gerado: Gerado): string {
  return `gerado-${gerado.colunas.join('-')}.csv`;
}

/** Colunas que podem servir de origem: as analisáveis (sem identificador e data). */
export function useColunasGeraveis(id: string | null): UseQueryResult<TipoColuna[]> {
  return useQuery({ ...opcoesColunas(id), select: filtrarAnalisaveis });
}

export function useOrigem(id: string | null, coluna: string | null): UseQueryResult<ResumoOrigem> {
  return useQuery({
    queryKey: chavesGerador.origem(id ?? '', coluna ?? ''),
    queryFn: () => requisitar<ResumoOrigem>(caminhoOrigem(id ?? '', coluna ?? '')),
    enabled: id !== null && coluna !== null,
  });
}

export function useOrigemPar(
  id: string | null,
  x: string | null,
  y: string | null,
): UseQueryResult<ResumoOrigemPar> {
  return useQuery({
    queryKey: chavesGerador.origemPar(id ?? '', x ?? '', y ?? ''),
    queryFn: () => requisitar<ResumoOrigemPar>(caminhoOrigemPar(id ?? '', x ?? '', y ?? '')),
    enabled: id !== null && x !== null && y !== null && x !== y,
  });
}

export function useGerarUnivariado() {
  return useMutation({
    mutationFn: (pedido: PedidoUnivariado) =>
      requisitar<Gerado>('/gerador/univariado', corpoJson('POST', pedido)),
  });
}

export function useGerarBivariado() {
  return useMutation({
    mutationFn: (pedido: PedidoBivariado) =>
      requisitar<Gerado>('/gerador/bivariado', corpoJson('POST', pedido)),
  });
}

interface PedidoAdotar {
  geradoId: string;
  modo: 'novo' | 'anexar';
  datasetId?: string;
}

export function useAdotar() {
  return useMutation({
    mutationFn: ({ geradoId, modo, datasetId }: PedidoAdotar) =>
      requisitar<Adotado>(
        `/gerador/${encodeURIComponent(geradoId)}/adotar`,
        corpoJson('POST', { modo, dataset_id: datasetId ?? null }),
      ),
  });
}

export function useBaixarCsv() {
  return useMutation({
    mutationFn: async (gerado: Gerado) => {
      baixarArquivo(await requisitarBlob(caminhoCsv(gerado.gerado_id)), nomeCsv(gerado));
    },
  });
}
