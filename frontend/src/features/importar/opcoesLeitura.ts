/** Detecções da leitura (MetadadosLeitura) ↔ campos da tela 1a ↔ formulário do POST /datasets. */
import type { components, paths } from '../../shared/api/schema';
import {
  OPCOES_CABECALHO,
  OPCOES_CODIFICACAO,
  OPCOES_DECIMAL,
  OPCOES_SEPARADOR,
  ROTULOS_FORMATO,
  TEXTOS_IMPORTAR as T,
} from './textos';

export type MetadadosLeitura = components['schemas']['MetadadosLeitura'];
type CorpoImportacao = NonNullable<
  paths['/api/datasets']['post']['requestBody']
>['content']['multipart/form-data'];
/** Opções de leitura que sobrescrevem a detecção (separador, decimal, codificacao, aba, tem_cabecalho). */
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

function valorCabecalho(tem: boolean | null): string | null {
  if (tem === null) return null;
  return tem ? 'sim' : 'nao';
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
  cabecalho: (m) => descrever('cabecalho', valorCabecalho(m.tem_cabecalho), OPCOES_CABECALHO, m),
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
  if (campo === 'cabecalho') return { ...opcoes, tem_cabecalho: valor === 'sim' };
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
