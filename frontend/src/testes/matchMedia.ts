import { vi } from 'vitest';

/** Simula window.matchMedia: só as consultas listadas correspondem. */
export function simularMatchMedia(consultasVerdadeiras: readonly string[] = []): void {
  vi.stubGlobal('matchMedia', (consulta: string) => ({
    matches: consultasVerdadeiras.includes(consulta),
    media: consulta,
    onchange: null,
    addEventListener: () => undefined,
    removeEventListener: () => undefined,
    addListener: () => undefined,
    removeListener: () => undefined,
    dispatchEvent: () => false,
  }));
}
