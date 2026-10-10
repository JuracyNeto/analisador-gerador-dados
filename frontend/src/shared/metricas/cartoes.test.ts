import { describe, expect, it } from 'vitest';
import { analiseContinua, analiseNominal, medida } from '../../testes/fixturesAnalise';
import { formatarNumero } from '../lib/formatar';
import { medidaAusente, propsDoCartao } from './cartoes';

const C = { media: 'Média', mediana: 'Mediana', iqr: 'Intervalo interquartil (IQR)' };

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

describe('medidaAusente', () => {
  it('é uma medida não aplicável com o motivo', () => {
    expect(medidaAusente('x')).toEqual({
      valor: null,
      aplicavel: false,
      motivo: 'x',
      calculo: null,
      interpretacao: null,
      formula: null,
    });
  });
});
