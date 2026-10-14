/** Grupos da lista de alertas (tela 7a): por coluna (ou par, ou linhas inteiras) ou por regra. */
import { TEXTOS_DETECTOR } from './textos';
import type { Agrupamento, Aviso } from './tipos';

export interface GrupoAvisos {
  chave: string;
  titulo: string;
  /** Nome de coluna em fonte mono (componentes.md); "Linhas inteiras" e regras não. */
  mono: boolean;
  avisos: Aviso[];
}

type Cabecalho = Omit<GrupoAvisos, 'avisos'>;

/** R2 fala do par; R5 e as cópias da R6 (colunas vazio) falam de linhas inteiras (D132). */
function cabecalhoDaColuna(aviso: Aviso): Cabecalho {
  if (aviso.colunas.length === 0) {
    return { chave: '', titulo: TEXTOS_DETECTOR.linhasInteiras, mono: false };
  }
  const titulo = aviso.colunas.join(TEXTOS_DETECTOR.separadorPar);
  return { chave: titulo, titulo, mono: true };
}

function cabecalhoDaRegra(aviso: Aviso): Cabecalho {
  return { chave: aviso.regra, titulo: TEXTOS_DETECTOR.regra(aviso), mono: false };
}

const CABECALHOS = {
  coluna: cabecalhoDaColuna,
  regra: cabecalhoDaRegra,
} as const satisfies Record<Agrupamento, (aviso: Aviso) => Cabecalho>;

/** Grupos na ordem em que aparecem (a da API: mais graves primeiro); dentro, a ordem da API. */
export function agrupar(avisos: readonly Aviso[], modo: Agrupamento): GrupoAvisos[] {
  const grupos = new Map<string, GrupoAvisos>();
  for (const aviso of avisos) {
    const cabecalho = CABECALHOS[modo](aviso);
    const grupo = grupos.get(cabecalho.chave);
    if (grupo === undefined) grupos.set(cabecalho.chave, { ...cabecalho, avisos: [aviso] });
    else grupo.avisos.push(aviso);
  }
  return [...grupos.values()];
}
