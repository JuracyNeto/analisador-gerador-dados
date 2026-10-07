import { formatarInteiro } from '../../shared/lib/formatar';
import { contarColunas, contarLinhas } from '../../shared/lib/pluralizar';

export const NOME_EXEMPLO = 'pesquisa_saude.txt';

function linhasEColunas(linhas: number, colunas: number): string {
  return `${contarLinhas(linhas)} e ${contarColunas(colunas)}`;
}

export const TEXTOS_IMPORTAR = {
  titulo: 'Importar arquivo',
  ajuda:
    'Envie sua tabela de dados. Nós descobrimos sozinhos como ela foi escrita, e você confere antes de seguir.',
  area: {
    titulo: 'Arraste e solte seu arquivo aqui',
    soltar: 'Solte para enviar',
    apoio: 'ou escolha no computador. Tamanho máximo: 50 MB.',
    botao: 'Escolher arquivo',
    rotuloEntrada: 'Arquivo de dados',
    rotuloFormatos: 'Formatos aceitos',
    rotuloProgresso: 'Envio em andamento',
    enviando: (nome: string) => `Enviando ${nome}…`,
  },
  formatosAceitos: ['.txt', '.csv', '.tsv', '.xlsx', '.json'],
  exemplo: { pergunta: 'Sem dados à mão?', link: `Abrir ${NOME_EXEMPLO} de exemplo` },
  erro: {
    titulo: (nome: string) => `Não conseguimos ler este arquivo: ${nome}`,
    usarExemplo: 'Usar o arquivo de exemplo',
  },
  deteccoes: {
    titulo: 'O que detectamos',
    lemos: (linhas: number, colunas: number) => `Lemos ${linhasEColunas(linhas, colunas)}.`,
    corrijaAbaixo: 'Se algo estiver diferente do seu arquivo, corrija abaixo.',
    semArquivo: 'Para corrigir a leitura, envie o arquivo de novo.',
  },
  campos: {
    formato: 'Formato',
    separador: 'Separador',
    decimal: 'Decimal',
    codificacao: 'Codificação',
    aba: 'Aba',
    cabecalho: 'Cabeçalho',
  },
  valorDetectado: (valor: string) => `Outro ( ${valor} )`,
  previa: {
    titulo: 'Prévia',
    subtitulo: (n: number, total: number) =>
      `${formatarInteiro(n)} primeiras linhas de ${formatarInteiro(total)}`,
    legenda: 'Prévia dos dados importados',
    carregando: 'Carregando a prévia do arquivo…',
  },
  acoes: { lerDeNovo: 'Ler de novo', lendo: 'Lendo…', continuar: 'Continuar para Variáveis' },
  toast: {
    titulo: (linhas: number, colunas: number) =>
      `Arquivo lido: ${linhasEColunas(linhas, colunas)}.`,
    descricao: 'As etapas 2 a 8 foram liberadas.',
  },
} as const;

export const ROTULOS_FORMATO = {
  txt: 'Texto (TXT)',
  csv: 'CSV',
  tsv: 'TSV (tabulação)',
  xlsx: 'Planilha (XLSX)',
  json: 'JSON',
} as const;

export const OPCOES_SEPARADOR = [
  { valor: ';', rotulo: 'Ponto e vírgula ( ; )' },
  { valor: ',', rotulo: 'Vírgula ( , )' },
  { valor: '\t', rotulo: 'Tabulação' },
  { valor: '|', rotulo: 'Barra vertical ( | )' },
  // A API usa a expressão regular de 2+ espaços para "espaço múltiplo" (SEPARADOR_ESPACOS, spec 01).
  { valor: '\\s{2,}', rotulo: 'Espaço' },
] as const;

export const OPCOES_DECIMAL = [
  { valor: ',', rotulo: 'Vírgula ( , )' },
  { valor: '.', rotulo: 'Ponto ( . )' },
] as const;

export const OPCOES_CODIFICACAO = [
  { valor: 'utf-8', rotulo: 'UTF-8' },
  { valor: 'utf-8-sig', rotulo: 'UTF-8 com BOM' },
  { valor: 'cp1252', rotulo: 'Windows-1252' },
  { valor: 'latin-1', rotulo: 'Latin-1 (ISO-8859-1)' },
] as const;

export const OPCOES_CABECALHO = [
  { valor: 'sim', rotulo: 'Sim, 1ª linha' },
  { valor: 'nao', rotulo: 'Não, só dados' },
] as const;
