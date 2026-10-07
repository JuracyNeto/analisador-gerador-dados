import { act, waitFor } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { chavesDataset } from '../../shared/api/dataset';
import { chamadasPara, simularApi } from '../../testes/api';
import { COLUNAS_SAUDE, criarColuna, ID_DATASET } from '../../testes/fixtures/datasets';
import { criarClienteTeste, renderizarHook } from '../../testes/renderizar';
import { useAlterarTipo } from './api';

const CAMINHO_PATCH = `/datasets/${ID_DATASET}/colunas/cidade`;
const CAMINHO_COLUNAS = `/datasets/${ID_DATASET}/colunas`;

function prepararCliente() {
  const cliente = criarClienteTeste();
  cliente.setQueryData(chavesDataset.colunas(ID_DATASET), COLUNAS_SAUDE);
  cliente.setQueryData(chavesDataset.diagnostico(ID_DATASET), { qualquer: true });
  return cliente;
}

/** Monta o hook com o cache preparado e pede o novo tipo para `cidade`. */
function alterarTipoDeCidade(tipo: 'ordinal' | 'continua') {
  const cliente = prepararCliente();
  const { result } = renderizarHook(() => useAlterarTipo(ID_DATASET), { cliente });
  act(() => {
    result.current.mutate({ coluna: 'cidade', alteracao: { tipo } });
  });
  return { cliente, result };
}

describe('useAlterarTipo', () => {
  it('envia o PATCH, atualiza o cache na hora e invalida o diagnóstico', async () => {
    const falso = simularApi([
      {
        metodo: 'PATCH',
        caminho: CAMINHO_PATCH,
        corpo: criarColuna({ coluna: 'cidade', tipo: 'ordinal', origem: 'manual' }),
      },
      { caminho: CAMINHO_COLUNAS, corpo: COLUNAS_SAUDE },
    ]);
    const { cliente, result } = alterarTipoDeCidade('ordinal');

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });
    expect(chamadasPara(falso, 'PATCH', CAMINHO_PATCH)[0]?.corpo).toEqual({ tipo: 'ordinal' });
    expect(cliente.getQueryState(chavesDataset.diagnostico(ID_DATASET))?.isInvalidated).toBe(true);
  });

  it('desfaz a mudança otimista quando a API recusa', async () => {
    simularApi([
      {
        metodo: 'PATCH',
        caminho: CAMINHO_PATCH,
        status: 400,
        corpo: {
          codigo: 'TIPO_INCOMPATIVEL',
          mensagem: 'Esta coluna tem textos; não pode ser numérica.',
          sugestao: 'Escolha um tipo qualitativo.',
        },
      },
      { caminho: CAMINHO_COLUNAS, corpo: COLUNAS_SAUDE },
    ]);
    const { cliente, result } = alterarTipoDeCidade('continua');

    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });
    const colunas = cliente.getQueryData<typeof COLUNAS_SAUDE>(chavesDataset.colunas(ID_DATASET));
    expect(colunas?.find((c) => c.coluna === 'cidade')?.tipo).toBe('nominal');
  });
});
