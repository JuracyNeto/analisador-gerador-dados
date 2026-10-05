import { useCallback, useState } from 'react';
import { useConsultaMidia } from '../../shared/lib/useConsultaMidia';
import { useTeclaEsc } from '../../shared/lib/useTeclaEsc';

const CONSULTA_TELA_LARGA = '(min-width: 1280px)';

export interface EstadoBarra {
  recolhida: boolean;
  sobreposta: boolean;
  alternar: () => void;
  recolher: () => void;
}

/** ≥ 1280 px começa expandida; abaixo, recolhida. Expandir em tela média abre por cima do conteúdo. */
export function useBarraRecolhivel(): EstadoBarra {
  const telaLarga = useConsultaMidia(CONSULTA_TELA_LARGA);
  // null = o usuário ainda não escolheu; segue a largura da tela.
  const [escolha, setEscolha] = useState<boolean | null>(null);
  const expandida = escolha ?? telaLarga;
  const sobreposta = expandida && !telaLarga;

  const alternar = useCallback(() => {
    setEscolha(!expandida);
  }, [expandida]);
  const recolher = useCallback(() => {
    setEscolha(false);
  }, []);
  useTeclaEsc(sobreposta, recolher);

  return { recolhida: !expandida, sobreposta, alternar, recolher };
}
