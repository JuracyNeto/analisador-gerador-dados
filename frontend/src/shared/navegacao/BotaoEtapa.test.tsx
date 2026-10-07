import { screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { renderizarComProvedores } from '../../testes/renderizar';
import BotaoEtapa from './BotaoEtapa';

describe('BotaoEtapa', () => {
  it('voltar é secundário, com a seta para trás, e leva à etapa anterior', async () => {
    const { usuario, roteador } = renderizarComProvedores(
      <BotaoEtapa para="/importar" sentido="voltar">
        Voltar para Importar
      </BotaoEtapa>,
      { rota: '/variaveis' },
    );
    const botao = screen.getByRole('button', { name: /Voltar para Importar/ });

    expect(botao).toHaveTextContent('arrow_back');
    await usuario.click(botao);
    expect(roteador.state.location.pathname).toBe('/importar');
  });

  it('avançar é primário, com a seta para a frente no fim', async () => {
    const { usuario, roteador } = renderizarComProvedores(
      <BotaoEtapa para="/limpeza" sentido="avancar">
        Continuar para Limpeza
      </BotaoEtapa>,
      { rota: '/variaveis' },
    );
    const botao = screen.getByRole('button', { name: /Continuar para Limpeza/ });

    expect(botao.textContent).toBe('Continuar para Limpezaarrow_forward');
    await usuario.click(botao);
    expect(roteador.state.location.pathname).toBe('/limpeza');
  });
});
