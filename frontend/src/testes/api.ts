/** Falso de fetch para testes: responde por rota (método + caminho) e guarda as chamadas. */
import { type Mock, vi } from 'vitest';

export interface RotaFalsa {
  metodo?: 'GET' | 'POST' | 'PATCH' | 'DELETE';
  /** Caminho sem o prefixo /api e sem query, ex.: '/datasets/ds-1/colunas'. */
  caminho: string;
  status?: number;
  corpo?: unknown;
}

export interface ChamadaFeita {
  url: string;
  corpo: unknown;
}

export type FetchFalso = Mock<typeof fetch>;

export function respostaJson(status: number, corpo: unknown): Response {
  return new Response(JSON.stringify(corpo), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });
}

function urlDe(entrada: RequestInfo | URL): string {
  if (typeof entrada === 'string') return entrada;
  return entrada instanceof URL ? entrada.href : entrada.url;
}

function caminhoDe(entrada: RequestInfo | URL): string {
  const [caminho = ''] = urlDe(entrada).split('?');
  return caminho;
}

function lerCorpo(corpo: BodyInit | null | undefined): unknown {
  if (typeof corpo !== 'string') return corpo;
  const lido: unknown = JSON.parse(corpo);
  return lido;
}

function casa(rota: RotaFalsa, metodo: string, caminho: string): boolean {
  return (rota.metodo ?? 'GET') === metodo && `/api${rota.caminho}` === caminho;
}

/** Troca o fetch global (restaurado pelo `afterEach` de `src/testes/configuracao.ts`, M1.1). */
export function simularApi(rotas: readonly RotaFalsa[]): FetchFalso {
  const falso = vi.fn<typeof fetch>((entrada, opcoes) => {
    const metodo = opcoes?.method ?? 'GET';
    const caminho = caminhoDe(entrada);
    const rota = rotas.find((r) => casa(r, metodo, caminho));
    const resposta = rota
      ? respostaJson(rota.status ?? 200, rota.corpo ?? null)
      : respostaJson(500, {
          codigo: 'ROTA_NAO_SIMULADA',
          mensagem: `${metodo} ${caminho}`,
          sugestao: '',
        });
    return Promise.resolve(resposta);
  });
  vi.stubGlobal('fetch', falso);
  return falso;
}

export function chamadasPara(falso: FetchFalso, metodo: string, caminho: string): ChamadaFeita[] {
  return falso.mock.calls
    .filter(
      ([entrada, opcoes]) =>
        (opcoes?.method ?? 'GET') === metodo && caminhoDe(entrada) === `/api${caminho}`,
    )
    .map(([entrada, opcoes]) => ({ url: urlDe(entrada), corpo: lerCorpo(opcoes?.body) }));
}
