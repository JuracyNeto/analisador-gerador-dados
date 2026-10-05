import { formatarInteiro } from '../shared/lib/formatar';
import type { EtapaFutura } from './etapas';

function quantidade(n: number, singular: string, plural: string): string {
  return `${formatarInteiro(n)} ${n === 1 ? singular : plural}`;
}

export const TEXTOS_APP = {
  marcaLinha1: 'Analisador e Gerador',
  marcaLinha2: 'de Dados',
  simboloMarca: 'x̄',
  etapasDaAnalise: 'Etapas da análise',
  etapasBloqueadas: 'As etapas 2 a 8 ficam disponíveis depois que você importar um arquivo.',
  concluida: 'Concluída',
  bloqueada: 'Bloqueada',
  recolherBarra: 'Recolher barra',
  expandirBarra: 'Expandir barra',
  fecharBarra: 'Fechar a barra de etapas',
  disponivelNaVersao: (versao: string): string => `Disponível na versão ${versao}.`,
  nenhumArquivo: 'Nenhum arquivo importado',
  trocarArquivo: 'Trocar arquivo',
  dimensoes: (linhas: number, colunas: number): string =>
    `${quantidade(linhas, 'linha', 'linhas')} × ${quantidade(colunas, 'coluna', 'colunas')}`,
  tema: 'Tema',
  temaClaro: 'Tema claro',
  temaEscuro: 'Tema escuro',
  pularParaConteudo: 'Pular para o conteúdo',
  abrindoEtapa: 'Abrindo a etapa…',
  ajudaFutura: 'Esta etapa faz parte do roteiro do projeto e ainda não foi liberada.',
  titulosFuturos: {
    5: 'Análise bivariada',
    6: 'Gerador de dados',
    7: 'Detector de dados artificiais',
  } satisfies Record<EtapaFutura['numero'], string>,
} as const;
