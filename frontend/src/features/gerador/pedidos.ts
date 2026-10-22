/** Estado dos formulários → pedido da API (puro). Campo nulo = "use o valor da origem". */
import { formatarNumero } from '../../shared/lib/formatar';
import type {
  Modo,
  Origem,
  PedidoBivariado,
  PedidoUnivariado,
  ResumoOrigem,
  ResumoOrigemPar,
  TipoManual,
} from './tipos';
import {
  type Leitura,
  errosDe,
  lerChance,
  lerDesvio,
  lerNumero,
  lerQuantidade,
  lerQuantidadePares,
  lerSemente,
} from './validacao';

export type ResultadoPedido<P, C extends string> =
  { ok: true; pedido: P } | { ok: false; erros: Partial<Record<C, string>> };

const TIPOS_NUMERICOS = new Set(['continua', 'discreta']);

/** Texto do campo: o digitado ou, sem edição, o valor da origem formatado. */
export function textoCampo(texto: string | null, valor: number | null | undefined): string {
  if (texto !== null) return texto;
  return valor === null || valor === undefined ? '' : formatarNumero(valor);
}

/** Sem edição, usa o valor exato da origem (não o texto arredondado da tela). */
function lerComOrigem(
  texto: string | null,
  valor: number | null | undefined,
  ler: (texto: string) => Leitura<number>,
): Leitura<number> {
  if (texto === null && valor !== null && valor !== undefined) return { ok: true, valor };
  return ler(texto ?? '');
}

function valorDe<T>(leitura: Leitura<T>): T | null {
  return leitura.ok ? leitura.valor : null;
}

// Univariado ------------------------------------------------------------------------------

export interface EstadoUnivariado {
  origem: Origem;
  coluna: string | null;
  tipoManual: TipoManual;
  quantidade: string;
  modo: Modo;
  media: string | null;
  desvio: string | null;
  chance: string | null;
  semente: string;
  limitar: boolean;
}

export type CampoUnivariado = 'quantidade' | 'semente' | 'media' | 'desvio' | 'chance';

export interface ContextoUnivariado {
  datasetId: string | null;
  coluna: string | null;
  resumo: ResumoOrigem | undefined;
}

export const ESTADO_INICIAL_UNIVARIADO: EstadoUnivariado = {
  origem: 'coluna',
  coluna: null,
  tipoManual: 'continua',
  quantidade: '500',
  modo: 'preservar',
  media: null,
  desvio: null,
  chance: null,
  semente: '',
  limitar: false,
};

export function origemUnivariada(estado: EstadoUnivariado, contexto: ContextoUnivariado): Origem {
  return contexto.datasetId === null ? 'manual' : estado.origem;
}

export function tipoUnivariado(
  estado: EstadoUnivariado,
  contexto: ContextoUnivariado,
): string | undefined {
  return origemUnivariada(estado, contexto) === 'manual'
    ? estado.tipoManual
    : contexto.resumo?.tipo;
}

export function modoUnivariado(estado: EstadoUnivariado, contexto: ContextoUnivariado): Modo {
  if (origemUnivariada(estado, contexto) === 'manual') return 'parametros';
  return contexto.resumo?.so_preservar === true ? 'preservar' : estado.modo;
}

export function ehNumerica(tipo: string | undefined): boolean {
  return tipo !== undefined && TIPOS_NUMERICOS.has(tipo);
}

function leiturasDosParametros(
  estado: EstadoUnivariado,
  contexto: ContextoUnivariado,
): (readonly [CampoUnivariado, Leitura<number>])[] {
  const tipo = tipoUnivariado(estado, contexto);
  const resumo = contexto.resumo;
  if (tipo === 'binaria') {
    return [['chance', lerComOrigem(estado.chance, resumo?.chance, lerChance)]];
  }
  return [
    ['media', lerComOrigem(estado.media, resumo?.media, lerNumero)],
    ['desvio', lerComOrigem(estado.desvio, resumo?.desvio, lerDesvio)],
  ];
}

function origemDoPedido(
  estado: EstadoUnivariado,
  contexto: ContextoUnivariado,
): NonNullable<PedidoUnivariado['origem']> | null {
  if (origemUnivariada(estado, contexto) === 'manual') return null;
  const { datasetId, coluna } = contexto;
  return datasetId !== null && coluna !== null ? { dataset_id: datasetId, coluna } : null;
}

export function montarPedidoUnivariado(
  estado: EstadoUnivariado,
  contexto: ContextoUnivariado,
): ResultadoPedido<PedidoUnivariado, CampoUnivariado> {
  const modo = modoUnivariado(estado, contexto);
  const quantidade = lerQuantidade(estado.quantidade);
  const semente = lerSemente(estado.semente);
  const parametros = modo === 'parametros' ? leiturasDosParametros(estado, contexto) : [];
  const erros = errosDe<CampoUnivariado>([
    ['quantidade', quantidade],
    ['semente', semente],
    ...parametros,
  ]);
  if (!quantidade.ok || !semente.ok || Object.keys(erros).length > 0) return { ok: false, erros };
  const valores = new Map(parametros.map(([campo, leitura]) => [campo, valorDe(leitura)]));
  return {
    ok: true,
    pedido: corpoUnivariado(estado, contexto, {
      x: quantidade.valor,
      semente: semente.valor,
      modo,
      valores,
    }),
  };
}

interface Lidos {
  x: number;
  semente: number | null;
  modo: Modo;
  valores: ReadonlyMap<CampoUnivariado, number | null>;
}

function corpoUnivariado(
  estado: EstadoUnivariado,
  contexto: ContextoUnivariado,
  lidos: Lidos,
): PedidoUnivariado {
  const manual = origemUnivariada(estado, contexto) === 'manual';
  const valor = (campo: CampoUnivariado) => lidos.valores.get(campo) ?? null;
  return {
    origem: origemDoPedido(estado, contexto),
    tipo: manual ? estado.tipoManual : null,
    x: lidos.x,
    modo: lidos.modo,
    media: valor('media'),
    desvio: valor('desvio'),
    p: valor('chance'),
    semente: lidos.semente,
    limitar_faixa: !manual && ehNumerica(tipoUnivariado(estado, contexto)) && estado.limitar,
  };
}

// Bivariado -------------------------------------------------------------------------------

export interface EstadoBivariado {
  origem: Origem;
  x: string | null;
  y: string | null;
  mediaX: string | null;
  mediaY: string | null;
  desvioX: string | null;
  desvioY: string | null;
  rho: number | null;
  quantidade: string;
  exato: boolean;
  semente: string;
}

export type CampoBivariado = 'quantidade' | 'semente' | 'mediaX' | 'mediaY' | 'desvioX' | 'desvioY';

export interface ContextoBivariado {
  datasetId: string | null;
  x: string | null;
  y: string | null;
  par: ResumoOrigemPar | undefined;
  /** O arquivo tem duas colunas numéricas (ou elas ainda estão chegando). */
  parPossivel: boolean;
}

export const ESTADO_INICIAL_BIVARIADO: EstadoBivariado = {
  origem: 'coluna',
  x: null,
  y: null,
  mediaX: null,
  mediaY: null,
  desvioX: null,
  desvioY: null,
  rho: null,
  quantidade: '500',
  exato: true,
  semente: '',
};

export function origemBivariada(estado: EstadoBivariado, contexto: ContextoBivariado): Origem {
  return contexto.datasetId === null || !contexto.parPossivel ? 'manual' : estado.origem;
}

type LeitorCampo = (
  texto: string | null,
  ler: (texto: string) => Leitura<number>,
) => Leitura<number | null>;

/** Com origem, campo sem edição não vai no pedido: o servidor copia o valor exato do par. */
const lerOpcional: LeitorCampo = (texto, ler) =>
  texto === null ? { ok: true, valor: null } : ler(texto);

/** Sem origem, médias e desvios são obrigatórios. */
const lerObrigatorio: LeitorCampo = (texto, ler) => ler(texto ?? '');

export function montarPedidoBivariado(
  estado: EstadoBivariado,
  contexto: ContextoBivariado,
): ResultadoPedido<PedidoBivariado, CampoBivariado> {
  const comOrigem = origemBivariada(estado, contexto) === 'coluna';
  const lerCampo = comOrigem ? lerOpcional : lerObrigatorio;
  const quantidade = lerQuantidadePares(estado.quantidade);
  const semente = lerSemente(estado.semente);
  const campos = [
    ['mediaX', lerCampo(estado.mediaX, lerNumero)],
    ['mediaY', lerCampo(estado.mediaY, lerNumero)],
    ['desvioX', lerCampo(estado.desvioX, lerDesvio)],
    ['desvioY', lerCampo(estado.desvioY, lerDesvio)],
  ] as const;
  const erros = errosDe<CampoBivariado>([
    ['quantidade', quantidade],
    ['semente', semente],
    ...campos,
  ]);
  if (!quantidade.ok || !semente.ok || Object.keys(erros).length > 0) return { ok: false, erros };
  const valores = new Map(campos.map(([campo, leitura]) => [campo, valorDe(leitura)]));
  const lidos = { n: quantidade.valor, semente: semente.valor, valores };
  return { ok: true, pedido: corpoBivariado(estado, contexto, lidos) };
}

interface LidosPar {
  n: number;
  semente: number | null;
  valores: ReadonlyMap<CampoBivariado, number | null>;
}

function corpoBivariado(
  estado: EstadoBivariado,
  contexto: ContextoBivariado,
  lidos: LidosPar,
): PedidoBivariado {
  const comOrigem = origemBivariada(estado, contexto) === 'coluna';
  const valor = (campo: CampoBivariado) => lidos.valores.get(campo) ?? null;
  return {
    origem: comOrigem ? origemDoPar(contexto) : null,
    n: lidos.n,
    media_x: valor('mediaX'),
    media_y: valor('mediaY'),
    desvio_x: valor('desvioX'),
    desvio_y: valor('desvioY'),
    rho: comOrigem ? estado.rho : (estado.rho ?? 0),
    ajuste_exato: estado.exato,
    semente: lidos.semente,
  };
}

function origemDoPar(contexto: ContextoBivariado): NonNullable<PedidoBivariado['origem']> | null {
  const { datasetId, x, y } = contexto;
  if (datasetId === null || x === null || y === null) return null;
  return { dataset_id: datasetId, x, y };
}
