import { useQueryClient } from '@tanstack/react-query';
import { ErroApi } from '../../../shared/api/cliente';
import { chavesDataset } from '../../../shared/api/dataset';
import { formatarInteiro } from '../../../shared/lib/formatar';
import { useSessao } from '../../../shared/sessao/useSessao';
import { useAvisarErro } from '../../../shared/ui/useAvisarErro';
import { useToast } from '../../../shared/ui/useToast';
import { nomeCsv, useAdotar, useBaixarCsv } from '../api';
import { TEXTOS_GERADOR } from '../textos';
import type { Adotado, Gerado } from '../tipos';

const T = TEXTOS_GERADOR.toast;
const GERADO_NAO_ENCONTRADO = 'GERADO_NAO_ENCONTRADO';

/** Erro de uma ação: toast; se a geração saiu da memória, o resultado da tela some. */
function useTratarErro(aoExpirar: () => void): (erro: unknown) => void {
  const avisarErro = useAvisarErro();
  return (erro) => {
    if (erro instanceof ErroApi && erro.codigo === GERADO_NAO_ENCONTRADO) aoExpirar();
    avisarErro(erro);
  };
}

/** Baixar CSV, anexar ao dataset atual e usar como novo dataset (tela 6, ações do resultado). */
export function useAcoesGeracao(gerado: Gerado, aoExpirar: () => void) {
  const { dataset, definirDataset } = useSessao();
  const cliente = useQueryClient();
  const { mostrar } = useToast();
  const tratarErro = useTratarErro(aoExpirar);
  const baixar = useBaixarCsv();
  const adotar = useAdotar();
  const modoEmAndamento = adotar.isPending ? adotar.variables.modo : null;
  const aoAnexar = (adotado: Adotado) => {
    void cliente.invalidateQueries({ queryKey: chavesDataset.todas(adotado.dataset_id) });
    mostrar({
      tipo: 'sucesso',
      titulo: T.anexado(formatarInteiro(gerado.n), adotado.nome_arquivo),
    });
  };
  const aoUsar = (adotado: Adotado) => {
    definirDataset({ id: adotado.dataset_id, nomeArquivo: adotado.nome_arquivo });
    mostrar({ tipo: 'sucesso', titulo: T.novo(formatarInteiro(adotado.n_linhas)) });
  };

  return {
    podeAnexar: dataset !== null,
    baixando: baixar.isPending,
    anexando: modoEmAndamento === 'anexar',
    usando: modoEmAndamento === 'novo',
    baixar: () => {
      baixar.mutate(gerado, {
        onSuccess: () => {
          mostrar({ tipo: 'sucesso', titulo: T.baixado(nomeCsv(gerado)) });
        },
        onError: tratarErro,
      });
    },
    anexar: () => {
      if (dataset === null) return;
      adotar.mutate(
        { geradoId: gerado.gerado_id, modo: 'anexar', datasetId: dataset.id },
        { onSuccess: aoAnexar, onError: tratarErro },
      );
    },
    usarComoNovo: () => {
      adotar.mutate(
        { geradoId: gerado.gerado_id, modo: 'novo' },
        { onSuccess: aoUsar, onError: tratarErro },
      );
    },
  };
}
