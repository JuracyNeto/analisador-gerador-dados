/** Card "Início do arquivo": as primeiras linhas como estão escritas e o papel de cada uma. */
import type { MetadadosLeitura } from './opcoesLeitura';

export type PapelLinha = 'fora' | 'cabecalho' | 'dados';

export interface LinhaInicial {
  numero: number;
  celulas: string[];
  papel: PapelLinha;
}

export interface InicioArquivo {
  largura: number;
  linhas: LinhaInicial[];
}

function papelDaLinha(numero: number, linhaCabecalho: number): PapelLinha {
  if (numero < linhaCabecalho) return 'fora';
  return numero === linhaCabecalho ? 'cabecalho' : 'dados';
}

/** null quando não há linhas do arquivo para mostrar (JSON). Células completadas até a largura. */
export function descreverLinhasIniciais(meta: MetadadosLeitura): InicioArquivo | null {
  const linhaCabecalho = meta.linha_cabecalho;
  if (linhaCabecalho === null || meta.linhas_iniciais.length === 0) return null;
  const largura = Math.max(...meta.linhas_iniciais.map((linha) => linha.celulas.length));
  return {
    largura,
    linhas: meta.linhas_iniciais.map((linha) => ({
      numero: linha.numero,
      celulas: Array.from({ length: largura }, (_, i) => linha.celulas[i] ?? ''),
      papel: papelDaLinha(linha.numero, linhaCabecalho),
    })),
  };
}
