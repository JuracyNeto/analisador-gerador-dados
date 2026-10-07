import type { ReactNode } from 'react';
import { formatarDecimal, formatarInteiro, formatarNumero } from '../../shared/lib/formatar';
import type { ColunaTabela } from '../../shared/ui/Tabela';
import { formatarOpcional } from './formatacao';
import estilos from './frequencias.module.css';
import { TEXTOS_ANALISE } from './textos';
import type { LinhaFrequencia, TabelaFrequencia, TipoVariavel } from './tipos';

const T = TEXTOS_ANALISE.frequencias;

export type LinhaTabela =
  { tipo: 'linha'; indice: number; linha: LinhaFrequencia } | { tipo: 'total'; total: number };

type Coluna = ColunaTabela<LinhaTabela>;

export function linhasComTotal(tabela: TabelaFrequencia): LinhaTabela[] {
  const linhas: LinhaTabela[] = tabela.linhas.map((linha, indice) => ({
    tipo: 'linha',
    indice,
    linha,
  }));
  return [...linhas, { tipo: 'total', total: tabela.total }];
}

export function chaveDaLinha(linha: LinhaTabela): string {
  return linha.tipo === 'total' ? 'total' : String(linha.indice);
}

export function ehLinhaModal(tabela: TabelaFrequencia): (linha: LinhaTabela) => boolean {
  return (linha) => linha.tipo === 'linha' && linha.indice === tabela.indice_modal;
}

function colunaNumerica(
  id: string,
  titulo: ReactNode,
  daLinha: (linha: LinhaFrequencia) => ReactNode,
  doTotal: ReactNode = '',
): Coluna {
  return {
    id,
    titulo,
    alinhamento: 'direita',
    mono: true,
    celula: (linha) => (linha.tipo === 'total' ? <strong>{doTotal}</strong> : daLinha(linha.linha)),
  };
}

function colunaRotulo(titulo: string, mono: boolean): Coluna {
  return {
    id: 'rotulo',
    titulo,
    mono,
    celula: (linha) => (linha.tipo === 'total' ? <strong>{T.total}</strong> : linha.linha.rotulo),
  };
}

const colunaPontoMedio = colunaNumerica('ponto_medio', T.pontoMedio, (linha) =>
  formatarOpcional(linha.ponto_medio, (valor) => formatarNumero(valor)),
);

const categorica = (nome: string): Coluna[] => [colunaRotulo(nome, false)];

const PRIMEIRAS_COLUNAS = {
  continua: () => [colunaRotulo(T.classe, true), colunaPontoMedio],
  discreta: (nome: string) => [colunaRotulo(nome, true)],
  ordinal: categorica,
  nominal: categorica,
  binaria: categorica,
  identificador: categorica,
} satisfies Record<TipoVariavel, (nome: string) => Coluna[]>;

function colunasBase(total: number): Coluna[] {
  return [
    colunaNumerica(
      'fi',
      T.fi,
      (linha) => <span className={estilos.forte}>{formatarInteiro(linha.fi)}</span>,
      formatarInteiro(total),
    ),
    colunaNumerica('fr', T.fr, (linha) => formatarDecimal(linha.fr_pct), formatarDecimal(100)),
  ];
}

const COLUNAS_ACUMULADAS: Coluna[] = [
  colunaNumerica('fi_acumulada', T.fiAcumulada, (linha) =>
    formatarOpcional(linha.f_acum, formatarInteiro),
  ),
  colunaNumerica('fr_acumulada', T.frAcumulada, (linha) =>
    formatarOpcional(linha.fr_acum_pct, (valor) => formatarDecimal(valor)),
  ),
];

const COLUNA_ACUMULADA_ESMAECIDA = colunaNumerica(
  'fr_acumulada',
  <span className={estilos.esmaecida}>{T.frAcumuladaNaoAplicavel}</span>,
  () => (
    <span className={estilos.esmaecida}>
      <span aria-hidden="true">—</span>
      <span className={estilos.somenteLeitor}>{T.naoSeAplica}</span>
    </span>
  ),
);

export function colunasDaTabela(tabela: TabelaFrequencia, nomeColuna: string): Coluna[] {
  const acumuladas = tabela.acumulada_aplicavel ? COLUNAS_ACUMULADAS : [COLUNA_ACUMULADA_ESMAECIDA];
  return [
    ...PRIMEIRAS_COLUNAS[tabela.tipo](nomeColuna),
    ...colunasBase(tabela.total),
    ...acumuladas,
  ];
}

export function notasDaTabela(tabela: TabelaFrequencia, nFaltantes: number): string[] {
  const notas: string[] = [];
  if (tabela.h !== null) notas.push(T.notaClasses(formatarNumero(tabela.h)));
  if (tabela.motivo_acumulada !== null) notas.push(tabela.motivo_acumulada);
  if (nFaltantes > 0) notas.push(T.faltantes(nFaltantes));
  return notas;
}
