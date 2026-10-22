import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { useRef, useState } from 'react';
import { expect, it } from 'vitest';
import { useFocoNoPrimeiroErro } from './useFocoNoPrimeiroErro';

function Formulario() {
  const formulario = useRef<HTMLFormElement>(null);
  const [erro, setErro] = useState(false);
  const marcarEnvio = useFocoNoPrimeiroErro(formulario);
  return (
    <form
      ref={formulario}
      onSubmit={(evento) => {
        evento.preventDefault();
        setErro(true);
        marcarEnvio();
      }}
    >
      <input aria-label="Nome" />
      <input aria-label="Idade" aria-invalid={erro} />
      <button type="submit">Enviar</button>
    </form>
  );
}

it('depois do envio, o foco vai para o primeiro campo inválido', async () => {
  render(<Formulario />);

  await userEvent.click(screen.getByRole('button', { name: 'Enviar' }));

  expect(screen.getByRole('textbox', { name: 'Idade' })).toHaveFocus();
});

it('antes do envio, não mexe no foco', () => {
  render(<Formulario />);

  expect(document.body).toHaveFocus();
});
