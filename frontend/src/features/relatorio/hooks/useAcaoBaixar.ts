import { useAvisarErro } from '../../../shared/ui/useAvisarErro';
import { useToast } from '../../../shared/ui/useToast';
import {
  caminhoRelatorio,
  nomeArquivoRelatorio,
  type SelecaoRelatorio,
  useBaixarRelatorio,
} from '../api';
import { TEXTOS_RELATORIO } from '../textos';

export function useAcaoBaixar(datasetId: string, nomeArquivo: string) {
  const { mostrar } = useToast();
  const avisarErro = useAvisarErro();
  const baixar = useBaixarRelatorio();

  return {
    baixando: baixar.isPending,
    baixar: (selecao: SelecaoRelatorio, offline: boolean) => {
      const nome = nomeArquivoRelatorio(nomeArquivo);
      baixar.mutate(
        { caminho: caminhoRelatorio(datasetId, { ...selecao, offline }), nomeArquivo: nome },
        {
          onSuccess: () => {
            mostrar({ tipo: 'sucesso', titulo: TEXTOS_RELATORIO.baixado(nome) });
          },
          onError: avisarErro,
        },
      );
    },
  };
}
