/** Leitura e validação dos campos do gerador (funções puras; mensagens da spec 16). */
import { lerNumeroPtBr } from '../../shared/lib/formatar';
import { TEXTOS_GERADOR } from './textos';

const E = TEXTOS_GERADOR.erros;
export const LIMITE_GERACAO = 1_000_000;
export const MIN_PARES = 3;
export const MAX_SEMENTE = 4_294_967_295;

export type Leitura<T> = { ok: true; valor: T } | { ok: false; erro: string };

function ok<T>(valor: T): Leitura<T> {
  return { ok: true, valor };
}

function falha<T>(erro: string): Leitura<T> {
  return { ok: false, erro };
}

function inteiroEntre(texto: string, minimo: number, maximo: number): number | null {
  const valor = lerNumeroPtBr(texto);
  if (valor === null || !Number.isInteger(valor)) return null;
  return valor >= minimo && valor <= maximo ? valor : null;
}

export function lerQuantidade(texto: string): Leitura<number> {
  const valor = inteiroEntre(texto, 1, LIMITE_GERACAO);
  return valor === null ? falha(E.quantidade) : ok(valor);
}

export function lerQuantidadePares(texto: string): Leitura<number> {
  const valor = inteiroEntre(texto, MIN_PARES, LIMITE_GERACAO);
  return valor === null ? falha(E.quantidadePares) : ok(valor);
}

/** Vazia = o servidor sorteia uma semente e a devolve (D109). */
export function lerSemente(texto: string): Leitura<number | null> {
  if (texto.trim() === '') return ok(null);
  const valor = inteiroEntre(texto, 0, MAX_SEMENTE);
  return valor === null ? falha(E.semente) : ok(valor);
}

export function lerNumero(texto: string): Leitura<number> {
  const valor = lerNumeroPtBr(texto);
  return valor === null ? falha(E.numero) : ok(valor);
}

export function lerDesvio(texto: string): Leitura<number> {
  const valor = lerNumeroPtBr(texto);
  if (valor === null) return falha(E.numero);
  return valor > 0 ? ok(valor) : falha(E.desvio);
}

export function lerChance(texto: string): Leitura<number> {
  const valor = lerNumeroPtBr(texto);
  return valor !== null && valor >= 0 && valor <= 1 ? ok(valor) : falha(E.chance);
}

/** Erros por campo, a partir das leituras que falharam. */
export function errosDe<C extends string>(
  leituras: readonly (readonly [C, Leitura<unknown>])[],
): Partial<Record<C, string>> {
  const erros: Partial<Record<C, string>> = {};
  for (const [campo, leitura] of leituras) {
    if (!leitura.ok) erros[campo] = leitura.erro;
  }
  return erros;
}
