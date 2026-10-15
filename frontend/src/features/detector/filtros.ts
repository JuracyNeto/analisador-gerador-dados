import type { Aviso, Severidade } from './tipos';

/** Só os avisos das severidades marcadas, na ordem da API. */
export function filtrarPorSeveridade(
  avisos: readonly Aviso[],
  marcadas: ReadonlySet<Severidade>,
): Aviso[] {
  return avisos.filter((aviso) => marcadas.has(aviso.severidade));
}
