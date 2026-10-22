import { contarColunas, contarLinhas } from '../shared/lib/pluralizar';

export const TEXTOS_APP = {
  marcaLinha1: 'Analisador e Gerador',
  marcaLinha2: 'de Dados',
  simboloMarca: 'x̄',
  etapasDaAnalise: 'Etapas da análise',
  barraLateral: 'Barra lateral',
  etapasBloqueadas: 'As etapas 2 a 8 ficam disponíveis depois de importar um arquivo.',
  concluida: 'Concluída',
  bloqueada: 'Bloqueada',
  recolherBarra: 'Recolher barra',
  expandirBarra: 'Expandir barra',
  fecharBarra: 'Fechar a barra de etapas',
  nenhumArquivo: 'Nenhum arquivo importado',
  trocarArquivo: 'Trocar arquivo',
  trocaComAjustes: {
    aviso: 'Trocar de arquivo desfaz o trabalho feito neste.',
    detalhe: 'Os tipos corrigidos, a limpeza e os dados gerados não vêm junto.',
    confirmar: 'Trocar mesmo assim',
    cancelar: 'Cancelar',
  },
  dimensoes: (linhas: number, colunas: number): string =>
    `${contarLinhas(linhas)} × ${contarColunas(colunas)}`,
  tema: 'Tema',
  temaClaro: 'Tema claro',
  temaEscuro: 'Tema escuro',
  pularParaConteudo: 'Pular para o conteúdo',
  abrindoEtapa: 'Abrindo a etapa…',
} as const;
