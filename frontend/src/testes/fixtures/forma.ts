/** Fixtures do contrato `Forma` (spec 09), com os números do print 4e. */
import type { components } from '../../shared/api/schema';
import { figura, medida, naoSeAplica } from './blocosAnalise';

type Esquemas = components['schemas'];
type Forma = Esquemas['Forma'];
type Ajuste = Esquemas['Ajuste'];

export const MOTIVO_BINOMIAL_CONTINUA =
  'Binomial não se aplica a quantitativas contínuas: precisa de contagens de sucessos em n tentativas.';
export const MOTIVO_FORMA_NOMINAL =
  'Forma e distribuição não se aplica a qualitativas nominais: as distribuições Normal e Binomial exigem números.';
export const FRASE_CONJUNTA =
  'Distribuição aproximadamente simétrica e mesocúrtica; compatível com a Normal (p = 0,21).';

function ajusteNaoAplicavel(distribuicao: Ajuste['distribuicao'], motivo: string): Ajuste {
  return {
    distribuicao,
    aplicavel: false,
    motivo,
    parametros: [],
    teste: null,
    complementar: null,
    frase: null,
    calculo: null,
    formula: null,
  };
}

export const normalCompativel: Ajuste = {
  distribuicao: 'normal',
  aplicavel: true,
  motivo: null,
  parametros: [
    { simbolo: 'μ̂', nome: 'média', valor: 70.31 },
    { simbolo: 'σ̂', nome: 'desvio padrão', valor: 11.2 },
  ],
  teste: { nome: 'Shapiro-Wilk', estatistica: 0.9912, gl: null, p_valor: 0.21, compativel: true },
  complementar: { nome: 'Qui-quadrado', estatistica: 3.2, gl: 4, p_valor: 0.525, compativel: true },
  frase: 'Os dados são compatíveis com a distribuição Normal.',
  calculo: 'Shapiro-Wilk: W = 0,9912 · p = 0,21 ≥ 0,05',
  formula: 'normal',
};

export const formaContinua: Forma = {
  assimetria: medida(0.32, {
    interpretacao: 'Aproximadamente simétrica: a cauda direita é só um pouco mais longa.',
    calculo: 'G₁ = [√(227·226) / 225] · 12,5 / 125,4^(3/2) = 0,32',
    formula: 'assimetria',
  }),
  assimetria_pearson_1: medida(0.4677, { formula: 'assimetria_pearson_1' }),
  assimetria_pearson_2: medida(0.7016, { formula: 'assimetria_pearson_2' }),
  curtose: medida(-0.18, {
    interpretacao: 'Mesocúrtica: caudas parecidas com as da Normal.',
    calculo: 'G₂ = -0,18 (na Normal, G₂ = 0; n = 227)',
    formula: 'curtose',
  }),
  curtose_percentilica: medida(0.1786, { formula: 'curtose_percentilica' }),
  classificacao_assimetria: 'simetrica',
  sentido_assimetria: 'direita',
  classificacao_curtose: 'mesocurtica',
  normal: normalCompativel,
  binomial: ajusteNaoAplicavel('binomial', MOTIVO_BINOMIAL_CONTINUA),
  tentativas: null,
  interpretacao: FRASE_CONJUNTA,
  figuras: [
    {
      ...figura('histograma_normal', 'Histograma + Normal', false),
      titulo: 'Histograma de peso_kg com curva Normal (n = 227)',
    },
    { ...figura('qqplot', 'QQ-plot', false), titulo: 'QQ-plot de peso_kg contra a Normal' },
  ],
};

export const formaDiscreta: Forma = {
  ...formaContinua,
  normal: ajusteNaoAplicavel(
    'normal',
    'Normal não se aplica: a aproximação pela Normal precisa de pelo menos 30 valores.',
  ),
  binomial: {
    distribuicao: 'binomial',
    aplicavel: true,
    motivo: null,
    parametros: [
      { simbolo: 'n', nome: 'número de tentativas', valor: 8 },
      { simbolo: 'p̂', nome: 'probabilidade de sucesso', valor: 0.3906 },
      { simbolo: 'E[X]', nome: 'valor esperado', valor: 3.125 },
      { simbolo: 'Var', nome: 'variância', valor: 1.904 },
    ],
    teste: { nome: 'Qui-quadrado', estatistica: 4.008, gl: 2, p_valor: 0.135, compativel: true },
    complementar: null,
    frase: 'Os dados são compatíveis com a distribuição Binomial.',
    calculo: 'Qui-quadrado: χ² = 4,008 · gl = 2 · p = 0,135 ≥ 0,05',
    formula: 'binomial',
  },
  tentativas: 8,
  figuras: [
    {
      ...figura('binomial', 'Observado × Binomial', false, 'faltas'),
      titulo: 'faltas: observado × Binomial (n = 8; p = 0,3906)',
    },
  ],
};

const MOTIVO_BINARIA = 'não se aplica a binárias: os valores são categorias.';

export const formaBinaria: Forma = {
  assimetria: naoSeAplica(`Assimetria ${MOTIVO_BINARIA}`),
  assimetria_pearson_1: naoSeAplica(`1º coeficiente de Pearson ${MOTIVO_BINARIA}`),
  assimetria_pearson_2: naoSeAplica(`2º coeficiente de Pearson ${MOTIVO_BINARIA}`),
  curtose: naoSeAplica(`Curtose ${MOTIVO_BINARIA}`),
  curtose_percentilica: naoSeAplica(`Curtose percentílica ${MOTIVO_BINARIA}`),
  classificacao_assimetria: null,
  sentido_assimetria: null,
  classificacao_curtose: null,
  normal: ajusteNaoAplicavel(
    'normal',
    'Normal não se aplica a binárias: com dois valores, a distribuição é a Bernoulli.',
  ),
  binomial: {
    distribuicao: 'bernoulli',
    aplicavel: true,
    motivo: null,
    parametros: [
      { simbolo: 'p̂', nome: 'proporção de sucesso', valor: 0.3 },
      { simbolo: 'E[X]', nome: 'valor esperado', valor: 0.3 },
      { simbolo: 'Var', nome: 'variância', valor: 0.21 },
    ],
    teste: null,
    complementar: null,
    frase:
      'Com p estimado dos próprios dados, a Bernoulli repete as proporções observadas; não há teste de aderência.',
    calculo: 'p̂ = 0,3 · Var = p(1 − p) = 0,21',
    formula: 'bernoulli',
  },
  tentativas: null,
  interpretacao: null,
  figuras: [],
};
