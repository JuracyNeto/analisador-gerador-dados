import { useCallback, useState } from 'react';
import type { EscolhasLimpeza, TipoAcao } from '../tipos';

/** Escolha por linha de seção; ausente = "manter" (Dnn-manter). */
export function useEscolhasLimpeza() {
  const [valores, setValores] = useState<EscolhasLimpeza>({});
  const escolher = useCallback((chave: string, acao: TipoAcao) => {
    setValores((atuais) => ({ ...atuais, [chave]: acao }));
  }, []);
  const limpar = useCallback(() => {
    setValores({});
  }, []);
  return { valores, escolher, limpar };
}
