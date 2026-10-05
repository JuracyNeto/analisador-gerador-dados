import { describe, expect, it } from 'vitest';
import { corpoJson } from './corpoJson';

describe('corpoJson', () => {
  it('monta método, cabeçalho e corpo em JSON', () => {
    expect(corpoJson('PATCH', { tipo: 'ordinal' })).toEqual({
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: '{"tipo":"ordinal"}',
    });
  });
});
