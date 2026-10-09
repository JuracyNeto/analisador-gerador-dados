import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it } from 'vitest';
import { FRASE_CONJUNTA, MOTIVO_BINOMIAL_CONTINUA } from '../../../testes/fixtures/forma';
import {
  analiseBinaria,
  analiseContinua,
  analiseDiscreta,
  propsPainel,
} from '../../../testes/fixturesAnalise';
import { renderizarComProvedores } from '../../../testes/renderizar';
import { TEXTOS_ANALISE } from '../textos';
import AbaForma from './AbaForma';

const F = TEXTOS_ANALISE.forma;

describe('AbaForma', () => {
  it('contínua: 4 cards, nota, frase conjunta e os 2 gráficos (print 4e)', () => {
    renderizarComProvedores(<AbaForma {...propsPainel(analiseContinua)} />);

    for (const rotulo of [F.assimetria, F.curtose, F.ajusteNormal, F.ajusteBinomial]) {
      expect(screen.getByText(rotulo)).toBeInTheDocument();
    }
    expect(screen.getByText('Compatível com a Normal')).toBeInTheDocument();
    expect(screen.getByText(MOTIVO_BINOMIAL_CONTINUA)).toBeInTheDocument();
    expect(screen.getByText(/Coeficientes de Pearson/)).toBeInTheDocument();
    expect(screen.getByText(FRASE_CONJUNTA)).toBeInTheDocument();
    expect(
      screen.getByText('Histograma de peso_kg com curva Normal (n = 227)'),
    ).toBeInTheDocument();
    expect(screen.getByText('QQ-plot de peso_kg contra a Normal')).toBeInTheDocument();
    expect(screen.queryByRole('textbox', { name: F.tentativas.rotulo })).not.toBeInTheDocument();
  });

  it('discreta: campo de tentativas com o n usado; aplicar avisa a página', async () => {
    const usuario = userEvent.setup();
    const props = propsPainel(analiseDiscreta);
    renderizarComProvedores(<AbaForma {...props} />);

    const campo = screen.getByRole('textbox', { name: F.tentativas.rotulo });
    expect(campo).toHaveValue('8');
    await usuario.clear(campo);
    await usuario.type(campo, '10{Enter}');

    expect(props.aoMudarTentativas).toHaveBeenCalledWith(10);
    expect(screen.getByText('Compatível com a Binomial')).toBeInTheDocument();
  });

  it('binária: card Bernoulli e nenhum gráfico', () => {
    renderizarComProvedores(<AbaForma {...propsPainel(analiseBinaria)} />);

    expect(screen.getByText(F.ajusteBernoulli)).toBeInTheDocument();
    expect(screen.queryByRole('region', { name: F.tituloGraficos })).not.toBeInTheDocument();
    expect(screen.queryByRole('textbox')).not.toBeInTheDocument();
  });
});
