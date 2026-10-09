import { useQuery, type UseQueryResult } from '@tanstack/react-query';
import { requisitar } from '../../shared/api/cliente';
import { caminhoDataset, chavesDataset } from '../../shared/api/dataset';
import { podeRepetir } from '../../shared/api/erros';
import type { Bivariada, MatrizCorrelacao, Par, Previsao } from './tipos';

/** Sob `chavesDataset.bivariada(id)`: limpeza e troca de tipo invalidam tudo da etapa 5. */
export const chavesBivariada = {
  par: (id: string, par: Par | null) =>
    [...chavesDataset.bivariada(id), 'par', par?.x ?? '', par?.y ?? ''] as const,
  matriz: (id: string) => [...chavesDataset.bivariada(id), 'matriz'] as const,
  previsao: (id: string, par: Par, valor: number | null) =>
    [...chavesDataset.bivariada(id), 'previsao', par.x, par.y, valor] as const,
};

function buscaDoPar(par: Par, extra: Record<string, string> = {}): string {
  return new URLSearchParams({ x: par.x, y: par.y, ...extra }).toString();
}

export function caminhoBivariada(id: string, par: Par): string {
  return caminhoDataset(id, `/bivariada?${buscaDoPar(par)}`);
}

export function caminhoPrevisao(id: string, par: Par, valor: number): string {
  return caminhoDataset(id, `/bivariada/prever?${buscaDoPar(par, { valor: String(valor) })}`);
}

export function caminhoCorrelacoes(id: string): string {
  return caminhoDataset(id, '/correlacoes');
}

const CODIGOS_DEFINITIVOS = new Set([
  'COLUNA_NAO_NUMERICA',
  'COLUNAS_IGUAIS',
  'POUCOS_PARES',
  'SEM_VARIACAO',
  'COLUNA_NAO_ENCONTRADA',
]);

export function podeTentarDeNovo(erro: unknown): boolean {
  return podeRepetir(erro, CODIGOS_DEFINITIVOS);
}

export function useBivariada(id: string, par: Par | null): UseQueryResult<Bivariada> {
  return useQuery({
    queryKey: chavesBivariada.par(id, par),
    queryFn: () => requisitar<Bivariada>(caminhoBivariada(id, par ?? { x: '', y: '' })),
    enabled: par !== null,
  });
}

/** A matriz não depende do par: carrega junto com a bivariada, em paralelo (§6). */
export function useMatriz(id: string): UseQueryResult<MatrizCorrelacao> {
  return useQuery({
    queryKey: chavesBivariada.matriz(id),
    queryFn: () => requisitar<MatrizCorrelacao>(caminhoCorrelacoes(id)),
  });
}

/** Só consulta depois do clique em "Prever" (valor confirmado). */
export function usePrevisaoNaApi(
  id: string,
  par: Par,
  valor: number | null,
): UseQueryResult<Previsao> {
  return useQuery({
    queryKey: chavesBivariada.previsao(id, par, valor),
    queryFn: () => requisitar<Previsao>(caminhoPrevisao(id, par, valor ?? 0)),
    enabled: valor !== null,
  });
}
