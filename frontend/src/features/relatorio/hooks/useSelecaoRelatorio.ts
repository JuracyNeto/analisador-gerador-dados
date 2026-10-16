import { useState } from 'react';
import { SECOES_RELATORIO, type SecaoRelatorio } from '../api';
import { alternar, secaoDisponivel } from '../selecao';

/**
 * Guarda o que foi desmarcado: tudo começa marcado, inclusive colunas que chegam depois e a
 * seção Gerador quando a geração aparece na sessão.
 */
export function useSelecaoRelatorio(colunasDisponiveis: readonly string[], gerado: string | null) {
  const [secoesFora, setSecoesFora] = useState<ReadonlySet<SecaoRelatorio>>(() => new Set());
  const [colunasFora, setColunasFora] = useState<ReadonlySet<string>>(() => new Set());

  return {
    secoes: SECOES_RELATORIO.filter(
      (secao) => !secoesFora.has(secao) && secaoDisponivel(secao, gerado !== null),
    ),
    colunas: colunasDisponiveis.filter((coluna) => !colunasFora.has(coluna)),
    gerado,
    alternarSecao: (secao: SecaoRelatorio) => {
      setSecoesFora((atual) => alternar(atual, secao));
    },
    alternarColuna: (coluna: string) => {
      setColunasFora((atual) => alternar(atual, coluna));
    },
  };
}

export type SelecaoNaTela = ReturnType<typeof useSelecaoRelatorio>;
