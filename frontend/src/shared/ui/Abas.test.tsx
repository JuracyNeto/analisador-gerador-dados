import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { useState } from 'react';
import { expect, it } from 'vitest';
import { esperarSemViolacoes } from '../../testes/acessibilidade';
import Abas from './Abas';

const ABAS = [
  { id: 'frequencias', rotulo: 'Frequências' },
  { id: 'tendencia', rotulo: 'Tendência central' },
  {
    id: 'separatrizes',
    rotulo: 'Separatrizes',
    desabilitada: true,
    motivo: 'Separatrizes não se aplicam a Qualitativa nominal: as categorias não têm ordem.',
  },
  { id: 'dispersao', rotulo: 'Dispersão' },
] as const;

type IdAba = (typeof ABAS)[number]['id'];

function AbasControladas() {
  const [ativa, setAtiva] = useState<IdAba>('frequencias');
  return (
    <Abas rotulo="Análises da coluna" abas={ABAS} ativa={ativa} aoMudar={setAtiva}>
      <p>Conteúdo de {ativa}</p>
    </Abas>
  );
}

it('liga a aba ativa ao painel', async () => {
  render(<AbasControladas />);

  expect(screen.getByRole('tablist', { name: 'Análises da coluna' })).toBeInTheDocument();
  expect(screen.getByRole('tab', { name: 'Frequências' })).toHaveAttribute('aria-selected', 'true');
  expect(screen.getByRole('tabpanel', { name: 'Frequências' })).toHaveTextContent(
    'Conteúdo de frequencias',
  );
  await userEvent.click(screen.getByRole('tab', { name: 'Tendência central' }));
  expect(screen.getByRole('tabpanel', { name: 'Tendência central' })).toHaveTextContent(
    'Conteúdo de tendencia',
  );
});

it('setas passam pela aba desabilitada sem selecioná-la', async () => {
  render(<AbasControladas />);
  await userEvent.click(screen.getByRole('tab', { name: 'Tendência central' }));

  await userEvent.keyboard('{ArrowRight}');
  expect(screen.getByRole('tab', { name: 'Separatrizes' })).toHaveFocus();
  expect(screen.getByRole('tab', { name: 'Tendência central' })).toHaveAttribute(
    'aria-selected',
    'true',
  );

  await userEvent.keyboard('{ArrowRight}');
  expect(screen.getByRole('tab', { name: 'Dispersão' })).toHaveAttribute('aria-selected', 'true');

  await userEvent.keyboard('{Home}');
  expect(screen.getByRole('tab', { name: 'Frequências' })).toHaveAttribute('aria-selected', 'true');
});

it('aba desabilitada não abre e explica o motivo no tooltip', async () => {
  const { container } = render(<AbasControladas />);
  const desabilitada = screen.getByRole('tab', { name: 'Separatrizes' });

  await userEvent.click(desabilitada);
  await userEvent.hover(desabilitada);

  expect(desabilitada).toHaveAttribute('aria-disabled', 'true');
  expect(screen.getByRole('tab', { name: 'Frequências' })).toHaveAttribute('aria-selected', 'true');
  expect(screen.getByRole('tooltip', { hidden: true })).toBeVisible();
  expect(desabilitada).toHaveAccessibleDescription(/as categorias não têm ordem\.$/u);
  // Com o balão aberto, a lista de abas continua só com abas (aria-required-children).
  await esperarSemViolacoes(container);
});
