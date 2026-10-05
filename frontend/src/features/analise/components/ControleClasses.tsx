import { useId } from 'react';
import Icone from '../../../shared/ui/Icone';
import { LIMITES_CLASSES } from '../parametros';
import { TEXTOS_ANALISE } from '../textos';
import estilos from './ControleClasses.module.css';

const T = TEXTOS_ANALISE.frequencias;

interface Props {
  k: number;
  kSturges: number;
  aoMudar: (k: number) => void;
}

export default function ControleClasses({ k, kSturges, aoMudar }: Readonly<Props>) {
  const idRotulo = useId();

  return (
    <div className={estilos.controle} role="group" aria-labelledby={idRotulo}>
      <span id={idRotulo} className={estilos.rotulo}>
        {T.numeroClasses}
      </span>
      <div className={estilos.passo}>
        <button
          type="button"
          className={estilos.botao}
          aria-label={T.menos}
          disabled={k <= LIMITES_CLASSES.minimo}
          onClick={() => {
            aoMudar(k - 1);
          }}
        >
          <Icone nome="remove" tamanho={18} />
        </button>
        <output className={estilos.valor} aria-live="polite">
          {k}
        </output>
        <button
          type="button"
          className={estilos.botao}
          aria-label={T.mais}
          disabled={k >= LIMITES_CLASSES.maximo}
          onClick={() => {
            aoMudar(k + 1);
          }}
        >
          <Icone nome="add" tamanho={18} />
        </button>
      </div>
      <span className={estilos.sturges}>{T.sturges(kSturges)}</span>
    </div>
  );
}
