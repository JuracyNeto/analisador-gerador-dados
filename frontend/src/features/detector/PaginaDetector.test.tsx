import { screen, within } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { type RotaFalsa, simularApi } from '../../testes/api';
import { exigir } from '../../testes/exigir';
import { criarPagina } from '../../testes/fixtures/datasets';
import {
  avisoR1,
  avisoR4,
  avisoR7,
  linhasDados,
  resultadoDetector,
  resultadoVazio,
  VAZIO_DETECTOR,
} from '../../testes/fixtures/detector';
import { esperarSemViolacoes, TEMPO_AXE } from '../../testes/acessibilidade';
import { DATASET_TESTE, renderizarComProvedores } from '../../testes/renderizar';
import PaginaDetector from './PaginaDetector';
import { TEXTOS_DETECTOR as T } from './textos';

vi.mock('../../shared/graficos/Grafico', () => import('../../testes/graficoFalso'));

const BASE = `/datasets/${DATASET_TESTE.id}`;

function rotas(resultado = resultadoDetector): RotaFalsa[] {
  return [
    { caminho: BASE, corpo: criarPagina() },
    { caminho: `${BASE}/detector`, corpo: resultado },
    { caminho: `${BASE}/linhas`, corpo: linhasDados(178, 203) },
  ];
}

function renderizarPagina(rota = '/detector', resultado = resultadoDetector) {
  simularApi(rotas(resultado));
  return renderizarComProvedores(<PaginaDetector />, { rota, dataset: DATASET_TESTE });
}

function titulosDosGrupos(): string[] {
  return screen.getAllByRole('heading', { level: 2 }).map((titulo) => titulo.textContent);
}

describe('PaginaDetector', () => {
  it(
    'não tem violações de acessibilidade, com alertas e com o drawer aberto',
    async () => {
      const { container, usuario } = renderizarPagina();
      await screen.findByRole('heading', { name: resultadoDetector.resumo.frase });
      await esperarSemViolacoes(container);

      const [primeiro] = screen.getAllByRole('button', { name: 'Ver na tabela' });
      await usuario.click(exigir(primeiro, 'botão "Ver na tabela"'));
      await screen.findByRole('dialog');

      await esperarSemViolacoes(document.body);
    },
    TEMPO_AXE,
  );

  it(
    'sem alertas, não tem violações de acessibilidade',
    async () => {
      const { container } = renderizarPagina('/detector', resultadoVazio);
      await screen.findByText(VAZIO_DETECTOR);

      await esperarSemViolacoes(container);
    },
    TEMPO_AXE,
  );

  it('"Analisar de novo" anuncia o resultado num aviso (leitor de tela)', async () => {
    const { usuario } = renderizarPagina();
    await screen.findByRole('heading', { name: resultadoDetector.resumo.frase });

    await usuario.click(screen.getByRole('button', { name: T.analisarDeNovo }));

    expect(
      await screen.findByText(T.analisadoDeNovo(resultadoDetector.resumo.frase)),
    ).toBeInTheDocument();
  });

  it('resumo, filtros e alertas agrupados por coluna; o 1º de cada grupo aberto (7a)', async () => {
    renderizarPagina();

    expect(
      await screen.findByRole('heading', { name: resultadoDetector.resumo.frase }),
    ).toBeInTheDocument();
    expect(titulosDosGrupos()).toEqual([
      resultadoDetector.resumo.frase,
      'altura_m1 alerta',
      'altura_m × peso_kg1 alerta',
      'Linhas inteiras1 alerta',
      'peso_kg1 alerta',
      'idade2 alertas',
    ]);
    const idade = within(screen.getByRole('region', { name: /^idade/ }));
    expect(idade.getAllByRole('article')).toHaveLength(2);
    expect(idade.getAllByRole('button', { name: 'Ver explicação' })).toHaveLength(1);
    expect(screen.getByRole('button', { name: /Regras não verificadas/ })).toHaveAttribute(
      'aria-expanded',
      'false',
    );
  });

  it('desmarcar severidades filtra a lista e grava na URL; sem nenhuma, orienta', async () => {
    const { usuario, roteador } = renderizarPagina();
    await screen.findByRole('article', { name: avisoR1.titulo });

    await usuario.click(screen.getByRole('checkbox', { name: 'Suspeita alta (3)' }));

    expect(screen.queryByRole('article', { name: avisoR1.titulo })).not.toBeInTheDocument();
    expect(screen.getByRole('article', { name: avisoR4.titulo })).toBeInTheDocument();
    expect(roteador.state.location.search).toBe('?sev=atencao&sev=info');

    await usuario.click(screen.getByRole('checkbox', { name: 'Atenção (2)' }));
    await usuario.click(screen.getByRole('checkbox', { name: 'Informativo (1)' }));

    expect(screen.getByText(T.semSeveridade)).toBeInTheDocument();
    expect(screen.queryByRole('article')).not.toBeInTheDocument();
  });

  it('agrupar por regra; recarregar com a URL mantém os filtros', async () => {
    const { usuario } = renderizarPagina('/detector?sev=info');
    await screen.findByRole('article', { name: avisoR7.titulo });

    expect(screen.getAllByRole('article')).toHaveLength(1);
    expect(screen.getByRole('checkbox', { name: 'Suspeita alta (3)' })).not.toBeChecked();

    await usuario.click(screen.getByRole('radio', { name: 'Regra' }));

    expect(
      screen.getByRole('heading', { name: 'R7 · Valores distantes1 alerta' }),
    ).toBeInTheDocument();
  });

  it('"Ver na tabela" abre o drawer com as linhas do alerta e fecha devolvendo o foco', async () => {
    const { usuario } = renderizarPagina();
    const cartao = await screen.findByRole('article', { name: avisoR1.titulo });
    const botao = within(cartao).getByRole('button', { name: 'Ver na tabela' });

    await usuario.click(botao);

    const dialogo = screen.getByRole('dialog', { name: 'Linhas 181 a 200 · altura_m' });
    expect(within(dialogo).getByText('20 linhas destacadas.')).toBeInTheDocument();
    await usuario.keyboard('{Escape}');
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    expect(botao).toHaveFocus();
  });

  it('sem alertas: estado vazio com as 11 regras e o caminho para o Relatório (7c)', async () => {
    const { usuario, roteador } = renderizarPagina('/detector', resultadoVazio);

    expect(await screen.findByText(VAZIO_DETECTOR)).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Nenhum alerta' })).toBeInTheDocument();
    expect(screen.getByText(/Lei de Benford/)).toBeInTheDocument();

    await usuario.click(screen.getByRole('button', { name: 'Ver as 11 regras' }));
    const regras = within(screen.getByRole('dialog', { name: 'As 11 regras do detector' }));
    expect(regras.getAllByRole('listitem')).toHaveLength(11);
    expect(regras.getByText('R6 · Comparação temporal')).toBeInTheDocument();
    await usuario.click(regras.getByRole('button', { name: 'Fechar' }));

    await usuario.click(screen.getByRole('button', { name: 'Continuar para Relatório' }));
    expect(roteador.state.location.pathname).toBe('/relatorio');
  });

  it('erro da API mostra a mensagem com "Tentar de novo"', async () => {
    simularApi([
      {
        caminho: `${BASE}/detector`,
        status: 500,
        corpo: { codigo: 'ERRO', mensagem: 'Algo falhou.', sugestao: 'Tente de novo.' },
      },
    ]);
    renderizarComProvedores(<PaginaDetector />, { rota: '/detector', dataset: DATASET_TESTE });

    expect(await screen.findByText('Algo falhou.')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Tentar de novo' })).toBeInTheDocument();
  });

  it('sem arquivo importado orienta a ir para Importar', () => {
    renderizarComProvedores(<PaginaDetector />, { rota: '/detector' });

    expect(screen.getByText(T.semDataset)).toBeInTheDocument();
  });
});
