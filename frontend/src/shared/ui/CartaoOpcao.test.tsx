import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { useState } from 'react';
import { describe, expect, it } from 'vitest';
import CampoNumero from './CampoNumero';
import CartaoOpcao from './CartaoOpcao';

function Grupo({ desabilitarSegundo = false }: Readonly<{ desabilitarSegundo?: boolean }>) {
  const [modo, setModo] = useState<'a' | 'b'>('a');
  return (
    <fieldset>
      <legend>Modo</legend>
      <CartaoOpcao
        nome="modo"
        titulo="Preservar"
        descricao="Mesma média."
        selecionado={modo === 'a'}
        aoSelecionar={() => {
          setModo('a');
        }}
      />
      <CartaoOpcao
        nome="modo"
        titulo="Novos"
        selecionado={modo === 'b'}
        aoSelecionar={() => {
          setModo('b');
        }}
        desabilitado={desabilitarSegundo}
      >
        <CampoNumero
          rotulo="Média"
          valor="1"
          aoMudar={() => undefined}
          desabilitado={modo !== 'b'}
        />
      </CartaoOpcao>
    </fieldset>
  );
}

describe('CartaoOpcao', () => {
  it('é um rádio de verdade, com descrição e campos que acompanham a seleção', async () => {
    render(<Grupo />);
    const preservar = screen.getByRole('radio', { name: 'Preservar' });

    expect(preservar).toBeChecked();
    expect(preservar).toHaveAccessibleDescription('Mesma média.');
    expect(screen.getByRole('textbox', { name: 'Média' })).toBeDisabled();

    await userEvent.click(screen.getByRole('radio', { name: 'Novos' }));

    expect(screen.getByRole('radio', { name: 'Novos' })).toBeChecked();
    expect(screen.getByRole('textbox', { name: 'Média' })).toBeEnabled();
  });

  it('setas do teclado trocam a opção, como num grupo de rádios', async () => {
    render(<Grupo />);
    screen.getByRole('radio', { name: 'Preservar' }).focus();

    await userEvent.keyboard('{ArrowDown}');

    expect(screen.getByRole('radio', { name: 'Novos' })).toBeChecked();
  });

  it('desabilitado não deixa escolher', () => {
    render(<Grupo desabilitarSegundo />);

    expect(screen.getByRole('radio', { name: 'Novos' })).toBeDisabled();
  });
});
