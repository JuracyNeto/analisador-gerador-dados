import { type ConsultaSimples, type EstadoDeErro, estadoDeErro } from '../../shared/api/consulta';
import { podeTentarDeNovo } from './api';
import type { Bivariada, Par, TipoColuna } from './tipos';

export type EstadoBivariada =
  | { status: 'carregando-colunas' }
  | { status: 'poucas-colunas' }
  | { status: 'calculando'; par: Par }
  | EstadoDeErro
  | { status: 'pronta'; bivariada: Bivariada };

/** Colunas numéricas → par → análise do par (o par vem da URL ou das duas primeiras numéricas). */
export function estadoDaBivariada(
  colunas: ConsultaSimples<TipoColuna[]>,
  consulta: ConsultaSimples<Bivariada>,
  par: Par | null,
): EstadoBivariada {
  if (colunas.status === 'error') return estadoDeErro(colunas, podeTentarDeNovo);
  if (colunas.status === 'pending') return { status: 'carregando-colunas' };
  if (par === null) return { status: 'poucas-colunas' };
  if (consulta.status === 'error') return estadoDeErro(consulta, podeTentarDeNovo);
  if (consulta.data === undefined) return { status: 'calculando', par };
  return { status: 'pronta', bivariada: consulta.data };
}
