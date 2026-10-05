import Card from '../../../shared/ui/Card';
import Tabela from '../../../shared/ui/Tabela';
import {
  chaveDaLinha,
  colunasDaTabela,
  ehLinhaModal,
  linhasComTotal,
  notasDaTabela,
} from '../frequencias';
import { TEXTOS_ANALISE } from '../textos';
import type { TabelaFrequencia } from '../tipos';
import ControleClasses from './ControleClasses';
import paineis from './paineis.module.css';

const T = TEXTOS_ANALISE.frequencias;

interface Props {
  tabela: TabelaFrequencia;
  coluna: string;
  nFaltantes: number;
  /** Nº de classes mostrado no controle (URL ou o da tabela); null quando a tabela não tem classes. */
  k: number | null;
  atualizando: boolean;
  aoMudarClasses: (k: number) => void;
}

export default function TabelaFrequencias({
  tabela,
  coluna,
  nFaltantes,
  k,
  atualizando,
  aoMudarClasses,
}: Readonly<Props>) {
  const controle =
    k !== null && tabela.k_sturges !== null ? (
      <ControleClasses k={k} kSturges={tabela.k_sturges} aoMudar={aoMudarClasses} />
    ) : null;

  return (
    <Card titulo={tabela.k === null ? T.titulo(coluna) : T.tituloClasses} acoes={controle}>
      <div aria-busy={atualizando}>
        <Tabela
          legenda={T.titulo(coluna)}
          colunas={colunasDaTabela(tabela, coluna)}
          linhas={linhasComTotal(tabela)}
          chave={chaveDaLinha}
          destacada={ehLinhaModal(tabela)}
        />
      </div>
      {notasDaTabela(tabela, nFaltantes).map((nota) => (
        <p key={nota} className={paineis.nota}>
          {nota}
        </p>
      ))}
    </Card>
  );
}
