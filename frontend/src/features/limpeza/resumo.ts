import { formatarInteiro } from '../../shared/lib/formatar';
import { escolherForma } from '../../shared/lib/pluralizar';
import { soma } from './descricoes';
import { TEXTOS_LIMPEZA as T } from './textos';
import type { Diagnostico, ResultadoLimpeza } from './tipos';

export interface CardResumo {
  id: string;
  rotulo: string;
  valor: string;
  unidade: string;
  frase: string;
}

export interface AvisoLimpeza {
  tipo: 'sucesso';
  titulo: string;
  descricao: string;
}

interface TextosCard {
  rotulo: string;
  unidade: readonly [string, string];
}

function card(id: string, textos: TextosCard, total: number, frase: string): CardResumo {
  return {
    id,
    rotulo: textos.rotulo,
    valor: formatarInteiro(total),
    unidade: escolherForma(total, ...textos.unidade),
    frase,
  };
}

function fraseFaltantes(itens: Diagnostico['faltantes']): string {
  const maior = itens.toSorted((a, b) => b.n - a.n)[0];
  if (maior === undefined) return T.cards.faltantes.nenhum;
  return T.cards.faltantes.frase(itens.length, maior.coluna, maior.n);
}

function fraseDuplicados(grupos: Diagnostico['duplicados']): string {
  const primeiro = grupos[0];
  if (primeiro === undefined) return T.cards.duplicados.nenhum;
  return grupos.length === 1
    ? T.cards.duplicados.umaOrigem(primeiro.linha_original)
    : T.cards.duplicados.variasOrigens(grupos.length);
}

function fraseForaDeFaixa(itens: Diagnostico['fora_de_faixa']): string {
  if (itens.length === 0) return T.cards.foraDeFaixa.nenhum;
  return itens.some((i) => i.origem === 'usuario')
    ? T.cards.foraDeFaixa.usuario
    : T.cards.foraDeFaixa.iqr;
}

/** 4 cards do topo da tela 3 (tipo misto não tem card no design; aparece só como seção). */
export function resumirDiagnostico(d: Diagnostico): CardResumo[] {
  const grupos = soma(d.inconsistencias.map((i) => i.grupos.length));
  return [
    card(
      'faltantes',
      T.cards.faltantes,
      soma(d.faltantes.map((f) => f.n)),
      fraseFaltantes(d.faltantes),
    ),
    card(
      'duplicados',
      T.cards.duplicados,
      soma(d.duplicados.map((g) => g.copias.length)),
      fraseDuplicados(d.duplicados),
    ),
    card(
      'fora_de_faixa',
      T.cards.foraDeFaixa,
      soma(d.fora_de_faixa.map((i) => i.ocorrencias.length)),
      fraseForaDeFaixa(d.fora_de_faixa),
    ),
    card(
      'grafias',
      T.cards.grafias,
      grupos,
      grupos === 0 ? T.cards.grafias.nenhum : T.cards.grafias.frase,
    ),
  ];
}

export function temProblemas(d: Diagnostico): boolean {
  return [d.faltantes, d.duplicados, d.fora_de_faixa, d.inconsistencias, d.tipo_misto].some(
    (lista) => lista.length > 0,
  );
}

export function avisoLimpezaAplicada(
  nAntes: number,
  resultado: ResultadoLimpeza,
  nAcoes: number,
): AvisoLimpeza {
  return {
    tipo: 'sucesso',
    titulo: T.toast.aplicada(nAntes - resultado.n_linhas),
    descricao: T.toast.acoes(nAcoes),
  };
}

export function avisoLimpezaDesfeita(resultado: ResultadoLimpeza): AvisoLimpeza {
  return { tipo: 'sucesso', titulo: T.toast.desfeita(resultado.n_linhas), descricao: T.log.vazio };
}
