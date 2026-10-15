import { createContext, useContext } from 'react';
import type { Aviso } from '../tipos';

type VerNaTabela = (aviso: Aviso) => void;

/** A página abre o drawer "Ver na tabela"; os cartões, alguns níveis abaixo, só pedem (§6). */
export const ContextoVerNaTabela = createContext<VerNaTabela | null>(null);

/** `null` fora da página do detector: o cartão fica sem o botão. */
export function useVerNaTabela(): VerNaTabela | null {
  return useContext(ContextoVerNaTabela);
}
