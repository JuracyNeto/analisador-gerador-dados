import { screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it } from 'vitest';
import { formatarNumero } from '../../../shared/lib/formatar';
import { chamadasPara, type FetchFalso, simularApi } from '../../../testes/api';
import { ID_DATASET } from '../../../testes/fixtures/datasets';
import {
  analiseContinua,
  posicaoAcima,
  posicaoQuartil,
  propsPainel,
} from '../../../testes/fixturesAnalise';
import { renderizarComProvedores } from '../../../testes/renderizar';
import { TEXTOS_ANALISE } from '../textos';
import type { Posicao } from '../tipos';
import AbaSeparatrizes from './AbaSeparatrizes';

const P = TEXTOS_ANALISE.posicao;
const CAMINHO_POSICAO = `/datasets/${ID_DATASET}/colunas/peso_kg/posicao`;
const URL_POSICAO = `/api${CAMINHO_POSICAO}`;

function responderPosicao(posicao: Posicao) {
  return simularApi([{ caminho: CAMINHO_POSICAO, corpo: posicao }]);
}

function urlsChamadas(api: FetchFalso): string[] {
  return chamadasPara(api, 'GET', CAMINHO_POSICAO).map((chamada) => chamada.url);
}

async function digitarValor(texto: string) {
  const user = userEvent.setup();
  renderizarComProvedores(<AbaSeparatrizes {...propsPainel(analiseContinua)} />);
  await user.type(screen.getByLabelText('Valor de peso_kg'), texto);
  return user;
}

describe('AbaSeparatrizes', () => {
  it('mostra quartis, decis e os 9 percentis em destaque, com os 99 recolhidos', () => {
    responderPosicao(posicaoQuartil);
    renderizarComProvedores(<AbaSeparatrizes {...propsPainel(analiseContinua)} />);

    expect(
      within(screen.getByRole('region', { name: 'Quartis' })).getAllByRole('term'),
    ).toHaveLength(3);
    expect(within(screen.getByRole('region', { name: 'Decis' })).getAllByRole('term')).toHaveLength(
      9,
    );
    expect(
      within(screen.getByRole('region', { name: 'Percentis' })).getAllByRole('term'),
    ).toHaveLength(9);
    expect(screen.getByText(TEXTOS_ANALISE.separatrizes.verTodos)).toBeInTheDocument();
  });

  it('consulta a posição depois da pausa na digitação e destaca a separatriz', async () => {
    const api = responderPosicao(posicaoQuartil);
    await digitarValor('75');

    expect(await screen.findByText(posicaoQuartil.frase)).toBeInTheDocument();
    expect(urlsChamadas(api)).toEqual([`${URL_POSICAO}?valor=75&tipo=quartil`]);
    const q3 = within(screen.getByRole('region', { name: 'Quartis' })).getByText(
      'Q3',
    ).parentElement;
    expect(q3).toHaveAttribute('data-destaque', 'true');
    expect(screen.getByRole('img', { name: /fica no 3º quartil/ })).toBeInTheDocument();
  });

  it('trocar para Decil refaz a consulta com o novo tipo', async () => {
    const api = responderPosicao(posicaoQuartil);
    const user = await digitarValor('75');
    await screen.findByText(posicaoQuartil.frase);

    await user.click(screen.getByRole('radio', { name: 'Decil' }));

    await waitFor(() => {
      expect(urlsChamadas(api)).toContain(`${URL_POSICAO}?valor=75&tipo=decil`);
    });
  });

  it('texto que não é número mostra o erro do campo e não chama a API', async () => {
    const api = responderPosicao(posicaoQuartil);
    await digitarValor('abc');

    expect(screen.getByText(P.erroValor)).toBeInTheDocument();
    expect(urlsChamadas(api)).toEqual([]);
  });

  it('valor acima do maior dado mostra o aviso de fora da faixa', async () => {
    responderPosicao(posicaoAcima);
    await digitarValor('120');

    expect(await screen.findByText(P.foraTitulo)).toBeInTheDocument();
    expect(screen.getByText(P.acima(formatarNumero(92.9)))).toBeInTheDocument();
  });

  it('sem "posicao" aplicável (ordinal), o painel não aparece', () => {
    const ordinal = {
      ...analiseContinua,
      aplicavel: { ...analiseContinua.aplicavel, posicao: false },
    };
    renderizarComProvedores(<AbaSeparatrizes {...propsPainel(ordinal)} />);

    expect(screen.queryByText(P.titulo)).toBeNull();
  });
});
