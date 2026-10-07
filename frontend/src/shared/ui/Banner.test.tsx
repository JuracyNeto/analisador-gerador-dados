import { render, screen } from '@testing-library/react';
import { expect, it } from 'vitest';
import Banner from './Banner';

it('erro é anunciado como alerta', () => {
  render(
    <Banner variante="erro" titulo="Não conseguimos ler este arquivo: relatorio_final.pdf">
      PDF não é um formato de tabela.
    </Banner>,
  );

  const alerta = screen.getByRole('alert');
  expect(alerta).toHaveTextContent('Não conseguimos ler este arquivo: relatorio_final.pdf');
  expect(alerta).toHaveTextContent('PDF não é um formato de tabela.');
});

it('info é uma nota e mostra as ações', () => {
  render(
    <Banner variante="info" acoes={<a href="#ajuda">Saiba mais</a>}>
      Média e mediana estão próximas.
    </Banner>,
  );

  expect(screen.getByRole('note')).toHaveTextContent('Média e mediana estão próximas.');
  expect(screen.getByRole('link', { name: 'Saiba mais' })).toBeInTheDocument();
});
