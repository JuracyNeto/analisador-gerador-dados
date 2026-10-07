import { keepPreviousData, useQuery, type UseQueryResult } from '@tanstack/react-query';
import { ErroApi, requisitar } from '../../shared/api/cliente';
import { caminhoDataset, chavesDataset } from '../../shared/api/dataset';
import type { Analise, Posicao, TipoSeparatriz } from './tipos';

export interface ConsultaPosicao {
  datasetId: string;
  coluna: string;
  valor: number | null;
  tipo: TipoSeparatriz;
}

/**
 * Chaves sob `chavesDataset.analises(id)` (convenção do M1.6): limpeza e troca de tipo
 * invalidam análise e posição de uma vez (tabela de invalidação do M1.6).
 */
export const chavesAnalise = {
  analise: (datasetId: string, coluna: string, classes: number | null) =>
    [...chavesDataset.analises(datasetId), coluna, classes] as const,
  posicao: (datasetId: string, coluna: string, valor: number | null, tipo: TipoSeparatriz) =>
    [...chavesDataset.analises(datasetId), coluna, 'posicao', valor, tipo] as const,
};

function caminhoColuna(datasetId: string, coluna: string): string {
  return caminhoDataset(datasetId, `/colunas/${encodeURIComponent(coluna)}`);
}

export function caminhoAnalise(datasetId: string, coluna: string, classes: number | null): string {
  const base = `${caminhoColuna(datasetId, coluna)}/analise`;
  return classes === null
    ? base
    : `${base}?${new URLSearchParams({ classes: String(classes) }).toString()}`;
}

export function caminhoPosicao(consulta: ConsultaPosicao & { valor: number }): string {
  const parametros = new URLSearchParams({ valor: String(consulta.valor), tipo: consulta.tipo });
  return `${caminhoColuna(consulta.datasetId, consulta.coluna)}/posicao?${parametros.toString()}`;
}

const CODIGOS_DEFINITIVOS = new Set(['COLUNA_IGNORADA', 'COLUNA_VAZIA', 'COLUNA_NAO_ENCONTRADA']);

/** Erros que não mudam ao repetir a requisição não ganham botão "Tentar de novo". */
export function podeTentarDeNovo(erro: unknown): boolean {
  return !(erro instanceof ErroApi && CODIGOS_DEFINITIVOS.has(erro.codigo));
}

export function useAnalise(
  datasetId: string,
  coluna: string | null,
  classes: number | null,
): UseQueryResult<Analise> {
  return useQuery({
    queryKey: chavesAnalise.analise(datasetId, coluna ?? '', classes),
    queryFn: () => requisitar<Analise>(caminhoAnalise(datasetId, coluna ?? '', classes)),
    enabled: coluna !== null,
    // Mantém a tabela na tela ao mudar o nº de classes; ao trocar de coluna mostra o carregando (4h).
    placeholderData: (anterior) =>
      coluna !== null && anterior?.coluna === coluna ? anterior : undefined,
  });
}

export function usePosicao(consulta: ConsultaPosicao): UseQueryResult<Posicao> {
  const { datasetId, coluna, valor, tipo } = consulta;
  return useQuery({
    queryKey: chavesAnalise.posicao(datasetId, coluna, valor, tipo),
    queryFn: () =>
      requisitar<Posicao>(caminhoPosicao({ datasetId, coluna, tipo, valor: valor ?? 0 })),
    enabled: valor !== null,
    placeholderData: keepPreviousData,
  });
}
