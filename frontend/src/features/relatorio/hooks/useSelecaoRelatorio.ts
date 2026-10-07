import { useState } from 'react';
import { SECOES_RELATORIO, type SecaoRelatorio } from '../api';
import { alternar } from '../selecao';

/** Guarda o que foi desmarcado: tudo começa marcado, inclusive colunas que chegam depois. */
export function useSelecaoRelatorio(colunasDisponiveis: readonly string[]) {
  const [secoesFora, setSecoesFora] = useState<ReadonlySet<SecaoRelatorio>>(() => new Set());
  const [colunasFora, setColunasFora] = useState<ReadonlySet<string>>(() => new Set());

  return {
    secoes: SECOES_RELATORIO.filter((secao) => !secoesFora.has(secao)),
    colunas: colunasDisponiveis.filter((coluna) => !colunasFora.has(coluna)),
    alternarSecao: (secao: SecaoRelatorio) => {
      setSecoesFora((atual) => alternar(atual, secao));
    },
    alternarColuna: (coluna: string) => {
      setColunasFora((atual) => alternar(atual, coluna));
    },
  };
}

export type SelecaoNaTela = ReturnType<typeof useSelecaoRelatorio>;
