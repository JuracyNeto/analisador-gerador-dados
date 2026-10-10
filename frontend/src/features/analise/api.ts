import { keepPreviousData, useQuery, type UseQueryResult } from '@tanstack/react-query';
import { requisitar } from '../../shared/api/cliente';
import { caminhoDataset, chavesDataset } from '../../shared/api/dataset';
import { podeRepetir } from '../../shared/api/erros';
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
/** Pedidos da análise que mudam o resultado (URL da tela 4, D78). */
export interface OpcoesAnalise {
  classes: number | null;
  tentativas: number | null;
}

export const chavesAnalise = {
  analise: (datasetId: string, coluna: string, opcoes: OpcoesAnalise) =>
    [...chavesDataset.analises(datasetId), coluna, opcoes.classes, opcoes.tentativas] as const,
  posicao: (datasetId: string, coluna: string, valor: number | null, tipo: TipoSeparatriz) =>
    [...chavesDataset.analises(datasetId), coluna, 'posicao', valor, tipo] as const,
};

function caminhoColuna(datasetId: string, coluna: string): string {
  return caminhoDataset(datasetId, `/colunas/${encodeURIComponent(coluna)}`);
}

export function caminhoAnalise(datasetId: string, coluna: string, opcoes: OpcoesAnalise): string {
  const parametros = new URLSearchParams();
  if (opcoes.classes !== null) parametros.set('classes', String(opcoes.classes));
  if (opcoes.tentativas !== null) parametros.set('tentativas', String(opcoes.tentativas));
  const busca = parametros.toString();
  const base = `${caminhoColuna(datasetId, coluna)}/analise`;
  return busca === '' ? base : `${base}?${busca}`;
}

export function caminhoPosicao(consulta: ConsultaPosicao & { valor: number }): string {
  const parametros = new URLSearchParams({ valor: String(consulta.valor), tipo: consulta.tipo });
  return `${caminhoColuna(consulta.datasetId, consulta.coluna)}/posicao?${parametros.toString()}`;
}

const CODIGOS_DEFINITIVOS = new Set(['COLUNA_IGNORADA', 'COLUNA_VAZIA', 'COLUNA_NAO_ENCONTRADA']);

/** Erros que não mudam ao repetir a requisição não ganham botão "Tentar de novo". */
export function podeTentarDeNovo(erro: unknown): boolean {
  return podeRepetir(erro, CODIGOS_DEFINITIVOS);
}

export function useAnalise(
  datasetId: string,
  coluna: string | null,
  opcoes: OpcoesAnalise,
): UseQueryResult<Analise> {
  return useQuery({
    queryKey: chavesAnalise.analise(datasetId, coluna ?? '', opcoes),
    queryFn: () => requisitar<Analise>(caminhoAnalise(datasetId, coluna ?? '', opcoes)),
    enabled: coluna !== null,
    // Mantém a tela ao mudar classes ou tentativas; ao trocar de coluna mostra o carregando (4h).
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
