import { useId } from 'react';
import ChipFiltro from '../../../shared/ui/ChipFiltro';
import Segmented from '../../../shared/ui/Segmented';
import { ORDEM_SEVERIDADES, SEVERIDADES } from '../../../shared/ui/severidades';
import { TEXTOS_DETECTOR as T } from '../textos';
import type { Agrupamento, FiltrosDetector, ResumoDetector, Severidade } from '../tipos';
import estilos from './BarraFiltros.module.css';

const AGRUPAMENTOS = (['coluna', 'regra'] as const).map((valor) => ({
  valor,
  rotulo: T.agrupamentos[valor],
}));

interface PropsBarraFiltros {
  porSeveridade: ResumoDetector['por_severidade'];
  filtros: FiltrosDetector;
  aoAlternar: (severidade: Severidade) => void;
  aoAgrupar: (agrupar: Agrupamento) => void;
}

/** "Mostrar" com um chip por severidade e o Segmented "Agrupar por" (7a). */
export default function BarraFiltros({
  porSeveridade,
  filtros,
  aoAlternar,
  aoAgrupar,
}: Readonly<PropsBarraFiltros>) {
  const idMostrar = useId();
  return (
    <div className={estilos.barra}>
      <div role="group" aria-labelledby={idMostrar} className={estilos.grupo}>
        <span id={idMostrar} className={estilos.rotulo}>
          {T.mostrar}
        </span>
        {ORDEM_SEVERIDADES.map((severidade) => (
          <ChipFiltro
            key={severidade}
            rotulo={T.chip(SEVERIDADES[severidade].palavra, porSeveridade[severidade])}
            marcado={filtros.severidades.has(severidade)}
            cor={SEVERIDADES[severidade].token}
            aoAlternar={() => {
              aoAlternar(severidade);
            }}
          />
        ))}
      </div>
      <div className={estilos.grupo}>
        <span className={estilos.rotulo} aria-hidden="true">
          {T.agruparPor}
        </span>
        <Segmented
          rotulo={T.agruparPor}
          opcoes={AGRUPAMENTOS}
          valor={filtros.agrupar}
          aoMudar={aoAgrupar}
        />
      </div>
    </div>
  );
}
