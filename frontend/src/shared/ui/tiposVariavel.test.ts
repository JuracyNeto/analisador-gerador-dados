import { describe, expect, it } from 'vitest';
import { ehAuxiliar, ehNumerico, estiloDoTipo, ORDEM_TIPOS, TIPOS_VARIAVEL } from './tiposVariavel';

describe('tiposVariavel', () => {
  it('ORDEM_TIPOS cobre os 7 tipos sem repetir', () => {
    expect(new Set(ORDEM_TIPOS).size).toBe(Object.keys(TIPOS_VARIAVEL).length);
  });

  it('usa rótulos e ícones do design', () => {
    expect(TIPOS_VARIAVEL.continua).toEqual({
      icone: 'straighten',
      rotuloCurto: 'Contínua',
      rotuloCompleto: 'Quantitativa contínua',
      token: '--tipo-continua',
    });
    expect(TIPOS_VARIAVEL.identificador.rotuloCompleto).toBe('Identificador (ignorada)');
  });

  it('cores saem dos tokens do tipo', () => {
    expect(estiloDoTipo('ordinal')).toEqual({
      color: 'var(--tipo-ordinal)',
      backgroundColor: 'var(--tipo-ordinal-suave)',
      borderColor: 'color-mix(in oklab, var(--tipo-ordinal) 35%, transparent)',
    });
  });

  it('só discreta e contínua são numéricas', () => {
    expect(ORDEM_TIPOS.filter(ehNumerico)).toEqual(['continua', 'discreta']);
  });

  it('data e identificador são auxiliares (fora das análises)', () => {
    expect(ORDEM_TIPOS.filter(ehAuxiliar)).toEqual(['data', 'identificador']);
    expect(TIPOS_VARIAVEL.data).toEqual({
      icone: 'calendar_month',
      rotuloCurto: 'Data',
      rotuloCompleto: 'Data ou hora (ignorada)',
      token: '--tipo-data',
    });
  });
});
