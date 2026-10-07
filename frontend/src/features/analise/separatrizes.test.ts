import { describe, expect, it } from 'vitest';
import { formatarNumero } from '../../shared/lib/formatar';
import { analiseContinua, posicaoAcima, posicaoQuartil } from '../../testes/fixturesAnalise';
import {
  descricaoDaRegua,
  montarRegua,
  percentisVisiveis,
  percentualNaRegua,
  rotuloDestacado,
  textoForaDaFaixa,
} from './separatrizes';
import { TEXTOS_ANALISE } from './textos';
import type { Separatrizes } from './tipos';
import { exigir } from '../../testes/exigir';

const separatrizes: Separatrizes = exigir(
  analiseContinua.separatrizes,
  'analiseContinua.separatrizes',
);
const P = TEXTOS_ANALISE.posicao;

describe('rotuloDestacado', () => {
  it('valor no 3º quartil destaca Q3', () => {
    expect(rotuloDestacado(posicaoQuartil)).toBe('Q3');
  });

  it('percentil usa o prefixo P', () => {
    expect(rotuloDestacado({ ...posicaoQuartil, tipo: 'percentil', indice: 66 })).toBe('P66');
  });

  it('fora da faixa ou sem consulta não destaca nada', () => {
    expect(rotuloDestacado(posicaoAcima)).toBeNull();
    expect(rotuloDestacado(undefined)).toBeNull();
  });
});

describe('percentisVisiveis', () => {
  it('mostra os 9 destaques', () => {
    expect(percentisVisiveis(separatrizes, null).map((p) => p.rotulo)).toEqual(
      separatrizes.destaques,
    );
  });

  it('inclui o percentil consultado, na ordem', () => {
    expect(percentisVisiveis(separatrizes, 'P66').map((p) => p.rotulo)).toEqual([
      'P1',
      'P5',
      'P10',
      'P25',
      'P50',
      'P66',
      'P75',
      'P90',
      'P95',
      'P99',
    ]);
  });
});

describe('percentualNaRegua', () => {
  it('posição = (v − mín) / (máx − mín)', () => {
    expect(percentualNaRegua(69.8, 43.8, 92.9)).toBeCloseTo(52.95, 2);
  });

  it('limita a 0–100% fora da faixa', () => {
    expect(percentualNaRegua(120, 43.8, 92.9)).toBe(100);
    expect(percentualNaRegua(10, 43.8, 92.9)).toBe(0);
  });

  it('com todos os valores iguais, fica no meio', () => {
    expect(percentualNaRegua(5, 5, 5)).toBe(50);
  });
});

describe('montarRegua', () => {
  it('pinta a faixa entre Q2 e Q3 e põe as marcas dos quartis', () => {
    const regua = montarRegua(posicaoQuartil);

    expect(regua.marcador).toBeCloseTo(63.54, 2);
    expect(regua.faixa.inicio).toBeCloseTo(52.95, 2);
    expect(regua.faixa.inicio + regua.faixa.largura).toBeCloseTo(69.45, 2);
    expect(regua.marcas.map((m) => m.rotulo)).toEqual(['Q1', 'Q2', 'Q3']);
  });

  it('acima do máximo: marcador e faixa vão até o fim', () => {
    const regua = montarRegua(posicaoAcima);

    expect(regua.marcador).toBe(100);
    expect(regua.faixa.inicio + regua.faixa.largura).toBe(100);
  });
});

describe('descricaoDaRegua e textoForaDaFaixa', () => {
  it('descreve a régua para leitor de tela', () => {
    expect(descricaoDaRegua(posicaoQuartil)).toBe(
      `Régua de ${formatarNumero(43.8)} a ${formatarNumero(92.9)} com Q1, Q2 e Q3; o valor ${formatarNumero(75)} fica no 3º quartil (entre Q2 e Q3).`,
    );
  });

  it('explica quando o valor passa do maior dado', () => {
    expect(textoForaDaFaixa(posicaoAcima)).toBe(P.acima(formatarNumero(92.9)));
    expect(textoForaDaFaixa(posicaoQuartil)).toBeNull();
  });
});
