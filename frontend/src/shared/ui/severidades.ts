/** Severidade do detector → ícone, palavra e token de cor (spec 16, tokens.md). */
import type { CSSProperties } from 'react';
import type { components } from '../api/schema';

export type Severidade = components['schemas']['Severidade'];

interface ConfiguracaoSeveridade {
  icone: string;
  palavra: string;
  token: `--sev-${Severidade}`;
}

export const SEVERIDADES = {
  alta: { icone: 'report', palavra: 'Suspeita alta', token: '--sev-alta' },
  atencao: { icone: 'warning', palavra: 'Atenção', token: '--sev-atencao' },
  info: { icone: 'info', palavra: 'Informativo', token: '--sev-info' },
} as const satisfies Record<Severidade, ConfiguracaoSeveridade>;

/** Da mais forte para a mais fraca, como a API ordena os avisos. */
export const ORDEM_SEVERIDADES = [
  'alta',
  'atencao',
  'info',
] as const satisfies readonly Severidade[];

export function corDaSeveridade(severidade: Severidade): string {
  return `var(${SEVERIDADES[severidade].token})`;
}

/** Texto na cor da severidade sobre o fundo suave dela (BadgeSeveridade). */
export function estiloDaSeveridade(severidade: Severidade): CSSProperties {
  const { token } = SEVERIDADES[severidade];
  return { color: `var(${token})`, backgroundColor: `var(${token}-suave)` };
}
