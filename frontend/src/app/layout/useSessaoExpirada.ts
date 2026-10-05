import { useQueryClient } from '@tanstack/react-query';
import { useEffect, useRef } from 'react';
import { useNavigate } from 'react-router';
import { chavesDataset } from '../../shared/api/dataset';
import { ehDatasetNaoEncontrado, textoDoErro } from '../../shared/api/erros';
import { CAMINHOS } from '../../shared/navegacao/caminhos';
import { useSessao } from '../../shared/sessao/useSessao';
import { useToast } from '../../shared/ui/useToast';

/**
 * D61/Dnn-sessao: DATASET_NAO_ENCONTRADO em qualquer consulta ou mutação encerra a sessão,
 * avisa uma vez por dataset ("Sua sessão expirou. Envie o arquivo novamente."), apaga o cache dele e volta para Importar.
 */
export function useSessaoExpirada(): void {
  const clienteConsultas = useQueryClient();
  const { dataset, encerrar } = useSessao();
  const { mostrar } = useToast();
  const navegar = useNavigate();
  const idAtual = dataset?.id ?? null;
  const ultimoAvisado = useRef<string | null>(null);

  useEffect(() => {
    if (idAtual === null) return undefined;
    const id = idAtual;
    const aoFalhar = (erro: unknown): void => {
      if (!ehDatasetNaoEncontrado(erro) || ultimoAvisado.current === id) return;
      ultimoAvisado.current = id;
      const { mensagem, sugestao } = textoDoErro(erro);
      encerrar();
      clienteConsultas.removeQueries({ queryKey: chavesDataset.todas(id) });
      mostrar({ tipo: 'erro', titulo: mensagem, descricao: sugestao });
      void navegar(CAMINHOS.importar);
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
  }, [clienteConsultas, idAtual, encerrar, mostrar, navegar]);
}
