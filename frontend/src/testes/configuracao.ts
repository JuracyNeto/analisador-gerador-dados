import '@testing-library/jest-dom/vitest';
import { cleanup, configure } from '@testing-library/react';
import { afterEach, beforeEach, vi } from 'vitest';
import { simularMatchMedia } from './matchMedia';

// Páginas com lazy() demoram mais que 1 s na primeira transformação do Vite (máquina ou CI ocupados).
configure({ asyncUtilTimeout: 5000 });

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
