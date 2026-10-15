import { type ReactNode, useId, useState } from 'react';
import estilos from './Accordion.module.css';
import Icone from './Icone';

type VarianteAccordion = 'detalhes' | 'secao';

interface PropsAccordion {
  titulo: ReactNode;
  /** Texto à direita do gatilho (ex.: "2 regras, com motivo"). */
  complemento?: ReactNode;
  abertoInicial?: boolean;
  /** `detalhes`: gatilho 44 (Detalhes técnicos); `secao`: 52 com título 15/600 (Regras não verificadas). */
  variante?: VarianteAccordion;
  children: ReactNode;
}

/** Conteúdo recolhível (componentes.md §Accordion); o conteúdo só é montado quando aberto. */
export default function Accordion({
  titulo,
  complemento,
  abertoInicial = false,
  variante = 'detalhes',
  children,
}: Readonly<PropsAccordion>) {
  const [aberto, setAberto] = useState(abertoInicial);
  const id = useId();
  return (
    <div className={estilos.accordion} data-variante={variante}>
      <button
        type="button"
        className={estilos.gatilho}
        aria-expanded={aberto}
        aria-controls={id}
        onClick={() => {
          setAberto((atual) => !atual);
        }}
      >
        <Icone nome={aberto ? 'expand_more' : 'chevron_right'} tamanho={20} />
        <span className={estilos.titulo}>{titulo}</span>
        {complemento === undefined ? null : (
          <span className={estilos.complemento}>{complemento}</span>
        )}
      </button>
      <div id={id} className={estilos.conteudo} hidden={!aberto}>
        {aberto ? children : null}
      </div>
    </div>
  );
}
