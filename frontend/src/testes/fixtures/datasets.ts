import type { components } from '../../shared/api/schema';

type Esquemas = components['schemas'];
type TipoColuna = Esquemas['TipoColuna'];
type MetadadosLeitura = Esquemas['MetadadosLeitura'];
type LinhaDados = Esquemas['LinhaDados'];
type ResumoDataset = Esquemas['ResumoDataset'];
type PaginaDataset = Esquemas['PaginaDataset'];
type DatasetCriado = Esquemas['DatasetCriado'];

export const ID_DATASET = 'ds-1';
export const NOME_ARQUIVO = 'pesquisa_saude.txt';

export function criarColuna(
  dados: Pick<TipoColuna, 'coluna' | 'tipo'> & Partial<TipoColuna>,
): TipoColuna {
  return {
    motivo: 'Motivo de teste.',
    origem: 'auto',
    n_validos: 230,
    n_faltantes: 0,
    n_distintos: 10,
    exemplos: [],
    categorias_ordem: [],
    contagens: {},
    ...dados,
  };
}

export const COLUNAS_SAUDE: TipoColuna[] = [
  criarColuna({
    coluna: 'id',
    tipo: 'identificador',
    motivo: 'O nome da coluna indica um código (id).',
    n_distintos: 230,
    exemplos: ['1', '2', '3', '4'],
  }),
  criarColuna({
    coluna: 'sexo',
    tipo: 'binaria',
    motivo: 'Tem só dois valores: F e M.',
    n_distintos: 2,
    exemplos: ['F', 'M'],
  }),
  criarColuna({
    coluna: 'idade',
    tipo: 'discreta',
    motivo: 'Números inteiros com 28 valores diferentes (contagem).',
    n_validos: 229,
    n_faltantes: 1,
    exemplos: ['34', '27', '45', '52'],
  }),
  criarColuna({
    coluna: 'altura_m',
    tipo: 'continua',
    motivo: 'Números com casas decimais.',
    n_validos: 229,
    n_faltantes: 1,
    exemplos: ['1,62', '1,78', '1,58'],
  }),
  criarColuna({
    coluna: 'peso_kg',
    tipo: 'continua',
    motivo: 'Números com casas decimais.',
    n_validos: 227,
    n_faltantes: 3,
    exemplos: ['58,2', '79,6', '63,0'],
  }),
  criarColuna({
    coluna: 'escolaridade',
    tipo: 'ordinal',
    motivo: 'Os valores seguem uma escala conhecida: fundamental < médio < superior < pós.',
    categorias_ordem: ['fundamental', 'médio', 'superior', 'pós'],
    contagens: { fundamental: 38, médio: 96, superior: 71, pós: 25 },
  }),
  criarColuna({
    coluna: 'cidade',
    tipo: 'nominal',
    motivo: 'São categorias sem ordem natural (7 categorias).',
    n_validos: 228,
    n_faltantes: 2,
    exemplos: ['Goiânia', 'Anápolis'],
  }),
  criarColuna({
    coluna: 'satisfacao',
    tipo: 'ordinal',
    motivo: 'Os valores seguem uma escala conhecida: ruim < regular < bom < ótimo.',
    categorias_ordem: ['ruim', 'regular', 'bom', 'ótimo'],
    contagens: { ruim: 21, regular: 54, bom: 102, ótimo: 53 },
  }),
];

export const METADADOS_SAUDE: MetadadosLeitura = {
  formato: 'txt',
  codificacao: 'utf-8',
  separador: ';',
  decimal: ',',
  linha_cabecalho: 1,
  n_linhas: 230,
  n_colunas: 8,
  abas: [],
  avisos: [],
  motivos: {
    formato: 'Pela extensão e pelo conteúdo.',
    separador: 'Aparece 7 vezes em todas as linhas.',
    decimal: 'Valores como 1,72 e 68,4.',
    codificacao: 'Acentos lidos sem erro (Goiânia).',
    cabecalho: 'A 1ª linha tem só nomes, sem números.',
  },
  linhas_iniciais: [
    { numero: 1, celulas: ['id', 'sexo', 'idade'] },
    { numero: 2, celulas: ['1', 'F', '34'] },
    { numero: 3, celulas: ['2', 'M', '27'] },
  ],
};

/** Planilha com título na 1ª linha, linha vazia e o cabeçalho na 3ª. */
export const METADADOS_COM_TITULO: MetadadosLeitura = {
  ...METADADOS_SAUDE,
  formato: 'xlsx',
  separador: null,
  decimal: null,
  codificacao: null,
  linha_cabecalho: 3,
  abas: ['Dados'],
  motivos: {
    formato: 'Pela extensão do arquivo.',
    cabecalho: 'A linha 3 é a primeira só com nomes; as linhas acima ficam de fora.',
  },
  linhas_iniciais: [
    { numero: 1, celulas: ['Pesquisa de satisfação', ''] },
    { numero: 2, celulas: [] },
    { numero: 3, celulas: ['nome', 'nota'] },
    { numero: 4, celulas: ['Ana', '8.5'] },
  ],
};

export const LINHAS_SAUDE: LinhaDados[] = [
  {
    linha: 1,
    valores: {
      id: 1,
      sexo: 'F',
      idade: 34,
      altura_m: 1.62,
      peso_kg: 58.2,
      escolaridade: 'médio',
      cidade: 'Goiânia',
      satisfacao: 'bom',
    },
  },
  {
    linha: 2,
    valores: {
      id: 2,
      sexo: 'M',
      idade: 27,
      altura_m: 1.78,
      peso_kg: null,
      escolaridade: 'fundamental',
      cidade: 'Goiania',
      satisfacao: 'regular',
    },
  },
  {
    linha: 3,
    valores: {
      id: 3,
      sexo: 'F',
      idade: 45,
      altura_m: 1.58,
      peso_kg: 63,
      escolaridade: 'pós',
      cidade: 'Anápolis',
      satisfacao: 'ruim',
    },
  },
];

export function criarResumo(dados: Partial<ResumoDataset> = {}): ResumoDataset {
  return {
    dataset_id: ID_DATASET,
    nome_arquivo: NOME_ARQUIVO,
    metadados: METADADOS_SAUDE,
    n_linhas: 230,
    n_linhas_original: 230,
    n_colunas: 8,
    log_limpeza: [],
    opcoes_leitura: {},
    tem_ajustes: false,
    ...dados,
  };
}

export function criarPagina(resumo: ResumoDataset = criarResumo()): PaginaDataset {
  return {
    resumo,
    versao: 'atual',
    pagina: 1,
    tamanho: 20,
    total_paginas: 12,
    linhas: LINHAS_SAUDE,
  };
}

export const DATASET_CRIADO: DatasetCriado = {
  dataset_id: ID_DATASET,
  nome_arquivo: NOME_ARQUIVO,
  metadados: METADADOS_SAUDE,
  previa: LINHAS_SAUDE,
  colunas: COLUNAS_SAUDE,
};
