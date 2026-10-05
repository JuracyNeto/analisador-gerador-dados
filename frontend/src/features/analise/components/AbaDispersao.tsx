import Banner from '../../../shared/ui/Banner';
import { estaAplicavel } from '../abas';
import { cartoesDispersao, notaPopulacional } from '../cartoes';
import { TEXTOS_ANALISE } from '../textos';
import type { PropsPainel } from '../tipos';
import GradeCardsMetrica from './GradeCardsMetrica';
import paineis from './paineis.module.css';

export default function AbaDispersao({ analise }: Readonly<PropsPainel>) {
  const { dispersao } = analise;
  // A aba fica desabilitada quando não há dispersão (abasDaAnalise); a guarda só estreita o tipo.
  if (dispersao === null) return null;
  const nota = notaPopulacional(dispersao);

  return (
    <div className={paineis.aba}>
      <GradeCardsMetrica cartoes={cartoesDispersao(dispersao)} formulas={analise.formulas} />
      {nota === null ? null : <p className={paineis.nota}>{nota}</p>}
      {estaAplicavel(analise, 'cv') ? (
        <Banner variante="info">{TEXTOS_ANALISE.cartoes.faixasCv}</Banner>
      ) : null}
    </div>
  );
}
