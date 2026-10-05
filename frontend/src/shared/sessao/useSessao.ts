import { useContext } from 'react';
import { ContextoSessao } from './contextoSessao';
import type { ValorSessao } from './tipos';

export function useSessao(): ValorSessao {
  const valor = useContext(ContextoSessao);
  if (valor === null) throw new Error('useSessao precisa estar dentro de <SessaoProvider>.');
  return valor;
}
