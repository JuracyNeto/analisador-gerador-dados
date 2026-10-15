import { Fragment } from 'react';
import { VISUALMENTE_OCULTO, juntarClasses } from '../../../shared/lib/classes';
import { formatarCelula } from '../../../shared/lib/formatarCelula';
import type { TrechoCarregado } from '../hooks/useLinhasDoAviso';
import { TEXTOS_DETECTOR } from '../textos';
import type { LinhaDados, Severidade } from '../tipos';
import estilos from './TabelaLinhas.module.css';

const T = TEXTOS_DETECTOR.drawer;
const RETICENCIAS = '…';

interface PropsTabelaLinhas {
  legenda: string;
  trechos: readonly TrechoCarregado[];
  destacadas: ReadonlySet<number>;
  /** Colunas do aviso: cabeçalho na cor da severidade e valor em 600 nas linhas destacadas. */
  afetadas: readonly string[];
  severidade: Severidade;
}

interface PropsLinha {
  linha: LinhaDados;
  colunas: readonly string[];
  afetadas: ReadonlySet<string>;
  destacada: boolean;
}

function Linha({ linha, colunas, afetadas, destacada }: Readonly<PropsLinha>) {
  return (
    <tr className={destacada ? estilos.destacada : undefined}>
      <th scope="row" className={estilos.numero}>
        {linha.linha}
        {destacada ? <span className={VISUALMENTE_OCULTO}>{T.destacada}</span> : null}
      </th>
      {colunas.map((coluna) => {
        const valor = linha.valores[coluna];
        return (
          <td
            key={coluna}
            className={juntarClasses(
              typeof valor === 'number' && estilos.direita,
              afetadas.has(coluna) && estilos.afetada,
            )}
          >
            {formatarCelula(valor)}
          </td>
        );
      })}
    </tr>
  );
}

function Cabecalho({ colunas, afetadas }: Readonly<Pick<PropsLinha, 'colunas' | 'afetadas'>>) {
  return (
    <thead>
      <tr>
        <th scope="col" className={estilos.numero}>
          {T.linha}
        </th>
        {colunas.map((coluna) => (
          <th
            key={coluna}
            scope="col"
            className={juntarClasses(afetadas.has(coluna) && estilos.colunaAfetada)}
          >
            {coluna}
          </th>
        ))}
      </tr>
    </thead>
  );
}

/** Linhas do drawer (7b): trechos com contexto, separados por "…", e as do alerta destacadas. */
export default function TabelaLinhas({
  legenda,
  trechos,
  destacadas,
  afetadas,
  severidade,
}: Readonly<PropsTabelaLinhas>) {
  const colunas = Object.keys(trechos.flatMap((trecho) => trecho.linhas)[0]?.valores ?? {});
  const colunasAfetadas = new Set(afetadas);
  return (
    <table className={estilos.tabela} data-severidade={severidade}>
      <caption className={VISUALMENTE_OCULTO}>{legenda}</caption>
      <Cabecalho colunas={colunas} afetadas={colunasAfetadas} />
      <tbody>
        {trechos.map(({ trecho, linhas }, i) => (
          <Fragment key={trecho.de}>
            {i === 0 ? null : (
              <tr className={estilos.separador}>
                <td colSpan={colunas.length + 1}>{RETICENCIAS}</td>
              </tr>
            )}
            {linhas.map((linha) => (
              <Linha
                key={linha.linha}
                linha={linha}
                colunas={colunas}
                afetadas={colunasAfetadas}
                destacada={destacadas.has(linha.linha)}
              />
            ))}
          </Fragment>
        ))}
      </tbody>
    </table>
  );
}
