import { TEXTOS_ANALISE } from './textos';
import type { Analise, IdAba } from './tipos';

export interface DefinicaoAba {
  id: IdAba;
  rotulo: string;
  desabilitada?: boolean;
  motivo?: string;
}

const ORDEM_ABAS: readonly IdAba[] = [
  'frequencias',
  'tendencia',
  'separatrizes',
  'dispersao',
  'forma',
  'graficos',
];

/** Abas que dependem de `aplicavel` (contrato da visão geral); as demais valem para todo tipo. */
const CHAVE_APLICAVEL: Partial<Record<IdAba, string>> = {
  separatrizes: 'separatrizes',
  dispersao: 'dispersao',
  forma: 'forma',
};

export function estaAplicavel(analise: Analise, chave: string): boolean {
  return analise.aplicavel[chave] === true;
}

export function motivoNaoAplicavel(analise: Analise, item: string): string {
  const encontrado = analise.nao_aplicavel.find((naoAplicavel) => naoAplicavel.item === item);
  return encontrado?.motivo ?? TEXTOS_ANALISE.motivoPadrao;
}

function definirAba(analise: Analise, id: IdAba): DefinicaoAba {
  const rotulo = TEXTOS_ANALISE.abas[id];
  const chave = CHAVE_APLICAVEL[id];
  if (chave === undefined || estaAplicavel(analise, chave)) return { id, rotulo };
  return { id, rotulo, desabilitada: true, motivo: motivoNaoAplicavel(analise, chave) };
}

export function abasDaAnalise(analise: Analise): DefinicaoAba[] {
  return ORDEM_ABAS.map((id) => definirAba(analise, id));
}

export function abaEfetiva(pedida: IdAba, abas: readonly DefinicaoAba[]): IdAba {
  const aba = abas.find((candidata) => candidata.id === pedida);
  return aba !== undefined && aba.desabilitada !== true ? pedida : 'frequencias';
}
