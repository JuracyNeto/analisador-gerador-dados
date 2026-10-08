/** Colunas analisáveis do dataset, compartilhadas por Análise e Relatório. */
import { useQuery, type UseQueryResult } from '@tanstack/react-query';
import { ehAuxiliar } from '../ui/tiposVariavel';
import { opcoesColunas, type TipoColuna } from './dataset';

/** Identificadores e datas ficam fora das análises (D17, D90). */
export function filtrarAnalisaveis(colunas: readonly TipoColuna[]): TipoColuna[] {
  return colunas.filter((coluna) => !ehAuxiliar(coluna.tipo));
}

export function useColunasAnalisaveis(datasetId: string): UseQueryResult<TipoColuna[]> {
  return useQuery({ ...opcoesColunas(datasetId), select: filtrarAnalisaveis });
}
