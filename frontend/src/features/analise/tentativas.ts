/** Número de tentativas da Binomial (discreta, D96): leitura do campo e maior valor observado. */
import { formatarInteiro, lerNumeroPtBr } from '../../shared/lib/formatar';
import { TEXTOS_ANALISE } from './textos';
import type { Analise } from './tipos';

const T = TEXTOS_ANALISE.forma.tentativas;

export type ResultadoTentativas =
  { status: 'ok'; n: number } | { status: 'erro'; mensagem: string };

/** Mesma regra da API: inteiro e pelo menos o maior valor observado. */
export function validarTentativas(texto: string, maximo: number): ResultadoTentativas {
  const n = lerNumeroPtBr(texto);
  if (n === null || !Number.isInteger(n)) return { status: 'erro', mensagem: T.erroInteiro };
  if (n < maximo) return { status: 'erro', mensagem: T.erroMinimo(formatarInteiro(maximo)) };
  return { status: 'ok', n };
}

/** Na discreta, a tabela de frequências lista os valores em ordem; o último é o maior. */
export function maiorValorObservado(analise: Analise): number | null {
  const valores = analise.frequencias.linhas
    .map((linha) => linha.valor)
    .filter((valor): valor is number => typeof valor === 'number');
  return valores.length === 0 ? null : Math.max(...valores);
}
