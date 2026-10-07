import Grafico from '../../../shared/graficos/Grafico';
import Card from '../../../shared/ui/Card';
import { TEXTOS_ANALISE } from '../textos';
import type { Figura } from '../tipos';
import estilos from './CardGrafico.module.css';

const ALTURA_PADRAO = 300;

interface Props {
  figura: Figura;
  altura?: number;
}

export default function CardGrafico({ figura, altura = ALTURA_PADRAO }: Readonly<Props>) {
  return (
    <Card>
      <Grafico
        titulo={figura.titulo}
        resumo={figura.resumo}
        figura={figura.dados}
        altura={altura}
      />
      <p className={estilos.porque}>
        <strong>{TEXTOS_ANALISE.graficos.porque}</strong> {figura.porque}
      </p>
    </Card>
  );
}
