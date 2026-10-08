import { formatarInteiro } from '../../shared/lib/formatar';
import type { TipoVariavel } from '../../shared/ui/tiposVariavel';

export const TEXTOS_VARIAVEIS = {
  titulo: 'Variáveis',
  ajuda:
    'Classificamos cada coluna pelo que ela contém. Confira o motivo e corrija o tipo se não concordar.',
  carregando: 'Carregando os tipos das colunas…',
  resumo: 'Resumo dos tipos',
  tabela: {
    legenda: 'Tipos detectados por coluna',
    coluna: 'Coluna',
    tipo: 'Tipo detectado',
    motivo: 'Por quê',
    validos: 'Válidos / faltantes',
    exemplos: 'Exemplos',
    corrigir: 'Corrigir tipo',
    rotuloSelect: (coluna: string) => `Tipo de ${coluna}`,
  },
  ordem: {
    titulo: 'Ordem das categorias',
    instrucao:
      'Arraste para mudar a ordem, do menor para o maior. Pelo teclado: foque um item e use ↑ e ↓.',
    rotuloLista: (coluna: string) => `Ordem das categorias de ${coluna}`,
    movendo: 'Movendo…',
    mover: (nome: string) => `Mover ${nome}`,
    subir: (nome: string) => `Subir ${nome}`,
    descer: (nome: string) => `Descer ${nome}`,
    anuncio: (nome: string, posicao: number, total: number) =>
      `${nome} agora está na posição ${formatarInteiro(posicao)} de ${formatarInteiro(total)}.`,
  },
  toastTipo: (coluna: string, rotuloTipo: string) =>
    `Tipo de ${coluna} alterado para ${rotuloTipo}.`,
  continuar: 'Continuar para Limpeza',
  voltar: 'Voltar para Importar',
} as const;

/** Singular e plural no resumo do topo ("2 contínuas · 1 discreta"). */
export const NOMES_RESUMO = {
  continua: ['contínua', 'contínuas'],
  discreta: ['discreta', 'discretas'],
  ordinal: ['ordinal', 'ordinais'],
  nominal: ['nominal', 'nominais'],
  binaria: ['binária', 'binárias'],
  data: ['data', 'datas'],
  identificador: ['identificador', 'identificadores'],
} as const satisfies Record<TipoVariavel, readonly [string, string]>;
