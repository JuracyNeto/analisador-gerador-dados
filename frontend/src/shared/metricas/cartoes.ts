/** `Medida` da API → props do `CardMetrica`; usado pela Análise e pela Bivariada (D104). */
import type { ComponentProps } from 'react';
import type { components } from '../api/schema';
import type CardMetrica from '../ui/CardMetrica';
import { formatarValorMedida } from './formatacao';
import { TEXTOS_METRICAS } from './textos';

export type Medida = components['schemas']['Medida'];
export type Formula = components['schemas']['Formula'];
type PropsCardMetrica = ComponentProps<typeof CardMetrica>;

/** Linha de apoio no "Ver fórmula": a fórmula vem da medida de apoio e o cálculo vem pronto. */
export interface ApoioCartao {
  medida: Medida;
  calculo: string;
}

export interface DefinicaoCartao {
  id: string;
  rotulo: string;
  medida: Medida;
  apoio?: ApoioCartao | undefined;
  selo?: string | undefined;
  unidade?: string | undefined;
  casasSignificativas?: number | undefined;
  tamanhoValor?: 'normal' | 'menor' | undefined;
}

function acharFormula(formulas: readonly Formula[], chave: string | null): Formula | undefined {
  return chave === null ? undefined : formulas.find((formula) => formula.chave === chave);
}

function formulaDoCartao(
  { medida, apoio }: DefinicaoCartao,
  formulas: readonly Formula[],
): PropsCardMetrica['formula'] {
  const formula = acharFormula(formulas, (apoio?.medida ?? medida).formula);
  if (formula === undefined) return undefined;
  const calculo = apoio?.calculo ?? medida.calculo;
  return calculo === null ? { expressao: formula.texto } : { expressao: formula.texto, calculo };
}

export function propsDoCartao(
  definicao: DefinicaoCartao,
  formulas: readonly Formula[],
): PropsCardMetrica {
  const { rotulo, medida } = definicao;
  if (!medida.aplicavel) {
    return {
      rotulo,
      valor: '—',
      naoAplicavel: { motivo: medida.motivo ?? TEXTOS_METRICAS.motivoPadrao },
    };
  }
  const formula = formulaDoCartao(definicao, formulas);
  return {
    rotulo,
    valor: formatarValorMedida(medida.valor, definicao.casasSignificativas),
    ...(definicao.unidade === undefined ? {} : { unidade: definicao.unidade }),
    ...(definicao.tamanhoValor === undefined ? {} : { tamanhoValor: definicao.tamanhoValor }),
    ...(definicao.selo === undefined ? {} : { selo: definicao.selo }),
    ...(medida.interpretacao === null ? {} : { interpretacao: medida.interpretacao }),
    ...(formula === undefined ? {} : { formula }),
  };
}

/** Medida que não se aplica, com o motivo no formato da spec 16. */
export function medidaAusente(motivo: string): Medida {
  return {
    valor: null,
    aplicavel: false,
    motivo,
    calculo: null,
    interpretacao: null,
    formula: null,
  };
}
