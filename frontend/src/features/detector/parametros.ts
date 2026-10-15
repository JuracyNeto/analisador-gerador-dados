/** Filtros da tela 7 na URL (`?sev=alta&sev=atencao&agrupar=regra`), como a tela 4 (D78, D140). */
import { ORDEM_SEVERIDADES } from '../../shared/ui/severidades';
import type { Agrupamento, FiltrosDetector, Severidade } from './tipos';

const SEVERIDADE = 'sev';
const AGRUPAR = 'agrupar';
const AGRUPAMENTOS: readonly Agrupamento[] = ['coluna', 'regra'];
const AGRUPAMENTO_PADRAO: Agrupamento = 'coluna';

export const TODAS_SEVERIDADES: ReadonlySet<Severidade> = new Set(ORDEM_SEVERIDADES);

function ehSeveridade(valor: string): valor is Severidade {
  return ORDEM_SEVERIDADES.some((severidade) => severidade === valor);
}

/** Sem `sev`: todas; `sev=` vazio: nenhuma; só valores inválidos: todas (padrão). */
function lerSeveridades(busca: URLSearchParams): ReadonlySet<Severidade> {
  const valores = busca.getAll(SEVERIDADE);
  const validas = valores.filter(ehSeveridade);
  if (validas.length > 0) return new Set(validas);
  const nenhuma = valores.length > 0 && valores.every((valor) => valor === '');
  return nenhuma ? new Set() : TODAS_SEVERIDADES;
}

export function lerParametros(busca: URLSearchParams): FiltrosDetector {
  const agrupar = busca.get(AGRUPAR);
  return {
    severidades: lerSeveridades(busca),
    agrupar: AGRUPAMENTOS.find((valor) => valor === agrupar) ?? AGRUPAMENTO_PADRAO,
  };
}

/** O padrão (todas, por coluna) não vai para a URL; os demais parâmetros ficam. */
export function escreverParametros(
  busca: URLSearchParams,
  { severidades, agrupar }: FiltrosDetector,
): URLSearchParams {
  const nova = new URLSearchParams(busca);
  nova.delete(SEVERIDADE);
  nova.delete(AGRUPAR);
  if (severidades.size === 0) nova.append(SEVERIDADE, '');
  else if (severidades.size < TODAS_SEVERIDADES.size) {
    for (const severidade of ORDEM_SEVERIDADES) {
      if (severidades.has(severidade)) nova.append(SEVERIDADE, severidade);
    }
  }
  if (agrupar !== AGRUPAMENTO_PADRAO) nova.set(AGRUPAR, agrupar);
  return nova;
}
