import { pluralizar } from '../../shared/lib/pluralizar';
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
  analisarDeNovo: 'Analisar de novo',
  analisando: 'Analisando…',
  analisadoDeNovo: (frase: string): string => `Análise refeita: ${frase}.`,
  carregando: (arquivo: string): string => `Aplicando as 11 regras em ${arquivo}…`,
  alertasNoGrupo: (quantidade: number): string => pluralizar(quantidade, 'alerta', 'alertas'),
  semSeveridade: 'Marque ao menos uma severidade para ver os alertas.',
  semAlertasMarcados: 'Nenhum alerta com as severidades marcadas. Marque outra severidade acima.',
  naoVerificadas: {
    titulo: 'Regras não verificadas',
    complemento: (quantidade: number): string =>
      `${pluralizar(quantidade, 'regra', 'regras')}, com motivo`,
  },
  vazio: {
    titulo: 'Nenhum alerta',
    verRegras: 'Ver as 11 regras',
    textoPadrao:
      'Nenhuma das 11 regras encontrou suspeitas. Isso não garante que os dados sejam reais, mas não vimos sinais comuns de dados artificiais.',
  },
  regras: {
    titulo: 'As 11 regras do detector',
    subtitulo: 'Cada regra procura um sinal comum de dados inseridos ou gerados.',
    rotuloCorpo: 'Lista das regras',
  },
  drawer: {
    rotuloCorpo: 'Linhas do alerta',
    legenda: (titulo: string): string => `${titulo}, com as linhas do alerta destacadas`,
    linha: 'linha',
    destacada: ' (destacada)',
    destacadas: (quantidade: number): string =>
      `${pluralizar(quantidade, 'linha destacada', 'linhas destacadas')}.`,
    carregando: 'Buscando as linhas…',
    exportar: 'Exportar estas linhas',
    rodape: (trechos: string, total: string | null): string =>
      total === null ? `Linhas ${trechos}` : `Linhas ${trechos} de ${total}`,
  },
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
  separadorTitulo: ' · ',
  regra: (aviso: Pick<Aviso, 'regra' | 'nome_regra'>): string =>
    `${aviso.regra} · ${aviso.nome_regra}`,
} as const;

/** Nome e intuição de cada regra ("Ver as 11 regras", tela 7c); nomes iguais aos da API (spec 16). */
export const REGRAS_DETECTOR = [
  {
    regra: 'R1',
    nome: 'Bloco alinhado',
    intuicao:
      "Em dados reais, pedaços pequenos variam bastante; um bloco que 'bate' tudo pode ter sido colocado para alinhar as estatísticas.",
  },
  {
    regra: 'R2',
    nome: 'Correlação por blocos',
    intuicao:
      "Se poucos dados novos fazem a correlação subir muito, eles podem ter sido adicionados para 'puxar' a relação.",
  },
  {
    regra: 'R3',
    nome: 'Formato numérico',
    intuicao: 'Uma mudança de formato no meio dos dados pode indicar outra origem.',
  },
  {
    regra: 'R4',
    nome: 'Valores redondos',
    intuicao:
      'Quando números são inventados ou digitados de cabeça, as pessoas tendem a arredondar.',
  },
  {
    regra: 'R5',
    nome: 'Duplicatas',
    intuicao: 'Linhas repetidas podem ter sido copiadas de outras partes do arquivo.',
  },
  {
    regra: 'R6',
    nome: 'Comparação temporal',
    intuicao: 'Dados novos que copiam os antigos ou variam pouco demais podem ter sido inseridos.',
  },
  {
    regra: 'R7',
    nome: 'Valores distantes',
    intuicao: 'Valores extremos podem ser erros de digitação ou casos especiais.',
  },
  {
    regra: 'R8',
    nome: 'Lei de Benford',
    intuicao:
      "Em muitos dados reais, o dígito 1 aparece no início cerca de 30% das vezes; números inventados tendem a ser mais 'uniformes'.",
  },
  {
    regra: 'R9',
    nome: 'Último dígito',
    intuicao:
      'Medições reais têm o último dígito quase aleatório; pessoas evitam ou repetem certos dígitos.',
  },
  {
    regra: 'R10',
    nome: 'Normal perfeita demais',
    intuicao:
      'Dados reais quase nunca são tão perfeitos; isso é típico de números gerados por computador.',
  },
  {
    regra: 'R11',
    nome: 'Sequência',
    intuicao: 'Em dados reais, a sequência costuma parecer aleatória.',
  },
] as const;
