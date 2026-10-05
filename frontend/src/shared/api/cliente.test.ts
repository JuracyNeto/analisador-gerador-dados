import { describe, expect, it, vi } from 'vitest';
import { respostaJson } from '../../testes/api';
import { ErroApi, requisitar } from './cliente';

describe('requisitar', () => {
  it('retorna o corpo quando a resposta é ok', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(respostaJson(200, { status: 'ok' })));

    await expect(requisitar('/saude')).resolves.toEqual({ status: 'ok' });
    expect(fetch).toHaveBeenCalledWith('/api/saude', undefined);
  });

  it('converte o erro padronizado da API em ErroApi', async () => {
    const corpo = {
      codigo: 'DATASET_NAO_ENCONTRADO',
      mensagem: 'Sua sessão expirou.',
      sugestao: 'Envie de novo.',
    };
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(respostaJson(404, corpo)));

    await expect(requisitar('/datasets/x')).rejects.toMatchObject({
      status: 404,
      codigo: 'DATASET_NAO_ENCONTRADO',
      message: 'Sua sessão expirou.',
      sugestao: 'Envie de novo.',
    });
  });

  it('usa mensagem amigável quando o servidor está fora do ar', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('Failed to fetch')));

    const erro: unknown = await requisitar('/saude').catch((e: unknown) => e);

    expect(erro).toBeInstanceOf(ErroApi);
    expect((erro as ErroApi).codigo).toBe('SEM_CONEXAO');
  });

  it('usa mensagem amigável quando o erro não tem o formato padrão', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response('<html>', { status: 500 })));

    await expect(requisitar('/saude')).rejects.toMatchObject({
      status: 500,
      codigo: 'ERRO_DESCONHECIDO',
    });
  });

  it('trata o 502 do proxy (backend parado) como sem conexão', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(null, { status: 502 })));

    await expect(requisitar('/saude')).rejects.toMatchObject({
      status: 502,
      codigo: 'SEM_CONEXAO',
    });
  });
});
