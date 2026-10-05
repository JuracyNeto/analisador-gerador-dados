/** Consultas e chaves de um dataset compartilhadas entre features (D68). */
import { queryOptions, skipToken } from '@tanstack/react-query';
import { requisitar } from './cliente';
import type { components } from './schema';

export type PaginaDataset = components['schemas']['PaginaDataset'];
export type ResumoDataset = components['schemas']['ResumoDataset'];
export type TipoColuna = components['schemas']['TipoColuna'];
export type LinhaDados = components['schemas']['LinhaDados'];

export const TAMANHO_PREVIA = 20;

export const chavesDataset = {
  todas: (id: string) => ['datasets', id] as const,
  primeiraPagina: (id: string) => ['datasets', id, 'primeira-pagina'] as const,
  colunas: (id: string) => ['datasets', id, 'colunas'] as const,
  diagnostico: (id: string) => ['datasets', id, 'diagnostico'] as const,
  analises: (id: string) => ['datasets', id, 'analise'] as const,
  relatorio: (id: string) => ['datasets', id, 'relatorio'] as const,
};

export function caminhoDataset(id: string, sufixo = ''): string {
  return `/datasets/${encodeURIComponent(id)}${sufixo}`;
}

/** Página 1 (20 linhas) + resumo: cabeçalho, prévia da tela 1 e log da limpeza usam a mesma chave. */
export function opcoesPrimeiraPagina(id: string | null) {
  return queryOptions({
    queryKey: chavesDataset.primeiraPagina(id ?? ''),
    queryFn:
      id === null
        ? skipToken
        : () =>
            requisitar<PaginaDataset>(
              caminhoDataset(id, `?pagina=1&tamanho=${String(TAMANHO_PREVIA)}`),
            ),
  });
}

export function opcoesColunas(id: string | null) {
  return queryOptions({
    queryKey: chavesDataset.colunas(id ?? ''),
    queryFn:
      id === null ? skipToken : () => requisitar<TipoColuna[]>(caminhoDataset(id, '/colunas')),
  });
}
