import { type RefObject, useEffect, useState } from 'react';

const INVALIDO = '[aria-invalid="true"]';

/**
 * Devolve a função a chamar no envio do formulário: depois da renderização com os erros, o foco
 * vai para o 1º campo inválido, que já diz o que corrigir (WCAG 3.3.1; D153). Sem erro, o foco
 * fica onde está.
 */
export function useFocoNoPrimeiroErro(formulario: RefObject<HTMLElement | null>): () => void {
  const [envios, setEnvios] = useState(0);
  useEffect(() => {
    if (envios === 0) return;
    formulario.current?.querySelector<HTMLElement>(INVALIDO)?.focus();
  }, [envios, formulario]);
  return () => {
    setEnvios((atual) => atual + 1);
  };
}
