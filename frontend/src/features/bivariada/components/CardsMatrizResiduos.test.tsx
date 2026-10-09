import { screen } from '@testing-library/react';
import type { UseQueryResult } from '@tanstack/react-query';
import { describe, expect, it, vi } from 'vitest';
import { bivariadaAlturaPeso, matrizExemplo } from '../../../testes/fixtures/bivariada';
import { exigir } from '../../../testes/exigir';
import { renderizarComProvedores } from '../../../testes/renderizar';
import { TEXTOS_BIVARIADA } from '../textos';
import type { MatrizCorrelacao } from '../tipos';
import CardMatriz from './CardMatriz';
import CardResiduos from './CardResiduos';

vi.mock('../../../shared/graficos/Grafico', () => import('../../../testes/graficoFalso'));

function consulta(parcial: Partial<UseQueryResult<MatrizCorrelacao>>) {
  return {
    isPending: false,
    isError: false,
    refetch: vi.fn(),
    ...parcial,
  } as UseQueryResult<MatrizCorrelacao>;
}

describe('CardMatriz', () => {
  it('mostra o heatmap com o resumo', () => {
    renderizarComProvedores(<CardMatriz consulta={consulta({ data: matrizExemplo })} />);

    const figura = screen.getByRole('figure', { name: 'Matriz de correlação (Pearson)' });
    expect(figura).toHaveAttribute('data-resumo', matrizExemplo.resumo);
  });

  it('sem figura (menos de 2 numéricas) mostra só o resumo', () => {
    const semFigura = { ...matrizExemplo, figura: null, resumo: 'Precisa de pelo menos duas.' };

    renderizarComProvedores(<CardMatriz consulta={consulta({ data: semFigura })} />);

    expect(screen.getByText('Precisa de pelo menos duas.')).toBeInTheDocument();
  });

  it('carregando e erro ficam só no card', async () => {
    const refetch = vi.fn();
    const { rerender, usuario } = renderizarComProvedores(
      <CardMatriz consulta={consulta({ isPending: true })} />,
    );
    expect(screen.getByText(TEXTOS_BIVARIADA.matriz.carregando)).toBeInTheDocument();

    rerender(<CardMatriz consulta={consulta({ isError: true, error: new Error('x'), refetch })} />);
    await usuario.click(screen.getByRole('button', { name: /Tentar de novo/ }));
    expect(refetch).toHaveBeenCalled();
  });
});

describe('CardResiduos', () => {
  it('gráfico e "Como ler os resíduos" com o resumo da API', () => {
    const figura = exigir(bivariadaAlturaPeso.figuras[1], 'figura de resíduos');

    renderizarComProvedores(<CardResiduos figura={figura} />);

    expect(screen.getByRole('figure', { name: 'Resíduos da regressão' })).toBeInTheDocument();
    expect(
      screen.getByRole('heading', { name: TEXTOS_BIVARIADA.residuos.comoLer }),
    ).toBeInTheDocument();
    expect(screen.getByText(figura.resumo)).toBeInTheDocument();
  });
});
