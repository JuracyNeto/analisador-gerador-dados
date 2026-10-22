import { screen, waitFor } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { chamadasPara, simularApi } from '../../../testes/api';
import { simularDownload } from '../../../testes/downloadFalso';
import { adotadoAnexo, adotadoNovo, geradoAltura } from '../../../testes/fixtures/gerador';
import { DATASET_TESTE, renderizarComProvedores } from '../../../testes/renderizar';
import { TEXTOS_GERADOR } from '../textos';
import ResultadoGeracao from './ResultadoGeracao';

vi.mock('../../../shared/graficos/Grafico', () => import('../../../testes/graficoFalso'));

const T = TEXTOS_GERADOR;
const ADOTAR = `/gerador/${geradoAltura.gerado_id}/adotar`;

function renderizar(aoExpirar = vi.fn(), dataset: typeof DATASET_TESTE | null = DATASET_TESTE) {
  const tela = renderizarComProvedores(
    <ResultadoGeracao
      gerado={geradoAltura}
      gerando={false}
      aoExpirar={aoExpirar}
      aoGerarDeNovo={null}
    />,
    { dataset },
  );
  return { ...tela, aoExpirar };
}

describe('ResultadoGeracao', () => {
  it('baixa o CSV com o nome da geração', async () => {
    simularApi([{ caminho: `/gerador/${geradoAltura.gerado_id}/csv`, corpo: 'altura_m' }]);
    const { nomesBaixados } = simularDownload();
    const { usuario } = renderizar();

    await usuario.click(screen.getByRole('button', { name: T.acoes.baixar }));

    expect(await screen.findByText(T.toast.baixado('gerado-altura_m.csv'))).toBeInTheDocument();
    expect(nomesBaixados).toEqual(['gerado-altura_m.csv']);
  });

  it('anexa ao dataset da sessão', async () => {
    const api = simularApi([{ metodo: 'POST', caminho: ADOTAR, status: 201, corpo: adotadoAnexo }]);
    const { usuario } = renderizar();

    await usuario.click(await screen.findByRole('button', { name: T.acoes.anexar }));

    expect(await screen.findByText(T.toast.anexado(500, 'pesquisa_saude.txt'))).toBeInTheDocument();
    expect(chamadasPara(api, 'POST', ADOTAR)[0]?.corpo).toEqual({
      modo: 'anexar',
      dataset_id: DATASET_TESTE.id,
    });
  });

  it('usar como novo arquivo troca o dataset da sessão', async () => {
    simularApi([{ metodo: 'POST', caminho: ADOTAR, status: 201, corpo: adotadoNovo }]);
    const { usuario } = renderizar();

    await usuario.click(screen.getByRole('button', { name: T.acoes.usar }));

    expect(await screen.findByText(T.toast.novo(500))).toBeInTheDocument();
    expect(localStorage.getItem('sessao')).toContain('"id":"ds-novo"');
  });

  it('sem dataset não oferece anexar', () => {
    simularApi([]);
    renderizar(vi.fn(), null);

    expect(screen.queryByRole('button', { name: T.acoes.anexar })).not.toBeInTheDocument();
  });

  it('geração que saiu da memória limpa o resultado e avisa', async () => {
    simularApi([
      {
        metodo: 'POST',
        caminho: ADOTAR,
        status: 404,
        corpo: {
          codigo: 'GERADO_NAO_ENCONTRADO',
          mensagem: 'Os dados gerados não estão mais disponíveis.',
          sugestao: 'Gere de novo na etapa Gerador.',
        },
      },
    ]);
    const { usuario, aoExpirar } = renderizar();

    await usuario.click(screen.getByRole('button', { name: T.acoes.usar }));

    expect(
      await screen.findByText('Os dados gerados não estão mais disponíveis.'),
    ).toBeInTheDocument();
    await waitFor(() => {
      expect(aoExpirar).toHaveBeenCalled();
    });
  });

  it('estados vazio e gerando', () => {
    simularApi([]);
    const { rerender } = renderizarComProvedores(
      <ResultadoGeracao
        gerado={undefined}
        gerando={false}
        aoExpirar={vi.fn()}
        aoGerarDeNovo={null}
      />,
    );
    expect(screen.getByText(T.resultado.vazio.titulo)).toBeInTheDocument();

    rerender(
      <ResultadoGeracao gerado={undefined} gerando aoExpirar={vi.fn()} aoGerarDeNovo={null} />,
    );
    expect(screen.getByText(T.resultado.gerandoDados)).toBeInTheDocument();
  });
});
