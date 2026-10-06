import { act, renderHook } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { useEscolhasLimpeza } from './useEscolhasLimpeza';
import { useLimitesPorColuna } from './useLimitesPorColuna';

describe('useLimitesPorColuna', () => {
  it('guarda o texto digitado e expõe o JSON dos limites válidos', () => {
    const { result } = renderHook(() => useLimitesPorColuna());

    act(() => {
      result.current.alterar('idade', 'min', '1');
    });
    act(() => {
      result.current.alterar('idade', 'max', '110');
    });

    expect(result.current.textos.idade).toEqual({ min: '1', max: '110' });
    expect(result.current.json).toBe('{"idade":{"min":1,"max":110}}');
  });
});

describe('useEscolhasLimpeza', () => {
  it('escolhe por chave e limpa tudo', () => {
    const { result } = renderHook(() => useEscolhasLimpeza());

    act(() => {
      result.current.escolher('duplicados', 'remover');
    });
    expect(result.current.valores).toEqual({ duplicados: 'remover' });

    act(() => {
      result.current.limpar();
    });
    expect(result.current.valores).toEqual({});
  });
});
