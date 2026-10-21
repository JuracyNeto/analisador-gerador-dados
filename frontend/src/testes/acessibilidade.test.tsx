import { render } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { esperarSemViolacoes, violacoesAxe } from './acessibilidade';

describe('violacoesAxe', () => {
  it('acusa botão sem nome', async () => {
    const { container } = render(<button type="button" />);

    expect(await violacoesAxe(container)).toEqual([expect.stringMatching(/^button-name/u)]);
  });

  it('acusa título que pula de nível', async () => {
    const { container } = render(
      <div>
        <h1>Página</h1>
        <h3>Cartão</h3>
      </div>,
    );

    expect(await violacoesAxe(container)).toEqual([expect.stringMatching(/^heading-order/u)]);
  });

  it('aceita um trecho sem landmark nem h1 (componente isolado)', async () => {
    const { container } = render(<button type="button">Gerar dados</button>);

    await esperarSemViolacoes(container);
  });
});
