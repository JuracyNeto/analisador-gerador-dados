import { useState } from 'react';
import { urlDaApi } from '../../../shared/api/cliente';
import { useValorAtrasado } from '../../../shared/lib/useValorAtrasado';
import { caminhoRelatorio, type SelecaoRelatorio } from '../api';

// Com arquivos grandes cada prévia leva segundos: espera o último clique de uma sequência.
export const ATRASO_PREVIA_MS = 800;

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

  const carregando = src !== null && atual === null;
  return {
    /** As props do `PreviaRelatorio`. */
    pagina: {
      src,
      carregando,
      /** Já há uma prévia na tela: ela fica visível (esmaecida) enquanto a nova chega. */
      atualizando: carregando && carregada !== null,
      aoCarregar: (iframe: HTMLIFrameElement) => {
        if (src !== null) setCarregada({ src, iframe });
      },
    },
    pronta: atual !== null,
    imprimir: () => {
      atual?.iframe.contentWindow?.print();
    },
  };
}
