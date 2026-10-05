import { contarColunas, contarLinhas } from '../shared/lib/pluralizar';
import type { EtapaFutura } from './etapas';

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
    `${contarLinhas(linhas)} × ${contarColunas(colunas)}`,
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
