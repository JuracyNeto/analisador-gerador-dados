import { CAMINHOS } from '../shared/navegacao/caminhos';

export const ETAPAS = [
  { numero: 1, nome: 'Importar', caminho: CAMINHOS.importar },
  { numero: 2, nome: 'Variáveis', caminho: CAMINHOS.variaveis },
  { numero: 3, nome: 'Limpeza', caminho: CAMINHOS.limpeza },
  { numero: 4, nome: 'Análise univariada', caminho: CAMINHOS.analise },
  { numero: 5, nome: 'Bivariada', caminho: '/bivariada', disponivelEm: 'v0.2' },
  { numero: 6, nome: 'Gerador', caminho: '/gerador', disponivelEm: 'v0.3' },
  { numero: 7, nome: 'Detector', caminho: '/detector', disponivelEm: 'v0.3' },
  { numero: 8, nome: 'Relatório', caminho: CAMINHOS.relatorio },
] as const;

export type Etapa = (typeof ETAPAS)[number];

/** Etapa que ainda não existe nesta versão (D60). */
export type EtapaFutura = Extract<Etapa, { disponivelEm: string }>;

export function ehEtapaFutura(etapa: Etapa): etapa is EtapaFutura {
  return 'disponivelEm' in etapa;
}

export function etapaDoCaminho(caminho: string): Etapa | undefined {
  return ETAPAS.find(
    (etapa) => caminho === etapa.caminho || caminho.startsWith(`${etapa.caminho}/`),
  );
}
