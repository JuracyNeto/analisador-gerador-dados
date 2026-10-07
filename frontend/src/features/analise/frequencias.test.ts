import { describe, expect, it } from 'vitest';
import { formatarNumero } from '../../shared/lib/formatar';
import { analiseContinua, analiseNominal } from '../../testes/fixturesAnalise';
import { colunasDaTabela, ehLinhaModal, linhasComTotal, notasDaTabela } from './frequencias';
import { TEXTOS_ANALISE } from './textos';

const T = TEXTOS_ANALISE.frequencias;
const continua = analiseContinua.frequencias;
const nominal = analiseNominal.frequencias;

describe('colunasDaTabela', () => {
  it('contínua: classe, ponto médio, fi, fr%, Fi e Fr%', () => {
    expect(colunasDaTabela(continua, 'peso_kg').map((c) => c.id)).toEqual([
      'rotulo',
      'ponto_medio',
      'fi',
      'fr',
      'fi_acumulada',
      'fr_acumulada',
    ]);
    expect(colunasDaTabela(continua, 'peso_kg')[0]?.titulo).toBe(T.classe);
  });

  it('nominal: nome da coluna, fi, fr% e a acumulada esmaecida', () => {
    const colunas = colunasDaTabela(nominal, 'cidade');

    expect(colunas.map((c) => c.id)).toEqual(['rotulo', 'fi', 'fr', 'fr_acumulada']);
    expect(colunas[0]?.titulo).toBe('cidade');
  });

  it('discreta: valor em mono, sem ponto médio', () => {
    const discreta = { ...continua, tipo: 'discreta' as const, k: null, k_sturges: null, h: null };

    expect(colunasDaTabela(discreta, 'idade').map((c) => c.id)).toEqual([
      'rotulo',
      'fi',
      'fr',
      'fi_acumulada',
      'fr_acumulada',
    ]);
    expect(colunasDaTabela(discreta, 'idade')[0]?.mono).toBe(true);
  });
});

describe('linhasComTotal e ehLinhaModal', () => {
  it('acrescenta a linha Total no fim', () => {
    expect(linhasComTotal(continua).at(-1)).toEqual({ tipo: 'total', total: 227 });
  });

  it('destaca só a classe modal', () => {
    expect(linhasComTotal(continua).map(ehLinhaModal(continua))).toEqual([
      false,
      true,
      false,
      false,
    ]);
  });
});

describe('notasDaTabela', () => {
  it('contínua: explica ⊢ e a amplitude h e conta os faltantes', () => {
    expect(notasDaTabela(continua, 3)).toEqual([
      T.notaClasses(formatarNumero(16.5)),
      '3 faltantes ficaram de fora.',
    ]);
  });

  it('nominal: traz o motivo da acumulada vindo do backend', () => {
    expect(notasDaTabela(nominal, 0)).toEqual([nominal.motivo_acumulada]);
  });
});
