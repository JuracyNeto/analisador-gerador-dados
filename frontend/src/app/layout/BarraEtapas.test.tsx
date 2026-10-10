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
    screen.getByText('As etapas 2 a 8 ficam disponíveis depois que você importar um arquivo.'),
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

it('etapas futuras ficam bloqueadas mesmo com arquivo e dizem a versão', async () => {
  salvarSessao([1]);
  renderizarBarra('/importar');

  const gerador = screen.getByRole('button', { name: 'Gerador Bloqueada' });
  await userEvent.hover(gerador);

  expect(gerador).toHaveAttribute('aria-disabled', 'true');
  expect(screen.getByRole('tooltip')).toHaveTextContent('Disponível na versão v0.3.');
  expect(screen.getByRole('link', { name: 'Bivariada' })).toBeInTheDocument();
});

it('recolhida: nomes seguem acessíveis e o botão pede para expandir', async () => {
  const { aoAlternar } = renderizarBarra('/importar', true);

  expect(screen.getByRole('link', { name: 'Importar' })).toBeInTheDocument();
  expect(screen.queryByText(/ficam disponíveis depois/)).not.toBeInTheDocument();
  await userEvent.click(screen.getByRole('button', { name: 'Expandir barra' }));
  expect(aoAlternar).toHaveBeenCalledOnce();
});
