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

/** Monta o hook e envia o arquivo de teste. */
function renderizarEEnviar() {
  const renderizado = renderizarHook(useTudo);
  act(() => {
    renderizado.result.current.importacao.enviar(ARQUIVO);
  });
  return renderizado;
}

describe('useImportacao', () => {
  it('envia o arquivo, define a sessão, guarda as colunas no cache e avisa', async () => {
    const falso = simularApi([
      { metodo: 'POST', caminho: '/datasets', status: 201, corpo: DATASET_CRIADO },
    ]);
    const { result, cliente } = renderizarEEnviar();

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
    const { result } = renderizarEEnviar();

    await waitFor(() => {
      expect(result.current.importacao.erro?.message).toBe('O arquivo está vazio.');
    });
    expect(result.current.importacao.nomeArquivo).toBe('pesquisa_saude.txt');
    expect(result.current.sessao.dataset).toBeNull();
  });

  it('abrir o exemplo define a sessão', async () => {
    simularApi([
      { metodo: 'POST', caminho: '/datasets/exemplo', status: 201, corpo: DATASET_CRIADO },
    ]);
    const { result } = renderizarHook(useTudo);

    act(() => {
      result.current.importacao.abrirExemplo();
    });

    await waitFor(() => {
      expect(result.current.sessao.dataset?.nomeArquivo).toBe('pesquisa_saude.txt');
    });
  });
});
