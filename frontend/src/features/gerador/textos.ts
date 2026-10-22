import type { IdAba, Modo, Origem, TipoManual } from './tipos';

const TIPOS_NO_PLURAL = new Map([
  ['nominal', 'qualitativas nominais'],
  ['ordinal', 'qualitativas ordinais'],
]);

export const TEXTOS_GERADOR = {
  titulo: 'Gerador de dados',
  ajuda: 'Crie dados artificiais parecidos com os seus, ou com parâmetros que você escolher.',
  abas: { univariado: 'Univariado', bivariado: 'Bivariado' } satisfies Record<IdAba, string>,
  rotuloAbas: 'Tipo de geração',
  origem: {
    rotulo: 'Origem',
    univariado: { coluna: 'Coluna do dataset', manual: 'Parâmetros manuais' },
    bivariado: { coluna: 'Par do dataset', manual: 'Parâmetros manuais' },
    semPar: 'Este arquivo tem menos de duas colunas numéricas; gere o par com parâmetros manuais.',
  } satisfies { rotulo: string; semPar: string } & Record<IdAba, Record<Origem, string>>,
  coluna: 'Coluna',
  tipo: 'Tipo',
  tipos: {
    continua: 'Contínua',
    discreta: 'Discreta',
    binaria: 'Binária',
  } satisfies Record<TipoManual, string>,
  quantidade: 'Quantidade de valores (X)',
  quantidadePares: 'Quantidade de pares',
  modo: 'Modo',
  modos: {
    preservar: 'Preservar estatísticas',
    parametros: 'Novos parâmetros',
  } satisfies Record<Modo, string>,
  descricaoPreservar: (media: string, desvio: string) =>
    `Mesma média (${media}) e desvio (${desvio}) da coluna.`,
  descricaoPreservarCategorias: 'Mesmas frequências da coluna.',
  descricaoPreservarBinaria: (sucesso: string, chance: string) =>
    `Mesma chance de ${sucesso} (${chance}) da coluna.`,
  tipoNoPlural: (tipo: string) => TIPOS_NO_PLURAL.get(tipo) ?? tipo,
  soPreservar: (tipo: string) =>
    `Novos parâmetros não se aplicam a ${tipo}: só dá para preservar as frequências.`,
  media: 'Média',
  desvio: 'Desvio',
  chance: (sucesso: string) => `Chance de ${sucesso}`,
  chanceSemOrigem: 'Chance de 1',
  semente: 'Semente',
  sementeAjuda: '(repete o mesmo resultado)',
  limitar: 'Limitar à faixa original',
  limitarAjuda: (minimo: string, maximo: string) =>
    `Nenhum valor abaixo de ${minimo} ou acima de ${maximo}.`,
  x: 'X',
  y: 'Y',
  mediaDe: (coluna: string) => `Média de ${coluna}`,
  desvioDe: (coluna: string) => `Desvio de ${coluna}`,
  rho: 'Correlação alvo (ρ)',
  exato: 'Ajuste exato',
  exatoAjuda: 'A correlação dos dados gerados fica exatamente igual a ρ.',
  gerar: 'Gerar dados',
  gerando: 'Gerando…',
  carregandoOrigem: 'Lendo as medidas da coluna…',
  erros: {
    quantidade: 'Digite um número inteiro entre 1 e 1.000.000.',
    quantidadePares: 'Digite um número inteiro entre 3 e 1.000.000.',
    numero: 'Digite um número, por exemplo 70,3.',
    desvio: 'O desvio precisa ser maior que zero.',
    chance: 'Use um valor entre 0 e 1, por exemplo 0,5.',
    semente: 'A semente precisa ser um número inteiro entre 0 e 4.294.967.295.',
  },
  resultado: {
    titulo: 'Original × Gerado',
    subtitulo: (semente: number, modo: string) => `Semente ${String(semente)} · ${modo}`,
    medida: 'Medida',
    original: 'Original',
    gerado: (n: string) => `Gerado (${n})`,
    diferenca: 'Diferença',
    legenda: 'Comparação entre os dados originais e os gerados',
    comoGeramos: 'Como geramos',
    vazio: {
      titulo: 'Nenhum dado gerado ainda',
      descricao: 'Preencha o formulário e clique em Gerar dados.',
    },
    gerandoDados: 'Gerando os dados…',
  },
  modoNoSubtitulo: { bivariado: 'correlação alvo' },
  acoes: {
    baixar: 'Baixar CSV',
    anexar: 'Anexar ao dataset atual',
    usar: 'Usar como novo dataset',
  },
  toast: {
    valores: (n: string) => `Geramos ${n} valores.`,
    pares: (n: string) => `Geramos ${n} pares.`,
    baixado: (nome: string) => `CSV baixado: ${nome}.`,
    anexado: (n: string, arquivo: string) => `Anexamos ${n} linhas a ${arquivo}.`,
    novo: (n: string) => `Novo dataset criado: ${n} linhas.`,
  },
  descricaoSessao: (colunas: string, n: string) => `${colunas} · ${n}`,
  /** Geração que saiu da memória do servidor (D149): refaz o mesmo pedido, com a mesma semente. */
  expirado: {
    descricao: (semente: number) =>
      `Gere de novo: com a mesma semente (${String(semente)}), os dados saem iguais.`,
    acao: 'Gerar de novo',
  },
  navegacao: { voltar: 'Voltar para Bivariada', continuar: 'Continuar para Detector' },
};
