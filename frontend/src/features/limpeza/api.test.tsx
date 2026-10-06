import { act } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { chavesDataset } from '../../shared/api/dataset';
import { chamadasPara, simularApi } from '../../testes/api';
import { COLUNAS_SAUDE, ID_DATASET } from '../../testes/fixtures/datasets';
import { criarResultado } from '../../testes/fixtures/limpeza';
import { criarClienteTeste, renderizarHook } from '../../testes/renderizar';
import { caminhoDiagnostico, useAplicarLimpeza } from './api';

const CAMINHO_LIMPEZA = `/datasets/${ID_DATASET}/limpeza`;

describe('caminhoDiagnostico', () => {
  it('sem limites não manda a query', () => {
    expect(caminhoDiagnostico(ID_DATASET, '')).toBe(`/datasets/${ID_DATASET}/diagnostico`);
  });

  it('codifica os limites em JSON na query', () => {
    expect(caminhoDiagnostico(ID_DATASET, '{"idade":{"min":1,"max":110}}')).toBe(
      `/datasets/${ID_DATASET}/diagnostico?limites=%7B%22idade%22%3A%7B%22min%22%3A1%2C%22max%22%3A110%7D%7D`,
    );
  });
});

describe('useAplicarLimpeza', () => {
  it('envia o pedido e invalida tudo do dataset', async () => {
    const falso = simularApi([
      { metodo: 'POST', caminho: CAMINHO_LIMPEZA, corpo: criarResultado() },
    ]);
    const cliente = criarClienteTeste();
    cliente.setQueryData(chavesDataset.colunas(ID_DATASET), COLUNAS_SAUDE);
    const { result } = renderizarHook(() => useAplicarLimpeza(ID_DATASET), { cliente });
    const pedido = { acoes: [] };

    await act(async () => {
      await result.current.mutateAsync(pedido);
    });

    expect(chamadasPara(falso, 'POST', CAMINHO_LIMPEZA)[0]?.corpo).toEqual(pedido);
    expect(cliente.getQueryState(chavesDataset.colunas(ID_DATASET))?.isInvalidated).toBe(true);
  });
});
