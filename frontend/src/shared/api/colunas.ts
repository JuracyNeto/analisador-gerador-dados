/** Colunas analisáveis do dataset, compartilhadas por Análise e Relatório. */
import { useQuery, type UseQueryResult } from '@tanstack/react-query';
import { ehAuxiliar, ehNumerico } from '../ui/tiposVariavel';
import { opcoesColunas, type TipoColuna } from './dataset';

/** Identificadores e datas ficam fora das análises (D17, D90). */
export function filtrarAnalisaveis(colunas: readonly TipoColuna[]): TipoColuna[] {
  return colunas.filter((coluna) => !ehAuxiliar(coluna.tipo));
}

export function useColunasAnalisaveis(datasetId: string): UseQueryResult<TipoColuna[]> {
  return useQuery({ ...opcoesColunas(datasetId), select: filtrarAnalisaveis });
}

/** Bivariada: só discretas e contínuas (spec 10). */
export function filtrarNumericas(colunas: readonly TipoColuna[]): TipoColuna[] {
  return colunas.filter((coluna) => ehNumerico(coluna.tipo));
}

export function useColunasNumericas(datasetId: string): UseQueryResult<TipoColuna[]> {
  return useQuery({ ...opcoesColunas(datasetId), select: filtrarNumericas });
}
