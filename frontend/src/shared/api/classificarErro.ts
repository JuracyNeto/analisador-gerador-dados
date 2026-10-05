import { ErroApi } from './cliente';

const MAX_RETENTATIVAS = 2;

/** 4xx: o pedido está errado (arquivo ilegível, sessão expirada…); repetir não resolve. */
export function ehErroDeEntrada(erro: unknown): boolean {
  return erro instanceof ErroApi && erro.status >= 400 && erro.status < 500;
}

/** Política de retentativa das consultas (Dnn-sessao): sem repetir 4xx; rede e 5xx até 2 vezes. */
export function deveTentarDeNovo(falhas: number, erro: unknown): boolean {
  return !ehErroDeEntrada(erro) && falhas < MAX_RETENTATIVAS;
}
