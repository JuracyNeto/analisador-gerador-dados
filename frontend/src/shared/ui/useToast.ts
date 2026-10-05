import { useContext } from 'react';
import { ContextoToast, type ValorToast } from './contextoToast';

export function useToast(): ValorToast {
  const valor = useContext(ContextoToast);
  if (valor === null) throw new Error('useToast precisa estar dentro de <ToastProvider>.');
  return valor;
}
