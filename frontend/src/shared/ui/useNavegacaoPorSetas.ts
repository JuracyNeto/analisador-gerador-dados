import { type KeyboardEvent, useRef } from 'react';

const PASSO_POR_TECLA: Readonly<Partial<Record<string, number>>> = {
  ArrowRight: 1,
  ArrowDown: 1,
  ArrowLeft: -1,
  ArrowUp: -1,
};

export interface PropsItemNavegavel {
  ref: (elemento: HTMLElement | null) => void;
  tabIndex: 0 | -1;
  onKeyDown: (evento: KeyboardEvent<HTMLElement>) => void;
}

interface OpcoesNavegacao<T extends string> {
  ids: readonly T[];
  ativo: T;
  aoMudar: (id: T) => void;
  habilitado?: (id: T) => boolean;
}

/** Destino da tecla: setas andam em círculo; Home/End vão às pontas; outras teclas → undefined. */
export function idDestino<T>(ids: readonly T[], atual: T, tecla: string): T | undefined {
  if (tecla === 'Home') return ids[0];
  if (tecla === 'End') return ids.at(-1);
  const passo = PASSO_POR_TECLA[tecla];
  const indice = ids.indexOf(atual);
  if (passo === undefined || indice < 0) return undefined;
  return ids[(indice + passo + ids.length) % ids.length];
}

const sempreHabilitado = (): boolean => true;

/** Roving tabindex (WAI-ARIA). Devolve as props de cada item: `<button {...propsItem(id)} />`. */
export function useNavegacaoPorSetas<T extends string>({
  ids,
  ativo,
  aoMudar,
  habilitado = sempreHabilitado,
}: OpcoesNavegacao<T>): (id: T) => PropsItemNavegavel {
  const elementos = useRef(new Map<T, HTMLElement>());
  return (id: T) => ({
    ref: (elemento) => {
      if (elemento) {
        elementos.current.set(id, elemento);
      } else {
        elementos.current.delete(id);
      }
    },
    tabIndex: id === ativo ? 0 : -1,
    onKeyDown: (evento) => {
      const destino = idDestino(ids, id, evento.key);
      if (destino === undefined) return;
      evento.preventDefault();
      elementos.current.get(destino)?.focus();
      if (habilitado(destino)) aoMudar(destino);
    },
  });
}
