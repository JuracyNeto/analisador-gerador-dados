import { TEXTOS_ANALISE } from './textos';
import type { Figura } from './tipos';

const G = TEXTOS_ANALISE.graficos;

export interface OpcaoFigura {
  valor: string;
  rotulo: string;
  selo?: string;
}

/** O rótulo do segmento vem pronto do backend (`Figura.rotulo`, M1.5). */
export function opcoesDeFiguras(figuras: readonly Figura[]): OpcaoFigura[] {
  return figuras.map((figura) => ({
    valor: figura.id,
    rotulo: figura.rotulo,
    ...(figura.recomendado ? { selo: G.recomendado } : {}),
  }));
}

export function figuraAtiva(figuras: readonly Figura[], escolhida: string | null): Figura | null {
  return (
    figuras.find((figura) => figura.id === escolhida) ??
    figuras.find((figura) => figura.recomendado) ??
    figuras[0] ??
    null
  );
}
