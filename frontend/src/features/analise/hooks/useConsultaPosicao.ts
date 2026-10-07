import { useState } from 'react';
import { lerNumeroPtBr } from '../../../shared/lib/formatar';
import { useValorAtrasado } from '../../../shared/lib/useValorAtrasado';
import { usePosicao } from '../api';
import type { TipoSeparatriz } from '../tipos';

export const ATRASO_DIGITACAO_MS = 300;

/** Estado do painel "Onde está meu valor?": texto digitado, tipo de separatriz e a consulta com debounce. */
export function useConsultaPosicao(datasetId: string, coluna: string, habilitada: boolean) {
  const [texto, setTexto] = useState('');
  const [tipo, setTipo] = useState<TipoSeparatriz>('quartil');
  const textoAtrasado = useValorAtrasado(texto, ATRASO_DIGITACAO_MS);
  const valor = habilitada ? lerNumeroPtBr(textoAtrasado) : null;
  const posicao = usePosicao({ datasetId, coluna, valor, tipo });

  return {
    texto,
    setTexto,
    tipo,
    setTipo,
    invalido: texto.trim() !== '' && lerNumeroPtBr(texto) === null,
    posicao,
    // Campo apagado: some o resultado anterior (o placeholderData o manteria).
    posicaoAtual: valor === null ? undefined : posicao.data,
  };
}

export type ConsultaPosicaoNaTela = ReturnType<typeof useConsultaPosicao>;
