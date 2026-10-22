/** Trechos de linhas que o drawer "Ver na tabela" busca e mostra (tela 7b, D140). */
import { formatarInteiro } from '../../shared/lib/formatar';
import { TEXTOS_DETECTOR } from './textos';

const T = TEXTOS_DETECTOR.linhas;
/** Linhas de contexto antes e depois de cada linha destacada. */
export const CONTEXTO = 3;
const PRIMEIRA_LINHA = 1;
/** Como os exemplos da API (spec 16): até 8 números, com "…" se houver mais. */
const MAXIMO_NA_FRASE = 8;

export interface Trecho {
  de: number;
  ate: number;
}

/** Cada linha com ±3 de contexto (sem passar da 1ª); janelas que se tocam viram um trecho só. */
export function trechosDoExemplo(linhas: readonly number[], contexto = CONTEXTO): Trecho[] {
  const trechos: Trecho[] = [];
  for (const linha of [...new Set(linhas)].toSorted((a, b) => a - b)) {
    const de = Math.max(PRIMEIRA_LINHA, linha - contexto);
    const anterior = trechos.at(-1);
    if (anterior !== undefined && de <= anterior.ate + 1) anterior.ate = linha + contexto;
    else trechos.push({ de, ate: linha + contexto });
  }
  return trechos;
}

function seguidas(linhas: readonly number[]): boolean {
  return linhas.every((linha, i) => i === 0 || linha === (linhas[i - 1] ?? linha) + 1);
}

/** "a", "a e b", "a, b e c". */
function juntarComE(itens: readonly string[]): string {
  const ultimo = itens.at(-1) ?? '';
  return itens.length < 2 ? ultimo : `${itens.slice(0, -1).join(', ')} e ${ultimo}`;
}

function listar(numeros: readonly number[]): string {
  const escritos = numeros.map(formatarInteiro);
  if (escritos.length > MAXIMO_NA_FRASE) return `${escritos.slice(0, MAXIMO_NA_FRASE).join(', ')}…`;
  return juntarComE(escritos);
}

/** "Linha 77", "Linhas 1.200 a 1.238", "Linhas 99, 106, 160 e 178" (como os exemplos da API). */
export function descreverLinhas(linhas: readonly number[]): string {
  const ordenadas = [...new Set(linhas)].toSorted((a, b) => a - b);
  const [primeira] = ordenadas;
  const ultima = ordenadas.at(-1);
  if (primeira === undefined || ultima === undefined) return '';
  if (ordenadas.length === 1) return T.uma(formatarInteiro(primeira));
  if (ordenadas.length > 2 && seguidas(ordenadas)) {
    return T.faixa(formatarInteiro(primeira), formatarInteiro(ultima));
  }
  return T.lista(listar(ordenadas));
}

/** Da 1ª à última linha que veio de cada trecho: perto do fim, o arquivo acaba antes do contexto. */
export function trechosMostrados(
  carregados: readonly { linhas: readonly { linha: number }[] }[],
): Trecho[] {
  return carregados.flatMap(({ linhas }) => {
    const [primeira] = linhas;
    const ultima = linhas.at(-1);
    return primeira === undefined || ultima === undefined
      ? []
      : [{ de: primeira.linha, ate: ultima.linha }];
  });
}

/** Rodapé do drawer: "117–141" ou "1.196–1.241, 1.257–1.263 e 1.275–1.281". */
export function descreverTrechos(trechos: readonly Trecho[]): string {
  return juntarComE(trechos.map(({ de, ate }) => `${formatarInteiro(de)}–${formatarInteiro(ate)}`));
}
