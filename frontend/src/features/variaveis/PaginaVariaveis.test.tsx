import { screen, waitFor } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { chamadasPara, simularApi } from '../../testes/api';
import { COLUNAS_SAUDE, criarColuna, ID_DATASET } from '../../testes/fixtures/datasets';
import { DATASET_TESTE, renderizarComProvedores } from '../../testes/renderizar';
import PaginaVariaveis from './PaginaVariaveis';

const CAMINHO_COLUNAS = `/datasets/${ID_DATASET}/colunas`;
const CAMINHO_CIDADE = `${CAMINHO_COLUNAS}/cidade`;
const SELECT_CIDADE = { name: 'Tipo de cidade' };

describe('PaginaVariaveis', () => {
  it('mostra o resumo, a tabela e um editor por ordinal', async () => {
    simularApi([{ caminho: CAMINHO_COLUNAS, corpo: COLUNAS_SAUDE }]);
    renderizarComProvedores(<PaginaVariaveis />, { rota: '/variaveis', dataset: DATASET_TESTE });

    expect(await screen.findByText('Tipos detectados por coluna')).toBeInTheDocument();
    expect(screen.getByRole('list', { name: 'Resumo dos tipos' })).toHaveTextContent('2 contínuas');
    expect(screen.getAllByRole('list', { name: /Ordem das categorias de/ })).toHaveLength(2);
  });

  it('corrigir o tipo manda o PATCH e confirma com toast', async () => {
    const falso = simularApi([
      { caminho: CAMINHO_COLUNAS, corpo: COLUNAS_SAUDE },
      {
        metodo: 'PATCH',
        caminho: CAMINHO_CIDADE,
        corpo: criarColuna({ coluna: 'cidade', tipo: 'ordinal', origem: 'manual' }),
      },
    ]);
    const { usuario } = renderizarComProvedores(<PaginaVariaveis />, { dataset: DATASET_TESTE });

    await usuario.selectOptions(await screen.findByRole('combobox', SELECT_CIDADE), 'ordinal');

    expect(
      await screen.findByText('Tipo de cidade alterado para Qualitativa ordinal.'),
    ).toBeInTheDocument();
    expect(chamadasPara(falso, 'PATCH', CAMINHO_CIDADE)[0]?.corpo).toEqual({ tipo: 'ordinal' });
  });

  it('tipo recusado pela API mostra o erro e volta ao tipo anterior', async () => {
    simularApi([
      { caminho: CAMINHO_COLUNAS, corpo: COLUNAS_SAUDE },
      {
        metodo: 'PATCH',
        caminho: CAMINHO_CIDADE,
        status: 400,
        corpo: {
          codigo: 'TIPO_INCOMPATIVEL',
          mensagem: 'Esta coluna tem textos; não pode ser numérica.',
          sugestao: 'Escolha um tipo qualitativo.',
        },
      },
    ]);
    const { usuario } = renderizarComProvedores(<PaginaVariaveis />, { dataset: DATASET_TESTE });

    await usuario.selectOptions(await screen.findByRole('combobox', SELECT_CIDADE), 'continua');

    expect(
      await screen.findByText('Esta coluna tem textos; não pode ser numérica.'),
    ).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByRole('combobox', SELECT_CIDADE)).toHaveValue('nominal');
    });
  });

  it('sem dataset, orienta a importar', () => {
    renderizarComProvedores(<PaginaVariaveis />);
    expect(screen.getByText('Nenhum arquivo importado')).toBeInTheDocument();
  });
});
