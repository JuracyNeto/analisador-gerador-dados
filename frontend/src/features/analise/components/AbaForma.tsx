import Banner from '../../../shared/ui/Banner';
import { cartoesForma, notaCoeficientes } from '../cartoesForma';
import { maiorValorObservado } from '../tentativas';
import { TEXTOS_ANALISE } from '../textos';
import type { Analise, Figura, Forma, PropsPainel } from '../tipos';
import estilos from './AbaForma.module.css';
import CardGrafico from './CardGrafico';
import ControleTentativas from './ControleTentativas';
import GradeCardsMetrica from './GradeCardsMetrica';
import paineis from './paineis.module.css';

const ALTURA_GRAFICO = 320;

interface PropsBinomial {
  analise: Analise;
  forma: Forma;
  aoAplicar: (n: number) => void;
}

/** Só a discreta com Binomial tem o campo de tentativas (D96). */
function ControleBinomial({ analise, forma, aoAplicar }: Readonly<PropsBinomial>) {
  const maximo = maiorValorObservado(analise);
  const { binomial, tentativas } = forma;
  const temCampo = binomial.distribuicao === 'binomial' && binomial.aplicavel;
  if (!temCampo || tentativas === null || maximo === null) return null;
  // `key`: o campo volta ao valor usado sempre que a análise muda.
  return (
    <ControleTentativas
      key={tentativas}
      tentativas={tentativas}
      maximo={maximo}
      aoAplicar={aoAplicar}
    />
  );
}

function GraficosForma({ figuras }: Readonly<{ figuras: readonly Figura[] }>) {
  if (figuras.length === 0) return null;
  return (
    <section className={estilos.graficos} aria-label={TEXTOS_ANALISE.forma.tituloGraficos}>
      {figuras.map((figura) => (
        <CardGrafico key={figura.id} figura={figura} altura={ALTURA_GRAFICO} />
      ))}
    </section>
  );
}

/** Aba "Forma e distribuição" (print 4e): cards, nota, frase conjunta e gráficos. */
export default function AbaForma({ analise, aoMudarTentativas }: Readonly<PropsPainel>) {
  const { forma } = analise;
  // A aba fica desabilitada sem forma (abasDaAnalise); a guarda só estreita o tipo.
  if (forma === null) return null;
  const nota = notaCoeficientes(forma);

  return (
    <div className={paineis.aba}>
      <GradeCardsMetrica cartoes={cartoesForma(forma)} formulas={analise.formulas} />
      <ControleBinomial analise={analise} forma={forma} aoAplicar={aoMudarTentativas} />
      {nota === null ? null : <p className={paineis.nota}>{nota}</p>}
      {forma.interpretacao === null ? null : <Banner variante="info">{forma.interpretacao}</Banner>}
      <GraficosForma figuras={forma.figuras} />
    </div>
  );
}
