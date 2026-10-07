import type { Tema } from './tipos';

const CHAVE_TEMA = 'tema';
const CONSULTA_ESCURO = '(prefers-color-scheme: dark)';

export function ehTema(valor: unknown): valor is Tema {
  return valor === 'claro' || valor === 'escuro';
}

export function lerTemaSalvo(): Tema | null {
  try {
    const salvo = localStorage.getItem(CHAVE_TEMA);
    return ehTema(salvo) ? salvo : null;
  } catch {
    // Armazenamento bloqueado (modo privado, política do navegador): segue o sistema.
    return null;
  }
}

/** Devolve false se o navegador não deixou salvar; a escolha vale só nesta visita. */
export function salvarTema(tema: Tema): boolean {
  try {
    localStorage.setItem(CHAVE_TEMA, tema);
    return true;
  } catch {
    return false;
  }
}

export function temaDoSistema(): Tema {
  return window.matchMedia(CONSULTA_ESCURO).matches ? 'escuro' : 'claro';
}

export function temaDoDocumento(): Tema | null {
  const atual = document.documentElement.dataset.tema;
  return ehTema(atual) ? atual : null;
}

export function aplicarTema(tema: Tema): void {
  document.documentElement.dataset.tema = tema;
}

/** Chamado em main.tsx antes do render: a primeira pintura já sai no tema certo. */
export function aplicarTemaInicial(): Tema {
  const tema = lerTemaSalvo() ?? temaDoSistema();
  aplicarTema(tema);
  return tema;
}
