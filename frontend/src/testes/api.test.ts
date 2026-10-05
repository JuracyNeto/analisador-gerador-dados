import { describe, expect, it } from 'vitest';
import { chamadasPara, simularApi } from './api';

const CAMINHO = '/datasets/ds-1/limpeza';

describe('simularApi', () => {
  it('responde pela rota que casa método e caminho, ignorando a query', async () => {
    simularApi([{ caminho: '/datasets/ds-1', corpo: { ok: true } }]);

    const resposta = await fetch('/api/datasets/ds-1?pagina=1&tamanho=20');

    expect(resposta.status).toBe(200);
    await expect(resposta.json()).resolves.toEqual({ ok: true });
  });

  it('devolve 500 com o código ROTA_NAO_SIMULADA quando nada casa', async () => {
    simularApi([]);

    const resposta = await fetch('/api/outra');

    expect(resposta.status).toBe(500);
    await expect(resposta.json()).resolves.toMatchObject({ codigo: 'ROTA_NAO_SIMULADA' });
  });

  it('registra as chamadas com o corpo JSON já lido', async () => {
    const falso = simularApi([{ metodo: 'POST', caminho: CAMINHO, corpo: {} }]);

    await fetch(`/api${CAMINHO}`, { method: 'POST', body: JSON.stringify({ acoes: [] }) });

    expect(chamadasPara(falso, 'POST', CAMINHO)).toEqual([
      { url: `/api${CAMINHO}`, corpo: { acoes: [] } },
    ]);
  });
});
