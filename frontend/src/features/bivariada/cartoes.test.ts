import { describe, expect, it } from 'vitest';
import { propsDoCartao } from '../../shared/metricas/cartoes';
import {
  bivariadaAlturaPeso,
  EQUACAO,
  FRASE_FORCA,
  FRASE_SIGNIFICANCIA,
} from '../../testes/fixtures/bivariada';
import { cartoesBivariada, seloCorrelacao } from './cartoes';
import { TEXTOS_BIVARIADA } from './textos';

const C = TEXTOS_BIVARIADA.cartoes;

function props() {
  return cartoesBivariada(bivariadaAlturaPeso).map((cartao) =>
    propsDoCartao(cartao, bivariadaAlturaPeso.formulas),
  );
}

describe('cartoesBivariada', () => {
  it('monta r, R² e reta como no print 5a', () => {
    const cartoes = props();

    expect(cartoes.map((c) => c.rotulo)).toEqual([C.pearson, C.r2, C.reta]);
    expect(cartoes.map((c) => c.valor)).toEqual(['0,78', '61', EQUACAO]);
    expect(cartoes[1]?.unidade).toBe('%');
    expect(cartoes[0]?.selo).toBe('Correlação positiva forte');
  });

  it('o r junta a frase da força e a do teste t; a fórmula traz Spearman ao lado', () => {
    const [r] = props();

    expect(r?.interpretacao).toBe(`${FRASE_FORCA} ${FRASE_SIGNIFICANCIA}`);
    expect(r?.formula?.expressao).toContain('Σ(xᵢ − x̄)');
    expect(r?.formula?.calculo).toContain('ρ = 0,76');
  });

  it('a reta mostra a fórmula de regressão e o cálculo de a e b', () => {
    const reta = props()[2];

    expect(reta?.formula).toEqual({
      expressao: 'Ŷ = a + bX',
      calculo: 'b = Sxy / Sxx = 98,1 · a = ȳ − b·x̄ = −98,4',
    });
  });
});

describe('seloCorrelacao', () => {
  it.each([
    ['moderada', 'negativa', 'Correlação negativa moderada'],
    ['forte', 'negativa', 'Correlação negativa forte'],
    ['fraca', 'positiva', 'Correlação fraca'],
  ] as const)('%s %s → %s', (forca, sentido, selo) => {
    expect(seloCorrelacao({ ...bivariadaAlturaPeso, forca, sentido })).toBe(selo);
  });
});
