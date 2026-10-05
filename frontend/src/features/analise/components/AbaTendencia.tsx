import Banner from '../../../shared/ui/Banner';
import { cartoesTendencia } from '../cartoes';
import type { PropsPainel } from '../tipos';
import GradeCardsMetrica from './GradeCardsMetrica';
import paineis from './paineis.module.css';

export default function AbaTendencia({ analise }: Readonly<PropsPainel>) {
  return (
    <div className={paineis.aba}>
      <GradeCardsMetrica cartoes={cartoesTendencia(analise)} formulas={analise.formulas} />
      <div className={paineis.lista}>
        {analise.interpretacoes.map((texto) => (
          <Banner key={texto} variante="info">
            {texto}
          </Banner>
        ))}
      </div>
    </div>
  );
}
