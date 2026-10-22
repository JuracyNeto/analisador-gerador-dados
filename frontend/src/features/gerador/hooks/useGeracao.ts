import { useQueryClient } from '@tanstack/react-query';
import { useSessao } from '../../../shared/sessao/useSessao';
import { useAvisarErro } from '../../../shared/ui/useAvisarErro';
import { useToast } from '../../../shared/ui/useToast';
import { chavesGerador, useGerarBivariado, useGerarUnivariado } from '../api';
import { TEXTOS_GERADOR } from '../textos';
import type { Gerado, PedidoBivariado, PedidoUnivariado } from '../tipos';

const T = TEXTOS_GERADOR;

interface Refazivel<P> {
  variables: P | undefined;
  mutate: (pedido: P) => void;
}

/** O último pedido da aba de novo, com a semente da geração: os mesmos dados (D149). */
function refazerCom<P extends { semente?: number | null }>(
  mutacao: Refazivel<P>,
  semente: number,
): (() => void) | null {
  const pedido = mutacao.variables;
  if (pedido === undefined) return null;
  return () => {
    mutacao.mutate({ ...pedido, semente });
  };
}

/** Toast "Geramos 500 valores." e a geração guardada na sessão (relatório, M3.5). */
function useConcluirGeracao(): (gerado: Gerado) => void {
  const { mostrar } = useToast();
  const { definirUltimoGerado } = useSessao();
  const clienteConsultas = useQueryClient();
  return (gerado) => {
    // A volta à etapa mostra a última geração sem pedir de novo ao servidor.
    clienteConsultas.setQueryData(chavesGerador.geracao(gerado.gerado_id), gerado);
    const titulo =
      gerado.tipo === 'bivariado' ? T.toast.pares(gerado.n) : T.toast.valores(gerado.n);
    mostrar({ tipo: 'sucesso', titulo });
    definirUltimoGerado({
      id: gerado.gerado_id,
      descricao: T.descricaoSessao(gerado.colunas.join(' × '), gerado.n, gerado.tipo),
    });
  };
}

/** As duas gerações da tela (uma por aba), com o mesmo tratamento de sucesso e erro. */
export function useGeracao() {
  const concluir = useConcluirGeracao();
  const avisarErro = useAvisarErro();
  const univariado = useGerarUnivariado();
  const bivariado = useGerarBivariado();
  const opcoes = { onSuccess: concluir, onError: avisarErro };
  const gerarUnivariado = (pedido: PedidoUnivariado) => {
    univariado.mutate(pedido, opcoes);
  };
  const gerarBivariado = (pedido: PedidoBivariado) => {
    bivariado.mutate(pedido, opcoes);
  };
  return {
    univariado,
    bivariado,
    gerarUnivariado,
    gerarBivariado,
    refazer: (gerado: Gerado): (() => void) | null =>
      gerado.tipo === 'univariado'
        ? refazerCom({ variables: univariado.variables, mutate: gerarUnivariado }, gerado.semente)
        : refazerCom({ variables: bivariado.variables, mutate: gerarBivariado }, gerado.semente),
  };
}
