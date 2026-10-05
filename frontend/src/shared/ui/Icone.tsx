import type { CSSProperties } from 'react';
import { juntarClasses } from '../lib/classes';
import estilos from './Icone.module.css';

interface PropsIcone {
  nome: string;
  preenchido?: boolean;
  tamanho?: number;
  /** Sem rótulo o ícone é decorativo (aria-hidden); com rótulo vira role="img". */
  rotulo?: string | undefined;
  className?: string | undefined;
}

export default function Icone({
  nome,
  preenchido = false,
  tamanho = 20,
  rotulo,
  className,
}: Readonly<PropsIcone>) {
  const classes = juntarClasses(estilos.icone, preenchido && estilos.preenchido, className);
  const estilo: CSSProperties = { fontSize: tamanho };
  if (rotulo === undefined) {
    return (
      <span className={classes} style={estilo} aria-hidden="true">
        {nome}
      </span>
    );
  }
  return (
    <span className={classes} style={estilo} role="img" aria-label={rotulo}>
      {nome}
    </span>
  );
}
