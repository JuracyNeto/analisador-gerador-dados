import { screen } from '@testing-library/react';
import { Route, Routes } from 'react-router';
import { describe, expect, it } from 'vitest';
import { chamadasPara, simularApi } from '../../testes/api';
import { criarPagina, DATASET_CRIADO, ID_DATASET } from '../../testes/fixtures/datasets';
import { DATASET_TESTE, renderizarComProvedores } from '../../testes/renderizar';
import PaginaImportar from './PaginaImportar';

const CAMINHO_PAGINA = `/datasets/${ID_DATASET}`;
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

  it('corrigir o separador relê o arquivo com a opção nova', async () => {
    const { falso, usuario } = await enviarComSucesso();

    await usuario.selectOptions(await screen.findByRole('combobox', { name: 'Separador' }), ',');

    const envios = chamadasPara(falso, 'POST', '/datasets');
    expect(envios).toHaveLength(2);
    expect((envios[1]?.corpo as FormData).get('separador')).toBe(',');
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

  it('voltando com sessão e sem o arquivo: detecções só para leitura', async () => {
    simularApi([{ caminho: CAMINHO_PAGINA, corpo: criarPagina() }]);
    renderizarPagina(DATASET_TESTE);

    expect(
      await screen.findByText(/Para corrigir a leitura, envie o arquivo de novo\./),
    ).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'Ler de novo' })).not.toBeInTheDocument();
  });
});
