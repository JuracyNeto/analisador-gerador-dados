import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { expect, it, vi } from 'vitest';
import Botao from './Botao';

it('é um botão type="button" e o ícone não entra no nome', async () => {
  const aoClicar = vi.fn();
  render(
    <Botao iconeFinal="arrow_forward" onClick={aoClicar}>
      Continuar para Variáveis
    </Botao>,
  );

  const botao = screen.getByRole('button', { name: 'Continuar para Variáveis' });
  expect(botao).toHaveAttribute('type', 'button');
  await userEvent.click(botao);
  expect(aoClicar).toHaveBeenCalledOnce();
});

it('aceita type submit', () => {
  render(<Botao type="submit">Enviar</Botao>);

  expect(screen.getByRole('button', { name: 'Enviar' })).toHaveAttribute('type', 'submit');
});

it('carregando: desabilita, marca aria-busy e mostra o verbo no gerúndio', async () => {
  const aoClicar = vi.fn();
  render(
    <Botao carregando textoCarregando="Calculando…" onClick={aoClicar}>
      Calcular
    </Botao>,
  );

  const botao = screen.getByRole('button', { name: 'Calculando…' });
  expect(botao).toBeDisabled();
  expect(botao).toHaveAttribute('aria-busy', 'true');
  await userEvent.click(botao);
  expect(aoClicar).not.toHaveBeenCalled();
});
