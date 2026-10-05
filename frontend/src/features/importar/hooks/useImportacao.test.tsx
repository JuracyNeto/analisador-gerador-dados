import { act, screen, waitFor } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { chavesDataset } from '../../../shared/api/dataset';
import { useSessao } from '../../../shared/sessao/useSessao';
import { chamadasPara, simularApi } from '../../../testes/api';
import { COLUNAS_SAUDE, DATASET_CRIADO, ID_DATASET } from '../../../testes/fixtures/datasets';
import { renderizarHook } from '../../../testes/renderizar';
import { useImportacao } from './useImportacao';

const ARQUIVO = new File(['id;sexo'], 'pesquisa_saude.txt', { type: 'text/plain' });

function useTudo() {
  return { importacao: useImportacao(), sessao: useSessao() };
}

describe('useImportacao', () => {
  it('envia o arquivo, define a sessão, guarda as colunas no cache e avisa', async () => {
    const falso = simularApi([
      { metodo: 'POST', caminho: '/datasets', status: 201, corpo: DATASET_CRIADO },
    ]);
    const { result, cliente } = renderizarHook(useTudo);

    act(() => {
      result.current.importacao.enviar(ARQUIVO);
    });

    await waitFor(() => {
      expect(result.current.sessao.dataset).toEqual({
        id: ID_DATASET,
        nomeArquivo: 'pesquisa_saude.txt',
      });
    });
    expect(cliente.getQueryData(chavesDataset.colunas(ID_DATASET))).toEqual(COLUNAS_SAUDE);
    expect(await screen.findByText('Arquivo lido: 230 linhas e 8 colunas.')).toBeInTheDocument();
    const corpo = chamadasPara(falso, 'POST', '/datasets')[0]?.corpo as FormData;
    expect(corpo.get('arquivo')).toBe(ARQUIVO);
  });

  it('corrigir relê o mesmo arquivo com a correção acumulada', async () => {
    const falso = simularApi([
      { metodo: 'POST', caminho: '/datasets', status: 201, corpo: DATASET_CRIADO },
    ]);
    const { result } = renderizarHook(useTudo);
    act(() => {
      result.current.importacao.enviar(ARQUIVO);
    });
    await waitFor(() => {
      expect(result.current.importacao.corrigir).not.toBeNull();
    });

    act(() => {
      result.current.importacao.corrigir?.('separador', ',');
    });

    await waitFor(() => {
      expect(chamadasPara(falso, 'POST', '/datasets')).toHaveLength(2);
    });
    const segunda = chamadasPara(falso, 'POST', '/datasets')[1]?.corpo as FormData;
    expect(segunda.get('arquivo')).toBe(ARQUIVO);
    expect(segunda.get('separador')).toBe(',');
  });

  it('expõe o erro e o nome do arquivo para o banner', async () => {
    simularApi([
      {
        metodo: 'POST',
        caminho: '/datasets',
        status: 400,
        corpo: {
          codigo: 'ARQUIVO_VAZIO',
          mensagem: 'O arquivo está vazio.',
          sugestao: 'Escolha outro arquivo.',
        },
      },
    ]);
    const { result } = renderizarHook(useTudo);

    act(() => {
      result.current.importacao.enviar(ARQUIVO);
    });

    await waitFor(() => {
      expect(result.current.importacao.erro?.message).toBe('O arquivo está vazio.');
    });
    expect(result.current.importacao.nomeArquivo).toBe('pesquisa_saude.txt');
    expect(result.current.sessao.dataset).toBeNull();
  });

  it('o exemplo não pode ser corrigido, mas pode ser lido de novo', async () => {
    simularApi([
      { metodo: 'POST', caminho: '/datasets/exemplo', status: 201, corpo: DATASET_CRIADO },
    ]);
    const { result } = renderizarHook(useTudo);

    act(() => {
      result.current.importacao.abrirExemplo();
    });

    await waitFor(() => {
      expect(result.current.sessao.dataset).not.toBeNull();
    });
    expect(result.current.importacao.corrigir).toBeNull();
    expect(result.current.importacao.lerDeNovo).not.toBeNull();
  });
});
