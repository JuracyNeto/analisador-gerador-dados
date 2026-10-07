import type { SecaoRelatorio } from './api';

export const TEXTOS_RELATORIO = {
  titulo: 'Relatório',
  ajuda: 'Escolha o que entra. A prévia ao lado mostra exatamente como o relatório será impresso.',
  semDataset: 'Importe um arquivo para montar o relatório.',
  baixar: 'Baixar HTML',
  baixando: 'Gerando…',
  imprimir: 'Imprimir / salvar PDF',
  secoes: 'Seções',
  colunas: 'Colunas',
  rotulosSecoes: {
    leitura: 'Leitura',
    tipos: 'Tipos',
    limpeza: 'Limpeza',
    analises: 'Análises por coluna',
  } satisfies Record<SecaoRelatorio, string>,
  contador: (marcados: number, total: number) => `${String(marcados)} de ${String(total)}`,
  colunasSemAnalises: 'Marque "Análises por coluna" para escolher as colunas.',
  carregandoColunas: 'Carregando as colunas…',
  offline: 'Funciona sem internet',
  offlineAjuda:
    'Embute o motor dos gráficos no arquivo (cerca de 5 MB). Sem isso, o arquivo fica menor, mas os gráficos só aparecem com internet.',
  previa: 'Prévia · A4 retrato',
  tituloPrevia: 'Prévia do relatório',
  montando: 'Montando a prévia do relatório…',
  vazio: {
    titulo: 'Nada para mostrar',
    descricao: 'Marque ao menos uma seção para ver a prévia do relatório.',
  },
  baixado: (nome: string) => `Relatório baixado: ${nome}.`,
  voltar: 'Voltar para Análise',
};
