import '@testing-library/jest-dom/vitest';
import { cleanup } from '@testing-library/react';
import { afterEach, beforeEach, vi } from 'vitest';
import { simularMatchMedia } from './matchMedia';

beforeEach(() => {
  simularMatchMedia();
});

afterEach(() => {
  // Sem `globals: true` o Testing Library não limpa sozinho.
  cleanup();
  vi.unstubAllGlobals();
  vi.useRealTimers();
  localStorage.clear();
  document.documentElement.removeAttribute('data-tema');
  document.title = '';
});
