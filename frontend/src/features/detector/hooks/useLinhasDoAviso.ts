import type { UseQueryResult } from '@tanstack/react-query';
import { useLinhasDosTrechos } from '../api';
import { type Trecho, trechosDoExemplo } from '../trechos';
import type { Aviso, LinhaDados } from '../tipos';

export interface TrechoCarregado {
  trecho: Trecho;
  linhas: LinhaDados[];
}

export type EstadoLinhas =
  | { status: 'carregando' }
  | { status: 'erro'; erro: unknown; tentarDeNovo: () => void }
  | { status: 'pronto'; trechos: TrechoCarregado[] };

export interface LinhasDoAviso {
  trechos: Trecho[];
  destacadas: ReadonlySet<number>;
  estado: EstadoLinhas;
}

/** Junta as consultas dos trechos: a 1ª com erro vence; pronto só com todos carregados. */
export function estadoDosTrechos(
  trechos: readonly Trecho[],
  consultas: readonly Pick<UseQueryResult<LinhaDados[]>, 'data' | 'error' | 'refetch'>[],
): EstadoLinhas {
  const comErro = consultas.find((consulta) => consulta.error !== null);
  if (comErro !== undefined) {
    return {
      status: 'erro',
      erro: comErro.error,
      tentarDeNovo: () => {
        for (const consulta of consultas) void consulta.refetch();
      },
    };
  }
  const carregados = trechos.flatMap((trecho, i) => {
    const linhas = consultas[i]?.data;
    return linhas === undefined ? [] : [{ trecho, linhas }];
  });
  return carregados.length === trechos.length
    ? { status: 'pronto', trechos: carregados }
    : { status: 'carregando' };
}

/** Linhas do exemplo do aviso com ±3 de contexto, um pedido por trecho (tela 7b, D140). */
export function useLinhasDoAviso(datasetId: string, aviso: Aviso | null): LinhasDoAviso {
  const destacadas = aviso?.exemplo?.linhas ?? [];
  const trechos = trechosDoExemplo(destacadas);
  const consultas = useLinhasDosTrechos(datasetId, trechos);
  return {
    trechos,
    destacadas: new Set(destacadas),
    estado: estadoDosTrechos(trechos, consultas),
  };
}
