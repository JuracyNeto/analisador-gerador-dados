import { describe, expect, it, vi } from 'vitest';
import { simularMatchMedia } from '../../testes/matchMedia';
import { aplicarTemaInicial, salvarTema } from './preferencia';

describe('aplicarTemaInicial', () => {
  it('usa o tema salvo e marca o <html>', () => {
    localStorage.setItem('tema', 'escuro');

    expect(aplicarTemaInicial()).toBe('escuro');
    expect(document.documentElement).toHaveAttribute('data-tema', 'escuro');
  });

  it('segue o sistema quando não há tema salvo', () => {
    simularMatchMedia(['(prefers-color-scheme: dark)']);

    expect(aplicarTemaInicial()).toBe('escuro');
  });

  it('ignora valor inválido salvo', () => {
    localStorage.setItem('tema', 'roxo');

    expect(aplicarTemaInicial()).toBe('claro');
  });

  it('funciona com o localStorage bloqueado', () => {
    vi.spyOn(Storage.prototype, 'getItem').mockImplementation(() => {
      throw new Error('bloqueado');
    });

    expect(aplicarTemaInicial()).toBe('claro');
  });
});

describe('salvarTema', () => {
  it('salva e devolve true', () => {
    expect(salvarTema('escuro')).toBe(true);
    expect(localStorage.getItem('tema')).toBe('escuro');
  });

  it('devolve false quando não consegue salvar', () => {
    vi.spyOn(Storage.prototype, 'setItem').mockImplementation(() => {
      throw new Error('cheio');
    });

    expect(salvarTema('escuro')).toBe(false);
  });
});
