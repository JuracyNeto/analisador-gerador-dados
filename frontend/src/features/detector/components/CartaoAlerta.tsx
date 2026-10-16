import { useId, useState } from 'react';
import Botao from '../../../shared/ui/Botao';
import { TEXTOS_DETECTOR } from '../textos';
import type { Aviso } from '../tipos';
import estilos from './CartaoAlerta.module.css';
import ExplicacaoAlerta from './ExplicacaoAlerta';
import TopoAlerta from './TopoAlerta';

const T = TEXTOS_DETECTOR.cartao;

interface PropsCartaoAlerta {
  aviso: Aviso;
  /** O 1º alerta de cada grupo abre; os demais começam recolhidos, com "Ver explicação" (D140). */
  abertoInicial: boolean;
}

/** Alerta em 8 partes, na ordem da spec 16 (componentes.md §CartaoAlerta). */
export default function CartaoAlerta({ aviso, abertoInicial }: Readonly<PropsCartaoAlerta>) {
  const [aberto, setAberto] = useState(abertoInicial);
  const idTitulo = useId();
  const idExplicacao = useId();
  return (
    <article className={estilos.cartao} aria-labelledby={idTitulo}>
      <TopoAlerta aviso={aviso} />
      <div className={estilos.cabecalho}>
        <h3 id={idTitulo} className={estilos.titulo}>
          {aviso.titulo}
        </h3>
        <p className={estilos.resumo}>{aviso.resumo}</p>
      </div>
      {abertoInicial ? null : (
        <Botao
          variante="fantasma"
          tamanho="sm"
          className={estilos.alternar}
          iconeFinal={aberto ? 'expand_less' : 'expand_more'}
          aria-expanded={aberto}
          aria-controls={idExplicacao}
          onClick={() => {
            setAberto((atual) => !atual);
          }}
        >
          {aberto ? T.ocultarExplicacao : T.verExplicacao}
        </Botao>
      )}
      <div id={idExplicacao} className={estilos.explicacao} hidden={!aberto}>
        {aberto ? <ExplicacaoAlerta aviso={aviso} /> : null}
      </div>
    </article>
  );
}
