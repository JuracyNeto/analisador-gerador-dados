import type { UseQueryResult } from '@tanstack/react-query';
import Grafico from '../../../shared/graficos/Grafico';
import GradeCardsMetrica from '../../../shared/metricas/GradeCardsMetrica';
import Card from '../../../shared/ui/Card';
import { cartoesBivariada } from '../cartoes';
import type { Bivariada, Figura, MatrizCorrelacao } from '../tipos';
import CardMatriz from './CardMatriz';
import CardResiduos from './CardResiduos';
import estilos from './ConteudoBivariada.module.css';
import PainelPrevisao from './PainelPrevisao';

const ALTURA_DISPERSAO = 420;

function figuraPorId(bivariada: Bivariada, id: string): Figura | undefined {
  return bivariada.figuras.find((figura) => figura.id === id);
}

interface Props {
  bivariada: Bivariada;
  datasetId: string;
  matriz: UseQueryResult<MatrizCorrelacao>;
}

/** Tela 5a: cards, dispersão + (prever, matriz) lado a lado, e resíduos embaixo. */
export default function ConteudoBivariada({ bivariada, datasetId, matriz }: Readonly<Props>) {
  const dispersao = figuraPorId(bivariada, 'dispersao');
  const residuos = figuraPorId(bivariada, 'residuos');
  const par = { x: bivariada.x, y: bivariada.y };

  return (
    <div className={estilos.conteudo}>
      <GradeCardsMetrica cartoes={cartoesBivariada(bivariada)} formulas={bivariada.formulas} />
      <div className={estilos.grade}>
        {dispersao === undefined ? null : (
          <Card>
            <Grafico
              titulo={dispersao.titulo}
              resumo={dispersao.resumo}
              figura={dispersao.dados}
              altura={ALTURA_DISPERSAO}
            />
          </Card>
        )}
        <div className={estilos.lateral}>
          {/* `key`: trocar X ou Y apaga a previsão anterior. */}
          <PainelPrevisao key={`${par.x}|${par.y}`} datasetId={datasetId} par={par} />
          <CardMatriz consulta={matriz} />
        </div>
      </div>
      {residuos === undefined ? null : <CardResiduos figura={residuos} />}
    </div>
  );
}
