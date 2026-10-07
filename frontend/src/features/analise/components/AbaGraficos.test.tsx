import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import { analiseContinua, propsPainel } from '../../../testes/fixturesAnalise';
import { renderizarComProvedores } from '../../../testes/renderizar';
import AbaGraficos from './AbaGraficos';

vi.mock('../../../shared/graficos/Grafico', () => import('../../../testes/graficoFalso'));

describe('AbaGraficos', () => {
  it('abre no gráfico recomendado e mostra os outros menores', () => {
    renderizarComProvedores(<AbaGraficos {...propsPainel(analiseContinua)} />);

    expect(screen.getByRole('radio', { name: /Histograma/ })).toHaveAttribute(
      'aria-checked',
      'true',
    );
    expect(screen.getByText('recomendado')).toBeInTheDocument();
    expect(screen.getAllByRole('figure')).toHaveLength(3);
    expect(screen.getByText('Por que principal.')).toBeInTheDocument();
  });

  it('trocar o gráfico troca o "Por que" e o resumo', async () => {
    const user = userEvent.setup();
    renderizarComProvedores(<AbaGraficos {...propsPainel(analiseContinua)} />);

    await user.click(screen.getByRole('radio', { name: 'Boxplot' }));

    expect(screen.getByText('Por que boxplot.')).toBeInTheDocument();
    expect(screen.getByText('Resumo de boxplot.')).toBeInTheDocument();
  });
});
