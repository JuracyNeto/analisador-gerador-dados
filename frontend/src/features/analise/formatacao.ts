/** Número opcional (ponto médio, limites): ausente vira travessão. */
export function formatarOpcional(valor: number | null, formatar: (v: number) => string): string {
  return valor === null ? '—' : formatar(valor);
}
