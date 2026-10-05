import { Suspense, lazy, useId } from 'react';
import { useTema } from '../tema/useTema';
import EstadoCarregando from '../ui/EstadoCarregando';
import { TEXTOS_UI } from '../ui/textos';
import estilos from './Grafico.module.css';

const GraficoPlotly = lazy(() => import('./GraficoPlotly'));

const ALTURA_PADRAO = 360;

interface PropsGrafico {
  /** Descritivo: "Distribuição de peso_kg (n = 227)". */
  titulo: string;
  /** Resumo textual do que o gráfico mostra (acessibilidade e leitura rápida). */
  resumo: string;
  /** JSON do Plotly vindo do backend ({data, layout}), sem template. */
  figura: Readonly<Record<string, unknown>>;
  altura?: number;
}

export default function Grafico({
  titulo,
  resumo,
  figura,
  altura = ALTURA_PADRAO,
}: Readonly<PropsGrafico>) {
  const { tema } = useTema();
  const idResumo = useId();
  return (
    <figure className={estilos.figura} aria-label={titulo} aria-describedby={idResumo}>
      <figcaption className={estilos.titulo}>{titulo}</figcaption>
      <Suspense
        fallback={<EstadoCarregando forma="grafico" mensagem={TEXTOS_UI.carregandoGrafico} />}
      >
        <GraficoPlotly key={tema} figura={figura} altura={altura} />
      </Suspense>
      <p id={idResumo} className={estilos.resumo}>
        {resumo}
      </p>
    </figure>
  );
}
