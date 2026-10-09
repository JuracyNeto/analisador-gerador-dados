/** Fixtures da tela 5 (spec 10), com os números do print 5a. */
import type { components } from '../../shared/api/schema';
import { figura, medida } from './blocosAnalise';
import { criarColuna } from './datasets';

type Esquemas = components['schemas'];

export const EQUACAO = 'Ŷ = −98,4 + 98,1·X';
export const FRASE_FORCA = 'Quando altura_m aumenta, peso_kg tende a aumentar.';
export const FRASE_SIGNIFICANCIA =
  'A correlação é significativa (chance de acontecer por acaso: menos de 1 em 1.000).';
export const AVISO_EXTRAPOLACAO =
  'Os valores de altura_m vão de 1,48 a 1,96. Prever fora disso (extrapolar) pode dar resultados pouco confiáveis.';

export const colunasBivariada: Esquemas['TipoColuna'][] = [
  criarColuna({ coluna: 'id', tipo: 'identificador' }),
  criarColuna({ coluna: 'idade', tipo: 'continua' }),
  criarColuna({ coluna: 'altura_m', tipo: 'continua' }),
  criarColuna({ coluna: 'peso_kg', tipo: 'continua' }),
  criarColuna({ coluna: 'cidade', tipo: 'nominal' }),
];

function formula(chave: string, nome: string, texto: string): Esquemas['Formula'] {
  return { chave, nome, latex: texto, texto };
}

export const bivariadaAlturaPeso: Esquemas['Bivariada'] = {
  x: 'altura_m',
  y: 'peso_kg',
  n: 227,
  n_descartados: 3,
  pearson: medida(0.78, {
    calculo: 'r = Sxy / √(Sxx · Syy) = 12,4 / √(4,1 · 61,2) = 0,78',
    interpretacao: FRASE_FORCA,
    formula: 'pearson',
  }),
  teste_t: medida(0.0002, {
    calculo: 't = 18,7 · gl = 225 · p < 0,001',
    interpretacao: FRASE_SIGNIFICANCIA,
    formula: 'teste_t_correlacao',
  }),
  spearman: medida(0.76, { calculo: 'ρ = 0,76', formula: 'spearman' }),
  forca: 'forte',
  sentido: 'positiva',
  regressao: {
    a: -98.4,
    b: 98.1,
    equacao: EQUACAO,
    reta: medida(EQUACAO, {
      calculo: 'b = Sxy / Sxx = 98,1 · a = ȳ − b·x̄ = −98,4',
      interpretacao: 'A cada 1 a mais em altura_m, o valor previsto de peso_kg sobe cerca de 98,1.',
      formula: 'regressao',
    }),
    r2: medida(61.0, {
      calculo: 'R² = r² = 0,61',
      interpretacao: '61% da variação de peso_kg é explicada por altura_m.',
      formula: 'r2',
    }),
    se: medida(8.1, { formula: 'erro_padrao_estimativa' }),
  },
  faixa_x: { minimo: 1.48, maximo: 1.96 },
  interpretacoes: [FRASE_FORCA, FRASE_SIGNIFICANCIA],
  formulas: [
    formula('pearson', 'Correlação de Pearson', 'r = Σ(xᵢ − x̄)(yᵢ − ȳ) / √[…]'),
    formula('spearman', 'Correlação de Spearman', 'ρ = Pearson dos postos de X e de Y'),
    formula('regressao', 'Reta de regressão', 'Ŷ = a + bX'),
    formula('r2', 'Coeficiente de determinação', 'R² = r²'),
  ],
  figuras: [
    {
      ...figura('dispersao', 'Dispersão', true),
      titulo: 'peso_kg em função de altura_m (n = 227)',
    },
    {
      ...figura('residuos', 'Resíduos', false),
      titulo: 'Resíduos da regressão',
      resumo: 'Resíduo é a diferença entre o peso_kg real e o previsto.',
    },
  ],
};

export const matrizExemplo: Esquemas['MatrizCorrelacao'] = {
  colunas: ['idade', 'altura_m', 'peso_kg'],
  valores: [
    [1, 0.12, 0.21],
    [0.12, 1, 0.78],
    [0.21, 0.78, 1],
  ],
  resumo:
    'O par mais forte é altura_m × peso_kg (0,78). idade quase não se relaciona com as outras.',
  figura: { ...figura('matriz', 'Matriz', false), titulo: 'Matriz de correlação (Pearson)' },
};

export const previsaoDentro: Esquemas['Previsao'] = {
  x: 1.7,
  y_previsto: 68.37,
  extrapolacao: false,
  faixa_x: { minimo: 1.48, maximo: 1.96 },
  frase: 'Para altura_m = 1,7, o valor previsto de peso_kg é 68,37.',
  aviso: null,
};

export const previsaoExtrapolada: Esquemas['Previsao'] = {
  ...previsaoDentro,
  x: 2.1,
  y_previsto: 107.6,
  extrapolacao: true,
  frase: 'Para altura_m = 2,1, o valor previsto de peso_kg é 107,6.',
  aviso: AVISO_EXTRAPOLACAO,
};
