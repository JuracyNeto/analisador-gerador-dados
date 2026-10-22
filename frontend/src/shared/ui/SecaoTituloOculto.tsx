import { type ReactNode, useId } from 'react';

interface PropsSecaoTituloOculto {
  titulo: string;
  children: ReactNode;
}

/**
 * Seção com um h2 que só o leitor de tela lê: os cartões (h3) que vêm logo depois do título da
 * etapa (h1) ficam numa hierarquia sem pular nível, sem mudar o visual (WCAG 1.3.1, D153).
 */
export default function SecaoTituloOculto({ titulo, children }: Readonly<PropsSecaoTituloOculto>) {
  const id = useId();
  return (
    <section aria-labelledby={id}>
      <h2 id={id} className="visualmente-oculto">
        {titulo}
      </h2>
      {children}
    </section>
  );
}
