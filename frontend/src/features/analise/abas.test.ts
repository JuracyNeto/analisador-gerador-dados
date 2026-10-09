import { describe, expect, it } from 'vitest';
import { analiseContinua, analiseNominal } from '../../testes/fixturesAnalise';
import { MOTIVO_FORMA_NOMINAL } from '../../testes/fixtures/forma';
import { abaEfetiva, abasDaAnalise } from './abas';
import { TEXTOS_ANALISE } from './textos';

describe('abasDaAnalise', () => {
  it('mostra as 6 abas, com "Forma e distribuição" entre Dispersão e Gráficos', () => {
    expect(abasDaAnalise(analiseContinua).map((a) => a.rotulo)).toEqual([
      'Frequências',
      'Tendência central',
      'Separatrizes',
      'Dispersão',
      'Forma e distribuição',
      'Gráficos',
    ]);
  });

  it('contínua: nenhuma aba desabilitada', () => {
    expect(abasDaAnalise(analiseContinua).some((a) => a.desabilitada === true)).toBe(false);
  });

  it('nominal: Separatrizes, Dispersão e Forma desabilitadas com o motivo de nao_aplicavel', () => {
    const desabilitadas = abasDaAnalise(analiseNominal).filter((a) => a.desabilitada === true);

    expect(desabilitadas).toEqual([
      {
        id: 'separatrizes',
        rotulo: 'Separatrizes',
        desabilitada: true,
        motivo: analiseNominal.nao_aplicavel[0]?.motivo,
      },
      {
        id: 'dispersao',
        rotulo: 'Dispersão',
        desabilitada: true,
        motivo: analiseNominal.nao_aplicavel[1]?.motivo,
      },
      {
        id: 'forma',
        rotulo: 'Forma e distribuição',
        desabilitada: true,
        motivo: MOTIVO_FORMA_NOMINAL,
      },
    ]);
  });

  it('sem motivo no backend, usa o texto padrão', () => {
    const semMotivo = { ...analiseNominal, nao_aplicavel: [] };

    expect(abasDaAnalise(semMotivo).find((a) => a.id === 'dispersao')?.motivo).toBe(
      TEXTOS_ANALISE.motivoPadrao,
    );
  });
});

describe('abaEfetiva', () => {
  it('mantém a aba pedida quando ela está habilitada', () => {
    expect(abaEfetiva('separatrizes', abasDaAnalise(analiseContinua))).toBe('separatrizes');
  });

  it('volta para Frequências quando a aba pedida não se aplica à coluna', () => {
    expect(abaEfetiva('separatrizes', abasDaAnalise(analiseNominal))).toBe('frequencias');
  });
});
