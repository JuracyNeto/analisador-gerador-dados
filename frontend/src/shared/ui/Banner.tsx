import type { ReactNode } from 'react';
import { juntarClasses } from '../lib/classes';
import estilos from './Banner.module.css';
import Icone from './Icone';

type VarianteBanner = 'info' | 'atencao' | 'erro' | 'sucesso';

const ICONES = {
  info: 'info',
  atencao: 'warning',
  erro: 'error',
  sucesso: 'check_circle',
} as const satisfies Record<VarianteBanner, string>;
const PAPEIS = {
  info: 'note',
  atencao: 'note',
  erro: 'alert',
  sucesso: 'status',
} as const satisfies Record<VarianteBanner, string>;

interface PropsBanner {
  variante: VarianteBanner;
  titulo?: string | undefined;
  acoes?: ReactNode;
  children: ReactNode;
}

export default function Banner({ variante, titulo, acoes, children }: Readonly<PropsBanner>) {
  return (
    <div role={PAPEIS[variante]} className={juntarClasses(estilos.banner, estilos[variante])}>
      <Icone
        nome={ICONES[variante]}
        preenchido
        tamanho={variante === 'erro' ? 24 : 20}
        className={estilos.icone}
      />
      <div className={estilos.conteudo}>
        {titulo ? <p className={estilos.titulo}>{titulo}</p> : null}
        <div className={estilos.texto}>{children}</div>
        {acoes === undefined ? null : <div className={estilos.acoes}>{acoes}</div>}
      </div>
    </div>
  );
}
