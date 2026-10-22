import { describe, expect, it } from 'vitest';
import { TEXTOS_GERADOR as T } from './textos';

describe('textos do Gerador (spec 16)', () => {
  it('toasts no singular e no plural, com ponto de milhar', () => {
    expect(T.toast.valores(1)).toBe('Geramos 1 valor.');
    expect(T.toast.pares(1500)).toBe('Geramos 1.500 pares.');
    expect(T.toast.anexado(1, 'a.txt')).toBe('Anexamos 1 linha a a.txt.');
    expect(T.toast.novo(500)).toBe('Novo arquivo criado: 500 linhas.');
  });

  it('"arquivo" como no resto da interface e "desvio padrão" como na Análise', () => {
    expect(T.acoes).toMatchObject({
      anexar: 'Anexar ao arquivo atual',
      usar: 'Usar como novo arquivo',
    });
    expect(T.origem.bivariado.coluna).toBe('Par do arquivo');
    expect(T.desvioDe('peso')).toBe('Desvio padrão de peso');
    expect(T.descricaoPreservar('70,3', '11,2')).toBe(
      'Mesma média (70,3) e desvio padrão (11,2) da coluna.',
    );
  });
});
