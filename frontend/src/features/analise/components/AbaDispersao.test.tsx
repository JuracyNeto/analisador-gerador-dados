import { screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { analiseContinua, propsPainel } from '../../../testes/fixturesAnalise';
import { exigir } from '../../../testes/exigir';
import { renderizarComProvedores } from '../../../testes/renderizar';
import { notaPopulacional } from '../cartoes';
import { TEXTOS_ANALISE } from '../textos';
import AbaDispersao from './AbaDispersao';

const C = TEXTOS_ANALISE.cartoes;

describe('AbaDispersao', () => {
  it('mostra os 5 cards, o selo do CV, a nota populacional e as faixas do CV', () => {
    renderizarComProvedores(<AbaDispersao {...propsPainel(analiseContinua)} />);

    for (const rotulo of [C.desvioPadrao, C.cv, C.iqr, C.amplitude, C.variancia]) {
      expect(screen.getByText(rotulo)).toBeInTheDocument();
    }
    expect(screen.getByText('Variação moderada')).toBeInTheDocument();
    expect(screen.getByText(C.notaVariancia)).toBeInTheDocument();
    expect(
      screen.getByText(
        exigir(
          notaPopulacional(exigir(analiseContinua.dispersao, 'dispersão')),
          'nota populacional',
        ),
      ),
    ).toBeInTheDocument();
    expect(screen.getByText(C.faixasCv)).toBeInTheDocument();
  });
});
