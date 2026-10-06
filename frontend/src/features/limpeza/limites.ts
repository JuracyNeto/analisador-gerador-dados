import { formatarNumero, lerNumeroPtBr } from '../../shared/lib/formatar';
import { TEXTOS_LIMPEZA as T } from './textos';
import type { Limites } from './tipos';

export interface TextoLimite {
  min: string;
  max: string;
}

export interface ResultadoLimite {
  limites: Limites | null;
  erroMin: string | null;
  erroMax: string | null;
}

export const LIMITE_VAZIO: TextoLimite = { min: '', max: '' };

type Leitura = { estado: 'vazio' } | { estado: 'invalido' } | { estado: 'ok'; numero: number };

function lerCampo(texto: string): Leitura {
  if (texto.trim() === '') return { estado: 'vazio' };
  const numero = lerNumeroPtBr(texto);
  return numero === null ? { estado: 'invalido' } : { estado: 'ok', numero };
}

function numeroDe(leitura: Leitura): number | null {
  return leitura.estado === 'ok' ? leitura.numero : null;
}

function erroDe(leitura: Leitura): string | null {
  return leitura.estado === 'invalido' ? T.limites.erroNumero : null;
}

/** Campos Mínimo/Máximo de uma coluna → limite para a API ou mensagem de erro no campo. */
export function validarLimite(texto: TextoLimite): ResultadoLimite {
  const min = lerCampo(texto.min);
  const max = lerCampo(texto.max);
  const erroMin = erroDe(min);
  const erroMax = erroDe(max);
  if (erroMin !== null || erroMax !== null) return { limites: null, erroMin, erroMax };
  const vMin = numeroDe(min);
  const vMax = numeroDe(max);
  if (vMin === null && vMax === null) return { limites: null, erroMin: null, erroMax: null };
  if (vMin !== null && vMax !== null && vMin >= vMax) {
    return { limites: null, erroMin: T.limites.erroOrdem(formatarNumero(vMax)), erroMax: null };
  }
  return { limites: { min: vMin, max: vMax }, erroMin: null, erroMax: null };
}

/** JSON da query `?limites=` (colunas em ordem para a chave do cache ser estável); '' sem limites. */
export function serializarLimites(textos: Readonly<Record<string, TextoLimite>>): string {
  const validos = Object.entries(textos)
    .toSorted(([a], [b]) => a.localeCompare(b))
    .flatMap(([coluna, texto]) => {
      const { limites } = validarLimite(texto);
      return limites === null ? [] : [[coluna, limites] as const];
    });
  return validos.length === 0 ? '' : JSON.stringify(Object.fromEntries(validos));
}
