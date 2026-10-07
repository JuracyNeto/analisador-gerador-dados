import { afterEach, describe, expect, it, vi } from 'vitest';
import { simularDownload } from '../../testes/downloadFalso';
import { baixarArquivo } from './baixarArquivo';

describe('baixarArquivo', () => {
  afterEach(() => {
    vi.restoreAllMocks();
    vi.useRealTimers();
  });

  it('clica num link temporário com o nome do arquivo e libera a URL depois', () => {
    vi.useFakeTimers();
    const { nomesBaixados, liberar } = simularDownload();

    baixarArquivo(new Blob(['<html></html>']), 'relatorio-pesquisa_saude.html');
    vi.runAllTimers();

    expect(nomesBaixados).toEqual(['relatorio-pesquisa_saude.html']);
    expect(liberar).toHaveBeenCalledWith('blob:teste');
    expect(document.querySelector('a[download]')).toBeNull();
  });
});
