import { screen, waitFor, within } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { chamadasPara, type RotaFalsa, simularApi } from '../../testes/api';
import {
  COLUNAS_SAUDE,
  criarPagina,
  criarResumo,
  ID_DATASET,
} from '../../testes/fixtures/datasets';
import {
  criarEntradaLog,
  criarResultado,
  DIAGNOSTICO_SAUDE,
  DIAGNOSTICO_VAZIO,
} from '../../testes/fixtures/limpeza';
import { DATASET_TESTE, renderizarComProvedores } from '../../testes/renderizar';
import PaginaLimpeza from './PaginaLimpeza';

const BASE = `/datasets/${ID_DATASET}`;
const APLICAR = { name: 'Aplicar limpeza' };

function rotas(
  extras: RotaFalsa[] = [],
  diagnostico = DIAGNOSTICO_SAUDE,
  resumo = criarResumo(),
): RotaFalsa[] {
  return [
    { caminho: `${BASE}/diagnostico`, corpo: diagnostico },
    { caminho: `${BASE}/colunas`, corpo: COLUNAS_SAUDE },
    { caminho: BASE, corpo: criarPagina(resumo) },
    ...extras,
  ];
}

function renderizar() {
  return renderizarComProvedores(<PaginaLimpeza />, { rota: '/limpeza', dataset: DATASET_TESTE });
}

describe('PaginaLimpeza', () => {
  it('mostra cards e seções com tudo em "Manter" e o aplicar desabilitado', async () => {
    simularApi(rotas());
    renderizar();

    const faltantes = await screen.findByRole('region', { name: 'Faltantes' });
    expect(
      within(faltantes).getByRole('combobox', { name: 'Ação para peso_kg (Faltantes)' }),
    ).toHaveValue('manter');
    expect(screen.getByText('Cópias exatas da linha 44.')).toBeInTheDocument();
    expect(screen.getByRole('button', APLICAR)).toBeDisabled();
  });

  it('aplica a ação escolhida e confirma com toast', async () => {
    const falso = simularApi(
      rotas([
        { metodo: 'POST', caminho: `${BASE}/limpeza`, corpo: criarResultado({ n_linhas: 230 }) },
      ]),
    );
    const { usuario } = renderizar();

    await usuario.selectOptions(
      await screen.findByRole('combobox', { name: 'Ação para peso_kg (Faltantes)' }),
      'preencher_mediana',
    );
    await usuario.click(screen.getByRole('button', APLICAR));

    expect(
      await screen.findByText('Limpeza aplicada: nenhuma linha removida.'),
    ).toBeInTheDocument();
    expect(chamadasPara(falso, 'POST', `${BASE}/limpeza`)[0]?.corpo).toEqual({
      acoes: [
        {
          problema: 'faltantes',
          acao: 'preencher_mediana',
          coluna: 'peso_kg',
          valor: null,
          limites: null,
          grupo: null,
        },
      ],
    });
  });

  it('limites válidos refazem o diagnóstico com ?limites=', async () => {
    const falso = simularApi(rotas());
    const { usuario } = renderizar();
    const idade = await screen.findByRole('group', { name: 'idade' });

    await usuario.type(within(idade).getByLabelText('Mínimo'), '120');
    await usuario.type(within(idade).getByLabelText('Máximo'), '110');
    expect(
      within(idade).getByText('O mínimo precisa ser menor que o máximo (110). Ajuste um dos dois.'),
    ).toBeInTheDocument();

    await usuario.clear(within(idade).getByLabelText('Mínimo'));
    await usuario.type(within(idade).getByLabelText('Mínimo'), '1');

    await waitFor(
      () => {
        const urls = chamadasPara(falso, 'GET', `${BASE}/diagnostico`).map((c) => c.url);
        expect(urls.some((url) => url.includes('limites=') && url.includes('idade'))).toBe(true);
      },
      { timeout: 2000 },
    );
  });

  it('sem problemas: estado vazio com "Continuar para Análise"', async () => {
    simularApi(rotas([], DIAGNOSTICO_VAZIO));
    renderizar();

    expect(await screen.findByText('Nenhum problema encontrado')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Continuar para Análise/ })).toBeInTheDocument();
  });

  it('desfazer tudo chama a API e avisa', async () => {
    const resumo = criarResumo({ n_linhas: 227, log_limpeza: [criarEntradaLog()] });
    const falso = simularApi(
      rotas(
        [
          {
            metodo: 'POST',
            caminho: `${BASE}/limpeza/desfazer`,
            corpo: criarResultado({ n_linhas: 230, log: [] }),
          },
        ],
        DIAGNOSTICO_SAUDE,
        resumo,
      ),
    );
    const { usuario } = renderizar();

    await screen.findByText('Removemos 3 linhas duplicadas.');
    await usuario.click(screen.getByRole('button', { name: 'Desfazer tudo' }));

    expect(
      await screen.findByText('Limpeza desfeita: voltamos às 230 linhas do arquivo.'),
    ).toBeInTheDocument();
    expect(chamadasPara(falso, 'POST', `${BASE}/limpeza/desfazer`)).toHaveLength(1);
  });

  it('"Voltar para Variáveis" leva à etapa 2', async () => {
    simularApi(rotas());
    const { usuario, roteador } = renderizar();

    await usuario.click(await screen.findByRole('button', { name: /Voltar para Variáveis/ }));
    expect(roteador.state.location.pathname).toBe('/variaveis');
  });

  it('com problemas: "Continuar para Análise" leva à etapa 4', async () => {
    simularApi(rotas());
    const { usuario, roteador } = renderizar();

    await usuario.click(await screen.findByRole('button', { name: /Continuar para Análise/ }));
    expect(roteador.state.location.pathname).toBe('/analise');
  });
});
