import { screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { chamadasPara, type FetchFalso, type RotaFalsa, simularApi } from '../../testes/api';
import {
  bivariadaAlturaPeso,
  colunasBivariada,
  EQUACAO,
  matrizExemplo,
} from '../../testes/fixtures/bivariada';
import { DATASET_TESTE, renderizarComProvedores } from '../../testes/renderizar';
import PaginaBivariada from './PaginaBivariada';
import { TEXTOS_BIVARIADA } from './textos';

vi.mock('../../shared/graficos/Grafico', () => import('../../testes/graficoFalso'));

const T = TEXTOS_BIVARIADA;
const BASE = `/datasets/${DATASET_TESTE.id}`;
const ROTA_COLUNAS: RotaFalsa = { caminho: `${BASE}/colunas`, corpo: colunasBivariada };
const ROTA_BIVARIADA: RotaFalsa = { caminho: `${BASE}/bivariada`, corpo: bivariadaAlturaPeso };
const ROTA_MATRIZ: RotaFalsa = { caminho: `${BASE}/correlacoes`, corpo: matrizExemplo };

function renderizarPagina(rota = '/bivariada?x=altura_m&y=peso_kg') {
  return renderizarComProvedores(<PaginaBivariada />, { rota, dataset: DATASET_TESTE });
}

describe('PaginaBivariada', () => {
  let api: FetchFalso;

  beforeEach(() => {
    api = simularApi([ROTA_COLUNAS, ROTA_BIVARIADA, ROTA_MATRIZ]);
  });

  it('mostra os cards, os 3 gráficos e o painel de previsão (5a)', async () => {
    renderizarPagina();

    expect(await screen.findByText(EQUACAO)).toBeInTheDocument();
    expect(screen.getByText('Correlação positiva forte')).toBeInTheDocument();
    expect(
      screen.getByRole('figure', { name: 'peso_kg em função de altura_m (n = 227)' }),
    ).toBeInTheDocument();
    expect(screen.getByRole('figure', { name: 'Resíduos da regressão' })).toBeInTheDocument();
    expect(
      await screen.findByRole('figure', { name: 'Matriz de correlação (Pearson)' }),
    ).toBeInTheDocument();
    expect(screen.getByRole('textbox', { name: 'altura_m' })).toBeInTheDocument();
  });

  it('pede a bivariada do par da URL', async () => {
    renderizarPagina('/bivariada?x=peso_kg&y=altura_m');
    await screen.findByText(EQUACAO);

    expect(chamadasPara(api, 'GET', `${BASE}/bivariada`)[0]?.url).toBe(
      `/api${BASE}/bivariada?x=peso_kg&y=altura_m`,
    );
    expect(screen.getByLabelText(T.seletores.x)).toHaveValue('peso_kg');
  });

  it('sem URL usa as duas primeiras numéricas e "Trocar X e Y" grava na URL', async () => {
    const { usuario, roteador } = renderizarPagina('/bivariada');
    await screen.findByText(EQUACAO);
    expect(chamadasPara(api, 'GET', `${BASE}/bivariada`)[0]?.url).toBe(
      `/api${BASE}/bivariada?x=idade&y=altura_m`,
    );

    await usuario.click(screen.getByRole('button', { name: T.seletores.trocar }));

    await waitFor(() => {
      expect(roteador.state.location.search).toBe('?x=altura_m&y=idade');
    });
  });

  it('com menos de duas numéricas orienta a corrigir os tipos', async () => {
    simularApi([{ ...ROTA_COLUNAS, corpo: colunasBivariada.slice(0, 2) }, ROTA_MATRIZ]);
    renderizarPagina('/bivariada');

    expect(await screen.findByText(T.vazio.titulo)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: T.vazio.acao })).toBeInTheDocument();
  });

  it('POUCOS_PARES mostra a mensagem sem "Tentar de novo"', async () => {
    simularApi([
      ROTA_COLUNAS,
      ROTA_MATRIZ,
      {
        caminho: `${BASE}/bivariada`,
        status: 400,
        corpo: {
          codigo: 'POUCOS_PARES',
          mensagem: 'Só há 2 linhas com altura_m e peso_kg preenchidas; são precisas pelo menos 3.',
          sugestao: 'Confira os faltantes na etapa Limpeza.',
        },
      },
    ]);
    renderizarPagina();

    expect(await screen.findByText(/Só há 2 linhas/)).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /Tentar de novo/ })).toBeNull();
  });

  it('erro na matriz não derruba os cards', async () => {
    simularApi([
      ROTA_COLUNAS,
      ROTA_BIVARIADA,
      {
        caminho: `${BASE}/correlacoes`,
        status: 500,
        corpo: { codigo: 'ERRO_INTERNO', mensagem: 'Algo deu errado.', sugestao: 'Tente de novo.' },
      },
    ]);
    renderizarPagina();

    expect(await screen.findByText(EQUACAO)).toBeInTheDocument();
    expect(await screen.findByText('Algo deu errado.')).toBeInTheDocument();
  });

  it('voltar para a Análise e continuar para o Relatório', async () => {
    const { usuario, roteador } = renderizarPagina();
    await screen.findByText(EQUACAO);

    expect(screen.getByRole('button', { name: T.navegacao.voltar })).toBeInTheDocument();
    await usuario.click(screen.getByRole('button', { name: T.navegacao.continuar }));
    expect(roteador.state.location.pathname).toBe('/relatorio');
  });

  it('sem arquivo importado orienta a ir para Importar', () => {
    renderizarComProvedores(<PaginaBivariada />, { rota: '/bivariada' });

    expect(screen.getByText(T.semDataset)).toBeInTheDocument();
  });
});
