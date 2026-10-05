/** Estreita `T | null | undefined` para `T` nos testes, com erro claro se a fixture mudar. */
export function exigir<T>(valor: T | null | undefined, descricao: string): T {
  if (valor === null || valor === undefined) throw new Error(`Fixture sem ${descricao}.`);
  return valor;
}
