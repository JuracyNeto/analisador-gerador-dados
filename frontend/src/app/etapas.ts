import { CAMINHOS } from '../shared/navegacao/caminhos';

export const ETAPAS = [
  { numero: 1, nome: 'Importar', caminho: CAMINHOS.importar },
  { numero: 2, nome: 'Variáveis', caminho: CAMINHOS.variaveis },
  { numero: 3, nome: 'Limpeza', caminho: CAMINHOS.limpeza },
  { numero: 4, nome: 'Análise univariada', caminho: CAMINHOS.analise },
  { numero: 5, nome: 'Bivariada', caminho: CAMINHOS.bivariada },
  { numero: 6, nome: 'Gerador', caminho: CAMINHOS.gerador },
  { numero: 7, nome: 'Detector', caminho: CAMINHOS.detector },
  { numero: 8, nome: 'Relatório', caminho: CAMINHOS.relatorio },
] as const;

export type Etapa = (typeof ETAPAS)[number];

export function etapaDoCaminho(caminho: string): Etapa | undefined {
  return ETAPAS.find(
    (etapa) => caminho === etapa.caminho || caminho.startsWith(`${etapa.caminho}/`),
  );
}
