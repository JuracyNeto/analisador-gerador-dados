import type { components } from '../../shared/api/schema';
import { figura } from './blocosAnalise';
import { criarColuna, ID_DATASET, NOME_ARQUIVO } from './datasets';

type Esquemas = components['schemas'];

export const colunasGerador: Esquemas['TipoColuna'][] = [
  criarColuna({ coluna: 'id', tipo: 'identificador' }),
  criarColuna({ coluna: 'altura_m', tipo: 'continua' }),
  criarColuna({ coluna: 'peso_kg', tipo: 'continua' }),
  criarColuna({ coluna: 'cidade', tipo: 'nominal' }),
];

export const origemAltura: Esquemas['ResumoOrigem'] = {
  coluna: 'altura_m',
  tipo: 'continua',
  n: 221,
  media: 1.6861,
  desvio: 0.0931,
  minimo: 1.47,
  maximo: 1.93,
  sucesso: null,
  fracasso: null,
  chance: null,
  so_preservar: false,
};

export const origemCidade: Esquemas['ResumoOrigem'] = {
  ...origemAltura,
  coluna: 'cidade',
  tipo: 'nominal',
  media: null,
  desvio: null,
  minimo: null,
  maximo: null,
  so_preservar: true,
};

export const origemPar: Esquemas['ResumoOrigemPar'] = {
  x: 'altura_m',
  y: 'peso_kg',
  n: 218,
  media_x: 1.686,
  media_y: 70.17,
  desvio_x: 0.0931,
  desvio_y: 11.41,
  r: 0.7019,
};

export const EXPLICACAO =
  'Sorteamos 500 valores de uma curva Normal com a mesma média (1,686) e desvio (0,0931) de altura_m, usando a semente 42, e ajustamos para bater exatamente essas medidas.';

export const geradoAltura: Esquemas['Gerado'] = {
  gerado_id: 'g-1',
  tipo: 'univariado',
  colunas: ['altura_m'],
  n: 500,
  semente: 42,
  origem: { dataset_id: ID_DATASET, nome_arquivo: NOME_ARQUIVO, colunas: ['altura_m'] },
  metodo: 'Normal com reescala',
  explicacao: EXPLICACAO,
  parametros: [
    { nome: 'Origem', valor: 'altura_m (pesquisa_saude.txt)' },
    { nome: 'Modo', valor: 'Preservar estatísticas' },
    { nome: 'Semente', valor: '42' },
  ],
  amostra: [{ altura_m: 1.72 }],
  comparacao: [
    { estatistica: 'n', original: 221, gerado: 500, diferenca: 279 },
    { estatistica: 'Média', original: 1.6861, gerado: 1.6861, diferenca: 0 },
    { estatistica: 'Assimetria', original: 0.245, gerado: 0.021, diferenca: -0.224 },
  ],
  formulas: [
    {
      chave: 'normal',
      nome: 'Sorteio da Normal',
      latex: 'g_i \\sim \\mathcal{N}(\\mu, \\sigma^2)',
      texto: 'gᵢ ~ Normal(μ, σ²)',
    },
  ],
  figuras: [
    {
      ...figura('sobreposicao', 'Sobreposição', true),
      titulo: 'altura_m: original e gerado sobrepostos',
      resumo: 'As duas distribuições têm formas parecidas.',
    },
  ],
};

export const geradoPares: Esquemas['Gerado'] = {
  ...geradoAltura,
  gerado_id: 'g-2',
  tipo: 'bivariado',
  colunas: ['altura_m', 'peso_kg'],
  metodo: 'Cholesky',
  parametros: [{ nome: 'Semente', valor: '5' }],
  semente: 5,
  comparacao: [{ estatistica: 'Correlação (r)', original: 0.7019, gerado: 0.7019, diferenca: 0 }],
};

export const adotadoNovo: Esquemas['Adotado'] = {
  dataset_id: 'ds-novo',
  nome_arquivo: 'gerado-altura_m.csv',
  n_linhas: 500,
  modo: 'novo',
};

export const adotadoAnexo: Esquemas['Adotado'] = {
  dataset_id: ID_DATASET,
  nome_arquivo: NOME_ARQUIVO,
  n_linhas: 730,
  modo: 'anexar',
};
