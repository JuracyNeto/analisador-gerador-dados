/** Peças comuns dos estados de tela montados a partir de consultas (Análise e Bivariada). */

/** O pedaço de UseQueryResult que as telas usam (UseQueryResult é compatível por estrutura). */
export interface ConsultaSimples<T> {
  status: 'pending' | 'error' | 'success';
  data: T | undefined;
  error: unknown;
  isPlaceholderData: boolean;
  refetch: () => unknown;
}

export interface EstadoDeErro {
  status: 'erro';
  erro: unknown;
  tentarDeNovo: (() => void) | null;
}

/** Erro da consulta, com "Tentar de novo" só quando repetir pode dar certo. */
export function estadoDeErro(
  consulta: ConsultaSimples<unknown>,
  podeTentarDeNovo: (erro: unknown) => boolean,
): EstadoDeErro {
  const tentarDeNovo = () => {
    void consulta.refetch();
  };
  return {
    status: 'erro',
    erro: consulta.error,
    tentarDeNovo: podeTentarDeNovo(consulta.error) ? tentarDeNovo : null,
  };
}
