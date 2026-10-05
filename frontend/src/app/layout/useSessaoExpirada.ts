import { useQueryClient } from '@tanstack/react-query';
import { useEffect } from 'react';
import { useNavigate } from 'react-router';
import { ehDatasetNaoEncontrado, textoDoErro } from '../../shared/api/erros';
import { useSessao } from '../../shared/sessao/useSessao';
import { useToast } from '../../shared/ui/useToast';
import { ETAPAS } from '../etapas';

/** D61: DATASET_NAO_ENCONTRADO em qualquer consulta ou mutação encerra a sessão, avisa e leva para Importar. */
export function useSessaoExpirada(): void {
  const clienteConsultas = useQueryClient();
  const { encerrar } = useSessao();
  const { mostrar } = useToast();
  const navegar = useNavigate();

  useEffect(() => {
    const aoFalhar = (erro: unknown): void => {
      if (!ehDatasetNaoEncontrado(erro)) return;
      const { mensagem, sugestao } = textoDoErro(erro);
      encerrar();
      mostrar({ tipo: 'erro', titulo: mensagem, descricao: sugestao });
      void navegar(ETAPAS[0].caminho);
    };
    const pararConsultas = clienteConsultas.getQueryCache().subscribe((evento) => {
      if (evento.type === 'updated' && evento.action.type === 'error')
        aoFalhar(evento.action.error);
    });
    const pararMutacoes = clienteConsultas.getMutationCache().subscribe((evento) => {
      if (evento.type === 'updated' && evento.action.type === 'error')
        aoFalhar(evento.action.error);
    });
    return () => {
      pararConsultas();
      pararMutacoes();
    };
  }, [clienteConsultas, encerrar, mostrar, navegar]);
}
