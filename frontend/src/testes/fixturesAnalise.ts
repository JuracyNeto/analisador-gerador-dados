import { vi } from 'vitest';
import type { components } from '../shared/api/schema';
import type { PropsPainel } from '../features/analise/tipos';
import { criarColuna, ID_DATASET } from './fixtures/datasets';

type Esquemas = components['schemas'];
type Analise = Esquemas['Analise'];
type Medida = Esquemas['Medida'];
type LinhaFrequencia = Esquemas['LinhaFrequencia'];
type ValorSeparatriz = Esquemas['ValorSeparatriz'];
type TipoColuna = Esquemas['TipoColuna'];

export function medida(valor: Medida['valor'], extra: Partial<Medida> = {}): Medida {
  return {
    valor,
    aplicavel: true,
    motivo: null,
    calculo: null,
    interpretacao: null,
    formula: null,
    ...extra,
  };
}

export function naoSeAplica(motivo: string): Medida {
  return {
    valor: null,
    aplicavel: false,
    motivo,
    calculo: null,
    interpretacao: null,
    formula: null,
  };
}

export const colunasPesquisa: TipoColuna[] = [
  criarColuna({ coluna: 'id', tipo: 'identificador' }),
  criarColuna({ coluna: 'sexo', tipo: 'binaria' }),
  criarColuna({ coluna: 'peso_kg', tipo: 'continua' }),
  criarColuna({ coluna: 'cidade', tipo: 'nominal' }),
  criarColuna({ coluna: 'quando', tipo: 'data' }),
];

const N = 227;

function linhaClasse(
  rotulo: string,
  limites: readonly [number, number],
  fi: number,
  fAcumulada: number,
): LinhaFrequencia {
  const [inferior, superior] = limites;
  return {
    rotulo,
    valor: null,
    limite_inferior: inferior,
    limite_superior: superior,
    ponto_medio: (inferior + superior) / 2,
    fi,
    fri: fi / N,
    fr_pct: (fi / N) * 100,
    f_acum: fAcumulada,
    fr_acum: fAcumulada / N,
    fr_acum_pct: (fAcumulada / N) * 100,
  };
}

function linhaCategoria(rotulo: string, fi: number, total: number): LinhaFrequencia {
  return {
    rotulo,
    valor: rotulo,
    limite_inferior: null,
    limite_superior: null,
    ponto_medio: null,
    fi,
    fri: fi / total,
    fr_pct: (fi / total) * 100,
    f_acum: null,
    fr_acum: null,
    fr_acum_pct: null,
  };
}

function separatriz(prefixo: string, indice: number, p: number, valor: number): ValorSeparatriz {
  return { rotulo: `${prefixo}${String(indice)}`, p, valor };
}

export const quartisPeso: ValorSeparatriz[] = [
  separatriz('Q', 1, 0.25, 62.1),
  separatriz('Q', 2, 0.5, 69.8),
  separatriz('Q', 3, 0.75, 77.9),
];

function figura(id: string, rotulo: string, recomendado: boolean): Esquemas['Figura'] {
  return {
    id,
    rotulo,
    titulo: `Figura ${id} de peso_kg`,
    resumo: `Resumo de ${id}.`,
    porque: `Por que ${id}.`,
    recomendado,
    dados: { data: [], layout: {} },
  };
}

const APLICAVEL_NUMERICA = {
  acumulada: true,
  media: true,
  mediana: true,
  moda_czuber: true,
  proporcao: false,
  separatrizes: true,
  posicao: true,
  dispersao: true,
  variancia: true,
  cv: true,
};

export const analiseContinua: Analise = {
  coluna: 'peso_kg',
  tipo: 'continua',
  n: N,
  n_faltantes: 3,
  aplicavel: APLICAVEL_NUMERICA,
  nao_aplicavel: [
    {
      item: 'proporcao',
      motivo: 'Proporção não se aplica a quantitativas contínuas: precisa de duas categorias.',
    },
  ],
  frequencias: {
    tipo: 'continua',
    total: N,
    k: 3,
    k_sturges: 9,
    h: 16.5,
    metodo_classes: 'usuario',
    acumulada_aplicavel: true,
    motivo_acumulada: null,
    indice_modal: 1,
    linhas: [
      linhaClasse('43,5 ⊢ 60,0', [43.5, 60], 33, 33),
      linhaClasse('60,0 ⊢ 76,5', [60, 76.5], 132, 165),
      linhaClasse('76,5 ⊢ 93,0', [76.5, 93], 62, N),
    ],
  },
  tendencia: {
    media: medida(70.3, {
      calculo: '= 15.958,1 / 227 = 70,3',
      interpretacao: 'Em média, os valores ficam em 70,3.',
      formula: 'media',
    }),
    mediana: medida(69.8, {
      interpretacao: 'Metade dos valores fica até 69,8.',
      formula: 'mediana',
    }),
    moda: {
      valores: [72],
      classificacao: 'unimodal',
      interpretacao: 'O valor que mais se repete é 72 (9 vezes).',
    },
    moda_czuber: medida(68.9, {
      interpretacao: 'Estimada a partir da classe mais comum.',
      formula: 'moda_czuber',
    }),
    proporcao: naoSeAplica(
      'Proporção não se aplica a quantitativas contínuas: precisa de duas categorias.',
    ),
  },
  separatrizes: {
    quartis: quartisPeso,
    decis: Array.from({ length: 9 }, (_, i) => separatriz('D', i + 1, (i + 1) / 10, 56 + i * 3.6)),
    percentis: Array.from({ length: 99 }, (_, i) =>
      separatriz('P', i + 1, (i + 1) / 100, 44 + i * 0.49),
    ),
    destaques: ['P1', 'P5', 'P10', 'P25', 'P50', 'P75', 'P90', 'P95', 'P99'],
  },
  dispersao: {
    amplitude: medida(49.1, {
      interpretacao: 'Do menor (43,8) ao maior (92,9) valor.',
      formula: 'amplitude',
    }),
    variancia: medida(125.4, { formula: 'variancia' }),
    variancia_populacional: medida(124.85, { formula: 'variancia_populacional' }),
    desvio_padrao: medida(11.2, {
      calculo: '= √(28.348,2 / 226) = 11,2',
      interpretacao: 'Em geral, os valores ficam a cerca de 11,2 da média.',
      formula: 'desvio_padrao',
    }),
    desvio_padrao_populacional: medida(11.17),
    iqr: medida(15.8, { formula: 'iqr' }),
    cv: medida(15.9, { interpretacao: 'O desvio é 15,9% da média.', formula: 'cv' }),
    classificacao_cv: 'media',
  },
  interpretacoes: [
    'Média e mediana estão próximas (diferença de 0,5): os dados são quase simétricos.',
  ],
  formulas: [
    { chave: 'media', nome: 'Média', latex: '\\bar{x}=\\frac{\\sum x_i}{n}', texto: 'x̄ = Σxᵢ / n' },
    {
      chave: 'moda_czuber',
      nome: 'Moda de Czuber',
      latex: 'Mo=L_i+\\frac{\\Delta_1}{\\Delta_1+\\Delta_2}\\cdot h',
      texto: 'Mo = Lᵢ + [Δ₁ / (Δ₁ + Δ₂)] · h',
    },
    {
      chave: 'desvio_padrao',
      nome: 'Desvio padrão',
      latex: 's=\\sqrt{\\frac{\\sum (x_i-\\bar{x})^2}{n-1}}',
      texto: 's = √[Σ(xᵢ − x̄)² / (n − 1)]',
    },
  ],
  figuras: [
    figura('principal', 'Histograma', true),
    figura('boxplot', 'Boxplot', false),
    figura('ogiva', 'Ogiva', false),
  ],
};

const MOTIVO_DISPERSAO =
  'Desvio padrão não se aplica a qualitativas: precisa de distâncias entre números.';
const TOTAL_CIDADES = 228;

export const analiseNominal: Analise = {
  coluna: 'cidade',
  tipo: 'nominal',
  n: TOTAL_CIDADES,
  n_faltantes: 2,
  aplicavel: {
    acumulada: false,
    media: false,
    mediana: false,
    moda_czuber: false,
    proporcao: false,
    separatrizes: false,
    posicao: false,
    dispersao: false,
    variancia: false,
    cv: false,
  },
  // O backend emite separatrizes, dispersao e posicao quando não se aplicam (M1.4).
  nao_aplicavel: [
    {
      item: 'separatrizes',
      motivo: 'Separatrizes não se aplicam a qualitativas nominais: as categorias não têm ordem.',
    },
    { item: 'dispersao', motivo: MOTIVO_DISPERSAO },
    { item: 'posicao', motivo: '"Onde está meu valor?" só funciona com colunas numéricas.' },
  ],
  frequencias: {
    tipo: 'nominal',
    total: TOTAL_CIDADES,
    k: null,
    k_sturges: null,
    h: null,
    metodo_classes: null,
    acumulada_aplicavel: false,
    indice_modal: 0,
    motivo_acumulada:
      'Frequência acumulada não se aplica a qualitativas nominais: as cidades não têm uma ordem natural para somar "até aqui".',
    linhas: [
      linhaCategoria('Goiânia', 120, TOTAL_CIDADES),
      linhaCategoria('Anápolis', 70, TOTAL_CIDADES),
      linhaCategoria('Trindade', 38, TOTAL_CIDADES),
    ],
  },
  tendencia: {
    media: naoSeAplica('Média não se aplica a categorias sem número: não dá para somar cidades.'),
    mediana: naoSeAplica(
      'Mediana não se aplica a qualitativas nominais: as cidades não têm ordem.',
    ),
    moda: {
      valores: ['Goiânia'],
      classificacao: 'unimodal',
      interpretacao: 'A cidade mais frequente: 120 de 228 pessoas (52,6%).',
    },
    moda_czuber: naoSeAplica('Moda de Czuber só vale para dados em classes.'),
    proporcao: naoSeAplica(
      'Proporção não se aplica a qualitativas nominais: precisa de duas categorias.',
    ),
  },
  separatrizes: null,
  dispersao: null,
  interpretacoes: [],
  formulas: [],
  figuras: [{ ...figura('principal', 'Barras', true), titulo: 'Pessoas por cidade (n = 228)' }],
};

export const analiseBinaria: Analise = {
  ...analiseNominal,
  coluna: 'sexo',
  tipo: 'binaria',
  aplicavel: { ...analiseNominal.aplicavel, proporcao: true },
  tendencia: {
    ...analiseNominal.tendencia,
    proporcao: medida(0.52, { interpretacao: '52% das linhas são M.', formula: 'proporcao' }),
  },
};

export const posicaoQuartil: Esquemas['Posicao'] = {
  valor: 75,
  tipo: 'quartil',
  regiao: '3º quartil (entre Q2 e Q3)',
  indice: 3,
  limite_inferior: 69.8,
  limite_superior: 77.9,
  posicao_percentil: 66,
  fora_da_faixa: null,
  minimo: 43.8,
  maximo: 92.9,
  marcas: quartisPeso,
  frase:
    'O valor 75 está no 3º quartil (entre Q2 = 69,8 e Q3 = 77,9). Cerca de 66% dos dados são menores que ele.',
};

export const posicaoAcima: Esquemas['Posicao'] = {
  ...posicaoQuartil,
  valor: 120,
  regiao: '4º quartil (acima de Q3)',
  indice: 4,
  limite_inferior: 77.9,
  limite_superior: null,
  posicao_percentil: 100,
  fora_da_faixa: 'acima',
  frase: 'O valor 120 está no 4º quartil (acima de Q3 = 77,9). Todos os dados são menores que ele.',
};

export function propsPainel(analise: Analise): PropsPainel {
  return {
    analise,
    datasetId: ID_DATASET,
    atualizando: false,
    classes: null,
    aoMudarClasses: vi.fn(),
  };
}
