import { useContext } from 'react';
import { ContextoTema } from './contextoTema';
import type { ValorTema } from './tipos';

export function useTema(): ValorTema {
  const valor = useContext(ContextoTema);
  if (valor === null) throw new Error('useTema precisa estar dentro de <TemaProvider>.');
  return valor;
}
