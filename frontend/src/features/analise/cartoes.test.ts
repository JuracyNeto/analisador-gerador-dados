import { describe, expect, it } from 'vitest';
import { formatarNumero } from '../../shared/lib/formatar';
import { analiseBinaria, analiseContinua, analiseNominal } from '../../testes/fixturesAnalise';
import {
  cartoesDispersao,
  cartoesResumoCategorico,
  cartoesTendencia,
  notaPopulacional,
} from './cartoes';
import { propsDoCartao } from '../../shared/metricas/cartoes';
import { TEXTOS_ANALISE } from './textos';
import type { Analise, Dispersao, Moda } from './tipos';
import { exigir } from '../../testes/exigir';

const C = TEXTOS_ANALISE.cartoes;
const dispersao: Dispersao = exigir(analiseContinua.dispersao, 'dispersão da contínua');

function comModa(
  analise: Analise,
  valores: (number | string)[],
  classificacao: Moda['classificacao'],
): Analise {
  return {
    ...analise,
    tendencia: { ...analise.tendencia, moda: { valores, classificacao, interpretacao: 'x' } },
  };
}

describe('cartoesTendencia', () => {
  it('contínua: média, mediana e moda bruta, com a moda de Czuber no "Ver fórmula"', () => {
    const cartoes = cartoesTendencia(analiseContinua);
    const moda = cartoes[2];

    expect(cartoes.map((c) => c.rotulo)).toEqual(['Média', 'Mediana', 'Moda']);
    if (moda === undefined) throw new Error('falta o card da moda');
    expect(moda.medida.valor).toBe(formatarNumero(72));
    expect(propsDoCartao(moda, analiseContinua.formulas).formula).toEqual({
      expressao: 'Mo = Lᵢ + [Δ₁ / (Δ₁ + Δ₂)] · h',
      calculo: 'Moda de Czuber, pelas classes: Mo = 68,9',
    });
  });

  it('usa o cálculo da moda de Czuber que vem do backend sem repetir "Mo"', () => {
    const calculo = 'Mo = 6,8 + [167 / (167 + 108)] · 70,52 = 49,62';
    const analise = {
      ...analiseContinua,
      tendencia: {
        ...analiseContinua.tendencia,
        moda_czuber: { ...analiseContinua.tendencia.moda_czuber, calculo },
      },
    };
    const moda = exigir(cartoesTendencia(analise)[2], 'card da moda');

    expect(propsDoCartao(moda, analise.formulas).formula?.calculo).toBe(
      `Moda de Czuber, pelas classes: ${calculo}`,
    );
  });

  it('binária: proporção no lugar da média', () => {
    expect(cartoesTendencia(analiseBinaria).map((c) => c.rotulo)).toEqual([
      'Proporção',
      'Mediana',
      'Moda',
    ]);
  });

  it('nominal: média e mediana não se aplicam; a moda é a categoria', () => {
    const [media, mediana, moda] = cartoesTendencia(analiseNominal);

    expect([media?.medida.aplicavel, mediana?.medida.aplicavel]).toEqual([false, false]);
    expect(moda?.medida.valor).toBe('Goiânia');
  });

  it('várias modas aparecem juntas com o selo da classificação', () => {
    const moda = cartoesTendencia(comModa(analiseNominal, ['Goiânia', 'Anápolis'], 'bimodal'))[2];

    expect(moda?.medida.valor).toBe('Goiânia · Anápolis');
    expect(moda?.selo).toBe('Bimodal');
  });

  it('sem moda (amodal) mostra "Sem moda"', () => {
    expect(cartoesTendencia(comModa(analiseNominal, [], 'amodal'))[2]?.medida.valor).toBe(
      'Sem moda',
    );
  });
});

describe('cartoesDispersao', () => {
  it('segue a ordem do design, com selo do CV e nota da variância', () => {
    const cartoes = cartoesDispersao(dispersao);

    expect(cartoes.map((c) => c.id)).toEqual([
      'desvio_padrao',
      'cv',
      'iqr',
      'amplitude',
      'variancia',
    ]);
    expect(cartoes[1]).toMatchObject({ unidade: '%', selo: 'Variação moderada' });
    expect(cartoes[4]?.medida.interpretacao).toBe(C.notaVariancia);
  });
});

describe('cartoesResumoCategorico', () => {
  it('moda + média, mediana e desvio padrão não aplicáveis (design 4g)', () => {
    const cartoes = cartoesResumoCategorico(analiseNominal);

    expect(cartoes.map((c) => c.rotulo)).toEqual(['Moda', 'Média', 'Mediana', 'Desvio padrão']);
    expect(cartoes[3]?.medida).toMatchObject({
      aplicavel: false,
      motivo: analiseNominal.nao_aplicavel[1]?.motivo,
    });
  });
});

describe('notaPopulacional', () => {
  it('mostra σ e σ² ao lado dos valores amostrais (D18)', () => {
    expect(notaPopulacional(dispersao)).toBe(
      C.populacional(formatarNumero(11.17), formatarNumero(124.85)),
    );
  });

  it('some quando os populacionais não se aplicam', () => {
    const semPopulacional = {
      ...dispersao,
      desvio_padrao_populacional: { ...dispersao.desvio_padrao, aplicavel: false },
    };

    expect(notaPopulacional(semPopulacional)).toBeNull();
  });
});
