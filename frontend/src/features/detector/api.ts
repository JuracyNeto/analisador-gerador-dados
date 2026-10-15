import { useQueries, useQuery, type UseQueryResult } from '@tanstack/react-query';
import { requisitar } from '../../shared/api/cliente';
import { caminhoDataset, chavesDataset } from '../../shared/api/dataset';
import type { Trecho } from './trechos';
import type { LinhaDados, ResultadoDetector } from './tipos';

/** Sob `chavesDataset.detector(id)`: limpeza, troca de tipo e anexar invalidam o resultado. */
export const chavesDetector = {
  resultado: (id: string) => [...chavesDataset.detector(id), 'resultado'] as const,
  linhas: (id: string, trecho: Trecho) =>
    [...chavesDataset.detector(id), 'linhas', trecho.de, trecho.ate] as const,
};

export function caminhoDetector(id: string): string {
  return caminhoDataset(id, '/detector');
}

export function caminhoLinhas(id: string, { de, ate }: Trecho): string {
  return caminhoDataset(id, `/linhas?de=${String(de)}&ate=${String(ate)}`);
}

/** As 11 regras de uma vez; "Analisar de novo" é o `refetch`. */
export function useDetector(id: string): UseQueryResult<ResultadoDetector> {
  return useQuery({
    queryKey: chavesDetector.resultado(id),
    queryFn: () => requisitar<ResultadoDetector>(caminhoDetector(id)),
  });
}

/** Um pedido por trecho, em paralelo (§6). */
export function useLinhasDosTrechos(
  id: string,
  trechos: readonly Trecho[],
): UseQueryResult<LinhaDados[]>[] {
  return useQueries({
    queries: trechos.map((trecho) => ({
      queryKey: chavesDetector.linhas(id, trecho),
      queryFn: () => requisitar<LinhaDados[]>(caminhoLinhas(id, trecho)),
    })),
  });
}
