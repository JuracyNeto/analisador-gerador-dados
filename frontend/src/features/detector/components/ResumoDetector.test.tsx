import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import { resultadoDetector } from '../../../testes/fixtures/detector';
import { TODAS_SEVERIDADES } from '../parametros';
import BarraFiltros from './BarraFiltros';
import ResumoDetector from './ResumoDetector';

const { resumo } = resultadoDetector;

describe('ResumoDetector', () => {
  it('frase, detalhe e um contador por severidade com ícone e palavra (7a)', () => {
    render(<ResumoDetector resumo={resumo} />);

    expect(
      screen.getByRole('heading', { name: 'Encontramos 6 alertas em 3 colunas' }),
    ).toBeInTheDocument();
    expect(screen.getByText(resumo.detalhe)).toBeInTheDocument();
    const contadores = within(screen.getByRole('list', { name: 'Alertas por severidade' }));
    expect(contadores.getAllByRole('listitem').map((item) => item.textContent)).toEqual([
      '3reportSuspeita alta',
      '2warningAtenção',
      '1infoInformativo',
    ]);
  });
});

describe('BarraFiltros', () => {
  it('um chip por severidade com a contagem e o agrupamento marcado', () => {
    render(
      <BarraFiltros
        porSeveridade={resumo.por_severidade}
        filtros={{ severidades: new Set(['alta', 'info'] as const), agrupar: 'regra' }}
        aoAlternar={vi.fn()}
        aoAgrupar={vi.fn()}
      />,
    );

    const mostrar = within(screen.getByRole('group', { name: 'Mostrar' }));
    expect(mostrar.getByRole('checkbox', { name: 'Suspeita alta (3)' })).toBeChecked();
    expect(mostrar.getByRole('checkbox', { name: 'Atenção (2)' })).not.toBeChecked();
    expect(mostrar.getByRole('checkbox', { name: 'Informativo (1)' })).toBeChecked();
    expect(screen.getByRole('radio', { name: 'Regra' })).toBeChecked();
  });

  it('avisa qual severidade alternar e qual agrupamento escolher', async () => {
    const usuario = userEvent.setup();
    const aoAlternar = vi.fn();
    const aoAgrupar = vi.fn();
    render(
      <BarraFiltros
        porSeveridade={resumo.por_severidade}
        filtros={{ severidades: TODAS_SEVERIDADES, agrupar: 'coluna' }}
        aoAlternar={aoAlternar}
        aoAgrupar={aoAgrupar}
      />,
    );

    await usuario.click(screen.getByRole('checkbox', { name: 'Atenção (2)' }));
    await usuario.click(screen.getByRole('radio', { name: 'Regra' }));

    expect(aoAlternar).toHaveBeenCalledWith('atencao');
    expect(aoAgrupar).toHaveBeenCalledWith('regra');
  });
});
