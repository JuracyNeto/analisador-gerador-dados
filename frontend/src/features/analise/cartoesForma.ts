/** Contrato `Forma` (spec 09) → cartões da aba "Forma e distribuição" (print 4e). */
import { formatarNumero, formatarPValor } from '../../shared/lib/formatar';
import type { DefinicaoCartao } from './cartoes';
import { TEXTOS_ANALISE } from './textos';
import type { Ajuste, Forma, Medida, TesteAderencia } from './tipos';

const F = TEXTOS_ANALISE.forma;
const SEPARADOR = ' · ';
const SEPARADOR_CALCULO = ' | ';
const CASAS_COEFICIENTES = 4;
/** G₁ e G₂ com 3 algarismos, como no print 4e ("0,32"). */
const CASAS_FORMA = 3;

function parametrosEmTexto(ajuste: Ajuste): string {
  return ajuste.parametros
    .filter((p) => p.simbolo !== 'E[X]' && p.simbolo !== 'Var')
    .map((p) => `${p.simbolo} = ${formatarNumero(p.valor)}`)
    .join(SEPARADOR);
}

function textoComplementar(teste: TesteAderencia): string {
  const gl = teste.gl === null ? '' : `${SEPARADOR}gl = ${String(teste.gl)}`;
  const estatistica = `χ² = ${formatarNumero(teste.estatistica)}`;
  return F.complementar(
    `${teste.nome}: ${estatistica}${gl}${SEPARADOR}${formatarPValor(teste.p_valor)}`,
  );
}

function calculoDoAjuste(ajuste: Ajuste): string | null {
  const partes = [
    ajuste.calculo,
    ajuste.complementar ? textoComplementar(ajuste.complementar) : null,
  ];
  const presentes = partes.filter((parte): parte is string => parte !== null);
  return presentes.length === 0 ? null : presentes.join(SEPARADOR_CALCULO);
}

function valorDoAjuste(ajuste: Ajuste): string {
  if (ajuste.teste !== null) return formatarPValor(ajuste.teste.p_valor);
  const p = ajuste.parametros.find((parametro) => parametro.simbolo === 'p̂');
  return p === undefined ? '—' : `p̂ = ${formatarNumero(p.valor)}`;
}

/** `Ajuste` não é `Medida`: o p-valor vira o valor do card e a frase vira a interpretação. */
export function medidaDoAjuste(ajuste: Ajuste): Medida {
  if (!ajuste.aplicavel) {
    return {
      valor: null,
      aplicavel: false,
      motivo: ajuste.motivo,
      calculo: null,
      interpretacao: null,
      formula: null,
    };
  }
  const parametros = parametrosEmTexto(ajuste);
  const frase = [ajuste.frase, parametros].filter(Boolean).join(' ');
  return {
    valor: valorDoAjuste(ajuste),
    aplicavel: true,
    motivo: null,
    calculo: calculoDoAjuste(ajuste),
    interpretacao: frase === '' ? null : frase,
    formula: ajuste.formula,
  };
}

function seloDoAjuste(ajuste: Ajuste): string | undefined {
  if (ajuste.teste === null) return undefined;
  const nome = F.nomes[ajuste.distribuicao];
  return ajuste.teste.compativel ? F.compativel(nome) : F.afasta(nome);
}

export function seloAssimetria(forma: Forma): string | undefined {
  const classe = forma.classificacao_assimetria;
  if (classe === null) return undefined;
  return F.seloAssimetria[classe][forma.sentido_assimetria ?? 'nenhum'];
}

export function seloCurtose(forma: Forma): string | undefined {
  const classe = forma.classificacao_curtose;
  return classe === null ? undefined : F.seloCurtose[classe];
}

function rotuloDoSegundoAjuste(ajuste: Ajuste): string {
  return ajuste.distribuicao === 'bernoulli' ? F.ajusteBernoulli : F.ajusteBinomial;
}

export function cartoesForma(forma: Forma): DefinicaoCartao[] {
  const { normal, binomial } = forma;
  return [
    {
      id: 'assimetria',
      rotulo: F.assimetria,
      medida: forma.assimetria,
      casasSignificativas: CASAS_FORMA,
      selo: seloAssimetria(forma),
    },
    {
      id: 'curtose',
      rotulo: F.curtose,
      medida: forma.curtose,
      casasSignificativas: CASAS_FORMA,
      selo: seloCurtose(forma),
    },
    {
      id: 'normal',
      rotulo: F.ajusteNormal,
      medida: medidaDoAjuste(normal),
      selo: seloDoAjuste(normal),
    },
    {
      id: 'binomial',
      rotulo: rotuloDoSegundoAjuste(binomial),
      medida: medidaDoAjuste(binomial),
      selo: seloDoAjuste(binomial),
    },
  ];
}

function coeficiente(simbolo: string, medida: Medida): string | null {
  if (!medida.aplicavel || typeof medida.valor !== 'number') return null;
  return `${simbolo} = ${formatarNumero(medida.valor, CASAS_COEFICIENTES)}`;
}

/** Nota abaixo dos cards (como a nota populacional da Dispersão, D80). */
export function notaCoeficientes(forma: Forma): string | null {
  const pearson = [
    coeficiente('As₁', forma.assimetria_pearson_1),
    coeficiente('As₂', forma.assimetria_pearson_2),
  ].filter((parte): parte is string => parte !== null);
  const k = forma.curtose_percentilica;
  const partes = [
    pearson.length > 0 ? F.pearson(pearson.join(SEPARADOR)) : null,
    k.aplicavel && typeof k.valor === 'number'
      ? F.percentilica(formatarNumero(k.valor, CASAS_COEFICIENTES))
      : null,
  ].filter((parte): parte is string => parte !== null);
  return partes.length === 0 ? null : partes.join(' ');
}
