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
  cartao: {
    porQue: 'Por que chama atenção',
    podeSerNormal: 'Pode ser normal se…',
    exemplo: 'Exemplo',
    verNaTabela: 'Ver na tabela',
    oQueFazer: 'O que fazer:',
    verExplicacao: 'Ver explicação',
    ocultarExplicacao: 'Ocultar explicação',
  },
  detalhes: {
    titulo: 'Detalhes técnicos',
    medida: 'Medida',
    valor: 'Valor',
    limiar: 'Limiar',
    teste: 'Teste',
    pValor: 'p-valor',
    formula: 'Fórmula',
    traducao: (texto: string): string => `· ${texto}`,
  },
  separadorPar: ' × ',
  regra: (aviso: Pick<Aviso, 'regra' | 'nome_regra'>): string =>
    `${aviso.regra} · ${aviso.nome_regra}`,
} as const;
