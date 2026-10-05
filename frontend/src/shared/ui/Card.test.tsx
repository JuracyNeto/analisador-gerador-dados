import { render, screen } from '@testing-library/react';
import { expect, it } from 'vitest';
import Botao from './Botao';
import Card from './Card';

it('mostra título como h2, subtítulo e ações', () => {
  render(
    <Card
      titulo="Prévia"
      subtitulo="20 primeiras linhas de 230"
      acoes={<Botao variante="secundario">Ler de novo</Botao>}
    >
      <p>conteúdo</p>
    </Card>,
  );

  expect(screen.getByRole('heading', { level: 2, name: 'Prévia' })).toBeInTheDocument();
  expect(screen.getByText('20 primeiras linhas de 230')).toBeInTheDocument();
  expect(screen.getByRole('button', { name: 'Ler de novo' })).toBeInTheDocument();
  expect(screen.getByText('conteúdo')).toBeInTheDocument();
});

it('sem título não cria cabeçalho', () => {
  render(
    <Card>
      <p>só conteúdo</p>
    </Card>,
  );

  expect(screen.queryByRole('heading')).not.toBeInTheDocument();
});
