/** Peças pequenas do contrato `Analise` usadas pelas fixtures da análise e da forma. */
import type { components } from '../../shared/api/schema';

type Esquemas = components['schemas'];
type Medida = Esquemas['Medida'];

export function medida(valor: Medida['valor'], extra: Partial<Medida> = {}): Medida {
  return {
    valor,
    aplicavel: true,
    motivo: null,
    calculo: null,
    interpretacao: null,
    formula: null,
    ...extra,
  };
}

export function naoSeAplica(motivo: string): Medida {
  return {
    valor: null,
    aplicavel: false,
    motivo,
    calculo: null,
    interpretacao: null,
    formula: null,
  };
}

export function figura(
  id: string,
  rotulo: string,
  recomendado: boolean,
  coluna = 'peso_kg',
): Esquemas['Figura'] {
  return {
    id,
    rotulo,
    titulo: `Figura ${id} de ${coluna}`,
    resumo: `Resumo de ${id}.`,
    porque: `Por que ${id}.`,
    recomendado,
    dados: { data: [], layout: {} },
  };
}
