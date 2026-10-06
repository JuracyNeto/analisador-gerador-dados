import { useQuery } from '@tanstack/react-query';
import { opcoesColunas, opcoesPrimeiraPagina } from '../../../shared/api/dataset';
import { useValorAtrasado } from '../../../shared/lib/useValorAtrasado';
import { ehNumerico } from '../../../shared/ui/tiposVariavel';
import { useToast } from '../../../shared/ui/useToast';
import { ATRASO_LIMITES_MS, useAplicarLimpeza, useDesfazerLimpeza, useDiagnostico } from '../api';
import { avisoLimpezaAplicada, avisoLimpezaDesfeita } from '../resumo';
import { montarPedido, montarSecoes } from '../secoes';
import { useEscolhasLimpeza } from './useEscolhasLimpeza';
import { useLimitesPorColuna } from './useLimitesPorColuna';

/** Orquestra a tela 3: limites (com atraso), diagnóstico, escolhas, pedido, aplicar e desfazer. */
export function useLimpeza(datasetId: string) {
  const limites = useLimitesPorColuna();
  const limitesAtrasados = useValorAtrasado(limites.json, ATRASO_LIMITES_MS);
  const diagnostico = useDiagnostico(datasetId, limitesAtrasados);
  const colunas = useQuery(opcoesColunas(datasetId));
  const resumo = useQuery({
    ...opcoesPrimeiraPagina(datasetId),
    select: (pagina) => pagina.resumo,
  });
  const escolhas = useEscolhasLimpeza();
  const aplicar = useAplicarLimpeza(datasetId);
  const desfazer = useDesfazerLimpeza(datasetId);
  const toast = useToast();

  const secoes = diagnostico.data ? montarSecoes(diagnostico.data) : [];
  const pedido = montarPedido(secoes, escolhas.valores);

  function aplicarLimpeza(): void {
    const nAntes = diagnostico.data?.n_linhas ?? 0;
    aplicar.mutate(pedido, {
      onSuccess: (resultado) => {
        toast.mostrar(avisoLimpezaAplicada(nAntes, resultado, pedido.acoes.length));
        escolhas.limpar();
      },
    });
  }

  function desfazerTudo(): void {
    desfazer.mutate(undefined, {
      onSuccess: (resultado) => {
        toast.mostrar(avisoLimpezaDesfeita(resultado));
        escolhas.limpar();
      },
    });
  }

  return {
    limites,
    diagnostico,
    resumo,
    secoes,
    escolhas,
    pedido,
    colunasNumericas: (colunas.data ?? []).filter((c) => ehNumerico(c.tipo)).map((c) => c.coluna),
    podeDesfazer: (resumo.data?.log_limpeza.length ?? 0) > 0,
    aplicando: aplicar.isPending,
    desfazendo: desfazer.isPending,
    aplicarLimpeza,
    desfazerTudo,
  };
}

export type Limpeza = ReturnType<typeof useLimpeza>;
