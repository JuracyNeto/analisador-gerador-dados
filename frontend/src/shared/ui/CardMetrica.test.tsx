import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { expect, it } from 'vitest';
import CardMetrica from './CardMetrica';

it('mostra rótulo, valor com unidade, selo e interpretação', () => {
  render(
    <CardMetrica
      rotulo="Coeficiente de variação"
      valor="14,2"
      unidade="%"
      selo="Variação moderada"
      interpretacao="Os pesos variam cerca de 14% em torno da média."
    />,
  );

  const card = screen.getByRole('article');
  expect(screen.getByRole('heading', { name: 'Coeficiente de variação' })).toBeInTheDocument();
  expect(card).toHaveTextContent('14,2%');
  expect(card).toHaveTextContent('Variação moderada');
  expect(card).toHaveTextContent('Os pesos variam cerca de 14% em torno da média.');
});

it('abre e fecha a fórmula', async () => {
  render(
    <CardMetrica
      rotulo="Média"
      valor="70,3"
      unidade="kg"
      formula={{ expressao: 'x̄ = Σxᵢ / n', calculo: '16.150,1 / 227 = 70,3' }}
    />,
  );

  await userEvent.click(screen.getByRole('button', { name: 'Ver fórmula' }));
  expect(screen.getByRole('button', { name: 'Ocultar fórmula' })).toHaveAttribute(
    'aria-expanded',
    'true',
  );
  expect(screen.getByText('x̄ = Σxᵢ / n')).toBeVisible();
  expect(screen.getByText('16.150,1 / 227 = 70,3')).toBeVisible();

  await userEvent.click(screen.getByRole('button', { name: 'Ocultar fórmula' }));
  expect(screen.getByText('x̄ = Σxᵢ / n')).not.toBeVisible();
});

it('não aplicável fica esmaecido com motivo e sem fórmula', () => {
  render(
    <CardMetrica
      rotulo="Média"
      valor="70,3"
      formula={{ expressao: 'x̄ = Σxᵢ / n' }}
      naoAplicavel={{
        motivo: 'Média não se aplica a Qualitativa nominal: as categorias não são números.',
      }}
    />,
  );

  const card = screen.getByRole('article');
  expect(card).toHaveTextContent('Não se aplica');
  expect(card).toHaveTextContent('as categorias não são números.');
  expect(card).not.toHaveTextContent('70,3');
  expect(screen.queryByRole('button', { name: 'Ver fórmula' })).not.toBeInTheDocument();
});

it('valor menor para textos longos (equação da reta)', () => {
  render(<CardMetrica rotulo="Reta de regressão" valor="Ŷ = −74,87 + 86·X" tamanhoValor="menor" />);

  expect(screen.getByText('Ŷ = −74,87 + 86·X')).toHaveAttribute('data-tamanho', 'menor');
});
