import { useLocation } from 'react-router';
import { VISUALMENTE_OCULTO, juntarClasses } from '../../shared/lib/classes';
import { useSessao } from '../../shared/sessao/useSessao';
import Icone from '../../shared/ui/Icone';
import { ETAPAS, etapaDoCaminho } from '../etapas';
import { TEXTOS_APP } from '../textos';
import estilos from './BarraEtapas.module.css';
import { type ContextoEtapas, estadoDaEtapa } from './estadoEtapa';
import ItemEtapa from './ItemEtapa';

interface PropsBarraEtapas {
  recolhida: boolean;
  /** Aberta por cima do conteúdo em telas de 768 a 1279 px. */
  sobreposta: boolean;
  aoAlternar: () => void;
}

export default function BarraEtapas({
  recolhida,
  sobreposta,
  aoAlternar,
}: Readonly<PropsBarraEtapas>) {
  const { dataset, etapasVisitadas } = useSessao();
  const { pathname } = useLocation();
  const contexto: ContextoEtapas = {
    atual: etapaDoCaminho(pathname)?.numero ?? null,
    temDataset: dataset !== null,
    visitadas: etapasVisitadas,
  };
  return (
    <aside
      className={juntarClasses(
        estilos.barra,
        recolhida && estilos.recolhida,
        sobreposta && estilos.sobreposta,
      )}
    >
      <Marca recolhida={recolhida} />
      <nav aria-label={TEXTOS_APP.etapasDaAnalise} className={estilos.nav}>
        <ol className={estilos.lista}>
          {ETAPAS.map((etapa) => (
            <ItemEtapa
              key={etapa.numero}
              etapa={etapa}
              estado={estadoDaEtapa(etapa, contexto)}
              recolhida={recolhida}
            />
          ))}
        </ol>
      </nav>
      {contexto.temDataset || recolhida ? null : (
        <p className={estilos.aviso}>{TEXTOS_APP.etapasBloqueadas}</p>
      )}
      <BotaoRecolher recolhida={recolhida} aoAlternar={aoAlternar} />
    </aside>
  );
}

function Marca({ recolhida }: Readonly<{ recolhida: boolean }>) {
  return (
    <div className={estilos.marca}>
      <span className={estilos.simbolo} aria-hidden="true">
        {TEXTOS_APP.simboloMarca}
      </span>
      <span className={recolhida ? VISUALMENTE_OCULTO : estilos.nomeApp}>
        {TEXTOS_APP.marcaLinha1}{' '}
        <small className={estilos.nomeApp2}>{TEXTOS_APP.marcaLinha2}</small>
      </span>
    </div>
  );
}

function BotaoRecolher({
  recolhida,
  aoAlternar,
}: Readonly<{ recolhida: boolean; aoAlternar: () => void }>) {
  return (
    <div className={estilos.rodape}>
      <button
        type="button"
        className={estilos.recolher}
        aria-expanded={!recolhida}
        onClick={aoAlternar}
      >
        <Icone nome={recolhida ? 'left_panel_open' : 'left_panel_close'} tamanho={20} />
        <span className={recolhida ? VISUALMENTE_OCULTO : undefined}>
          {recolhida ? TEXTOS_APP.expandirBarra : TEXTOS_APP.recolherBarra}
        </span>
      </button>
    </div>
  );
}
