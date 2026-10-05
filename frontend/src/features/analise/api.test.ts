import { describe, expect, it } from 'vitest';
import { ErroApi } from '../../shared/api/cliente';
import { chavesDataset } from '../../shared/api/dataset';
import { caminhoAnalise, caminhoPosicao, chavesAnalise, podeTentarDeNovo } from './api';

describe('caminhos da API de análise', () => {
  it('pede a análise sem classes quando o usuário não mudou o número de classes', () => {
    expect(caminhoAnalise('ds1', 'peso_kg', null)).toBe('/datasets/ds1/colunas/peso_kg/analise');
  });

  it('manda o número de classes escolhido', () => {
    expect(caminhoAnalise('ds1', 'peso_kg', 12)).toBe(
      '/datasets/ds1/colunas/peso_kg/analise?classes=12',
    );
  });

  it('codifica nomes de coluna com espaço e acento', () => {
    expect(caminhoAnalise('ds1', 'renda média', null)).toBe(
      '/datasets/ds1/colunas/renda%20m%C3%A9dia/analise',
    );
  });

  it('pede a posição com valor e tipo de separatriz', () => {
    expect(
      caminhoPosicao({ datasetId: 'ds1', coluna: 'peso_kg', valor: 72.5, tipo: 'decil' }),
    ).toBe('/datasets/ds1/colunas/peso_kg/posicao?valor=72.5&tipo=decil');
  });

  it('usa o prefixo de análises do M1.6 (limpeza e troca de tipo invalidam análise e posição)', () => {
    expect(chavesAnalise.analise('ds1', 'peso_kg', null)).toEqual([
      'datasets',
      'ds1',
      'analise',
      'peso_kg',
      null,
    ]);
    expect(chavesAnalise.posicao('ds1', 'peso_kg', 75, 'quartil').slice(0, 3)).toEqual(
      chavesDataset.analises('ds1'),
    );
  });
});

describe('podeTentarDeNovo', () => {
  it.each(['COLUNA_IGNORADA', 'COLUNA_VAZIA', 'COLUNA_NAO_ENCONTRADA'])(
    'não oferece nova tentativa para %s',
    (codigo) => {
      expect(podeTentarDeNovo(new ErroApi(400, { codigo, mensagem: 'x', sugestao: 'y' }))).toBe(
        false,
      );
    },
  );

  it('oferece nova tentativa para falha de conexão', () => {
    expect(
      podeTentarDeNovo(new ErroApi(0, { codigo: 'SEM_CONEXAO', mensagem: 'x', sugestao: 'y' })),
    ).toBe(true);
  });
});
