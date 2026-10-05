import { formatarInteiro } from '../../shared/lib/formatar';
import { formatarCelula } from '../../shared/lib/formatarCelula';
import { escolherForma } from '../../shared/lib/pluralizar';
import { TEXTOS_LIMPEZA as T } from './textos';
import type { EntradaLog, Ocorrencia } from './tipos';

const MAX_NUMEROS = 5;
const MAX_OCORRENCIAS = 3;
const LISTA_PT = new Intl.ListFormat('pt-BR', { style: 'long', type: 'conjunction' });

export function soma(valores: readonly number[]): number {
  return valores.reduce((total, valor) => total + valor, 0);
}

export function listarComE(itens: readonly string[]): string {
  return LISTA_PT.format(itens);
}

/** "6,8; 106,4 e 712": com vírgula decimal, a vírgula não pode separar os itens. */
export function listarValores(itens: readonly string[]): string {
  if (itens.length <= 1) return itens.join('');
  return `${itens.slice(0, -1).join('; ')} e ${String(itens.at(-1))}`;
}

export function primeiraMaiuscula(texto: string): string {
  return texto.charAt(0).toUpperCase() + texto.slice(1);
}

/** "12, 141, 207" ou "1, 2, 3, 4, 5 e mais 2". */
export function listarNumeros(numeros: readonly number[], maximo = MAX_NUMEROS): string {
  const visiveis = numeros.slice(0, maximo).map(formatarInteiro).join(', ');
  const resto = numeros.length - maximo;
  return resto > 0 ? `${visiveis}${T.linhas.eMais(resto)}` : visiveis;
}

/** "linha 88" / "linhas 45, 46, 47". */
export function descreverLinhas(linhas: readonly number[]): string {
  return `${escolherForma(linhas.length, T.linhas.singular, T.linhas.plural)} ${listarNumeros(linhas)}`;
}

/** "Linhas 19 e 201: 0 e 230" (até 3 ocorrências + "e mais N"). */
export function descreverOcorrencias(ocorrencias: readonly Ocorrencia[]): string {
  const visiveis = ocorrencias.slice(0, MAX_OCORRENCIAS);
  const prefixo = primeiraMaiuscula(
    escolherForma(ocorrencias.length, T.linhas.singular, T.linhas.plural),
  );
  const linhas = listarComE(visiveis.map((o) => formatarInteiro(o.linha)));
  const valores = listarValores(visiveis.map((o) => formatarCelula(o.valor)));
  const resto = ocorrencias.length - visiveis.length;
  return `${prefixo} ${linhas}: ${valores}${resto > 0 ? T.linhas.eMais(resto) : ''}`;
}

/** Detalhe mono do log: "linhas 45, 46, 47" · "17,2 → 1,72". */
export function detalheDoLog(entrada: EntradaLog): string {
  const partes: string[] = [];
  if (entrada.linhas_afetadas.length > 0) partes.push(descreverLinhas(entrada.linhas_afetadas));
  if (entrada.antes_exemplo !== '' && entrada.depois_exemplo !== '') {
    partes.push(`${entrada.antes_exemplo} → ${entrada.depois_exemplo}`);
  }
  return partes.join(' · ');
}

export function chaveDoLog(entrada: EntradaLog): string {
  return [entrada.quando, entrada.problema, entrada.acao, entrada.coluna ?? ''].join('|');
}
