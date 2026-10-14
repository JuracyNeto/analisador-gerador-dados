import estilos from './BadgeSeveridade.module.css';
import Icone from './Icone';
import { estiloDaSeveridade, SEVERIDADES, type Severidade } from './severidades';

type TamanhoBadge = 'md' | 'sm';

const TAMANHO_ICONE = { md: 18, sm: 16 } as const satisfies Record<TamanhoBadge, number>;

interface PropsBadgeSeveridade {
  severidade: Severidade;
  /** `sm` no cabeçalho do drawer (24 px). */
  tamanho?: TamanhoBadge;
}

/** Severidade sempre com ícone preenchido + palavra + cor (spec 16). */
export default function BadgeSeveridade({
  severidade,
  tamanho = 'md',
}: Readonly<PropsBadgeSeveridade>) {
  const { icone, palavra } = SEVERIDADES[severidade];
  return (
    <span
      className={estilos.badge}
      data-severidade={severidade}
      data-tamanho={tamanho}
      style={estiloDaSeveridade(severidade)}
    >
      <Icone nome={icone} preenchido tamanho={TAMANHO_ICONE[tamanho]} />
      {palavra}
    </span>
  );
}
