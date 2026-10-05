import { act, renderHook } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { useValorAtrasado } from './useValorAtrasado';

describe('useValorAtrasado', () => {
  afterEach(() => {
    vi.useRealTimers();
  });

  it('só devolve o valor novo depois do atraso', () => {
    vi.useFakeTimers();
    const { result, rerender } = renderHook(({ valor }) => useValorAtrasado(valor, 600), {
      initialProps: { valor: 'a' },
    });

    rerender({ valor: 'b' });
    act(() => {
      vi.advanceTimersByTime(599);
    });
    expect(result.current).toBe('a');

    act(() => {
      vi.advanceTimersByTime(1);
    });
    expect(result.current).toBe('b');
  });

  it('reinicia a contagem a cada mudança', () => {
    vi.useFakeTimers();
    const { result, rerender } = renderHook(({ valor }) => useValorAtrasado(valor, 600), {
      initialProps: { valor: 'a' },
    });

    rerender({ valor: 'b' });
    act(() => {
      vi.advanceTimersByTime(400);
    });
    rerender({ valor: 'c' });
    act(() => {
      vi.advanceTimersByTime(400);
    });
    expect(result.current).toBe('a');

    act(() => {
      vi.advanceTimersByTime(200);
    });
    expect(result.current).toBe('c');
  });
});
