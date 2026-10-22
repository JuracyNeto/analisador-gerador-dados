import { useId } from 'react';
import EstadoCarregando from '../../../shared/ui/EstadoCarregando';
import EstadoVazio from '../../../shared/ui/EstadoVazio';
import { TEXTOS_RELATORIO } from '../textos';
import estilos from './PreviaRelatorio.module.css';

const T = TEXTOS_RELATORIO;

const COBERTURA = (
  <div className={estilos.cobertura}>
    <EstadoCarregando forma="grafico" mensagem={T.montando} />
  </div>
);

const ATUALIZANDO = (
  <div className={estilos.atualizando}>
    <p role="status" className={estilos.aviso}>
      {T.atualizando}
    </p>
  </div>
);

function cobertura(carregando: boolean, atualizando: boolean) {
  if (!carregando) return null;
  return atualizando ? ATUALIZANDO : COBERTURA;
}

interface PropsPagina {
  src: string;
  carregando: boolean;
  atualizando: boolean;
  aoCarregar: (iframe: HTMLIFrameElement) => void;
}

function PaginaPrevia({ src, carregando, atualizando, aoCarregar }: Readonly<PropsPagina>) {
  return (
    <div className={estilos.pagina} aria-busy={carregando}>
      <iframe
        src={src}
        title={T.tituloPrevia}
        className={estilos.iframe}
        onLoad={(evento) => {
          aoCarregar(evento.currentTarget);
        }}
      />
      {cobertura(carregando, atualizando)}
    </div>
  );
}

interface Props extends Omit<PropsPagina, 'src'> {
  src: string | null;
}

export default function PreviaRelatorio({ src, ...resto }: Readonly<Props>) {
  const idCabecalho = useId();

  return (
    <section className={estilos.area} aria-labelledby={idCabecalho}>
      <p id={idCabecalho} className={estilos.cabecalho}>
        {T.previa}
      </p>
      {src === null ? (
        <EstadoVazio icone="description" titulo={T.vazio.titulo} descricao={T.vazio.descricao} />
      ) : (
        <PaginaPrevia src={src} {...resto} />
      )}
    </section>
  );
}
