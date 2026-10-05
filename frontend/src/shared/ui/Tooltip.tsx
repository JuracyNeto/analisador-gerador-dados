import { type ReactElement, cloneElement, useCallback, useId, useState } from 'react';
import { juntarClasses } from '../lib/classes';
import { useTeclaEsc } from '../lib/useTeclaEsc';
import estilos from './Tooltip.module.css';

type PosicaoTooltip = 'acima' | 'direita';

/** O alvo precisa repassar aria-describedby para o elemento focável. */
interface AtributosAlvo {
  'aria-describedby'?: string | undefined;
}

interface PropsTooltip {
  texto: string;
  posicao?: PosicaoTooltip;
  children: ReactElement<AtributosAlvo>;
}

export default function Tooltip({ texto, posicao = 'acima', children }: Readonly<PropsTooltip>) {
  const id = useId();
  const [aberto, setAberto] = useState(false);
  const abrir = useCallback(() => {
    setAberto(true);
  }, []);
  const fechar = useCallback(() => {
    setAberto(false);
  }, []);
  useTeclaEsc(aberto, fechar);

  return (
    <span
      className={estilos.ancora}
      onMouseEnter={abrir}
      onMouseLeave={fechar}
      onFocus={abrir}
      onBlur={fechar}
    >
      {cloneElement(children, { 'aria-describedby': id })}
      <span
        role="tooltip"
        id={id}
        hidden={!aberto}
        className={juntarClasses(estilos.balao, posicao === 'direita' && estilos.direita)}
      >
        {texto}
      </span>
    </span>
  );
}
