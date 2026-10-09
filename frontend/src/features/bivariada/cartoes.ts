/** Contrato `Bivariada` (spec 10) → cards r de Pearson, R² e reta (print 5a). */
import type { DefinicaoCartao, Medida } from '../../shared/metricas/cartoes';
import { TEXTOS_BIVARIADA } from './textos';
import type { Bivariada } from './tipos';

const C = TEXTOS_BIVARIADA.cartoes;
const CASAS_R = 3;
const CASAS_R2 = 2;

function juntar(partes: readonly (string | null)[], separador: string): string | null {
  const presentes = partes.filter((parte): parte is string => parte !== null && parte !== '');
  return presentes.length === 0 ? null : presentes.join(separador);
}

/** r com a frase do teste t e o cálculo de Spearman ao lado (spec 10: "exibido ao lado"). */
function medidaDoR(bivariada: Bivariada): Medida {
  const { pearson, teste_t: testeT, spearman } = bivariada;
  return {
    ...pearson,
    interpretacao: juntar([pearson.interpretacao, testeT.interpretacao], ' '),
    calculo: juntar([pearson.calculo, testeT.calculo, spearman.calculo], ' | '),
  };
}

export function seloCorrelacao({ forca, sentido }: Bivariada): string {
  return forca === 'fraca' || sentido === 'nula' ? C.seloFraca : C.selo(sentido, forca);
}

export function cartoesBivariada(bivariada: Bivariada): DefinicaoCartao[] {
  const { regressao } = bivariada;
  return [
    {
      id: 'pearson',
      rotulo: C.pearson,
      medida: medidaDoR(bivariada),
      selo: seloCorrelacao(bivariada),
      casasSignificativas: CASAS_R,
    },
    { id: 'r2', rotulo: C.r2, medida: regressao.r2, unidade: '%', casasSignificativas: CASAS_R2 },
    { id: 'reta', rotulo: C.reta, medida: regressao.reta, tamanhoValor: 'menor' },
  ];
}
