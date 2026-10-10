import { describe, expect, it } from 'vitest';
import { criarPagina, ID_DATASET } from '../../testes/fixtures/datasets';
import { chamadasPara, simularApi } from '../../testes/api';
import { criarClienteTeste } from '../../testes/renderizar';
import { caminhoDataset, chavesDataset, opcoesPrimeiraPagina } from './dataset';

describe('chavesDataset', () => {
  it('todas as chaves começam pelo prefixo do dataset', () => {
    const prefixo = chavesDataset.todas(ID_DATASET);
    for (const chave of [
      chavesDataset.primeiraPagina(ID_DATASET),
      chavesDataset.colunas(ID_DATASET),
      chavesDataset.diagnostico(ID_DATASET),
      chavesDataset.analises(ID_DATASET),
      chavesDataset.bivariada(ID_DATASET),
      chavesDataset.relatorio(ID_DATASET),
    ]) {
      expect(chave.slice(0, prefixo.length)).toEqual(prefixo);
    }
  });
});

describe('caminhoDataset', () => {
  it('codifica o id e acrescenta o sufixo', () => {
    expect(caminhoDataset('a/b', '/colunas')).toBe('/datasets/a%2Fb/colunas');
  });
});

describe('opcoesPrimeiraPagina', () => {
  it('busca a página 1 com 20 linhas', async () => {
    const falso = simularApi([{ caminho: `/datasets/${ID_DATASET}`, corpo: criarPagina() }]);

    const pagina = await criarClienteTeste().query(opcoesPrimeiraPagina(ID_DATASET));

    expect(pagina.resumo.n_linhas).toBe(230);
    expect(chamadasPara(falso, 'GET', `/datasets/${ID_DATASET}`)[0]?.url).toBe(
      `/api/datasets/${ID_DATASET}?pagina=1&tamanho=20`,
    );
  });
});
