import { useState } from 'react';
import Grafico from '../../../shared/graficos/Grafico';
import Card from '../../../shared/ui/Card';
import EstadoVazio from '../../../shared/ui/EstadoVazio';
import Icone from '../../../shared/ui/Icone';
import Segmented from '../../../shared/ui/Segmented';
import { figuraAtiva, opcoesDeFiguras } from '../figuras';
import { TEXTOS_ANALISE } from '../textos';
import type { Figura, PropsPainel } from '../tipos';
import estilos from './AbaGraficos.module.css';

const G = TEXTOS_ANALISE.graficos;
const ALTURA_PRINCIPAL = 420;
const ALTURA_SECUNDARIA = 240;

const TITULO_PORQUE = (
  <span className={estilos.tituloPorque}>
    <Icone nome="lightbulb" />
    {G.porque}
  </span>
);

/** "Por que este gráfico?" e o resumo da figura ativa, à direita. */
function CardsLaterais({ figura }: Readonly<{ figura: Figura }>) {
  return (
    <aside className={estilos.lateral}>
      <Card titulo={TITULO_PORQUE}>
        <p className={estilos.texto}>{figura.porque}</p>
      </Card>
      <Card titulo={G.resumo}>
        <p className={estilos.texto}>{figura.resumo}</p>
      </Card>
    </aside>
  );
}

export default function AbaGraficos({ analise }: Readonly<PropsPainel>) {
  const [escolhida, setEscolhida] = useState<string | null>(null);
  const ativa = figuraAtiva(analise.figuras, escolhida);
  if (ativa === null)
    return (
      <EstadoVazio
        icone="scatter_plot"
        titulo={G.semFiguras.titulo}
        descricao={G.semFiguras.descricao}
      />
    );
  const secundarias = analise.figuras.filter((figura) => figura.id !== ativa.id);

  return (
    <div className={estilos.grade}>
      <Card>
        <div className={estilos.principal}>
          <Segmented
            rotulo={G.tipoGrafico}
            opcoes={opcoesDeFiguras(analise.figuras)}
            valor={ativa.id}
            aoMudar={setEscolhida}
          />
          <Grafico
            titulo={ativa.titulo}
            resumo={ativa.resumo}
            figura={ativa.dados}
            altura={ALTURA_PRINCIPAL}
          />
          {secundarias.length === 0 ? null : (
            <div className={estilos.secundarias}>
              {secundarias.map((figura) => (
                <Grafico
                  key={figura.id}
                  titulo={figura.titulo}
                  resumo={figura.resumo}
                  figura={figura.dados}
                  altura={ALTURA_SECUNDARIA}
                />
              ))}
            </div>
          )}
        </div>
      </Card>
      <CardsLaterais figura={ativa} />
    </div>
  );
}
