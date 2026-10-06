import { escolherForma, pluralizar } from '../../shared/lib/pluralizar';
import type { IdAba, TipoSeparatriz } from './tipos';

export const TEXTOS_ANALISE = {
  titulo: 'Análise univariada',
  ajuda:
    'Uma coluna por vez: como os valores se distribuem, onde fica o centro e quanto eles variam.',
  rotuloColuna: 'Coluna',
  rotuloAbas: 'Análises',
  abas: {
    frequencias: 'Frequências',
    tendencia: 'Tendência central',
    separatrizes: 'Separatrizes',
    dispersao: 'Dispersão',
    graficos: 'Gráficos',
  } satisfies Record<IdAba, string>,
  motivoPadrao: 'Não se aplica ao tipo desta coluna.',
  carregandoColunas: 'Carregando as colunas…',
  calculando: (coluna: string) => `Calculando as estatísticas de ${coluna}…`,
  semDataset: 'Importe um arquivo para analisar as colunas, uma de cada vez.',
  semColunas: {
    titulo: 'Nenhuma coluna para analisar',
    descricao:
      'Todas as colunas estão como identificador e ficam fora das análises. Corrija os tipos na etapa Variáveis.',
    acao: 'Ir para Variáveis',
  },
  frequencias: {
    tituloClasses: 'Tabela de frequências por classe',
    titulo: (coluna: string) => `Frequências de ${coluna}`,
    classe: 'Classe',
    pontoMedio: 'Ponto médio',
    fi: 'fi',
    fr: 'fr%',
    fiAcumulada: 'Fi',
    frAcumulada: 'Fr%',
    frAcumuladaNaoAplicavel: 'Fr% acum.',
    total: 'Total',
    naoSeAplica: 'Não se aplica',
    notaClasses: (h: string) =>
      `⊢ inclui o limite da esquerda e exclui o da direita. Amplitude de cada classe: h = ${h}.`,
    faltantes: (n: number) =>
      `${pluralizar(n, 'faltante', 'faltantes')} ${escolherForma(n, 'ficou', 'ficaram')} de fora.`,
    numeroClasses: 'Número de classes',
    menos: 'Diminuir o número de classes',
    mais: 'Aumentar o número de classes',
    sturges: (k: number) => `Sturges: ${String(k)}`,
  },
  cartoes: {
    media: 'Média',
    mediana: 'Mediana',
    moda: 'Moda',
    /** Linha de apoio do card "Moda" na contínua; `calculo` vem pronto do backend ("Mo = …"). */
    apoioCzuber: (calculo: string) => `Moda de Czuber, pelas classes: ${calculo}`,
    proporcao: 'Proporção',
    desvioPadrao: 'Desvio padrão',
    cv: 'Coeficiente de variação',
    iqr: 'Intervalo interquartil (IQR)',
    amplitude: 'Amplitude',
    variancia: 'Variância',
    semModa: 'Sem moda',
    seloModa: {
      amodal: undefined,
      unimodal: undefined,
      bimodal: 'Bimodal',
      multimodal: 'Multimodal',
    },
    seloCv: { baixa: 'Variação baixa', media: 'Variação moderada', alta: 'Variação alta' },
    notaVariancia: 'Fica na unidade dos dados ao quadrado; para ler, use o desvio padrão.',
    populacional: (desvio: string, variancia: string) =>
      `Valores amostrais (n − 1). Se os dados forem a população inteira: σ = ${desvio} e σ² = ${variancia}.`,
    faixasCv: 'CV abaixo de 15% indica variação baixa; de 15% a 30%, moderada; acima de 30%, alta.',
  },
  separatrizes: {
    titulo: (coluna: string) => `Separatrizes de ${coluna}`,
    quartis: 'Quartis',
    decis: 'Decis',
    percentis: 'Percentis',
    verTodos: 'Ver os 99 percentis',
    todosPercentis: 'Todos os percentis',
  },
  posicao: {
    titulo: 'Onde está meu valor?',
    campo: (coluna: string) => `Valor de ${coluna}`,
    comparar: 'Comparar com',
    tipos: { quartil: 'Quartil', decil: 'Decil', percentil: 'Percentil' } satisfies Record<
      TipoSeparatriz,
      string
    >,
    dica: 'Digite um valor para ver em que parte dos dados ele cai.',
    erroValor: 'Digite um número. Use vírgula para decimais, como 72,5.',
    foraTitulo: 'Fora da faixa observada.',
    abaixo: (minimo: string) => `O valor está abaixo do menor dado observado (${minimo}).`,
    acima: (maximo: string) => `O valor está acima do maior dado observado (${maximo}).`,
    minimo: 'mín',
    maximo: 'máx',
    descricaoRegua: (d: {
      minimo: string;
      maximo: string;
      marcas: string;
      valor: string;
      regiao: string;
    }) =>
      `Régua de ${d.minimo} a ${d.maximo} com ${d.marcas}; o valor ${d.valor} fica no ${d.regiao}.`,
  },
  graficos: {
    tipoGrafico: 'Tipo de gráfico',
    recomendado: 'recomendado',
    porque: 'Por que este gráfico?',
    resumo: 'Resumo do gráfico',
    semFiguras: {
      titulo: 'Nenhum gráfico disponível',
      descricao: 'Não há gráficos para esta coluna.',
    },
  },
};
