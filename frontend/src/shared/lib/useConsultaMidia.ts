import { useCallback, useSyncExternalStore } from 'react';

/** Acompanha uma media query (ex.: '(min-width: 1280px)'). */
export function useConsultaMidia(consulta: string): boolean {
  const assinar = useCallback(
    (aoMudar: () => void) => {
      const lista = window.matchMedia(consulta);
      lista.addEventListener('change', aoMudar);
      return () => {
        lista.removeEventListener('change', aoMudar);
      };
    },
    [consulta],
  );
  return useSyncExternalStore(assinar, () => window.matchMedia(consulta).matches);
}
