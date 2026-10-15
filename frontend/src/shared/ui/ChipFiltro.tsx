import type { CSSProperties } from 'react';
import estilos from './ChipFiltro.module.css';
import Icone from './Icone';

interface PropsChipFiltro {
  rotulo: string;
  marcado: boolean;
  /** Token da cor do chip marcado (ex.: `--sev-alta`); o fundo usa `{token}-suave`. */
  cor: `--${string}`;
  aoAlternar: () => void;
}

function estiloMarcado(cor: string): CSSProperties {
  return { color: `var(${cor})`, borderColor: `var(${cor})`, backgroundColor: `var(${cor}-suave)` };
}

/** Filtro liga/desliga em pílula (tela 7a): `role="checkbox"`, espaço e Enter alternam. */
export default function ChipFiltro({
  rotulo,
  marcado,
  cor,
  aoAlternar,
}: Readonly<PropsChipFiltro>) {
  return (
    <button
      type="button"
      role="checkbox"
      aria-checked={marcado}
      className={estilos.chip}
      style={marcado ? estiloMarcado(cor) : undefined}
      onClick={aoAlternar}
    >
      {marcado ? <Icone nome="check" tamanho={16} /> : null}
      {rotulo}
    </button>
  );
}
