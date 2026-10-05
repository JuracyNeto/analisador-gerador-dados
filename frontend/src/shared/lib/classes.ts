export type ClasseOpcional = string | false | null | undefined;

/** Classe global de base.css: esconde da tela e mantém para leitores de tela. */
export const VISUALMENTE_OCULTO = 'visualmente-oculto';

export function juntarClasses(...classes: readonly ClasseOpcional[]): string {
  return classes
    .filter((classe): classe is string => typeof classe === 'string' && classe !== '')
    .join(' ');
}
