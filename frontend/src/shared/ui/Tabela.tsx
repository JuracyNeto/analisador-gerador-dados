import type { ReactNode } from 'react';
import { VISUALMENTE_OCULTO, juntarClasses } from '../lib/classes';
import estilos from './Tabela.module.css';

export interface ColunaTabela<L> {
  id: string;
  titulo: ReactNode;
  celula: (linha: L) => ReactNode;
  alinhamento?: 'esquerda' | 'direita';
  mono?: boolean;
  /** A célula vira <th scope="row"> (rótulo da linha). */
  cabecalhoLinha?: boolean;
}

interface PropsTabela<L> {
  legenda: string;
  colunas: readonly ColunaTabela<L>[];
  linhas: readonly L[];
  chave: (linha: L) => string;
  alturaMaxima?: number | undefined;
  destacada?: ((linha: L) => boolean) | undefined;
  rodape?: ReactNode;
}

function classeAlinhamento<L>(coluna: ColunaTabela<L>): string | undefined {
  return coluna.alinhamento === 'direita' ? estilos.direita : undefined;
}

function classesDaCelula<L>(coluna: ColunaTabela<L>): string {
  return juntarClasses(classeAlinhamento(coluna), coluna.mono === true && estilos.mono);
}

export default function Tabela<L>({
  legenda,
  colunas,
  linhas,
  chave,
  alturaMaxima,
  destacada,
  rodape,
}: Readonly<PropsTabela<L>>) {
  const rolavel = alturaMaxima !== undefined;
  return (
    <div className={estilos.moldura}>
      <div
        className={estilos.rolagem}
        style={rolavel ? { maxHeight: alturaMaxima } : undefined}
        role={rolavel ? 'region' : undefined}
        aria-label={rolavel ? legenda : undefined}
        tabIndex={rolavel ? 0 : undefined}
      >
        <table className={estilos.tabela}>
          <caption className={VISUALMENTE_OCULTO}>{legenda}</caption>
          <thead>
            <tr>
              {colunas.map((coluna) => (
                <th key={coluna.id} scope="col" className={classeAlinhamento(coluna)}>
                  {coluna.titulo}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {linhas.map((linha) => (
              <LinhaTabela
                key={chave(linha)}
                linha={linha}
                colunas={colunas}
                destacada={destacada?.(linha) === true}
              />
            ))}
          </tbody>
        </table>
      </div>
      {rodape === undefined ? null : <div className={estilos.rodape}>{rodape}</div>}
    </div>
  );
}

interface PropsLinhaTabela<L> {
  linha: L;
  colunas: readonly ColunaTabela<L>[];
  destacada: boolean;
}

function LinhaTabela<L>({ linha, colunas, destacada }: Readonly<PropsLinhaTabela<L>>) {
  return (
    <tr data-destacada={destacada || undefined}>
      {colunas.map((coluna) =>
        coluna.cabecalhoLinha === true ? (
          <th key={coluna.id} scope="row" className={classesDaCelula(coluna)}>
            {coluna.celula(linha)}
          </th>
        ) : (
          <td key={coluna.id} className={classesDaCelula(coluna)}>
            {coluna.celula(linha)}
          </td>
        ),
      )}
    </tr>
  );
}
