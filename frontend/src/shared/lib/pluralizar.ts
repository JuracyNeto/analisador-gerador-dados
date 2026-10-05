import { formatarInteiro } from './formatar';

export function escolherForma(n: number, singular: string, plural: string): string {
  return n === 1 ? singular : plural;
}

/** "1 linha", "230 linhas", "1.234 linhas". */
export function pluralizar(n: number, singular: string, plural: string): string {
  return `${formatarInteiro(n)} ${escolherForma(n, singular, plural)}`;
}

export function contarLinhas(n: number): string {
  return pluralizar(n, 'linha', 'linhas');
}

export function contarColunas(n: number): string {
  return pluralizar(n, 'coluna', 'colunas');
}
