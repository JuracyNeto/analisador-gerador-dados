import { screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { chamadasPara, type RotaFalsa, simularApi } from '../../../testes/api';
import {
  AVISO_EXTRAPOLACAO,
  previsaoDentro,
  previsaoExtrapolada,
} from '../../../testes/fixtures/bivariada';
import { DATASET_TESTE, renderizarComProvedores } from '../../../testes/renderizar';
import { TEXTOS_BIVARIADA } from '../textos';
import PainelPrevisao from './PainelPrevisao';

const P = TEXTOS_BIVARIADA.previsao;
const PAR = { x: 'altura_m', y: 'peso_kg' };
const CAMINHO = `/datasets/${DATASET_TESTE.id}/bivariada/prever`;

function renderizar(corpo: unknown) {
  const rota: RotaFalsa = { caminho: CAMINHO, corpo };
  const api = simularApi([rota]);
  const tela = renderizarComProvedores(<PainelPrevisao datasetId={DATASET_TESTE.id} par={PAR} />);
  return { api, ...tela };
}

describe('PainelPrevisao', () => {
  it('prevê Y para o X digitado e mostra a frase', async () => {
    const { usuario, api } = renderizar(previsaoDentro);

    await usuario.type(screen.getByRole('textbox', { name: 'altura_m' }), '1,7');
    await usuario.click(screen.getByRole('button', { name: P.prever }));

    expect(await screen.findByText('68,37')).toBeInTheDocument();
    expect(screen.getByText(P.previsto('peso_kg'))).toBeInTheDocument();
    expect(screen.getByText(previsaoDentro.frase)).toHaveAttribute('aria-live', 'polite');
    expect(chamadasPara(api, 'GET', CAMINHO)[0]?.url).toContain('valor=1.7');
    expect(screen.queryByText(P.foraTitulo)).not.toBeInTheDocument();
  });

  it('fora da faixa mostra o aviso de extrapolação', async () => {
    const { usuario } = renderizar(previsaoExtrapolada);

    await usuario.type(screen.getByRole('textbox', { name: 'altura_m' }), '2,1{Enter}');

    expect(await screen.findByText(P.foraTitulo)).toBeInTheDocument();
    expect(screen.getByText(AVISO_EXTRAPOLACAO)).toBeInTheDocument();
  });

  it('valor inválido mostra o erro no campo e não consulta a API', async () => {
    const { usuario, api } = renderizar(previsaoDentro);

    await usuario.type(screen.getByRole('textbox', { name: 'altura_m' }), 'abc');
    await usuario.click(screen.getByRole('button', { name: P.prever }));

    expect(screen.getByText(P.erroValor)).toBeInTheDocument();
    expect(chamadasPara(api, 'GET', CAMINHO)).toHaveLength(0);
  });

  it('antes de prever mostra a dica', () => {
    renderizar(previsaoDentro);

    expect(screen.getByText(P.dica)).toBeInTheDocument();
  });
});
