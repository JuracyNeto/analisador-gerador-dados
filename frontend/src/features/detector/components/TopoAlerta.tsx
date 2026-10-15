import BadgeSeveridade from '../../../shared/ui/BadgeSeveridade';
import { TEXTOS_DETECTOR as T } from '../textos';
import type { Aviso } from '../tipos';
import estilos from './CartaoAlerta.module.css';

/** Severidade (parte 2) · "R4 · Valores redondos" · coluna(s) (componentes.md §CartaoAlerta). */
export default function TopoAlerta({ aviso }: Readonly<{ aviso: Aviso }>) {
  const colunas =
    aviso.colunas.length === 0 ? (
      <span className={estilos.regra}>{T.linhasInteiras}</span>
    ) : (
      <span className={estilos.colunas}>{aviso.colunas.join(T.separadorPar)}</span>
    );
  return (
    <div className={estilos.topo}>
      <BadgeSeveridade severidade={aviso.severidade} />
      <span className={estilos.regra}>{T.regra(aviso)}</span>
      <span className={estilos.espaco} />
      {colunas}
    </div>
  );
}
