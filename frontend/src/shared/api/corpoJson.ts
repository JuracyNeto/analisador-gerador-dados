/** Opções do fetch para enviar um corpo JSON. */
export function corpoJson(metodo: 'POST' | 'PATCH' | 'PUT', corpo: unknown): RequestInit {
  return {
    method: metodo,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(corpo),
  };
}
