import { useQueryClient } from '@tanstack/react-query';
import { ErroApi } from '../../../shared/api/cliente';
import { textoDoErro } from '../../../shared/api/erros';
import { chavesDataset } from '../../../shared/api/dataset';
import { useSessao } from '../../../shared/sessao/useSessao';
import { useAvisarErro } from '../../../shared/ui/useAvisarErro';
import { useToast } from '../../../shared/ui/useToast';
import { nomeCsv, useAdotar, useBaixarCsv } from '../api';
import { TEXTOS_GERADOR } from '../textos';
import type { Adotado, Gerado } from '../tipos';

const T = TEXTOS_GERADOR;
const GERADO_NAO_ENCONTRADO = 'GERADO_NAO_ENCONTRADO';

interface AoPerder {
  /** Tira o resultado da tela. */
  aoExpirar: () => void;
  /** Refaz o pedido desta geração; vira o botão "Gerar de novo" do aviso (D149). */
  aoGerarDeNovo: (() => void) | null;
}

/**
 * Erro de uma ação: toast. Se a geração saiu da memória, o resultado some e o aviso oferece
 * "Gerar de novo" (a pessoa já está na etapa Gerador).
 */
function useTratarErro(gerado: Gerado, { aoExpirar, aoGerarDeNovo }: AoPerder) {
  const avisarErro = useAvisarErro();
  const { mostrar } = useToast();
  return (erro: unknown) => {
    if (!(erro instanceof ErroApi) || erro.codigo !== GERADO_NAO_ENCONTRADO) {
      avisarErro(erro);
      return;
    }
    aoExpirar();
    mostrar({
      tipo: 'erro',
      titulo: textoDoErro(erro).mensagem,
      descricao: T.expirado.descricao(gerado.semente),
      acao:
        aoGerarDeNovo === null ? undefined : { rotulo: T.expirado.acao, aoClicar: aoGerarDeNovo },
    });
  };
}

/** Baixar CSV, anexar ao dataset atual e usar como novo dataset (tela 6, ações do resultado). */
export function useAcoesGeracao(gerado: Gerado, aoPerder: AoPerder) {
  const { dataset, definirDataset } = useSessao();
  const cliente = useQueryClient();
  const { mostrar } = useToast();
  const tratarErro = useTratarErro(gerado, aoPerder);
  const baixar = useBaixarCsv();
  const adotar = useAdotar();
  const modoEmAndamento = adotar.isPending ? adotar.variables.modo : null;
  const aoAnexar = (adotado: Adotado) => {
    void cliente.invalidateQueries({ queryKey: chavesDataset.todas(adotado.dataset_id) });
    mostrar({
      tipo: 'sucesso',
      titulo: T.toast.anexado(gerado.n, adotado.nome_arquivo),
    });
  };
  const aoUsar = (adotado: Adotado) => {
    definirDataset({ id: adotado.dataset_id, nomeArquivo: adotado.nome_arquivo });
    mostrar({ tipo: 'sucesso', titulo: T.toast.novo(adotado.n_linhas) });
  };

  return {
    podeAnexar: dataset !== null,
    baixando: baixar.isPending,
    anexando: modoEmAndamento === 'anexar',
    usando: modoEmAndamento === 'novo',
    baixar: () => {
      baixar.mutate(gerado, {
        onSuccess: () => {
          mostrar({ tipo: 'sucesso', titulo: T.toast.baixado(nomeCsv(gerado)) });
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
