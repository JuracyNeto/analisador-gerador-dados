import { describe, expect, it } from 'vitest';
import { formatarNumero } from '../../shared/lib/formatar';
import {
  analiseBinaria,
  analiseContinua,
  analiseNominal,
  medida,
} from '../../testes/fixturesAnalise';
import {
  cartoesDispersao,
  cartoesResumoCategorico,
  cartoesTendencia,
  notaPopulacional,
  propsDoCartao,
} from './cartoes';
import { TEXTOS_ANALISE } from './textos';
import type { Analise, Dispersao, Moda } from './tipos';

const C = TEXTOS_ANALISE.cartoes;
const dispersaoDaFixture = analiseContinua.dispersao;
if (dispersaoDaFixture === null) throw new Error('fixture contínua sem dispersão');
const dispersao: Dispersao = dispersaoDaFixture;

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

describe('propsDoCartao', () => {
  it('formata o valor e acha a fórmula pela chave da medida', () => {
    const definicao = { id: 'media', rotulo: C.media, medida: analiseContinua.tendencia.media };

    expect(propsDoCartao(definicao, analiseContinua.formulas)).toEqual({
      rotulo: 'Média',
      valor: formatarNumero(70.3),
      interpretacao: 'Em média, os valores ficam em 70,3.',
      formula: { expressao: 'x̄ = Σxᵢ / n', calculo: '= 15.958,1 / 227 = 70,3' },
    });
  });

  it('item não aplicável vira card esmaecido com o motivo do backend', () => {
    const definicao = { id: 'media', rotulo: C.media, medida: analiseNominal.tendencia.media };

    expect(propsDoCartao(definicao, [])).toEqual({
      rotulo: 'Média',
      valor: '—',
      naoAplicavel: {
        motivo: 'Média não se aplica a categorias sem número: não dá para somar cidades.',
      },
    });
  });

  it('sem fórmula com a chave da medida, o card não ganha "Ver fórmula"', () => {
    const definicao = { id: 'iqr', rotulo: C.iqr, medida: medida(15.8, { formula: 'iqr' }) };

    expect(propsDoCartao(definicao, analiseContinua.formulas)).not.toHaveProperty('formula');
  });

  it('valor de texto (mediana ordinal) aparece como veio', () => {
    expect(
      propsDoCartao({ id: 'mediana', rotulo: C.mediana, medida: medida('bom') }, []).valor,
    ).toBe('bom');
  });
});

describe('cartoesTendencia', () => {
  it('contínua: média, mediana e moda bruta, com a moda de Czuber no "Ver fórmula"', () => {
    const cartoes = cartoesTendencia(analiseContinua);
    const moda = cartoes[2];

    expect(cartoes.map((c) => c.rotulo)).toEqual(['Média', 'Mediana', 'Moda']);
    if (moda === undefined) throw new Error('falta o card da moda');
    expect(moda.medida.valor).toBe(formatarNumero(72));
    expect(propsDoCartao(moda, analiseContinua.formulas).formula).toEqual({
      expressao: 'Mo = Lᵢ + [Δ₁ / (Δ₁ + Δ₂)] · h',
      calculo: C.apoioCzuber(`= ${formatarNumero(68.9)}`),
    });
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
