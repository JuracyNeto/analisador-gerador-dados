import { screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { chamadasPara, type FetchFalso, type RotaFalsa, simularApi } from '../../testes/api';
import { analiseContinua, analiseNominal, colunasPesquisa } from '../../testes/fixturesAnalise';
import { DATASET_TESTE, renderizarComProvedores } from '../../testes/renderizar';
import PaginaAnalise from './PaginaAnalise';
import { TEXTOS_ANALISE } from './textos';

vi.mock('../../shared/graficos/Grafico', () => import('../../testes/graficoFalso'));

const BASE = `/datasets/${DATASET_TESTE.id}`;
const ROTA_COLUNAS: RotaFalsa = { caminho: `${BASE}/colunas`, corpo: colunasPesquisa };
const ROTAS_PADRAO: RotaFalsa[] = [
  ROTA_COLUNAS,
  { caminho: `${BASE}/colunas/peso_kg/analise`, corpo: analiseContinua },
  { caminho: `${BASE}/colunas/cidade/analise`, corpo: analiseNominal },
];

/** Sessão real com o dataset de teste (entra depois da 1ª renderização: começar com findBy…). */
function renderizarPagina(rota = '/analise?coluna=peso_kg') {
  return renderizarComProvedores(<PaginaAnalise />, { rota, dataset: DATASET_TESTE });
}

describe('PaginaAnalise', () => {
  let api: FetchFalso;

  beforeEach(() => {
    api = simularApi(ROTAS_PADRAO);
  });

  it('mostra "Calculando…" e depois a tabela da coluna da URL', async () => {
    renderizarPagina();

    expect(await screen.findByText(TEXTOS_ANALISE.calculando('peso_kg'))).toBeInTheDocument();
    expect(await screen.findByText('60,0 ⊢ 76,5')).toBeInTheDocument();
    expect(screen.getByLabelText('Coluna')).toHaveValue('peso_kg');
  });

  it('o seletor lista só colunas analisáveis e escreve a escolha na URL', async () => {
    const { usuario, roteador } = renderizarPagina();
    await screen.findByText('60,0 ⊢ 76,5');

    expect(screen.queryByRole('option', { name: 'id' })).toBeNull();
    await usuario.selectOptions(screen.getByLabelText('Coluna'), 'cidade');

    await waitFor(() => {
      expect(roteador.state.location.search).toBe('?coluna=cidade');
    });
    expect(await screen.findByRole('tab', { name: /Separatrizes/ })).toHaveAttribute(
      'aria-disabled',
      'true',
    );
  });

  it('mudar o número de classes pede de novo sem tirar a tabela da tela', async () => {
    const { usuario } = renderizarPagina();
    await screen.findByText('60,0 ⊢ 76,5');

    await usuario.click(screen.getByRole('button', { name: TEXTOS_ANALISE.frequencias.mais }));

    await waitFor(() => {
      expect(
        chamadasPara(api, 'GET', `${BASE}/colunas/peso_kg/analise`).map((c) => c.url),
      ).toContain(`/api${BASE}/colunas/peso_kg/analise?classes=4`);
    });
    expect(screen.getByText('60,0 ⊢ 76,5')).toBeInTheDocument();
  });

  it('COLUNA_VAZIA mostra a mensagem da API sem "Tentar de novo"', async () => {
    simularApi([
      ROTA_COLUNAS,
      {
        caminho: `${BASE}/colunas/peso_kg/analise`,
        status: 400,
        corpo: {
          codigo: 'COLUNA_VAZIA',
          mensagem: 'A coluna peso_kg não tem valores para analisar.',
          sugestao: 'Escolha outra coluna.',
        },
      },
    ]);
    renderizarPagina();

    expect(
      await screen.findByText('A coluna peso_kg não tem valores para analisar.'),
    ).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /Tentar de novo/ })).toBeNull();
  });

  it('sem colunas analisáveis orienta a corrigir os tipos', async () => {
    simularApi([{ ...ROTA_COLUNAS, corpo: colunasPesquisa.slice(0, 1) }]);
    renderizarPagina('/analise');

    expect(await screen.findByText(TEXTOS_ANALISE.semColunas.titulo)).toBeInTheDocument();
  });

  it('sem arquivo importado orienta a ir para Importar', () => {
    renderizarComProvedores(<PaginaAnalise />, { rota: '/analise' });

    expect(screen.getByText(TEXTOS_ANALISE.semDataset)).toBeInTheDocument();
  });

  it('voltar para Limpeza e continuar para Relatório no fim da tela', async () => {
    const { usuario, roteador } = renderizarPagina();
    await screen.findByText('60,0 ⊢ 76,5');

    expect(screen.getByRole('button', { name: /Voltar para Limpeza/ })).toBeInTheDocument();
    await usuario.click(screen.getByRole('button', { name: /Continuar para Relatório/ }));
    expect(roteador.state.location.pathname).toBe('/relatorio');
  });
});
