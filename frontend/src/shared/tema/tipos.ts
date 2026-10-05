export type Tema = 'claro' | 'escuro';

export interface ValorTema {
  tema: Tema;
  definirTema: (tema: Tema) => void;
}
