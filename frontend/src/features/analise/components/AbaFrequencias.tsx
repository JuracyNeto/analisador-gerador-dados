import { cartoesResumoCategorico } from '../cartoes';
import type { PropsPainel } from '../tipos';
import estilos from './AbaFrequencias.module.css';
import CardGrafico from './CardGrafico';
import GradeCardsMetrica from './GradeCardsMetrica';
import paineis from './paineis.module.css';
import TabelaFrequencias from './TabelaFrequencias';

export default function AbaFrequencias({
  analise,
  atualizando,
  classes,
  aoMudarClasses,
}: Readonly<PropsPainel>) {
  const { frequencias } = analise;
  const principal = analise.figuras.find((figura) => figura.id === 'principal');

  return (
    <div className={paineis.aba}>
      <div className={estilos.grade}>
        <TabelaFrequencias
          tabela={frequencias}
          coluna={analise.coluna}
          nFaltantes={analise.n_faltantes}
          k={classes ?? frequencias.k}
          atualizando={atualizando}
          aoMudarClasses={aoMudarClasses}
        />
        {principal === undefined ? null : <CardGrafico figura={principal} />}
      </div>
      {analise.dispersao === null ? (
        <GradeCardsMetrica
          cartoes={cartoesResumoCategorico(analise)}
          formulas={analise.formulas}
          colunas={4}
        />
      ) : null}
    </div>
  );
}
