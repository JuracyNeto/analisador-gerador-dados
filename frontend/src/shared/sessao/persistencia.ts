import type { DatasetSessao, GeradoSessao } from './tipos';

const CHAVE_SESSAO = 'sessao';

export interface EstadoSessao {
  readonly dataset: DatasetSessao | null;
  readonly etapasVisitadas: readonly number[];
  readonly ultimoGerado?: GeradoSessao;
}

export const SESSAO_VAZIA: EstadoSessao = { dataset: null, etapasVisitadas: [] };

function ehRegistro(valor: unknown): valor is Record<string, unknown> {
  return typeof valor === 'object' && valor !== null && !Array.isArray(valor);
}

function lerJson(texto: string): unknown {
  try {
    return JSON.parse(texto);
  } catch {
    return null;
  }
}

function lerDataset(valor: unknown): DatasetSessao | null {
  if (!ehRegistro(valor)) return null;
  const { id, nomeArquivo } = valor;
  return typeof id === 'string' && typeof nomeArquivo === 'string' ? { id, nomeArquivo } : null;
}

function lerGerado(valor: unknown): GeradoSessao | null {
  if (!ehRegistro(valor)) return null;
  const { id, descricao } = valor;
  return typeof id === 'string' && typeof descricao === 'string' ? { id, descricao } : null;
}

/** Acrescenta a última geração só quando existe (exactOptionalPropertyTypes). */
export function comGerado(estado: EstadoSessao, gerado: GeradoSessao | null): EstadoSessao {
  const base = { dataset: estado.dataset, etapasVisitadas: estado.etapasVisitadas };
  return gerado === null ? base : { ...base, ultimoGerado: gerado };
}

function lerEtapas(valor: unknown): number[] {
  return Array.isArray(valor)
    ? valor.filter((item: unknown): item is number => Number.isInteger(item))
    : [];
}

/** Valida o JSON salvo; qualquer coisa fora do formato vira sessão vazia. */
export function interpretarSessao(texto: string | null): EstadoSessao {
  if (texto === null) return SESSAO_VAZIA;
  const bruto = lerJson(texto);
  if (!ehRegistro(bruto)) return SESSAO_VAZIA;
  const dataset = lerDataset(bruto.dataset);
  const base =
    dataset === null
      ? SESSAO_VAZIA
      : { dataset, etapasVisitadas: lerEtapas(bruto.etapasVisitadas) };
  return comGerado(base, lerGerado(bruto.ultimoGerado));
}

export function comEtapaVisitada(estado: EstadoSessao, etapa: number): EstadoSessao {
  if (estado.etapasVisitadas.includes(etapa)) return estado;
  return { ...estado, etapasVisitadas: [...estado.etapasVisitadas, etapa] };
}

export function carregarSessao(): EstadoSessao {
  try {
    return interpretarSessao(localStorage.getItem(CHAVE_SESSAO));
  } catch {
    return SESSAO_VAZIA;
  }
}

/** Devolve false se o navegador não deixou salvar; a sessão vale só até recarregar. */
export function salvarSessao(estado: EstadoSessao): boolean {
  try {
    localStorage.setItem(CHAVE_SESSAO, JSON.stringify(estado));
    return true;
  } catch {
    return false;
  }
}
