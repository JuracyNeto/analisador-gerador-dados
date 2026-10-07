import { useCallback } from 'react';
import { ehDatasetNaoEncontrado, textoDoErro } from '../api/erros';
import { useToast } from './useToast';

/** Mostra o erro num toast; "sessão expirada" fica com o `useSessaoExpirada` (D61) para não avisar duas vezes. */
export function useAvisarErro(): (erro: unknown) => void {
  const toast = useToast();
  return useCallback(
    (erro: unknown) => {
      if (ehDatasetNaoEncontrado(erro)) return;
      const { mensagem, sugestao } = textoDoErro(erro);
      toast.mostrar({ tipo: 'erro', titulo: mensagem, descricao: sugestao });
    },
    [toast],
  );
}
