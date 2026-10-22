import { screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { expect, it, vi } from 'vitest';
import { renderizarComRotas } from '../../testes/renderizar';
import BarraEtapas from './BarraEtapas';

function renderizarBarra(caminho: string, recolhida = false) {
  const aoAlternar = vi.fn();
  renderizarComRotas(
    [
      {
        path: '*',
        element: <BarraEtapas recolhida={recolhida} sobreposta={false} aoAlternar={aoAlternar} />,
      },
    ],
    caminho,
  );
  return { aoAlternar };
}

function salvarSessao(etapasVisitadas: number[]) {
  localStorage.setItem(
    'sessao',
    JSON.stringify({ dataset: { id: 'd1', nomeArquivo: 'pesquisa_saude.txt' }, etapasVisitadas }),
  );
}

it('sem arquivo: só Importar abre e a frase explica o bloqueio', () => {
  renderizarBarra('/importar');

  const nav = screen.getByRole('navigation', { name: 'Etapas da análise' });
  expect(within(nav).getByRole('link', { name: 'Importar' })).toHaveAttribute(
    'aria-current',
    'step',
  );
  expect(within(nav).getByRole('button', { name: 'Variáveis Bloqueada' })).toHaveAttribute(
    'aria-disabled',
    'true',
  );
  expect(within(nav).getAllByRole('img', { name: 'Bloqueada' })).toHaveLength(7);
  expect(
    screen.getByText('As etapas 2 a 8 ficam disponíveis depois de importar um arquivo.'),
  ).toBeInTheDocument();
});

it('com arquivo: visitadas aparecem concluídas e a atual fica marcada', () => {
  salvarSessao([1, 2]);

  renderizarBarra('/limpeza');

  expect(screen.getByRole('link', { name: 'Importar Concluída' })).toBeInTheDocument();
  expect(screen.getByRole('link', { name: 'Variáveis Concluída' })).toBeInTheDocument();
  expect(screen.getByRole('link', { name: 'Limpeza' })).toHaveAttribute('aria-current', 'step');
  expect(screen.getByRole('link', { name: 'Análise univariada' })).not.toHaveAttribute(
    'aria-current',
  );
  expect(screen.queryByText(/ficam disponíveis depois/)).not.toBeInTheDocument();
});

it('com arquivo, Gerador e Detector abrem como as demais etapas', () => {
  salvarSessao([1]);
  renderizarBarra('/importar');

  expect(screen.getByRole('link', { name: 'Gerador' })).toBeInTheDocument();
  expect(screen.getByRole('link', { name: 'Detector' })).toBeInTheDocument();
  expect(screen.queryByRole('button', { name: /Bloqueada/ })).not.toBeInTheDocument();
});

it('recolhida: nomes seguem acessíveis e o botão pede para expandir', async () => {
  const { aoAlternar } = renderizarBarra('/importar', true);

  expect(screen.getByRole('link', { name: 'Importar' })).toBeInTheDocument();
  expect(screen.queryByText(/ficam disponíveis depois/)).not.toBeInTheDocument();
  await userEvent.click(screen.getByRole('button', { name: 'Expandir barra' }));
  expect(aoAlternar).toHaveBeenCalledOnce();
});
