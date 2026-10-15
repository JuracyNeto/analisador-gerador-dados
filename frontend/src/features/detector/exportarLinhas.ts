/** "Exportar estas linhas" (tela 7b): CSV montado no navegador, no formato que o app lê (D140). */
import { formatarCelula } from '../../shared/lib/formatarCelula';
import type { Aviso, LinhaDados } from './tipos';

type Celula = LinhaDados['valores'][string];

const SEPARADOR = ';';
/** Sem ponto de milhar: o CSV volta a ser lido como número (vírgula decimal, como o do Gerador). */
const NUMERO = new Intl.NumberFormat('pt-BR', { useGrouping: false, maximumFractionDigits: 10 });
const PRECISA_ASPAS = /[;"\r\n]/;
const COLUNA_LINHA = 'linha';
const COLUNA_DESTACADA = 'destacada';
const MARCA = { sim: 'sim', nao: 'não' } as const;
const PREFIXO_ARQUIVO = 'linhas';

function textoCsv(texto: string): string {
  return PRECISA_ASPAS.test(texto) ? `"${texto.replaceAll('"', '""')}"` : texto;
}

function celulaCsv(valor: Celula | undefined): string {
  if (valor === null || valor === undefined) return '';
  return typeof valor === 'number' ? NUMERO.format(valor) : textoCsv(formatarCelula(valor));
}

/** Uma linha por registro: número da linha, as colunas e se a linha está destacada. */
export function exportarLinhas(
  linhas: readonly LinhaDados[],
  colunas: readonly string[],
  destacadas: ReadonlySet<number>,
): string {
  const cabecalho = [COLUNA_LINHA, ...colunas, COLUNA_DESTACADA].map(textoCsv);
  const corpo = linhas.map((linha) => [
    String(linha.linha),
    ...colunas.map((coluna) => celulaCsv(linha.valores[coluna])),
    destacadas.has(linha.linha) ? MARCA.sim : MARCA.nao,
  ]);
  return [cabecalho, ...corpo].map((campos) => `${campos.join(SEPARADOR)}\n`).join('');
}

/** `linhas-R4-peso_kg.csv`; sem coluna (linhas inteiras), `linhas-R5.csv`. */
export function nomeDoCsv(aviso: Pick<Aviso, 'regra' | 'colunas'>): string {
  return `${[PREFIXO_ARQUIVO, aviso.regra, ...aviso.colunas].join('-')}.csv`;
}
