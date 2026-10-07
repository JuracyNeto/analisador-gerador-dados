import { vi } from 'vitest';

/** Substitui URL.createObjectURL e o clique em <a> (o jsdom não baixa arquivos). */
export function simularDownload() {
  const nomesBaixados: string[] = [];
  const liberar = vi.fn();
  Object.assign(URL, { createObjectURL: vi.fn(() => 'blob:teste'), revokeObjectURL: liberar });
  vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(function (
    this: HTMLAnchorElement,
  ) {
    nomesBaixados.push(this.download);
  });
  return { nomesBaixados, liberar };
}
