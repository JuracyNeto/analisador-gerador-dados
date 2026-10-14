import type { Aviso } from './tipos';

/** Textos da etapa 7 (telas 7a–7d, spec 16). */
export const TEXTOS_DETECTOR = {
  titulo: 'Detector de dados artificiais',
  ajuda:
    'Aplicamos 11 regras que procuram sinais comuns de dados inseridos ou gerados. Um alerta pede conferência, não é uma conclusão.',
  semDataset: 'Importe um arquivo para procurar sinais de dados inseridos ou gerados.',
  navegacao: { voltar: 'Voltar para Gerador', continuar: 'Continuar para Relatório' },
  alertasPorSeveridade: 'Alertas por severidade',
  mostrar: 'Mostrar',
  agruparPor: 'Agrupar por',
  agrupamentos: { coluna: 'Coluna', regra: 'Regra' },
  chip: (palavra: string, quantidade: number): string => `${palavra} (${String(quantidade)})`,
  linhasInteiras: 'Linhas inteiras',
  separadorPar: ' × ',
  regra: (aviso: Pick<Aviso, 'regra' | 'nome_regra'>): string =>
    `${aviso.regra} · ${aviso.nome_regra}`,
} as const;
