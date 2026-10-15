import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { useState } from 'react';
import { describe, expect, it } from 'vitest';
import Drawer from './Drawer';

function Tela() {
  const [aberto, setAberto] = useState(false);
  return (
    <>
      <button
        type="button"
        onClick={() => {
          setAberto(true);
        }}
      >
        Ver na tabela
      </button>
      <Drawer
        aberto={aberto}
        aoFechar={() => {
          setAberto(false);
        }}
        titulo="Linhas 120 a 138"
        subtitulo="19 linhas destacadas."
        rotuloCorpo="Linhas do alerta"
        rodape={<button type="button">Exportar estas linhas</button>}
      >
        <p>tabela</p>
      </Drawer>
    </>
  );
}

async function abrir() {
  const usuario = userEvent.setup();
  render(<Tela />);
  await usuario.click(screen.getByRole('button', { name: 'Ver na tabela' }));
  return usuario;
}

describe('Drawer', () => {
  it('abre como diálogo nomeado pelo título, com o foco no botão Fechar', async () => {
    await abrir();

    const dialogo = screen.getByRole('dialog', { name: 'Linhas 120 a 138' });
    expect(dialogo).toHaveAttribute('aria-modal', 'true');
    expect(screen.getByText('19 linhas destacadas.')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Fechar' })).toHaveFocus();
  });

  it('Tab fica preso dentro do drawer', async () => {
    const usuario = await abrir();

    await usuario.tab();
    expect(screen.getByRole('region', { name: 'Linhas do alerta' })).toHaveFocus();
    await usuario.tab();
    expect(screen.getByRole('button', { name: 'Exportar estas linhas' })).toHaveFocus();
    await usuario.tab();
    expect(screen.getByRole('button', { name: 'Fechar' })).toHaveFocus();
    await usuario.tab({ shift: true });
    expect(screen.getByRole('button', { name: 'Exportar estas linhas' })).toHaveFocus();
  });

  it('Esc fecha e devolve o foco a quem abriu', async () => {
    const usuario = await abrir();

    await usuario.keyboard('{Escape}');

    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Ver na tabela' })).toHaveFocus();
  });

  it('o botão Fechar e o clique fora fecham', async () => {
    const usuario = await abrir();
    await usuario.click(screen.getByRole('button', { name: 'Fechar' }));
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();

    await usuario.click(screen.getByRole('button', { name: 'Ver na tabela' }));
    await usuario.click(screen.getByTestId('fundo-drawer'));
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
  });
});
