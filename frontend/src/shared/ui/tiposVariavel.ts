/** Tipo de variável → ícone, rótulos e token de cor (tokens.md, "Tipos de variável"). */
import type { CSSProperties } from 'react';
import type { components } from '../api/schema';

export type TipoVariavel = components['schemas']['TipoVariavel'];

interface ConfiguracaoTipo {
  icone: string;
  rotuloCurto: string;
  rotuloCompleto: string;
  token: `--tipo-${TipoVariavel}`;
}

export const TIPOS_VARIAVEL = {
  nominal: {
    icone: 'sell',
    rotuloCurto: 'Nominal',
    rotuloCompleto: 'Qualitativa nominal',
    token: '--tipo-nominal',
  },
  ordinal: {
    icone: 'stairs',
    rotuloCurto: 'Ordinal',
    rotuloCompleto: 'Qualitativa ordinal',
    token: '--tipo-ordinal',
  },
  discreta: {
    icone: 'pin',
    rotuloCurto: 'Discreta',
    rotuloCompleto: 'Quantitativa discreta',
    token: '--tipo-discreta',
  },
  continua: {
    icone: 'straighten',
    rotuloCurto: 'Contínua',
    rotuloCompleto: 'Quantitativa contínua',
    token: '--tipo-continua',
  },
  binaria: {
    icone: 'toggle_on',
    rotuloCurto: 'Binária',
    rotuloCompleto: 'Binária',
    token: '--tipo-binaria',
  },
  data: {
    icone: 'calendar_month',
    rotuloCurto: 'Data',
    rotuloCompleto: 'Data ou hora (ignorada)',
    token: '--tipo-data',
  },
  identificador: {
    icone: 'fingerprint',
    rotuloCurto: 'Identificador',
    rotuloCompleto: 'Identificador (ignorada)',
    token: '--tipo-identificador',
  },
} as const satisfies Record<TipoVariavel, ConfiguracaoTipo>;

/** Ordem de exibição (resumo da tela 2 e Select "Corrigir tipo"). */
export const ORDEM_TIPOS = [
  'continua',
  'discreta',
  'ordinal',
  'nominal',
  'binaria',
  'data',
  'identificador',
] as const satisfies readonly TipoVariavel[];

export const ROTULO_CORRIGIDO = 'corrigido';
export const DICA_CORRIGIDO = 'corrigido por você';

const TIPOS_NUMERICOS: ReadonlySet<TipoVariavel> = new Set<TipoVariavel>(['discreta', 'continua']);

export function ehNumerico(tipo: TipoVariavel): boolean {
  return TIPOS_NUMERICOS.has(tipo);
}

/** Tipos auxiliares ficam fora das análises (D17, D90); espelha TIPOS_AUXILIARES do backend. */
const TIPOS_AUXILIARES: ReadonlySet<TipoVariavel> = new Set<TipoVariavel>([
  'identificador',
  'data',
]);

export function ehAuxiliar(tipo: TipoVariavel): boolean {
  return TIPOS_AUXILIARES.has(tipo);
}

export function corDoTipo(tipo: TipoVariavel): string {
  return `var(${TIPOS_VARIAVEL[tipo].token})`;
}

/** Texto, fundo suave e borda 35% da cor do tipo (componentes.md, ChipTipo). */
export function estiloDoTipo(tipo: TipoVariavel): CSSProperties {
  const { token } = TIPOS_VARIAVEL[tipo];
  return {
    color: `var(${token})`,
    backgroundColor: `var(${token}-suave)`,
    borderColor: `color-mix(in oklab, var(${token}) 35%, transparent)`,
  };
}
