import { useId } from 'react';
import Grafico from '../../../shared/graficos/Grafico';
import Card from '../../../shared/ui/Card';
import { TEXTOS_BIVARIADA } from '../textos';
import type { Figura } from '../tipos';
import estilos from './CardResiduos.module.css';

const ALTURA_RESIDUOS = 300;

/** Card largo da tela 5a: gráfico de resíduos × X e "Como ler os resíduos" ao lado. */
export default function CardResiduos({ figura }: Readonly<{ figura: Figura }>) {
  const idTitulo = useId();
  return (
    <Card>
      <div className={estilos.grade}>
        <Grafico
          titulo={figura.titulo}
          resumo={figura.porque}
          figura={figura.dados}
          altura={ALTURA_RESIDUOS}
        />
        <aside className={estilos.leitura} aria-labelledby={idTitulo}>
          <h3 id={idTitulo} className={estilos.titulo}>
            {TEXTOS_BIVARIADA.residuos.comoLer}
          </h3>
          <p className={estilos.texto}>{figura.resumo}</p>
        </aside>
      </div>
    </Card>
  );
}
