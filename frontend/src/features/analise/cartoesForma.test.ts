import { describe, expect, it } from 'vitest';
import {
  formaBinaria,
  formaContinua,
  formaDiscreta,
  MOTIVO_BINOMIAL_CONTINUA,
  normalCompativel,
} from '../../testes/fixtures/forma';
import { naoSeAplica } from '../../testes/fixtures/blocosAnalise';
import { exigir } from '../../testes/exigir';
import { propsDoCartao } from '../../shared/metricas/cartoes';
import { cartoesForma, medidaDoAjuste, notaCoeficientes } from './cartoesForma';
import { TEXTOS_ANALISE } from './textos';
import type { Forma } from './tipos';

const F = TEXTOS_ANALISE.forma;

function props(forma: Forma) {
  return cartoesForma(forma).map((cartao) => propsDoCartao(cartao, []));
}

describe('cartoesForma', () => {
  it('monta os 4 cards da contínua na ordem do print 4e', () => {
    const cartoes = props(formaContinua);

    expect(cartoes.map((c) => c.rotulo)).toEqual([
      F.assimetria,
      F.curtose,
      F.ajusteNormal,
      F.ajusteBinomial,
    ]);
    expect(cartoes.map((c) => c.valor)).toEqual(['0,32', '-0,18', 'p = 0,21', '—']);
    expect(cartoes.map((c) => c.selo)).toEqual([
      'Aprox. simétrica',
      'Mesocúrtica',
      'Compatível com a Normal',
      undefined,
    ]);
    expect(cartoes[3]?.naoAplicavel).toEqual({ motivo: MOTIVO_BINOMIAL_CONTINUA });
  });

  it('a interpretação do ajuste traz a frase e os parâmetros', () => {
    const [, , normal] = props(formaContinua);

    expect(normal?.interpretacao).toBe(
      'Os dados são compatíveis com a distribuição Normal. μ̂ = 70,31 · σ̂ = 11,2',
    );
  });

  it('normal reprovada ganha o selo "Afasta-se"', () => {
    const reprovada: Forma = {
      ...formaContinua,
      normal: {
        ...normalCompativel,
        teste: {
          ...exigir(normalCompativel.teste, 'teste da Normal'),
          p_valor: 0.0004,
          compativel: false,
        },
      },
    };

    const [, , normal] = props(reprovada);

    expect(normal?.valor).toBe('p < 0,001');
    expect(normal?.selo).toBe('Afasta-se da Normal');
  });

  it('assimetria forte à esquerda tem selo próprio', () => {
    const forte: Forma = {
      ...formaContinua,
      classificacao_assimetria: 'forte',
      sentido_assimetria: 'esquerda',
    };

    expect(props(forte)[0]?.selo).toBe('Forte à esquerda');
  });

  it('binomial com teste mostra o p-valor e as tentativas', () => {
    const binomial = props(formaDiscreta)[3];

    expect(binomial?.rotulo).toBe(F.ajusteBinomial);
    expect(binomial?.valor).toBe('p = 0,135');
    expect(binomial?.interpretacao).toContain('n = 8 · p̂ = 0,3906');
  });

  it('bernoulli mostra p̂ e não tem selo', () => {
    const bernoulli = props(formaBinaria)[3];

    expect(bernoulli?.rotulo).toBe(F.ajusteBernoulli);
    expect(bernoulli?.valor).toBe('p̂ = 0,3');
    expect(bernoulli?.selo).toBeUndefined();
  });

  it('assimetria e curtose não aplicáveis aparecem com o motivo', () => {
    const [assimetria] = props(formaBinaria);

    expect(assimetria?.naoAplicavel?.motivo).toBe(formaBinaria.assimetria.motivo);
  });
});

describe('medidaDoAjuste', () => {
  it('junta o cálculo do teste principal e o complementar', () => {
    expect(medidaDoAjuste(normalCompativel).calculo).toBe(
      'Shapiro-Wilk: W = 0,9912 · p = 0,21 ≥ 0,05 | Teste complementar (classes) · Qui-quadrado: χ² = 3,2 · gl = 4 · p = 0,525',
    );
  });
});

describe('notaCoeficientes', () => {
  it('lista os coeficientes de Pearson e a curtose percentílica', () => {
    expect(notaCoeficientes(formaContinua)).toBe(
      'Coeficientes de Pearson: As₁ = 0,4677 · As₂ = 0,7016. Curtose percentílica: K = 0,1786 (na Normal, K ≈ 0,263).',
    );
  });

  it('sem nada aplicável não há nota', () => {
    expect(notaCoeficientes(formaBinaria)).toBeNull();
  });

  it('só com o 2º coeficiente', () => {
    const parcial: Forma = {
      ...formaContinua,
      assimetria_pearson_1: naoSeAplica('x'),
      curtose_percentilica: naoSeAplica('y'),
    };

    expect(notaCoeficientes(parcial)).toBe('Coeficientes de Pearson: As₂ = 0,7016.');
  });
});
