import { Fragment } from 'react';
import { juntarClasses } from '../lib/classes';
import estilos from './EstadoCarregando.module.css';

export type FormaCarregando = 'cards' | 'tabela' | 'grafico';

/** Alturas (%) das barras do histograma de mentira (print 4h); valores únicos servem de key. */
const ALTURAS_BARRAS = [12, 30, 48, 70, 84, 77, 56, 34, 20] as const;
const CARTOES = [1, 2, 3] as const;
const LINHAS_TABELA = [1, 2, 3, 4, 5, 6] as const;

const ESQUELETO_CARDS = (
  <div className={estilos.cartoes}>
    {CARTOES.map((n) => (
      <div key={n} className={estilos.cartao}>
        <span className={juntarClasses(estilos.bloco, estilos.rotulo)} />
        <span className={juntarClasses(estilos.bloco, estilos.valor)} />
        <span className={juntarClasses(estilos.bloco, estilos.linha)} />
        <span className={juntarClasses(estilos.bloco, estilos.linhaCurta)} />
      </div>
    ))}
  </div>
);

const ESQUELETO_TABELA = (
  <div className={estilos.tabela}>
    {LINHAS_TABELA.map((n) => (
      <span key={n} className={juntarClasses(estilos.bloco, estilos.linhaTabela)} />
    ))}
  </div>
);

const ESQUELETO_GRAFICO = (
  <div className={estilos.grafico}>
    <div className={estilos.area}>
      {ALTURAS_BARRAS.map((altura) => (
        <span key={altura} className={estilos.barra} style={{ height: `${String(altura)}%` }} />
      ))}
    </div>
    <div className={estilos.textos}>
      <span className={juntarClasses(estilos.bloco, estilos.rotulo)} />
      <span className={juntarClasses(estilos.bloco, estilos.linha)} />
      <span className={juntarClasses(estilos.bloco, estilos.linhaCurta)} />
    </div>
  </div>
);

const ESQUELETOS = {
  cards: ESQUELETO_CARDS,
  tabela: ESQUELETO_TABELA,
  grafico: ESQUELETO_GRAFICO,
} as const satisfies Record<FormaCarregando, unknown>;

interface PropsEstadoCarregando {
  mensagem: string;
  /** Uma forma ou várias em sequência (ex.: `['cards', 'grafico']`). */
  forma?: FormaCarregando | readonly FormaCarregando[];
}

export default function EstadoCarregando({
  mensagem,
  forma = 'cards',
}: Readonly<PropsEstadoCarregando>) {
  const formas: readonly FormaCarregando[] = typeof forma === 'string' ? [forma] : forma;
  return (
    <div className={estilos.estado} aria-busy="true">
      <div className={estilos.esqueletos} aria-hidden="true">
        {formas.map((cada) => (
          <Fragment key={cada}>{ESQUELETOS[cada]}</Fragment>
        ))}
      </div>
      <p role="status" className={estilos.mensagem}>
        {mensagem}
      </p>
    </div>
  );
}
