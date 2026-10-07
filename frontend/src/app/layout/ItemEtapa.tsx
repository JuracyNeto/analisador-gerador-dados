import { Link } from 'react-router';
import { VISUALMENTE_OCULTO, juntarClasses } from '../../shared/lib/classes';
import Icone from '../../shared/ui/Icone';
import Tooltip from '../../shared/ui/Tooltip';
import type { Etapa } from '../etapas';
import { TEXTOS_APP } from '../textos';
import { type EstadoEtapa, dicaDaEtapa } from './estadoEtapa';
import estilos from './ItemEtapa.module.css';

const CLASSE_MARCADOR = {
  concluida: estilos.marcadorConcluida,
  atual: estilos.marcadorAtual,
  disponivel: estilos.marcadorDisponivel,
  bloqueada: estilos.marcadorBloqueada,
} satisfies Record<EstadoEtapa, string | undefined>;

const SUFIXOS = {
  concluida: TEXTOS_APP.concluida,
  bloqueada: TEXTOS_APP.bloqueada,
  atual: null,
  disponivel: null,
} as const satisfies Record<EstadoEtapa, string | null>;

interface PropsConteudo {
  etapa: Etapa;
  estado: EstadoEtapa;
  recolhida: boolean;
}

interface PropsAlvo extends PropsConteudo {
  /** Repassado pelo Tooltip (cloneElement). */
  'aria-describedby'?: string | undefined;
}

export default function ItemEtapa({ etapa, estado, recolhida }: Readonly<PropsConteudo>) {
  const dica = dicaDaEtapa(etapa, recolhida);
  const alvo =
    estado === 'bloqueada' ? (
      <EtapaBloqueada etapa={etapa} estado={estado} recolhida={recolhida} />
    ) : (
      <EtapaNavegavel etapa={etapa} estado={estado} recolhida={recolhida} />
    );
  return (
    <li className={estilos.linha}>
      {dica === null ? (
        alvo
      ) : (
        <Tooltip texto={dica} posicao="direita">
          {alvo}
        </Tooltip>
      )}
    </li>
  );
}

function EtapaNavegavel({
  etapa,
  estado,
  recolhida,
  'aria-describedby': descritaPor,
}: Readonly<PropsAlvo>) {
  const atual = estado === 'atual';
  return (
    <Link
      to={etapa.caminho}
      aria-current={atual ? 'step' : undefined}
      aria-describedby={descritaPor}
      className={juntarClasses(
        estilos.item,
        atual && estilos.atual,
        recolhida && estilos.recolhida,
      )}
    >
      <ConteudoEtapa etapa={etapa} estado={estado} recolhida={recolhida} />
    </Link>
  );
}

function EtapaBloqueada({
  etapa,
  estado,
  recolhida,
  'aria-describedby': descritaPor,
}: Readonly<PropsAlvo>) {
  return (
    <button
      type="button"
      aria-disabled="true"
      aria-describedby={descritaPor}
      className={juntarClasses(estilos.item, estilos.bloqueada, recolhida && estilos.recolhida)}
    >
      <ConteudoEtapa etapa={etapa} estado={estado} recolhida={recolhida} />
    </button>
  );
}

function ConteudoEtapa({ etapa, estado, recolhida }: Readonly<PropsConteudo>) {
  return (
    <>
      <span className={juntarClasses(estilos.marcador, CLASSE_MARCADOR[estado])} aria-hidden="true">
        {estado === 'concluida' ? <Icone nome="check" tamanho={18} /> : etapa.numero}
      </span>
      <span className={recolhida ? VISUALMENTE_OCULTO : estilos.nome}>{etapa.nome}</span>{' '}
      <SufixoEtapa estado={estado} recolhida={recolhida} />
    </>
  );
}

function SufixoEtapa({ estado, recolhida }: Readonly<Omit<PropsConteudo, 'etapa'>>) {
  const texto = SUFIXOS[estado];
  if (texto === null) return null;
  if (recolhida) return <span className={VISUALMENTE_OCULTO}>{texto}</span>;
  return estado === 'bloqueada' ? (
    <Icone nome="lock" tamanho={18} rotulo={texto} className={estilos.cadeado} />
  ) : (
    <span className={estilos.concluida}>{texto}</span>
  );
}
