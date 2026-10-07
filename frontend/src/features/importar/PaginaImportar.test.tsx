import { screen, waitFor } from '@testing-library/react';
import { Route, Routes } from 'react-router';
import { describe, expect, it } from 'vitest';
import { chamadasPara, simularApi } from '../../testes/api';
import {
  criarPagina,
  criarResumo,
  DATASET_CRIADO,
  ID_DATASET,
} from '../../testes/fixtures/datasets';
import { DATASET_TESTE, renderizarComProvedores } from '../../testes/renderizar';
import PaginaImportar from './PaginaImportar';
import { TEXTOS_IMPORTAR as T } from './textos';

const CAMINHO_PAGINA = `/datasets/${ID_DATASET}`;
const CAMINHO_LEITURA = `${CAMINHO_PAGINA}/leitura`;
const ARQUIVO = new File(['id;sexo'], 'pesquisa_saude.txt', { type: 'text/plain' });

function renderizarPagina(dataset: typeof DATASET_TESTE | null = null) {
  return renderizarComProvedores(
    <Routes>
      <Route path="/importar" element={<PaginaImportar />} />
      <Route path="/variaveis" element={<p>Tela de variáveis</p>} />
    </Routes>,
    { rota: '/importar', dataset },
  );
}

/** Simula a importação com sucesso, abre a página e envia o arquivo de teste. */
async function enviarComSucesso() {
  const falso = simularApi([
    { metodo: 'POST', caminho: '/datasets', status: 201, corpo: DATASET_CRIADO },
    { caminho: CAMINHO_PAGINA, corpo: criarPagina() },
    { metodo: 'POST', caminho: CAMINHO_LEITURA, corpo: DATASET_CRIADO },
  ]);
  const { usuario } = renderizarPagina();
  await usuario.upload(screen.getByLabelText('Arquivo de dados'), ARQUIVO);
  return { falso, usuario };
}

describe('PaginaImportar', () => {
  it('sem arquivo (1b): área de envio e link do exemplo', () => {
    renderizarPagina();

    expect(screen.getByText('Arraste e solte seu arquivo aqui')).toBeInTheDocument();
    expect(
      screen.getByRole('button', { name: 'Abrir pesquisa_saude.txt de exemplo' }),
    ).toBeInTheDocument();
  });

  it('envio com sucesso (1a): toast, detecções, prévia e continuar', async () => {
    const { usuario } = await enviarComSucesso();

    expect(await screen.findByText('Arquivo lido: 230 linhas e 8 colunas.')).toBeInTheDocument();
    expect(await screen.findByRole('combobox', { name: 'Separador' })).toHaveValue(';');
    expect(screen.getByRole('table', { name: 'Prévia dos dados importados' })).toBeInTheDocument();
    await usuario.click(screen.getByRole('button', { name: /Continuar para Variáveis/ }));
    expect(screen.getByText('Tela de variáveis')).toBeInTheDocument();
  });

  it('erro (1c): banner com o nome do arquivo, área continua disponível', async () => {
    simularApi([
      {
        metodo: 'POST',
        caminho: '/datasets',
        status: 400,
        corpo: {
          codigo: 'FORMATO_NAO_SUPORTADO',
          mensagem: 'Este tipo de arquivo não é aceito. Use TXT, CSV, TSV, XLSX ou JSON.',
          sugestao: 'Salve como CSV e envie de novo.',
        },
      },
    ]);
    const { usuario } = renderizarPagina();

    await usuario.upload(
      screen.getByLabelText('Arquivo de dados'),
      new File(['%PDF'], 'relatorio_final.txt'),
    );

    expect(
      await screen.findByText('Não conseguimos ler este arquivo: relatorio_final.txt'),
    ).toBeInTheDocument();
    expect(screen.getByText('Arraste e solte seu arquivo aqui')).toBeInTheDocument();
  });

  it('corrigir o separador relê no servidor o arquivo guardado, com a opção nova', async () => {
    const { falso, usuario } = await enviarComSucesso();

    await usuario.selectOptions(await screen.findByRole('combobox', { name: 'Separador' }), ',');

    expect(await screen.findByText('Arquivo lido de novo: 230 linhas e 8 colunas.')).toBeVisible();
    expect(chamadasPara(falso, 'POST', CAMINHO_LEITURA).map((c) => c.corpo)).toEqual([
      { separador: ',' },
    ]);
    expect(chamadasPara(falso, 'POST', '/datasets')).toHaveLength(1);
  });

  it('abrir o exemplo chama POST /datasets/exemplo', async () => {
    const falso = simularApi([
      { metodo: 'POST', caminho: '/datasets/exemplo', status: 201, corpo: DATASET_CRIADO },
      { caminho: CAMINHO_PAGINA, corpo: criarPagina() },
    ]);
    const { usuario } = renderizarPagina();

    await usuario.click(
      screen.getByRole('button', { name: 'Abrir pesquisa_saude.txt de exemplo' }),
    );

    expect(await screen.findByText('O que detectamos')).toBeInTheDocument();
    expect(chamadasPara(falso, 'POST', '/datasets/exemplo')).toHaveLength(1);
  });

  it('voltando de outra etapa, ainda dá para corrigir a leitura', async () => {
    const falso = simularApi([
      {
        caminho: CAMINHO_PAGINA,
        corpo: criarPagina(criarResumo({ opcoes_leitura: { aba: 'B' } })),
      },
      { metodo: 'POST', caminho: CAMINHO_LEITURA, corpo: DATASET_CRIADO },
    ]);
    const { usuario } = renderizarPagina(DATASET_TESTE);

    await usuario.selectOptions(await screen.findByRole('combobox', { name: 'Decimal' }), '.');

    await waitFor(() => {
      expect(chamadasPara(falso, 'POST', CAMINHO_LEITURA).map((c) => c.corpo)).toEqual([
        { aba: 'B', decimal: '.' },
      ]);
    });
  });

  it('com tipos corrigidos ou limpeza, pede confirmação antes de ler de novo', async () => {
    const falso = simularApi([
      { caminho: CAMINHO_PAGINA, corpo: criarPagina(criarResumo({ tem_ajustes: true })) },
      { metodo: 'POST', caminho: CAMINHO_LEITURA, corpo: DATASET_CRIADO },
    ]);
    const { usuario } = renderizarPagina(DATASET_TESTE);
    const lerDeNovo = await screen.findByRole('button', { name: 'Ler de novo' });

    await usuario.click(lerDeNovo);
    expect(screen.getByText(T.releitura.aviso)).toBeInTheDocument();
    await usuario.click(screen.getByRole('button', { name: T.releitura.cancelar }));
    expect(screen.queryByText(T.releitura.aviso)).not.toBeInTheDocument();
    expect(chamadasPara(falso, 'POST', CAMINHO_LEITURA)).toHaveLength(0);

    await usuario.click(lerDeNovo);
    await usuario.click(screen.getByRole('button', { name: T.releitura.confirmar }));
    await waitFor(() => {
      expect(chamadasPara(falso, 'POST', CAMINHO_LEITURA).map((c) => c.corpo)).toEqual([{}]);
    });
  });
});
