import { describe, expect, it } from 'vitest';
import { formatarDiferenca, formatarValor, subtituloResultado } from './comparacao';
import type { Gerado, LinhaComparacao } from './tipos';

function linha(
  estatistica: string,
  original: number | null,
  gerado: number | null,
): LinhaComparacao {
  const diferenca = original !== null && gerado !== null ? gerado - original : null;
  return { estatistica, original, gerado, diferenca };
}

describe('comparação', () => {
  it('formata n como inteiro, medidas com 4 algarismos e frequências em %', () => {
    expect(formatarValor(linha('n', 227, 500), 500)).toBe('500');
    expect(formatarValor(linha('Média', 70.31, 70.31), 70.3123)).toBe('70,31');
    expect(formatarValor(linha('fr% · F', 50, 25), 25)).toBe('25%');
    expect(formatarValor(linha('Média', null, 1), null)).toBe('—');
  });

  it('diferença com sinal; frequências em pontos percentuais', () => {
    expect(formatarDiferenca(linha('Mediana', 69.8, 70.1))).toBe('+0,3');
    expect(formatarDiferenca(linha('Assimetria', 0.32, 0.05))).toBe('−0,27');
    expect(formatarDiferenca(linha('Média', 70, 70))).toBe('0');
    // Na precisão dos valores mostrados: resto de arredondamento não aparece.
    expect(formatarDiferenca(linha('Média', 70.2079, 70.2081))).toBe('0,00');
    expect(formatarDiferenca(linha('Curtose', -0.3944, -0.3998))).toBe('−0,0054');
    expect(formatarDiferenca(linha('n', 219, 500))).toBe('+281');
    expect(formatarDiferenca(linha('fr% · F', 40.09, 42.33))).toBe('+2,2 p.p.');
    expect(formatarDiferenca(linha('Média', null, 70))).toBe('—');
  });

  it('subtítulo com a semente e o modo', () => {
    const base = { semente: 42, parametros: [{ nome: 'Modo', valor: 'Preservar estatísticas' }] };
    expect(subtituloResultado(base as unknown as Gerado)).toBe(
      'Semente 42 · preservar estatísticas',
    );
    expect(subtituloResultado({ semente: 5, parametros: [] } as unknown as Gerado)).toBe(
      'Semente 5 · correlação alvo',
    );
  });
});
