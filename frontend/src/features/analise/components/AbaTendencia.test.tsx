import { screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { formatarNumero } from '../../../shared/lib/formatar';
import { analiseContinua, analiseNominal, propsPainel } from '../../../testes/fixturesAnalise';
import { renderizarComProvedores } from '../../../testes/renderizar';
import AbaTendencia from './AbaTendencia';
import { exigir } from '../../../testes/exigir';

describe('AbaTendencia', () => {
  it('contínua: média, mediana e moda bruta, com a interpretação em banner', () => {
    renderizarComProvedores(<AbaTendencia {...propsPainel(analiseContinua)} />);

    expect(screen.getByText('Moda')).toBeInTheDocument();
    expect(screen.getByText(formatarNumero(72))).toBeInTheDocument();
    expect(screen.getByText(formatarNumero(70.3))).toBeInTheDocument();
    expect(
      screen.getByText(
        exigir(analiseContinua.interpretacoes[0], 'analiseContinua.interpretacoes[0]'),
      ),
    ).toBeInTheDocument();
  });

  it('nominal: média e mediana aparecem como não aplicáveis, com o motivo', () => {
    renderizarComProvedores(<AbaTendencia {...propsPainel(analiseNominal)} />);

    expect(
      screen.getByText(
        exigir(analiseNominal.tendencia.media.motivo, 'analiseNominal.tendencia.media.motivo'),
      ),
    ).toBeInTheDocument();
    expect(
      screen.getByText(
        exigir(analiseNominal.tendencia.mediana.motivo, 'analiseNominal.tendencia.mediana.motivo'),
      ),
    ).toBeInTheDocument();
    expect(screen.getByText('Goiânia')).toBeInTheDocument();
  });
});
