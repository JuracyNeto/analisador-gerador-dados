import type { ComponentProps } from 'react';
import type CardMetrica from '../../shared/ui/CardMetrica';
import { estaAplicavel, motivoNaoAplicavel } from './abas';
import { formatarValorMedida } from './formatacao';
import { TEXTOS_ANALISE } from './textos';
import type { Analise, Dispersao, Formula, Medida, Moda } from './tipos';

type PropsCardMetrica = ComponentProps<typeof CardMetrica>;

const C = TEXTOS_ANALISE.cartoes;

export interface DefinicaoCartao {
  id: string;
  rotulo: string;
  medida: Medida;
  /** Medida de apoio mostrada no "Ver fórmula" do card (moda de Czuber na contínua). */
  apoio?: Medida | undefined;
  selo?: string | undefined;
  unidade?: string | undefined;
  casasSignificativas?: number | undefined;
}

/** `Moda` não é `Medida` e não traz chave; no catálogo do M1.4 a fórmula da moda bruta é `moda`. */
const CHAVE_FORMULA_MODA = 'moda';

function acharFormula(formulas: readonly Formula[], chave: string | null): Formula | undefined {
  return chave === null ? undefined : formulas.find((formula) => formula.chave === chave);
}

function calculoDoCartao({ medida, apoio }: DefinicaoCartao): string | null {
  if (apoio === undefined) return medida.calculo;
  return C.apoioCzuber(apoio.calculo ?? `Mo = ${formatarValorMedida(apoio.valor)}`);
}

function formulaDoCartao(
  definicao: DefinicaoCartao,
  formulas: readonly Formula[],
): PropsCardMetrica['formula'] {
  const formula = acharFormula(formulas, (definicao.apoio ?? definicao.medida).formula);
  if (formula === undefined) return undefined;
  const calculo = calculoDoCartao(definicao);
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
      naoAplicavel: { motivo: medida.motivo ?? TEXTOS_ANALISE.motivoPadrao },
    };
  }
  const formula = formulaDoCartao(definicao, formulas);
  return {
    rotulo,
    valor: formatarValorMedida(medida.valor, definicao.casasSignificativas),
    ...(definicao.unidade === undefined ? {} : { unidade: definicao.unidade }),
    ...(definicao.selo === undefined ? {} : { selo: definicao.selo }),
    ...(medida.interpretacao === null ? {} : { interpretacao: medida.interpretacao }),
    ...(formula === undefined ? {} : { formula }),
  };
}

function medidaAusente(motivo: string): Medida {
  return {
    valor: null,
    aplicavel: false,
    motivo,
    calculo: null,
    interpretacao: null,
    formula: null,
  };
}

function comInterpretacao(medida: Medida, padrao: string): Medida {
  return { ...medida, interpretacao: medida.interpretacao ?? padrao };
}

/** `Moda` não é uma `Medida`: várias modas viram um texto só. */
export function medidaDaModa(moda: Moda): Medida {
  const valor =
    moda.valores.length === 0
      ? C.semModa
      : moda.valores.map((v) => formatarValorMedida(v)).join(' · ');
  return {
    valor,
    aplicavel: true,
    motivo: null,
    calculo: null,
    interpretacao: moda.interpretacao,
    formula: CHAVE_FORMULA_MODA,
  };
}

function cartaoModaSimples(moda: Moda): DefinicaoCartao {
  return {
    id: 'moda',
    rotulo: C.moda,
    medida: medidaDaModa(moda),
    selo: C.seloModa[moda.classificacao],
  };
}

function cartaoCentro(analise: Analise): DefinicaoCartao {
  const { tendencia } = analise;
  return estaAplicavel(analise, 'proporcao')
    ? { id: 'proporcao', rotulo: C.proporcao, medida: tendencia.proporcao }
    : { id: 'media', rotulo: C.media, medida: tendencia.media };
}

/** Spec 05: o card mostra a moda bruta; na contínua, a de Czuber (pelas classes) vai como apoio no "Ver fórmula". */
function cartaoModa(analise: Analise): DefinicaoCartao {
  const cartao = cartaoModaSimples(analise.tendencia.moda);
  return estaAplicavel(analise, 'moda_czuber')
    ? { ...cartao, apoio: analise.tendencia.moda_czuber }
    : cartao;
}

export function cartoesTendencia(analise: Analise): DefinicaoCartao[] {
  const mediana = { id: 'mediana', rotulo: C.mediana, medida: analise.tendencia.mediana };
  return [cartaoCentro(analise), mediana, cartaoModa(analise)];
}

export function cartoesDispersao(dispersao: Dispersao): DefinicaoCartao[] {
  const { classificacao_cv: classificacao } = dispersao;
  return [
    { id: 'desvio_padrao', rotulo: C.desvioPadrao, medida: dispersao.desvio_padrao },
    {
      id: 'cv',
      rotulo: C.cv,
      medida: dispersao.cv,
      unidade: '%',
      casasSignificativas: 3,
      selo: classificacao === null ? undefined : C.seloCv[classificacao],
    },
    { id: 'iqr', rotulo: C.iqr, medida: dispersao.iqr },
    { id: 'amplitude', rotulo: C.amplitude, medida: dispersao.amplitude },
    {
      id: 'variancia',
      rotulo: C.variancia,
      medida: comInterpretacao(dispersao.variancia, C.notaVariancia),
    },
  ];
}

/** Linha de 4 cards da aba Frequências quando não há dispersão (nominal, design 4g). */
export function cartoesResumoCategorico(analise: Analise): DefinicaoCartao[] {
  const { tendencia } = analise;
  return [
    cartaoModaSimples(tendencia.moda),
    { id: 'media', rotulo: C.media, medida: tendencia.media },
    { id: 'mediana', rotulo: C.mediana, medida: tendencia.mediana },
    {
      id: 'desvio_padrao',
      rotulo: C.desvioPadrao,
      medida: medidaAusente(motivoNaoAplicavel(analise, 'dispersao')),
    },
  ];
}

export function notaPopulacional(dispersao: Dispersao): string | null {
  const { desvio_padrao_populacional: desvio, variancia_populacional: variancia } = dispersao;
  if (!desvio.aplicavel || !variancia.aplicavel) return null;
  return C.populacional(formatarValorMedida(desvio.valor), formatarValorMedida(variancia.valor));
}
