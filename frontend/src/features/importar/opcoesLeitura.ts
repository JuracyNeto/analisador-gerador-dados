/** Detecções da leitura (MetadadosLeitura) ↔ campos da tela 1a ↔ formulário do POST /datasets. */
import type { components, paths } from '../../shared/api/schema';
import {
  OPCOES_CODIFICACAO,
  OPCOES_DECIMAL,
  OPCOES_SEPARADOR,
  ROTULOS_FORMATO,
  rotuloLinha,
  SEM_CABECALHO,
  TEXTOS_IMPORTAR as T,
} from './textos';

export type MetadadosLeitura = components['schemas']['MetadadosLeitura'];
type CorpoImportacao = NonNullable<
  paths['/api/datasets']['post']['requestBody']
>['content']['multipart/form-data'];
/** Opções de leitura que sobrescrevem a detecção (separador, decimal, codificacao, aba, linha_cabecalho). */
export type OpcoesLeitura = Partial<Omit<CorpoImportacao, 'arquivo'>>;

export type CampoDeteccao = keyof typeof T.campos;

export interface OpcaoLeitura {
  valor: string;
  rotulo: string;
}

export interface DescricaoCampo {
  campo: CampoDeteccao;
  rotulo: string;
  valor: string;
  rotuloValor: string;
  opcoes: readonly OpcaoLeitura[];
  motivo: string;
  corrigivel: boolean;
}

type Construtor = (meta: MetadadosLeitura, opcoes: OpcoesLeitura) => DescricaoCampo | null;

const ORDEM_CAMPOS: readonly CampoDeteccao[] = [
  'formato',
  'separador',
  'decimal',
  'codificacao',
  'aba',
  'cabecalho',
];

function comDetectado(lista: readonly OpcaoLeitura[], valor: string): readonly OpcaoLeitura[] {
  return lista.some((o) => o.valor === valor)
    ? lista
    : [...lista, { valor, rotulo: T.valorDetectado(valor) }];
}

function descrever(
  campo: CampoDeteccao,
  valor: string | null | undefined,
  lista: readonly OpcaoLeitura[],
  meta: MetadadosLeitura,
): DescricaoCampo | null {
  if (valor === null || valor === undefined) return null;
  const opcoes = comDetectado(lista, valor);
  return {
    campo,
    rotulo: T.campos[campo],
    valor,
    rotuloValor: opcoes.find((o) => o.valor === valor)?.rotulo ?? valor,
    opcoes,
    motivo: meta.motivos[campo] ?? '',
    corrigivel: campo !== 'formato',
  };
}

/** Linhas não vazias do início do arquivo + "Sem cabeçalho" (valor 0). */
function opcoesCabecalho(meta: MetadadosLeitura): readonly OpcaoLeitura[] {
  const linhas = meta.linhas_iniciais
    .filter((linha) => linha.celulas.length > 0)
    .map((linha) => ({ valor: String(linha.numero), rotulo: rotuloLinha(linha.numero) }));
  return [...linhas, SEM_CABECALHO];
}

function descreverCabecalho(meta: MetadadosLeitura): DescricaoCampo | null {
  const linha = meta.linha_cabecalho;
  return descrever('cabecalho', linha === null ? null : String(linha), opcoesCabecalho(meta), meta);
}

function descreverAba(meta: MetadadosLeitura, opcoes: OpcoesLeitura): DescricaoCampo | null {
  const lista = meta.abas.map((aba) => ({ valor: aba, rotulo: aba }));
  return descrever('aba', opcoes.aba ?? meta.abas[0], lista, meta);
}

const CONSTRUTORES: Record<CampoDeteccao, Construtor> = {
  formato: (m) =>
    descrever('formato', m.formato, [{ valor: m.formato, rotulo: ROTULOS_FORMATO[m.formato] }], m),
  separador: (m) => descrever('separador', m.separador, OPCOES_SEPARADOR, m),
  decimal: (m) => descrever('decimal', m.decimal, OPCOES_DECIMAL, m),
  codificacao: (m) => descrever('codificacao', m.codificacao, OPCOES_CODIFICACAO, m),
  aba: descreverAba,
  cabecalho: descreverCabecalho,
};

export function descreverDeteccoes(
  meta: MetadadosLeitura,
  opcoes: OpcoesLeitura,
): DescricaoCampo[] {
  return ORDEM_CAMPOS.map((campo) => CONSTRUTORES[campo](meta, opcoes)).filter(
    (descricao): descricao is DescricaoCampo => descricao !== null,
  );
}

/** Acumula a correção escolhida no Select; a releitura manda todas as correções juntas. */
export function aplicarCorrecao(
  opcoes: OpcoesLeitura,
  campo: CampoDeteccao,
  valor: string,
): OpcoesLeitura {
  if (campo === 'formato') return opcoes;
  if (campo === 'cabecalho') return { ...opcoes, linha_cabecalho: Number(valor) };
  return { ...opcoes, [campo]: valor };
}

export function montarFormulario(arquivo: File, opcoes: OpcoesLeitura): FormData {
  const formulario = new FormData();
  formulario.append('arquivo', arquivo);
  for (const [chave, valor] of Object.entries(opcoes)) {
    if (valor !== null) formulario.append(chave, String(valor));
  }
  return formulario;
}
