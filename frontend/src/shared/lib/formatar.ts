/**
 * Formatadores pt-BR. A regra de casas decimais é a mesma de
 * backend/app/compartilhado/numeros.py (M1.2): mesmos números na tela e no relatório.
 */

const LOCALE = 'pt-BR';
const VALOR_AUSENTE = '—';
const PADRAO_PT_BR = /^[+-]?(?:\d{1,3}(?:\.\d{3})+|\d+)(?:,\d+)?$/;
const PADRAO_PONTO_DECIMAL = /^[+-]?\d+\.\d+$/;
/** Sinal de menos tipográfico, como no backend (`com_sinal_de_menos`). */
const MENOS = '−';

function formatador(casas: number): Intl.NumberFormat {
  // signDisplay 'negative' evita "-0" quando o arredondamento zera um negativo.
  return new Intl.NumberFormat(LOCALE, { maximumFractionDigits: casas, signDisplay: 'negative' });
}

/** Casas decimais para mostrar `casasSignificativas` algarismos: max(0, cs − 1 − ⌊log10 |v|⌋). */
export function casasDecimais(valor: number, casasSignificativas: number): number {
  if (valor === 0) return 0;
  return Math.max(0, casasSignificativas - 1 - Math.floor(Math.log10(Math.abs(valor))));
}

function comSinalDeMenos(texto: string): string {
  return texto.startsWith('-') ? `${MENOS}${texto.slice(1)}` : texto;
}

/** 70.314 → "70,31"; 12345.6 → "12.346"; −0.394 → "−0,394" (sem zeros à direita). */
export function formatarNumero(valor: number, casasSignificativas = 4): string {
  if (!Number.isFinite(valor)) return VALOR_AUSENTE;
  return comSinalDeMenos(formatador(casasDecimais(valor, casasSignificativas)).format(valor));
}

/** 1234 → "1.234". */
export function formatarInteiro(valor: number): string {
  return Number.isFinite(valor) ? formatador(0).format(valor) : VALOR_AUSENTE;
}

/** Recebe o percentual já em 0–100: 21.6 → "21,6%". */
export function formatarPercentual(valor: number, casas = 1): string {
  return Number.isFinite(valor) ? `${formatador(casas).format(valor)}%` : VALOR_AUSENTE;
}

/**
 * Lê um número digitado em pt-BR ("1.234,5", "1,72", "-3" ou "−3").
 * Sem vírgula e com ponto fora do padrão de milhar ("1.72"), o ponto vale como decimal.
 */
export function lerNumeroPtBr(texto: string): number | null {
  const limpo = texto.trim().replace(MENOS, '-');
  if (PADRAO_PT_BR.test(limpo)) return Number(limpo.replaceAll('.', '').replace(',', '.'));
  return PADRAO_PONTO_DECIMAL.test(limpo) ? Number(limpo) : null;
}

/** Número com casas decimais fixas, pt-BR: formatarDecimal(4) → "4,0"; −2,5 com "−". */
export function formatarDecimal(valor: number, casas = 1): string {
  if (!Number.isFinite(valor)) return VALOR_AUSENTE;
  const formato = new Intl.NumberFormat('pt-BR', {
    minimumFractionDigits: casas,
    maximumFractionDigits: casas,
  });
  return comSinalDeMenos(formato.format(valor));
}

const CASAS_MOSTRADAS = /,(\d+)/u;

/**
 * Mesmas casas para todos os valores de uma coluna de tabela: as do valor que pede mais com
 * 4 algarismos (ponto médio 46,05 · 106,05, e não 106,1; quartis 62,30 · 77,95).
 */
export function formatadorDaColuna(
  valores: readonly number[],
  casasSignificativas = 4,
): (valor: number) => string {
  const casas = valores
    .filter((valor) => Number.isFinite(valor))
    .map(
      (valor) => CASAS_MOSTRADAS.exec(formatarNumero(valor, casasSignificativas))?.[1]?.length ?? 0,
    );
  const maximo = Math.max(0, ...casas);
  return (valor) => formatarDecimal(valor, maximo);
}

const P_VALOR_MINIMO = 0.001;

/** Mesma regra de `formatar_p_valor` do backend: "p < 0,001" ou "p = 0,213" (3 algarismos). */
export function formatarPValor(p: number): string {
  return p < P_VALOR_MINIMO ? 'p < 0,001' : `p = ${formatarNumero(p, 3)}`;
}
