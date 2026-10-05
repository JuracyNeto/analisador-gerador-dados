import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import { ErroApi } from '../../../shared/api/cliente';
import BannerErroImportacao from './BannerErroImportacao';

describe('BannerErroImportacao', () => {
  it('cita o arquivo, mostra a mensagem da API e oferece o exemplo', async () => {
    const aoUsarExemplo = vi.fn();
    const erro = new ErroApi(400, {
      codigo: 'FORMATO_NAO_SUPORTADO',
      mensagem: 'Este tipo de arquivo não é aceito. Use TXT, CSV, TSV, XLSX ou JSON.',
      sugestao: 'Salve como CSV e envie de novo.',
    });
    render(
      <BannerErroImportacao
        erro={erro}
        nomeArquivo="relatorio_final.pdf"
        aoUsarExemplo={aoUsarExemplo}
      />,
    );

    expect(
      screen.getByText('Não conseguimos ler este arquivo: relatorio_final.pdf'),
    ).toBeInTheDocument();
    expect(screen.getByText(/Salve como CSV e envie de novo\./)).toBeInTheDocument();
    await userEvent.click(screen.getByRole('button', { name: 'Usar o arquivo de exemplo' }));
    expect(aoUsarExemplo).toHaveBeenCalled();
  });
});
