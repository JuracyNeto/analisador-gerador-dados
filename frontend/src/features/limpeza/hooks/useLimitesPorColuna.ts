import { useCallback, useState } from 'react';
import { LIMITE_VAZIO, serializarLimites, type TextoLimite } from '../limites';

export function useLimitesPorColuna() {
  const [textos, setTextos] = useState<Readonly<Record<string, TextoLimite>>>({});
  const alterar = useCallback((coluna: string, campo: keyof TextoLimite, texto: string) => {
    setTextos((atuais) => ({
      ...atuais,
      [coluna]: { ...(atuais[coluna] ?? LIMITE_VAZIO), [campo]: texto },
    }));
  }, []);
  return { textos, alterar, json: serializarLimites(textos) };
}
