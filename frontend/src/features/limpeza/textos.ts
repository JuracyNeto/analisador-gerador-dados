import { formatarInteiro } from '../../shared/lib/formatar';
import { contarLinhas, pluralizar } from '../../shared/lib/pluralizar';

export const TEXTOS_LIMPEZA = {
  titulo: 'Limpeza',
  ajuda:
    'Encontramos alguns problemas comuns. Escolha o que fazer com cada um; nada muda até você clicar em "Aplicar limpeza".',
  carregando: 'Procurando problemas nos dados…',
  linhas: {
    singular: 'linha',
    plural: 'linhas',
    eMais: (n: number) => ` e mais ${formatarInteiro(n)}`,
  },
  cards: {
    faltantes: {
      rotulo: 'Faltantes',
      unidade: ['célula', 'células'],
      nenhum: 'Nenhum valor faltando.',
      frase: (colunas: number, maior: string, n: number) =>
        `Em ${pluralizar(colunas, 'coluna', 'colunas')}; ${maior} tem ${formatarInteiro(n)}.`,
    },
    duplicados: {
      rotulo: 'Duplicados',
      unidade: ['linha', 'linhas'],
      nenhum: 'Nenhuma linha repetida.',
      umaOrigem: (linha: number) => `Cópias exatas da linha ${formatarInteiro(linha)}.`,
      variasOrigens: (n: number) => `Cópias de ${pluralizar(n, 'linha', 'linhas')}.`,
    },
    foraDeFaixa: {
      rotulo: 'Fora de faixa',
      unidade: ['valor', 'valores'],
      nenhum: 'Nenhum valor fora da faixa.',
      usuario: 'Fora dos limites que você definiu.',
      iqr: 'Longe demais dos outros valores da coluna.',
    },
    grafias: {
      rotulo: 'Grafias diferentes',
      unidade: ['grupo', 'grupos'],
      nenhum: 'Nenhuma grafia diferente.',
      frase: 'Mesmo texto escrito de jeitos diferentes.',
    },
  },
  secoes: {
    cabecalhoAcao: 'Ação',
    rotuloAcao: (item: string) => `Ação para ${item}`,
    faltantes: {
      titulo: 'Faltantes',
      cabecalhos: ['Coluna', 'Linhas afetadas'],
      subtitulo: (n: number) => pluralizar(n, 'célula vazia', 'células vazias'),
    },
    duplicados: {
      titulo: 'Duplicados',
      cabecalhos: ['Linhas', 'Igual a'],
      subtitulo: (n: number) => pluralizar(n, 'linha igual', 'linhas iguais'),
      igualA: (linhas: string) => `${linhas} (todas as colunas iguais, exceto as de identificador)`,
    },
    foraDeFaixa: {
      titulo: 'Fora de faixa',
      cabecalhos: ['Coluna', 'Valores'],
      subtitulo: (n: number) => pluralizar(n, 'valor', 'valores'),
      faixa: (min: string, max: string, origem: string) =>
        `Faixa aceita: ${min} a ${max} (${origem})`,
      origem: { iqr: 'regra do IQR', usuario: 'seus limites' },
    },
    grafias: {
      titulo: 'Grafias diferentes',
      cabecalhos: ['Grupo', 'Variações encontradas'],
      subtitulo: (n: number, colunas: string) =>
        `${pluralizar(n, 'grupo', 'grupos')} em ${colunas}`,
      naColuna: (coluna: string) => `na coluna ${coluna}`,
    },
    tipoMisto: {
      titulo: 'Textos em colunas de números',
      cabecalhos: ['Coluna', 'Valores'],
      subtitulo: (n: number) => pluralizar(n, 'valor', 'valores'),
    },
  },
  acoes: {
    manter: 'Manter',
    manterNaoInformado: 'Manter como "não informado"',
    preencherMediana: (v: string) => `Preencher com a mediana (${v})`,
    preencherMedia: (v: string) => `Preencher com a média (${v})`,
    preencherModa: (v: string) => `Preencher com a moda (${v})`,
    removerLinha: 'Remover a linha',
    remover: 'Remover',
    removerValor: 'Remover o valor',
    limitar: (min: string, max: string) => `Limitar ao limite (${min} a ${max})`,
    unificar: (variacoes: string, forma: string) => `Unificar ${variacoes} → '${forma}'`,
  },
  limites: {
    titulo: 'Limites por coluna',
    subtitulo: 'Opcional. Valores fora destes limites contam como "fora de faixa".',
    minimo: 'Mínimo',
    maximo: 'Máximo',
    erroNumero: 'Use só números, com vírgula para decimais (ex.: 1,72).',
    erroOrdem: (max: string) =>
      `O mínimo precisa ser menor que o máximo (${max}). Ajuste um dos dois.`,
  },
  log: {
    titulo: 'O que fizemos',
    rotulo: 'Registro das ações',
    carregando: 'Carregando o registro…',
    vazio: 'Nada aplicado ainda. As ações que você aplicar aparecem aqui.',
    resultado: 'Resultado:',
    eram: (n: number) => ` (eram ${formatarInteiro(n)}).`,
  },
  botoes: {
    desfazer: 'Desfazer tudo',
    desfazendo: 'Desfazendo…',
    aplicar: 'Aplicar limpeza',
    aplicando: 'Aplicando…',
    semAcoes: 'Escolha ao menos uma ação diferente de "Manter".',
  },
  vazio: {
    titulo: 'Nenhum problema encontrado',
    descricao:
      'Não encontramos problemas comuns: sem faltantes, duplicados, valores fora de faixa ou grafias diferentes.',
    continuar: 'Continuar para Análise',
  },
  toast: {
    aplicada: (removidas: number) =>
      removidas === 0
        ? 'Limpeza aplicada: nenhuma linha removida.'
        : `Limpeza aplicada: ${pluralizar(removidas, 'linha removida', 'linhas removidas')}.`,
    acoes: (n: number) => `${pluralizar(n, 'ação aplicada', 'ações aplicadas')}.`,
    desfeita: (n: number) => `Limpeza desfeita: voltamos às ${contarLinhas(n)} do arquivo.`,
  },
} as const;
