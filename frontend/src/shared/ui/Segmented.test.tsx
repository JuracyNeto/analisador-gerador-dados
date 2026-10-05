import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { useState } from 'react';
import { expect, it } from 'vitest';
import Segmented from './Segmented';

type Separatriz = 'quartil' | 'decil' | 'percentil';

const OPCOES = [
  { valor: 'quartil', rotulo: 'Quartil' },
  { valor: 'decil', rotulo: 'Decil' },
  { valor: 'percentil', rotulo: 'Percentil' },
] as const;

function SegmentedControlado() {
  const [valor, setValor] = useState<Separatriz>('quartil');
  return <Segmented rotulo="Tipo de separatriz" opcoes={OPCOES} valor={valor} aoMudar={setValor} />;
}

it('é um grupo de rádios com a opção atual marcada', async () => {
  render(<SegmentedControlado />);

  expect(screen.getByRole('radiogroup', { name: 'Tipo de separatriz' })).toBeInTheDocument();
  expect(screen.getByRole('radio', { name: 'Quartil' })).toHaveAttribute('aria-checked', 'true');
  await userEvent.click(screen.getByRole('radio', { name: 'Decil' }));
  expect(screen.getByRole('radio', { name: 'Decil' })).toHaveAttribute('aria-checked', 'true');
});

it('setas mudam a opção e o foco, em círculo; só a marcada entra no Tab', async () => {
  render(<SegmentedControlado />);

  await userEvent.tab();
  expect(screen.getByRole('radio', { name: 'Quartil' })).toHaveFocus();
  await userEvent.keyboard('{ArrowLeft}');
  const percentil = screen.getByRole('radio', { name: 'Percentil' });
  expect(percentil).toHaveFocus();
  expect(percentil).toHaveAttribute('aria-checked', 'true');
  expect(screen.getByRole('radio', { name: 'Quartil' })).toHaveAttribute('tabindex', '-1');
});
