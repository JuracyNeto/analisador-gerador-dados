import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import type { ComponentProps } from 'react';
import { describe, expect, it, vi } from 'vitest';
import { formatarNumero } from '../../../shared/lib/formatar';
import { analiseContinua, analiseNominal } from '../../../testes/fixturesAnalise';
import { renderizarComProvedores } from '../../../testes/renderizar';
import { TEXTOS_ANALISE } from '../textos';
import TabelaFrequencias from './TabelaFrequencias';
import { exigir } from '../../../testes/exigir';

const T = TEXTOS_ANALISE.frequencias;

function renderizarTabela(props: Partial<ComponentProps<typeof TabelaFrequencias>> = {}) {
  const aoMudarClasses = vi.fn();
  renderizarComProvedores(
    <TabelaFrequencias
      tabela={analiseContinua.frequencias}
      coluna="peso_kg"
      nFaltantes={3}
      k={5}
      atualizando={false}
      aoMudarClasses={aoMudarClasses}
      {...props}
    />,
  );
  return aoMudarClasses;
}

describe('TabelaFrequencias', () => {
  it('mostra as classes com ⊢, a linha Total e a nota da amplitude', () => {
    renderizarTabela();

    expect(screen.getByText('60,0 ⊢ 76,5')).toBeInTheDocument();
    expect(screen.getByRole('row', { name: /Total/ })).toHaveTextContent('227');
    expect(screen.getByText(T.notaClasses(formatarNumero(16.5)))).toBeInTheDocument();
    expect(screen.getByText('Sturges: 9')).toBeInTheDocument();
  });

  it('o controle pede uma classe a mais ou a menos', async () => {
    const user = userEvent.setup();
    const aoMudarClasses = renderizarTabela();

    await user.click(screen.getByRole('button', { name: T.mais }));
    await user.click(screen.getByRole('button', { name: T.menos }));

    expect(aoMudarClasses.mock.calls).toEqual([[6], [4]]);
  });

  it('no mínimo de 3 classes, "menos" fica desabilitado', () => {
    renderizarTabela({ k: 3 });

    expect(screen.getByRole('button', { name: T.menos })).toBeDisabled();
  });

  it('nominal: sem controle de classes, com a acumulada esmaecida e o motivo', () => {
    renderizarTabela({
      tabela: analiseNominal.frequencias,
      coluna: 'cidade',
      k: null,
      nFaltantes: 2,
    });

    expect(screen.queryByRole('group', { name: T.numeroClasses })).toBeNull();
    expect(screen.getByText(T.frAcumuladaNaoAplicavel)).toBeInTheDocument();
    expect(
      screen.getByText(exigir(analiseNominal.frequencias.motivo_acumulada, 'motivo da acumulada')),
    ).toBeInTheDocument();
    expect(screen.getByText('2 faltantes ficaram de fora.')).toBeInTheDocument();
  });
});
