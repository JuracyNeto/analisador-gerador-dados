import { useState } from 'react';
import { urlDaApi } from '../../../shared/api/cliente';
import { useValorAtrasado } from '../../../shared/lib/useValorAtrasado';
import { caminhoRelatorio, type SelecaoRelatorio } from '../api';

export const ATRASO_PREVIA_MS = 400;

interface PreviaCarregada {
  src: string;
  iframe: HTMLIFrameElement;
}

export function usePreviaRelatorio(datasetId: string, selecao: SelecaoRelatorio | null) {
  // Prévia sempre offline: gráficos sem internet e impressão igual ao arquivo (D84).
  const caminho =
    selecao === null ? null : caminhoRelatorio(datasetId, { ...selecao, offline: true });
  const caminhoAtrasado = useValorAtrasado(caminho, ATRASO_PREVIA_MS);
  const src = caminho === null || caminhoAtrasado === null ? null : urlDaApi(caminhoAtrasado);
  // O iframe chega pelo onLoad: só imprime a prévia do src atual, já carregada.
  const [carregada, setCarregada] = useState<PreviaCarregada | null>(null);
  const atual = src !== null && carregada?.src === src ? carregada : null;

  return {
    src,
    carregando: src !== null && atual === null,
    pronta: atual !== null,
    aoCarregar: (iframe: HTMLIFrameElement) => {
      if (src !== null) setCarregada({ src, iframe });
    },
    imprimir: () => {
      atual?.iframe.contentWindow?.print();
    },
  };
}
