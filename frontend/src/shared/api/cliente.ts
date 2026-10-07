/** Cliente HTTP único da aplicação: prefixo /api e erros no formato {codigo, mensagem, sugestao}. */

export interface CorpoErroApi {
  codigo: string;
  mensagem: string;
  sugestao: string;
}

const PREFIXO_API = '/api';

const SEM_CONEXAO: CorpoErroApi = {
  codigo: 'SEM_CONEXAO',
  mensagem: 'Não conseguimos falar com o servidor.',
  sugestao: 'Verifique se o backend está rodando e tente novamente.',
};

const ERRO_DESCONHECIDO: CorpoErroApi = {
  codigo: 'ERRO_DESCONHECIDO',
  mensagem: 'O servidor respondeu de um jeito inesperado.',
  sugestao: 'Tente novamente em instantes.',
};

export class ErroApi extends Error {
  readonly status: number;
  readonly codigo: string;
  readonly sugestao: string;

  constructor(status: number, corpo: CorpoErroApi) {
    super(corpo.mensagem);
    this.name = 'ErroApi';
    this.status = status;
    this.codigo = corpo.codigo;
    this.sugestao = corpo.sugestao;
  }
}

function ehCorpoErroApi(valor: unknown): valor is CorpoErroApi {
  return typeof valor === 'object' && valor !== null && 'codigo' in valor && 'mensagem' in valor;
}

/** 502/503/504 sem corpo padrão vêm do proxy do Vite quando o backend está parado. */
const STATUS_SEM_CONEXAO = new Set([502, 503, 504]);

function corpoSemFormatoPadrao(status: number): CorpoErroApi {
  return STATUS_SEM_CONEXAO.has(status) ? SEM_CONEXAO : ERRO_DESCONHECIDO;
}

async function lerCorpoDeErro(resposta: Response): Promise<CorpoErroApi> {
  const corpo: unknown = await resposta.json().catch(() => null);
  return ehCorpoErroApi(corpo) ? corpo : corpoSemFormatoPadrao(resposta.status);
}

export function urlDaApi(caminho: string): string {
  return `${PREFIXO_API}${caminho}`;
}

async function buscar(caminho: string, opcoes?: RequestInit): Promise<Response> {
  const resposta = await fetch(urlDaApi(caminho), opcoes).catch(() => {
    throw new ErroApi(0, SEM_CONEXAO);
  });
  if (!resposta.ok) {
    throw new ErroApi(resposta.status, await lerCorpoDeErro(resposta));
  }
  return resposta;
}

/**
 * Faz a requisição e devolve o corpo tipado.
 * O `as T` é o único cast permitido: T vem dos tipos gerados do OpenAPI (schema.d.ts).
 */
export async function requisitar<T>(caminho: string, opcoes?: RequestInit): Promise<T> {
  const resposta = await buscar(caminho, opcoes);
  return (await resposta.json()) as T;
}

/** Para respostas que não são JSON (ex.: relatório HTML para download). */
export async function requisitarBlob(caminho: string): Promise<Blob> {
  const resposta = await buscar(caminho);
  return resposta.blob();
}
