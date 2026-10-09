import type { TipoColuna } from '../../shared/api/dataset';
import type { components } from '../../shared/api/schema';
import { ehAuxiliar, ORDEM_TIPOS, type TipoVariavel } from '../../shared/ui/tiposVariavel';

export type AlteracaoTipo = components['schemas']['AlteracaoTipo'];

export interface ContagemTipo {
  tipo: TipoVariavel;
  quantidade: number;
}

const MAX_EXEMPLOS = 4;

/** Resumo do topo da tela 2; identificador e data ficam de fora (são ignorados nas análises). */
export function contarPorTipo(colunas: readonly TipoColuna[]): ContagemTipo[] {
  return ORDEM_TIPOS.filter((tipo) => !ehAuxiliar(tipo))
    .map((tipo) => ({ tipo, quantidade: colunas.filter((c) => c.tipo === tipo).length }))
    .filter((contagem) => contagem.quantidade > 0);
}

/** "1,62; 1,78" quando há vírgula decimal (senão a vírgula separadora confunde); "F, M" no resto. */
export function juntarExemplos(exemplos: readonly string[]): string {
  const visiveis = exemplos.slice(0, MAX_EXEMPLOS);
  const separador = visiveis.some((exemplo) => exemplo.includes(',')) ? '; ' : ', ';
  return visiveis.join(separador);
}

/** Nova lista com o item de `de` em `para`; null se o movimento não é possível. */
export function moverItem<T>(lista: readonly T[], de: number, para: number): T[] | null {
  const item = lista[de];
  if (item === undefined || de === para || para < 0 || para >= lista.length) return null;
  return lista.toSpliced(de, 1).toSpliced(para, 0, item);
}

/** Atualização otimista do cache de colunas (o servidor confirma depois). */
export function aplicarAlteracao(
  colunas: readonly TipoColuna[] | undefined,
  coluna: string,
  alteracao: AlteracaoTipo,
): TipoColuna[] | undefined {
  return colunas?.map((atual): TipoColuna =>
    atual.coluna === coluna
      ? {
          ...atual,
          tipo: alteracao.tipo,
          origem: 'manual',
          categorias_ordem: alteracao.categorias_ordem ?? atual.categorias_ordem,
        }
      : atual,
  );
}
