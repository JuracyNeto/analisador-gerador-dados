import type { ReactNode } from 'react';
import { juntarClasses } from '../lib/classes';
import estilos from './CaixaSelecao.module.css';
import Icone from './Icone';

interface PropsCaixaSelecao {
  rotulo: ReactNode;
  marcada: boolean;
  aoMudar: (marcada: boolean) => void;
  desabilitada?: boolean;
}

export default function CaixaSelecao({
  rotulo,
  marcada,
  aoMudar,
  desabilitada = false,
}: Readonly<PropsCaixaSelecao>) {
  return (
    <label className={juntarClasses(estilos.caixa, desabilitada && estilos.desabilitada)}>
      <input
        type="checkbox"
        className={estilos.entrada}
        checked={marcada}
        disabled={desabilitada}
        onChange={(evento) => {
          aoMudar(evento.target.checked);
        }}
      />
      <span className={estilos.marca} aria-hidden="true">
        <Icone nome="check" tamanho={16} />
      </span>
      <span>{rotulo}</span>
    </label>
  );
}
