import { ErroApi } from '../../shared/api/cliente';
import { type ConsultaSimples, type EstadoDeErro, estadoDeErro } from '../../shared/api/consulta';
import { podeTentarDeNovo } from './api';
import type { Analise, TipoColuna } from './tipos';

export type EstadoAnalise =
  | { status: 'carregando-colunas' }
  | { status: 'sem-colunas' }
  | { status: 'calculando'; coluna: string }
  | EstadoDeErro
  | { status: 'pronta'; analise: Analise; atualizando: boolean };

export function estadoDaAnalise(
  colunas: ConsultaSimples<TipoColuna[]>,
  analise: ConsultaSimples<Analise>,
  coluna: string | null,
): EstadoAnalise {
  if (colunas.status === 'error') return estadoDeErro(colunas, podeTentarDeNovo);
  if (colunas.status === 'pending') return { status: 'carregando-colunas' };
  if (coluna === null) return { status: 'sem-colunas' };
  if (analise.status === 'error') return estadoDeErro(analise, podeTentarDeNovo);
  if (analise.data === undefined) return { status: 'calculando', coluna };
  return { status: 'pronta', analise: analise.data, atualizando: analise.isPlaceholderData };
}

const ERRO_TENTATIVAS = 'TENTATIVAS_INVALIDAS';

/** `?tentativas=` inválido na URL: "Tentar de novo" volta para o padrão (o maior valor, D96). */
export function comPadraoDeTentativas(
  estado: EstadoAnalise,
  usarPadrao: () => void,
): EstadoAnalise {
  const erroDeTentativas =
    estado.status === 'erro' &&
    estado.erro instanceof ErroApi &&
    estado.erro.codigo === ERRO_TENTATIVAS;
  return erroDeTentativas ? { ...estado, tentarDeNovo: usarPadrao } : estado;
}
