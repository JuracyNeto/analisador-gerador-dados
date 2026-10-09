import { describe, expect, it } from 'vitest';
import { ErroApi } from '../../shared/api/cliente';
import { chavesDataset } from '../../shared/api/dataset';
import {
  caminhoBivariada,
  caminhoCorrelacoes,
  caminhoPrevisao,
  chavesBivariada,
  podeTentarDeNovo,
} from './api';
import { comPar, lerPar, parEscolhido, trocado } from './parametros';
import { criarColuna } from '../../testes/fixtures/datasets';

const PAR = { x: 'altura m', y: 'peso_kg' };
const NUMERICAS = [
  criarColuna({ coluna: 'idade', tipo: 'continua' }),
  criarColuna({ coluna: 'altura_m', tipo: 'continua' }),
  criarColuna({ coluna: 'peso_kg', tipo: 'continua' }),
];

describe('caminhos da API da bivariada', () => {
  it('codifica X e Y na busca', () => {
    expect(caminhoBivariada('ds1', PAR)).toBe('/datasets/ds1/bivariada?x=altura+m&y=peso_kg');
    expect(caminhoPrevisao('ds1', PAR, 1.75)).toBe(
      '/datasets/ds1/bivariada/prever?x=altura+m&y=peso_kg&valor=1.75',
    );
    expect(caminhoCorrelacoes('ds1')).toBe('/datasets/ds1/correlacoes');
  });

  it('chaves sob o prefixo da bivariada (invalidadas pela limpeza e pela troca de tipo)', () => {
    const prefixo = chavesDataset.bivariada('ds1');
    for (const chave of [
      chavesBivariada.par('ds1', PAR),
      chavesBivariada.matriz('ds1'),
      chavesBivariada.previsao('ds1', PAR, 2),
    ]) {
      expect(chave.slice(0, prefixo.length)).toEqual(prefixo);
    }
  });

  it.each(['COLUNA_NAO_NUMERICA', 'COLUNAS_IGUAIS', 'POUCOS_PARES', 'SEM_VARIACAO'])(
    '%s não oferece "Tentar de novo"',
    (codigo) => {
      expect(podeTentarDeNovo(new ErroApi(400, { codigo, mensagem: 'x', sugestao: 'y' }))).toBe(
        false,
      );
    },
  );
});

describe('par na URL', () => {
  it('sem URL usa as duas primeiras numéricas', () => {
    expect(parEscolhido(lerPar(new URLSearchParams()), NUMERICAS)).toEqual({
      x: 'idade',
      y: 'altura_m',
    });
  });

  it('respeita a URL válida', () => {
    expect(parEscolhido(lerPar(new URLSearchParams('x=peso_kg&y=idade')), NUMERICAS)).toEqual({
      x: 'peso_kg',
      y: 'idade',
    });
  });

  it.each(['x=cidade&y=peso_kg', 'x=peso_kg&y=peso_kg', 'x=peso_kg'])(
    '%s cai no padrão',
    (busca) => {
      expect(parEscolhido(lerPar(new URLSearchParams(busca)), NUMERICAS)).toEqual({
        x: 'idade',
        y: 'altura_m',
      });
    },
  );

  it('com menos de duas numéricas não há par', () => {
    expect(parEscolhido({ x: null, y: null }, NUMERICAS.slice(0, 1))).toBeNull();
  });

  it('grava e troca o par', () => {
    expect(comPar(new URLSearchParams('a=1'), { x: 'a b', y: 'c' }).toString()).toBe(
      'a=1&x=a+b&y=c',
    );
    expect(trocado({ x: 'a', y: 'b' })).toEqual({ x: 'b', y: 'a' });
  });
});
