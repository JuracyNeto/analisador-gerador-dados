import { useId } from 'react';
import { juntarClasses } from '../../../shared/lib/classes';
import Banner from '../../../shared/ui/Banner';
import { agrupar, type GrupoAvisos } from '../agrupamento';
import { filtrarPorSeveridade } from '../filtros';
import { TEXTOS_DETECTOR as T } from '../textos';
import type { Aviso, FiltrosDetector } from '../tipos';
import CartaoAlerta from './CartaoAlerta';
import estilos from './ListaAlertas.module.css';

function GrupoAlertas({ grupo }: Readonly<{ grupo: GrupoAvisos }>) {
  const idTitulo = useId();
  return (
    <section className={estilos.grupo} aria-labelledby={idTitulo}>
      <h2 id={idTitulo} className={estilos.cabecalho}>
        <span className={juntarClasses(grupo.mono && estilos.mono)}>{grupo.titulo}</span>
        <span className={estilos.quantidade}>{T.alertasNoGrupo(grupo.avisos.length)}</span>
      </h2>
      {grupo.avisos.map((aviso, i) => (
        <CartaoAlerta
          key={`${aviso.regra}-${aviso.colunas.join('|')}`}
          aviso={aviso}
          abertoInicial={i === 0}
        />
      ))}
    </section>
  );
}

interface PropsListaAlertas {
  avisos: readonly Aviso[];
  filtros: FiltrosDetector;
}

/** Alertas filtrados e agrupados (7a); o 1º de cada grupo abre, os demais ficam recolhidos. */
export default function ListaAlertas({ avisos, filtros }: Readonly<PropsListaAlertas>) {
  if (filtros.severidades.size === 0) return <Banner variante="info">{T.semSeveridade}</Banner>;
  const visiveis = filtrarPorSeveridade(avisos, filtros.severidades);
  if (visiveis.length === 0) return <Banner variante="info">{T.semAlertasMarcados}</Banner>;
  return (
    <div className={estilos.lista}>
      {agrupar(visiveis, filtros.agrupar).map((grupo) => (
        <GrupoAlertas key={grupo.chave} grupo={grupo} />
      ))}
    </div>
  );
}
