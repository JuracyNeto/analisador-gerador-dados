import { renderHook } from '@testing-library/react';
import { expect, it } from 'vitest';
import { simularMatchMedia } from '../../testes/matchMedia';
import { useConsultaMidia } from './useConsultaMidia';

it('diz se a consulta de mídia corresponde', () => {
  simularMatchMedia(['(min-width: 1280px)']);

  expect(renderHook(() => useConsultaMidia('(min-width: 1280px)')).result.current).toBe(true);
  expect(renderHook(() => useConsultaMidia('(max-width: 600px)')).result.current).toBe(false);
});
