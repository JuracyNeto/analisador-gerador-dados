import { describe, expect, it } from 'vitest';
import {
  formatarDecimal,
  formatarInteiro,
  formatarNumero,
  formatarPercentual,
  formatarPValor,
  lerNumeroPtBr,
} from './formatar';

describe('formatarNumero', () => {
  it.each([
    [70.314, '70,31'],
    [12345.6, '12.346'],
    [0.0012346, '0,001235'],
    [0, '0'],
    [-3.14159, '-3,142'],
    [69.8, '69,8'],
    [1.72, '1,72'],
    [999.95, '1.000'],
  ])('formata %s como %s', (valor, esperado) => {
    expect(formatarNumero(valor)).toBe(esperado);
  });

  it('aceita outro número de casas significativas', () => {
    expect(formatarNumero(70.314, 2)).toBe('70');
  });

  it('usa travessão para valores não finitos', () => {
    expect(formatarNumero(Number.NaN)).toBe('—');
    expect(formatarNumero(Number.POSITIVE_INFINITY)).toBe('—');
  });
});

describe('formatarInteiro', () => {
  it.each([
    [1234, '1.234'],
    [1234567, '1.234.567'],
    [12.6, '13'],
  ])('formata %s como %s', (valor, esperado) => {
    expect(formatarInteiro(valor)).toBe(esperado);
  });
});

describe('formatarPercentual', () => {
  it.each([
    [21.6, 1, '21,6%'],
    [21.66, 1, '21,7%'],
    [100, 1, '100%'],
    [33.333, 2, '33,33%'],
    [-0.04, 1, '0%'],
  ])('formata %s com %s casas como %s', (valor, casas, esperado) => {
    expect(formatarPercentual(valor, casas)).toBe(esperado);
  });
});

describe('lerNumeroPtBr', () => {
  it.each([
    ['1,72', 1.72],
    ['1.234,5', 1234.5],
    ['1.234.567,89', 1234567.89],
    ['-3', -3],
    [' 7 ', 7],
    ['+2,5', 2.5],
    ['1.234', 1234],
    ['1.72', 1.72],
  ])('lê "%s" como %s', (texto, esperado) => {
    expect(lerNumeroPtBr(texto)).toBe(esperado);
  });

  it.each(['', '   ', 'abc', '1,2,3', '1.23.4', '12a', ',5'])('devolve null para "%s"', (texto) => {
    expect(lerNumeroPtBr(texto)).toBeNull();
  });
});

describe('formatarDecimal', () => {
  it.each([
    [40.43, 1, '40,4'],
    [100, 1, '100,0'],
    [4, 1, '4,0'],
    [1234.5, 2, '1.234,50'],
  ])('formata %d com %d casa(s) fixa(s): %s', (valor, casas, esperado) => {
    expect(formatarDecimal(valor, casas)).toBe(esperado);
  });
});

describe('formatarPValor', () => {
  it.each([
    [0.0004, 'p < 0,001'],
    [0.001, 'p = 0,001'],
    [0.2134, 'p = 0,213'],
    [0.05, 'p = 0,05'],
  ])('%s → %s', (p, esperado) => {
    expect(formatarPValor(p)).toBe(esperado);
  });
});
