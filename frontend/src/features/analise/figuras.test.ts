import { describe, expect, it } from 'vitest';
import { analiseContinua, analiseNominal } from '../../testes/fixturesAnalise';
import { figuraAtiva, opcoesDeFiguras } from './figuras';
import { exigir } from '../../testes/exigir';

describe('opcoesDeFiguras', () => {
  it('contínua: Histograma recomendado, Boxplot e Ogiva', () => {
    expect(opcoesDeFiguras(analiseContinua.figuras)).toEqual([
      { valor: 'principal', rotulo: 'Histograma', selo: 'recomendado' },
      { valor: 'boxplot', rotulo: 'Boxplot' },
      { valor: 'ogiva', rotulo: 'Ogiva' },
    ]);
  });

  it('nominal: o gráfico principal se chama Barras', () => {
    expect(opcoesDeFiguras(analiseNominal.figuras)[0]?.rotulo).toBe('Barras');
  });

  it('usa o rótulo que vem do backend, também para ids novos', () => {
    const nova = {
      ...exigir(analiseContinua.figuras[0], 'primeira figura'),
      id: 'qq',
      recomendado: false,
      rotulo: 'QQ-plot',
    };
    expect(opcoesDeFiguras([nova])[0]?.rotulo).toBe('QQ-plot');
  });
});

describe('figuraAtiva', () => {
  it('começa na recomendada', () => {
    expect(figuraAtiva(analiseContinua.figuras, null)?.id).toBe('principal');
  });

  it('usa a escolhida quando ela existe e volta à recomendada quando não existe', () => {
    expect(figuraAtiva(analiseContinua.figuras, 'ogiva')?.id).toBe('ogiva');
    expect(figuraAtiva(analiseNominal.figuras, 'ogiva')?.id).toBe('principal');
  });

  it('sem figuras devolve null', () => {
    expect(figuraAtiva([], null)).toBeNull();
  });
});
