import { render, screen } from '@testing-library/react';
import { expect, it } from 'vitest';
import Botao from './Botao';
import EstadoVazio from './EstadoVazio';

it('mostra título, próximo passo e ação', () => {
  render(
    <EstadoVazio
      icone="upload_file"
      titulo="Nenhum arquivo importado"
      descricao="Importe um arquivo para ver as variáveis."
      acao={<Botao>Importar arquivo</Botao>}
    />,
  );

  expect(screen.getByRole('heading', { name: 'Nenhum arquivo importado' })).toBeInTheDocument();
  expect(screen.getByText('Importe um arquivo para ver as variáveis.')).toBeInTheDocument();
  expect(screen.getByRole('button', { name: 'Importar arquivo' })).toBeInTheDocument();
});
