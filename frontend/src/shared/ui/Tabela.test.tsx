import { render, screen, within } from '@testing-library/react';
import { expect, it } from 'vitest';
import Tabela, { type ColunaTabela } from './Tabela';

interface Linha {
  classe: string;
  fi: number;
}

const COLUNAS: readonly ColunaTabela<Linha>[] = [
  {
    id: 'classe',
    titulo: 'Classe (kg)',
    celula: (linha) => linha.classe,
    mono: true,
    cabecalhoLinha: true,
  },
  { id: 'fi', titulo: 'fi', celula: (linha) => linha.fi, alinhamento: 'direita' },
];

const LINHAS: readonly Linha[] = [
  { classe: '60,0 ⊢ 65,5', fi: 12 },
  { classe: '65,5 ⊢ 71,0', fi: 30 },
];

it('monta a tabela com legenda, cabeçalhos com scope e linha destacada', () => {
  render(
    <Tabela
      legenda="Frequências de peso_kg"
      colunas={COLUNAS}
      linhas={LINHAS}
      chave={(linha) => linha.classe}
      destacada={(linha) => linha.fi === 30}
      rodape="Total: 42"
    />,
  );

  const tabela = screen.getByRole('table', { name: 'Frequências de peso_kg' });
  expect(within(tabela).getByRole('columnheader', { name: 'Classe (kg)' })).toHaveAttribute(
    'scope',
    'col',
  );
  expect(within(tabela).getByRole('rowheader', { name: '65,5 ⊢ 71,0' })).toHaveAttribute(
    'scope',
    'row',
  );
  expect(within(tabela).getByRole('cell', { name: '30' })).toBeInTheDocument();
  const linhas = within(tabela).getAllByRole('row');
  expect(linhas[2]).toHaveAttribute('data-destacada', 'true');
  expect(linhas[1]).not.toHaveAttribute('data-destacada');
  expect(screen.getByText('Total: 42')).toBeInTheDocument();
});

it('com altura máxima a rolagem vira região focável', () => {
  render(
    <Tabela
      legenda="Prévia"
      colunas={COLUNAS}
      linhas={LINHAS}
      chave={(linha) => linha.classe}
      alturaMaxima={520}
    />,
  );

  expect(screen.getByRole('region', { name: 'Prévia' })).toHaveAttribute('tabindex', '0');
});
