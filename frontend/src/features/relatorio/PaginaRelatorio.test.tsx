import { fireEvent, screen, waitFor, within } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { chamadasPara, type FetchFalso, simularApi } from '../../testes/api';
import { simularDownload } from '../../testes/downloadFalso';
import { exigir } from '../../testes/exigir';
import { colunasPesquisa } from '../../testes/fixturesAnalise';
import { DATASET_TESTE, renderizarComProvedores } from '../../testes/renderizar';
import PaginaRelatorio from './PaginaRelatorio';
import { TEXTOS_RELATORIO } from './textos';

const T = TEXTOS_RELATORIO;
const BASE = `/datasets/${DATASET_TESTE.id}`;

function previa(): HTMLIFrameElement {
  return screen.getByTitle(T.tituloPrevia);
}

const GERADO = { id: 'g-1', descricao: 'peso_kg · 500 valores' };

/** Sessão real com o dataset de teste (entra depois da 1ª renderização: começar com findBy…). */
function renderizarPagina(ultimoGerado: typeof GERADO | null = null) {
  return renderizarComProvedores(<PaginaRelatorio />, { dataset: DATASET_TESTE, ultimoGerado });
}

describe('PaginaRelatorio', () => {
  let api: FetchFalso;

  beforeEach(() => {
    // O corpo do relatório não importa nos testes (o jsdom não carrega o iframe).
    api = simularApi([
      { caminho: `${BASE}/colunas`, corpo: colunasPesquisa },
      { caminho: `${BASE}/relatorio`, corpo: '<html></html>' },
    ]);
  });

  it('sem geração, começa com 7 de 8 seções e a caixa Gerador desabilitada', async () => {
    renderizarPagina();

    const secoes = await screen.findByRole('group', { name: /^Seções/ });
    expect(within(secoes).getAllByRole('checkbox')).toHaveLength(8);
    expect(within(secoes).getAllByRole('checkbox', { checked: true })).toHaveLength(7);
    expect(within(secoes).getByText('7 de 8')).toBeInTheDocument();
    const gerador = within(secoes).getByRole('checkbox', { name: T.rotulosSecoes.gerador });
    expect(gerador).toBeDisabled();
    expect(gerador).not.toBeChecked();
    expect(within(secoes).getByText(T.semGeracao)).toBeInTheDocument();
    const colunas = await screen.findByRole('group', { name: /^Colunas/ });
    expect(within(colunas).getAllByRole('checkbox', { checked: true })).toHaveLength(3);
    expect(within(colunas).queryByText('id')).toBeNull();
  });

  it('a prévia usa a seleção e sempre funciona offline', async () => {
    renderizarPagina();

    await waitFor(() => {
      expect(previa().getAttribute('src')).toBe(
        `/api${BASE}/relatorio?secoes=leitura&secoes=tipos&secoes=limpeza&secoes=analises&secoes=distribuicoes&secoes=bivariada&secoes=detector&colunas=sexo&colunas=peso_kg&colunas=cidade&offline=true`,
      );
    });
  });

  it('com geração na sessão, as 8 seções começam marcadas e a prévia leva a geração', async () => {
    renderizarPagina(GERADO);

    const secoes = await screen.findByRole('group', { name: /^Seções/ });
    await waitFor(() => {
      expect(within(secoes).getByText('8 de 8')).toBeInTheDocument();
    });
    expect(within(secoes).getByRole('checkbox', { name: T.rotulosSecoes.gerador })).toBeEnabled();
    expect(within(secoes).queryByText(T.semGeracao)).toBeNull();
    await waitFor(() => {
      expect(previa().getAttribute('src')).toContain('&secoes=gerador&secoes=detector&');
    });
    expect(previa().getAttribute('src')).toContain('&gerado=g-1&offline=true');
  });

  it('desmarcar Gerador tira a geração do pedido', async () => {
    const { usuario } = renderizarPagina(GERADO);
    const gerador = await screen.findByRole('checkbox', { name: T.rotulosSecoes.gerador });
    await waitFor(() => {
      expect(gerador).toBeEnabled();
    });

    await usuario.click(gerador);

    await waitFor(() => {
      expect(previa().getAttribute('src')).not.toContain('gerado=');
    });
    expect(previa().getAttribute('src')).not.toContain('secoes=gerador');
  });

  it('desmarcar uma coluna atualiza a prévia depois da pausa', async () => {
    const { usuario } = renderizarPagina();
    await usuario.click(await screen.findByRole('checkbox', { name: /peso_kg/ }));

    await waitFor(() => {
      expect(previa().getAttribute('src')).not.toContain('peso_kg');
    });
  });

  it('sem "Análises por coluna" e sem "Distribuições", as colunas ficam desabilitadas', async () => {
    const { usuario } = renderizarPagina();
    await screen.findByRole('checkbox', { name: /peso_kg/ });

    await usuario.click(screen.getByRole('checkbox', { name: T.rotulosSecoes.analises }));
    expect(screen.getByRole('checkbox', { name: /peso_kg/ })).toBeEnabled();
    await usuario.click(screen.getByRole('checkbox', { name: T.rotulosSecoes.distribuicoes }));

    expect(screen.getByRole('checkbox', { name: /peso_kg/ })).toBeDisabled();
    expect(screen.getByText(T.colunasSemAnalises)).toBeInTheDocument();
  });

  it('sem nenhuma seção, mostra o estado vazio e desliga os botões', async () => {
    const { usuario } = renderizarPagina();
    await screen.findByRole('group', { name: /^Seções/ });
    for (const rotulo of Object.values(T.rotulosSecoes)) {
      const caixa = screen.getByRole('checkbox', { name: rotulo });
      if (!caixa.hasAttribute('disabled')) await usuario.click(caixa);
    }

    expect(screen.getByText(T.vazio.titulo)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: T.baixar })).toBeDisabled();
    expect(screen.getByRole('button', { name: T.imprimir })).toBeDisabled();
  });

  it('baixar usa a opção "Funciona sem internet" e o nome do arquivo', async () => {
    const { nomesBaixados } = simularDownload();
    const { usuario } = renderizarPagina();
    await screen.findByRole('checkbox', { name: /peso_kg/ });

    await usuario.click(screen.getByRole('checkbox', { name: new RegExp(T.offline) }));
    await usuario.click(screen.getByRole('button', { name: T.baixar }));

    expect(await screen.findByText(T.baixado('relatorio-pesquisa_saude.html'))).toBeInTheDocument();
    expect(nomesBaixados).toEqual(['relatorio-pesquisa_saude.html']);
    const pedidos = chamadasPara(api, 'GET', `${BASE}/relatorio`);
    expect(pedidos.some((chamada) => chamada.url.endsWith('offline=false'))).toBe(true);
  });

  it('erro ao baixar vira toast com a mensagem da API', async () => {
    simularApi([
      { caminho: `${BASE}/colunas`, corpo: colunasPesquisa },
      {
        caminho: `${BASE}/relatorio`,
        status: 422,
        corpo: { codigo: 'COLUNA_INVALIDA', mensagem: 'Coluna não encontrada.', sugestao: 'x' },
      },
    ]);
    const { usuario } = renderizarPagina();
    await screen.findByRole('checkbox', { name: /peso_kg/ });

    await usuario.click(screen.getByRole('button', { name: T.baixar }));

    expect(await screen.findByText('Coluna não encontrada.')).toBeInTheDocument();
  });

  it('imprimir chama o print da prévia carregada', async () => {
    const { usuario } = renderizarPagina();
    await screen.findByRole('checkbox', { name: /peso_kg/ });
    await waitFor(() => {
      expect(previa().getAttribute('src')).toContain('colunas=cidade');
    });
    const janela = exigir(previa().contentWindow, 'janela da prévia');
    const imprimir = vi.spyOn(janela, 'print').mockImplementation(() => undefined);

    expect(screen.getByRole('button', { name: T.imprimir })).toBeDisabled();
    fireEvent.load(previa());
    await usuario.click(screen.getByRole('button', { name: T.imprimir }));

    expect(imprimir).toHaveBeenCalled();
  });

  it('sem arquivo importado orienta a ir para Importar', () => {
    renderizarComProvedores(<PaginaRelatorio />);

    expect(screen.getByText(T.semDataset)).toBeInTheDocument();
  });

  it('"Voltar para Detector" leva à etapa 7', async () => {
    const { usuario, roteador } = renderizarPagina();

    await usuario.click(await screen.findByRole('button', { name: /Voltar para Detector/ }));
    expect(roteador.state.location.pathname).toBe('/detector');
  });
});
