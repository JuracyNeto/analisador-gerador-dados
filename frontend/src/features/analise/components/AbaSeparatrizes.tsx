import { estaAplicavel } from '../abas';
import { useConsultaPosicao } from '../hooks/useConsultaPosicao';
import { rotuloDestacado } from '../separatrizes';
import type { PropsPainel } from '../tipos';
import estilos from './AbaSeparatrizes.module.css';
import PainelPosicao from './PainelPosicao';
import TabelaSeparatrizes from './TabelaSeparatrizes';

export default function AbaSeparatrizes({ analise, datasetId }: Readonly<PropsPainel>) {
  const comPainel = estaAplicavel(analise, 'posicao');
  const consulta = useConsultaPosicao(datasetId, analise.coluna, comPainel);
  // A aba fica desabilitada sem separatrizes (abasDaAnalise); a guarda só estreita o tipo.
  if (analise.separatrizes === null) return null;

  return (
    <div className={estilos.grade} data-com-painel={comPainel}>
      <TabelaSeparatrizes
        coluna={analise.coluna}
        separatrizes={analise.separatrizes}
        destaque={rotuloDestacado(consulta.posicaoAtual)}
      />
      {comPainel ? <PainelPosicao coluna={analise.coluna} consulta={consulta} /> : null}
    </div>
  );
}
