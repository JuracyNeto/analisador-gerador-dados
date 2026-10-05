import { act, renderHook } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { useValorAtrasado } from './useValorAtrasado';

function montarComRelogioFalso() {
  vi.useFakeTimers();
  return renderHook(({ valor }) => useValorAtrasado(valor, 600), {
    initialProps: { valor: 'a' },
  });
}

function avancar(ms: number): void {
  act(() => {
    vi.advanceTimersByTime(ms);
  });
}

describe('useValorAtrasado', () => {
  afterEach(() => {
    vi.useRealTimers();
  });

  it('só devolve o valor novo depois do atraso', () => {
    const { result, rerender } = montarComRelogioFalso();

    rerender({ valor: 'b' });
    avancar(599);
    expect(result.current).toBe('a');

    avancar(1);
    expect(result.current).toBe('b');
  });

  it('reinicia a contagem a cada mudança', () => {
    const { result, rerender } = montarComRelogioFalso();

    rerender({ valor: 'b' });
    avancar(400);
    rerender({ valor: 'c' });
    avancar(400);
    expect(result.current).toBe('a');

    avancar(200);
    expect(result.current).toBe('c');
  });
});
