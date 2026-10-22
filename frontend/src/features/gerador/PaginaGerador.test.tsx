import { screen, waitFor, within } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { chamadasPara, type RotaFalsa, simularApi } from '../../testes/api';
import {
  colunasGerador,
  EXPLICACAO,
  geradoAltura,
  geradoPares,
  origemAltura,
  origemCidade,
  origemPar,
} from '../../testes/fixtures/gerador';
import { esperarSemViolacoes, TEMPO_AXE } from '../../testes/acessibilidade';
import { DATASET_TESTE, renderizarComProvedores } from '../../testes/renderizar';
import PaginaGerador from './PaginaGerador';
import { TEXTOS_GERADOR } from './textos';

vi.mock('../../shared/graficos/Grafico', () => import('../../testes/graficoFalso'));

const T = TEXTOS_GERADOR;
const BASE = `/datasets/${DATASET_TESTE.id}`;
const ROTAS: RotaFalsa[] = [
  { caminho: `${BASE}/colunas`, corpo: colunasGerador },
  { caminho: '/gerador/origem', corpo: origemAltura },
  { caminho: '/gerador/origem-par', corpo: origemPar },
  { metodo: 'POST', caminho: '/gerador/univariado', status: 201, corpo: geradoAltura },
  { metodo: 'POST', caminho: '/gerador/bivariado', status: 201, corpo: geradoPares },
];

function renderizarPagina(rota = '/gerador', dataset: typeof DATASET_TESTE | null = DATASET_TESTE) {
  return renderizarComProvedores(<PaginaGerador />, { rota, dataset });
}

describe('PaginaGerador', () => {
  it(
    'não tem violações de acessibilidade, no formulário e no resultado',
    async () => {
      simularApi(ROTAS);
      const { container, usuario } = renderizarPagina();
      await screen.findByText(/Mesma média/);
      await esperarSemViolacoes(container);

      await usuario.click(screen.getByRole('button', { name: T.gerar }));
      await screen.findByText(EXPLICACAO);

      await esperarSemViolacoes(container);
    },
    TEMPO_AXE,
  );

  it('abre no Univariado com a 1ª coluna e as medidas dela (6a)', async () => {
    simularApi(ROTAS);
    renderizarPagina();

    expect(
      await screen.findByText('Mesma média (1,686) e desvio (0,0931) da coluna.'),
    ).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: T.abas.univariado })).toHaveAttribute(
      'aria-selected',
      'true',
    );
    expect(screen.getByLabelText(T.coluna)).toHaveValue('altura_m');
    expect(screen.getByRole('textbox', { name: T.media })).toBeDisabled();
    expect(screen.getByRole('textbox', { name: T.media })).toHaveValue('1,686');
    expect(screen.getByText(T.limitarAjuda('1,47', '1,93'))).toBeInTheDocument();
    expect(screen.getByText(T.resultado.vazio.titulo)).toBeInTheDocument();
  });

  it('gera, mostra a comparação, o gráfico e a explicação e guarda a geração na sessão', async () => {
    const api = simularApi(ROTAS);
    const { usuario } = renderizarPagina();
    await screen.findByText(/Mesma média/);

    await usuario.type(screen.getByRole('textbox', { name: /Semente/ }), '42');
    await usuario.click(screen.getByRole('button', { name: T.gerar }));

    expect(await screen.findByText(EXPLICACAO)).toBeInTheDocument();
    expect(chamadasPara(api, 'POST', '/gerador/univariado')[0]?.corpo).toMatchObject({
      origem: { dataset_id: DATASET_TESTE.id, coluna: 'altura_m' },
      x: 500,
      modo: 'preservar',
      semente: 42,
    });
    const tabela = screen.getByRole('table', { name: T.resultado.legenda });
    expect(within(tabela).getByText('−0,224')).toBeInTheDocument();
    expect(screen.getByText('Semente 42 · preservar estatísticas')).toBeInTheDocument();
    expect(
      screen.getByRole('figure', { name: 'altura_m: original e gerado sobrepostos' }),
    ).toBeInTheDocument();
    expect(screen.getByText(T.toast.valores('500'))).toBeInTheDocument();
    expect(localStorage.getItem('sessao')).toContain('"ultimoGerado":{"id":"g-1"');
  });

  it('quantidade inválida mostra o erro e não chama a API', async () => {
    const api = simularApi(ROTAS);
    const { usuario } = renderizarPagina();
    await screen.findByText(/Mesma média/);

    const quantidade = screen.getByRole('textbox', { name: T.quantidade });
    await usuario.clear(quantidade);
    await usuario.type(quantidade, '0');
    await usuario.click(screen.getByRole('button', { name: T.gerar }));

    expect(screen.getByText(T.erros.quantidade)).toBeInTheDocument();
    expect(chamadasPara(api, 'POST', '/gerador/univariado')).toHaveLength(0);
    // O foco vai para o 1º campo com erro (o botão não diz o que corrigir).
    expect(quantidade).toHaveFocus();
  });

  it('coluna nominal só preserva: "Novos parâmetros" fica desabilitado com o motivo', async () => {
    simularApi([
      ...ROTAS.filter((rota) => rota.caminho !== '/gerador/origem'),
      { caminho: '/gerador/origem', corpo: origemCidade },
    ]);
    renderizarPagina();

    expect(await screen.findByText(T.soPreservar('qualitativas nominais'))).toBeInTheDocument();
    expect(screen.getByRole('radio', { name: T.modos.parametros })).toBeDisabled();
    expect(screen.getByText(T.descricaoPreservarCategorias)).toBeInTheDocument();
  });

  it('aba Bivariado na URL: par preenchido e só o que foi editado vai no pedido (6b)', async () => {
    const api = simularApi(ROTAS);
    const { usuario, roteador } = renderizarPagina('/gerador?aba=bivariado');

    expect(await screen.findByDisplayValue('70,17')).toBeInTheDocument();
    expect(screen.getByRole('slider', { name: T.rho })).toHaveAttribute('aria-valuetext', '0,70');
    await usuario.click(screen.getByRole('button', { name: T.gerar }));

    await screen.findByText(T.toast.pares('500'));
    expect(chamadasPara(api, 'POST', '/gerador/bivariado')[0]?.corpo).toMatchObject({
      origem: { dataset_id: DATASET_TESTE.id, x: 'altura_m', y: 'peso_kg' },
      media_x: null,
      rho: null,
      ajuste_exato: true,
    });
    await usuario.click(screen.getByRole('tab', { name: T.abas.univariado }));
    expect(roteador.state.location.search).toBe('?aba=univariado');
  });

  it('bivariado com menos de duas colunas numéricas: só parâmetros manuais, com a nota', async () => {
    const umaNumerica = colunasGerador.filter((coluna) => coluna.coluna !== 'peso_kg');
    simularApi([{ caminho: `${BASE}/colunas`, corpo: umaNumerica }, ...ROTAS.slice(1)]);

    renderizarPagina('/gerador?aba=bivariado');

    expect(await screen.findByText(T.origem.semPar)).toBeInTheDocument();
    expect(screen.queryByRole('radiogroup', { name: T.origem.rotulo })).not.toBeInTheDocument();
    expect(screen.queryByLabelText(T.y)).not.toBeInTheDocument();
    expect(screen.getByRole('textbox', { name: T.mediaDe(T.x) })).toBeEnabled();
  });

  it('sem dataset, só parâmetros manuais com o tipo', async () => {
    const api = simularApi(ROTAS);
    const { usuario } = renderizarPagina('/gerador', null);

    expect(screen.queryByRole('radiogroup', { name: T.origem.rotulo })).not.toBeInTheDocument();
    await usuario.type(screen.getByRole('textbox', { name: T.media }), '10');
    await usuario.type(screen.getByRole('textbox', { name: T.desvio }), '2');
    await usuario.click(screen.getByRole('button', { name: T.gerar }));

    await waitFor(() => {
      expect(chamadasPara(api, 'POST', '/gerador/univariado')[0]?.corpo).toMatchObject({
        origem: null,
        tipo: 'continua',
        modo: 'parametros',
        media: 10,
        desvio: 2,
      });
    });
  });

  it('voltar para a Bivariada e continuar para o Detector', async () => {
    simularApi(ROTAS);
    const { usuario, roteador } = renderizarPagina();

    expect(screen.getByRole('button', { name: 'Voltar para Bivariada' })).toBeInTheDocument();
    await usuario.click(screen.getByRole('button', { name: 'Continuar para Detector' }));
    expect(roteador.state.location.pathname).toBe('/detector');
  });
  it('geração expirada: o aviso oferece "Gerar de novo", com o mesmo pedido e a mesma semente', async () => {
    const api = simularApi([
      ...ROTAS,
      {
        metodo: 'POST',
        caminho: `/gerador/${geradoAltura.gerado_id}/adotar`,
        status: 404,
        corpo: {
          codigo: 'GERADO_NAO_ENCONTRADO',
          mensagem: 'Os dados gerados não estão mais disponíveis.',
          sugestao: 'Gere de novo na etapa Gerador.',
        },
      },
    ]);
    const { usuario } = renderizarPagina();
    await screen.findByText(/Mesma média/);
    await usuario.click(screen.getByRole('button', { name: T.gerar }));

    await usuario.click(await screen.findByRole('button', { name: T.acoes.usar }));

    const aviso = await screen.findByRole('alert');
    expect(within(aviso).getByText('Os dados gerados não estão mais disponíveis.')).toBeVisible();
    expect(within(aviso).getByText(T.expirado.descricao(geradoAltura.semente))).toBeVisible();
    expect(screen.getByText(T.resultado.vazio.titulo)).toBeInTheDocument();
    await usuario.click(within(aviso).getByRole('button', { name: T.expirado.acao }));

    await waitFor(() => {
      expect(chamadasPara(api, 'POST', '/gerador/univariado')).toHaveLength(2);
    });
    const [primeiro, segundo] = chamadasPara(api, 'POST', '/gerador/univariado');
    expect(segundo?.corpo).toEqual({ ...(primeiro?.corpo as object), semente: 42 });
  });

  it('ao voltar para a etapa, mostra a última geração da sessão na aba do tipo dela', async () => {
    simularApi([...ROTAS, { caminho: `/gerador/${geradoPares.gerado_id}`, corpo: geradoPares }]);
    const ultimoGerado = { id: geradoPares.gerado_id, descricao: 'altura_m × peso_kg · 500 pares' };

    const { usuario } = renderizarComProvedores(<PaginaGerador />, {
      rota: '/gerador?aba=bivariado',
      dataset: DATASET_TESTE,
      ultimoGerado,
    });

    expect(await screen.findByText(T.resultado.titulo)).toBeInTheDocument();
    expect(screen.getByText(EXPLICACAO)).toBeInTheDocument();
    await usuario.click(screen.getByRole('tab', { name: T.abas.univariado }));
    expect(await screen.findByText(T.resultado.vazio.titulo)).toBeInTheDocument();
  });

  it('a última geração que saiu da memória do servidor não aparece', async () => {
    simularApi([
      ...ROTAS,
      {
        caminho: `/gerador/${geradoAltura.gerado_id}`,
        status: 404,
        corpo: { codigo: 'GERADO_NAO_ENCONTRADO', mensagem: 'Sumiu.', sugestao: 'Gere de novo.' },
      },
    ]);
    const ultimoGerado = { id: geradoAltura.gerado_id, descricao: 'altura_m · 500 valores' };

    renderizarComProvedores(<PaginaGerador />, {
      rota: '/gerador',
      dataset: DATASET_TESTE,
      ultimoGerado,
    });

    await screen.findByText(/Mesma média/);
    expect(screen.getByText(T.resultado.vazio.titulo)).toBeInTheDocument();
    expect(screen.queryByRole('alert')).not.toBeInTheDocument();
  });
});
