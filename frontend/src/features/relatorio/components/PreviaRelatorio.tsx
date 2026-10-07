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

interface PropsPagina {
  src: string;
  carregando: boolean;
  aoCarregar: (iframe: HTMLIFrameElement) => void;
}

function PaginaPrevia({ src, carregando, aoCarregar }: Readonly<PropsPagina>) {
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
      {carregando ? COBERTURA : null}
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
