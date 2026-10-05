import type { components } from '../../shared/api/schema';
import { COLUNAS_SAUDE } from './datasets';

type Esquemas = components['schemas'];
type Diagnostico = Esquemas['Diagnostico'];
type EntradaLog = Esquemas['EntradaLog'];
type ResultadoLimpeza = Esquemas['ResultadoLimpeza'];

export const DIAGNOSTICO_SAUDE: Diagnostico = {
  n_linhas: 230,
  faltantes: [
    {
      coluna: 'peso_kg',
      n: 3,
      linhas: [12, 141, 207],
      sugeridos: { media: 70.3, mediana: 69.8, moda: 72 },
    },
    {
      coluna: 'cidade',
      n: 2,
      linhas: [64, 190],
      sugeridos: { media: null, mediana: null, moda: 'Goiânia' },
    },
  ],
  duplicados: [{ linha_original: 44, copias: [45, 46, 47] }],
  fora_de_faixa: [
    {
      coluna: 'idade',
      limite_inferior: 1,
      limite_superior: 110,
      origem: 'usuario',
      ocorrencias: [
        { linha: 19, valor: 0 },
        { linha: 201, valor: 230 },
      ],
    },
    {
      coluna: 'peso_kg',
      limite_inferior: 38.5,
      limite_superior: 102.1,
      origem: 'iqr',
      ocorrencias: [
        { linha: 99, valor: 6.8 },
        { linha: 160, valor: 712 },
      ],
    },
  ],
  inconsistencias: [
    {
      coluna: 'cidade',
      grupos: [
        {
          forma_preferida: 'Goiânia',
          variacoes: [
            { texto: 'Goiânia', n: 80 },
            { texto: 'Goiania', n: 6 },
            { texto: 'goiânia', n: 2 },
          ],
        },
        {
          forma_preferida: 'Anápolis',
          variacoes: [
            { texto: 'Anápolis', n: 40 },
            { texto: 'Anapolis', n: 3 },
          ],
        },
      ],
    },
  ],
  tipo_misto: [],
};

export const DIAGNOSTICO_VAZIO: Diagnostico = {
  n_linhas: 227,
  faltantes: [],
  duplicados: [],
  fora_de_faixa: [],
  inconsistencias: [],
  tipo_misto: [],
};

export function criarEntradaLog(dados: Partial<EntradaLog> = {}): EntradaLog {
  return {
    problema: 'duplicados',
    acao: 'remover',
    coluna: null,
    linhas_afetadas: [45, 46, 47],
    antes_exemplo: '',
    depois_exemplo: '',
    quando: '2026-10-20T10:00:00Z',
    frase: 'Removemos 3 linhas duplicadas.',
    ...dados,
  };
}

export function criarResultado(dados: Partial<ResultadoLimpeza> = {}): ResultadoLimpeza {
  return {
    log: [criarEntradaLog()],
    n_linhas: 227,
    n_linhas_original: 230,
    colunas: COLUNAS_SAUDE,
    ...dados,
  };
}
