import { useEffect } from 'react';

/** Escuta Esc no documento enquanto `ativo`. `aoPressionar` deve ser estável (useCallback). */
export function useTeclaEsc(ativo: boolean, aoPressionar: () => void): void {
  useEffect(() => {
    if (!ativo) return undefined;
    const aoTeclar = (evento: KeyboardEvent): void => {
      if (evento.key === 'Escape') aoPressionar();
    };
    document.addEventListener('keydown', aoTeclar);
    return () => {
      document.removeEventListener('keydown', aoTeclar);
    };
  }, [ativo, aoPressionar]);
}
