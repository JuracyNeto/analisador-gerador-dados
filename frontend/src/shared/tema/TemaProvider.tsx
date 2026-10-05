import { type ReactNode, useCallback, useMemo, useState } from 'react';
import { ContextoTema } from './contextoTema';
import { aplicarTema, aplicarTemaInicial, salvarTema, temaDoDocumento } from './preferencia';
import type { Tema } from './tipos';

interface PropsTemaProvider {
  children: ReactNode;
}

export default function TemaProvider({ children }: Readonly<PropsTemaProvider>) {
  const [tema, setTema] = useState<Tema>(() => temaDoDocumento() ?? aplicarTemaInicial());

  const definirTema = useCallback((novo: Tema) => {
    // Aplica no <html> antes do render: quem lê tokens (Grafico) já vê o tema novo.
    aplicarTema(novo);
    salvarTema(novo);
    setTema(novo);
  }, []);

  const valor = useMemo(() => ({ tema, definirTema }), [tema, definirTema]);

  return <ContextoTema value={valor}>{children}</ContextoTema>;
}
