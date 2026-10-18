import type { components } from '../../shared/api/schema';
import { figura } from './blocosAnalise';

type Esquemas = components['schemas'];
type Aviso = Esquemas['AvisoDetector'];

const DETALHES: Esquemas['DetalhesAviso'] = {
  medida: 'Valores fora das cercas de Tukey ou com |z| > 3',
  valor: '2 moderados e 0 extremos',
  limiar: 'Moderado: fora de 18 a 81 (1,5·IQR)',
  teste: null,
  p_valor: null,
  p_em_palavras: null,
  formula: 'IQR = Q3 − Q1 · z = (x − x̄) / s',
};

function linhasDe(inicio: number, fim: number): number[] {
  return Array.from({ length: fim - inicio + 1 }, (_, i) => inicio + i);
}

/** Aviso com textos curtos; cada teste muda só o que importa. */
export function criarAviso(parcial: Partial<Aviso> & Pick<Aviso, 'regra' | 'nome_regra'>): Aviso {
  return {
    severidade: 'atencao',
    colunas: ['peso_kg'],
    titulo: `Título ${parcial.regra}`,
    resumo: `Resumo ${parcial.regra}.`,
    por_que: `Por que ${parcial.regra}.`,
    exemplo: null,
    pode_ser_normal: `…normal ${parcial.regra}.`,
    o_que_fazer: `Fazer ${parcial.regra}.`,
    detalhes: DETALHES,
    figura: null,
    ...parcial,
  };
}

export const avisoR1 = criarAviso({
  regra: 'R1',
  nome_regra: 'Bloco alinhado',
  severidade: 'alta',
  colunas: ['altura_m'],
  titulo: 'Bloco alinhado ao restante dos dados em altura_m',
  resumo:
    'Um bloco de 20 linhas (181–200) tem média e desvio quase idênticos aos do restante dos dados (diferença de 0,021%).',
  por_que:
    "Em dados reais, pedaços pequenos variam bastante; um bloco que 'bate' tudo pode ter sido colocado para alinhar as estatísticas.",
  pode_ser_normal: '…o conjunto foi ordenado ou amostrado de forma sistemática.',
  o_que_fazer: 'Confira de onde vieram essas linhas e se foram geradas ou ajustadas depois.',
  exemplo: {
    linhas: linhasDe(181, 200),
    valores: linhasDe(181, 200).map(() => '1,7'),
    texto: 'Linhas 181 a 200: média 1,702 (resto 1,702) · DP 0,09034 (resto 0,09036)',
  },
  detalhes: {
    medida:
      'Janelas de 20 linhas seguidas e o fim do arquivo (de 10 a 150 linhas): diferença de média (dᵤ) e de desvio (dₛ) para o restante das linhas, em desvios padrão do restante',
    valor: 'dᵤ = 0 · dₛ = 0,000206',
    limiar: 'dᵤ e dₛ < 0,01 e menos de 1% dos embaralhamentos com uma janela tão parecida',
    teste: 'Simulação: 1.000 embaralhamentos da coluna (semente fixa)',
    p_valor: 0.002,
    p_em_palavras: 'chance de acontecer por acaso: cerca de 1 em 500',
    formula: 'dᵤ = |x̄_bloco − x̄_resto| / s_resto · dₛ = |s_bloco − s_resto| / s_resto',
  },
  figura: { ...figura('blocos', 'Média por bloco', true, 'altura_m'), titulo: 'Média por bloco' },
});

export const avisoR2 = criarAviso({
  regra: 'R2',
  nome_regra: 'Correlação por blocos',
  severidade: 'alta',
  colunas: ['altura_m', 'peso_kg'],
  titulo: 'Correlação puxada em altura_m e peso_kg',
  resumo: 'A correlação geral entre altura_m e peso_kg é 0,78, mas a média dos blocos é só 0,41.',
  exemplo: { linhas: [97, 98], valores: ['1,6 · 60,1', '1,9 · 95'], texto: 'Linhas 97 e 98: …' },
});

export const avisoR5 = criarAviso({
  regra: 'R5',
  nome_regra: 'Duplicatas',
  severidade: 'alta',
  colunas: [],
  titulo: 'Linhas iguais em sequência',
  resumo:
    'Encontramos 3 linhas iguais a outras do arquivo; as linhas 44 a 47 são iguais e seguidas.',
  exemplo: {
    linhas: [44, 45, 46, 47],
    valores: ['M · 39 · 1,9', 'M · 39 · 1,9', 'M · 39 · 1,9', 'M · 39 · 1,9'],
    texto: 'Linhas 44 a 47: M · 39 · 1,9',
  },
});

export const avisoR4 = criarAviso({
  regra: 'R4',
  nome_regra: 'Valores redondos',
  titulo: 'Muitos valores redondos em peso_kg',
  resumo:
    '46% dos valores terminam em 0 ou 5; em medições reais o esperado seria cerca de 20% (2,3× mais).',
  exemplo: {
    linhas: [120, 121, 122],
    valores: ['70', '75', '80'],
    texto: 'Linhas 120 a 122: 70, 75, 80',
  },
  detalhes: {
    medida: 'Valores que terminam em 0 ou 5',
    valor: '46% (104 de 227)',
    limiar: 'p < 0,01 e pelo menos 1,5× o esperado (20%)',
    teste: 'Binomial unilateral',
    p_valor: 0.0003,
    p_em_palavras: 'chance de acontecer por acaso: menos de 1 em 1.000',
    formula: 'P(X ≥ 104), X ~ Binomial(227; 0,2)',
  },
});

export const avisoR9 = criarAviso({
  regra: 'R9',
  nome_regra: 'Último dígito',
  colunas: ['idade'],
  titulo: 'Último dígito repetido em idade',
  figura: figura('ultimo_digito', 'Último dígito', true, 'idade'),
});

export const avisoR7 = criarAviso({
  regra: 'R7',
  nome_regra: 'Valores distantes',
  severidade: 'info',
  colunas: ['idade'],
  titulo: 'Duas idades distantes das demais',
  resumo: '2 valores de idade estão muito longe dos demais (ex.: 94); o limite usual seria 81.',
  exemplo: { linhas: [1, 160], valores: ['89', '94'], texto: 'Linhas 1 e 160: 89; 94' },
});

/** Na ordem da API: severidade, regra, coluna. */
export const AVISOS = [avisoR1, avisoR2, avisoR5, avisoR4, avisoR9, avisoR7];

export const NAO_APLICADAS: Esquemas['RegraNaoAplicada'][] = [
  {
    regra: 'R8',
    nome_regra: 'Lei de Benford',
    coluna: 'idade',
    motivo: 'precisa de valores que variem em várias ordens de grandeza',
    frase:
      'Lei de Benford não verificada em idade: precisa de valores que variem em várias ordens de grandeza.',
  },
  {
    regra: 'R6',
    nome_regra: 'Comparação temporal',
    coluna: null,
    motivo: 'o arquivo não tem uma coluna de data',
    frase: 'Comparação temporal não verificada: o arquivo não tem uma coluna de data.',
  },
];

export const resultadoDetector: Esquemas['ResultadoDetector'] = {
  resumo: {
    total: 6,
    por_severidade: { alta: 3, atencao: 2, info: 1 },
    colunas_afetadas: ['altura_m', 'peso_kg', 'idade'],
    regras_verificadas: 9,
    regras_nao_aplicadas: 2,
    frase: 'Encontramos 6 alertas em 3 colunas',
    detalhe: 'altura_m, peso_kg e idade · 9 regras verificadas, 2 não se aplicam a este arquivo',
    vazio: null,
  },
  avisos: AVISOS,
  nao_aplicadas: NAO_APLICADAS,
};

export const VAZIO_DETECTOR =
  'Nenhuma das 11 regras encontrou suspeitas. Isso não garante que os dados sejam reais, mas não vimos sinais comuns de dados artificiais.';

export const resultadoVazio: Esquemas['ResultadoDetector'] = {
  resumo: {
    ...resultadoDetector.resumo,
    total: 0,
    por_severidade: { alta: 0, atencao: 0, info: 0 },
    colunas_afetadas: [],
    frase: 'Nenhum alerta',
    detalhe: '9 regras verificadas, 2 não se aplicam a este arquivo',
    vazio: VAZIO_DETECTOR,
  },
  avisos: [],
  nao_aplicadas: NAO_APLICADAS,
};

/** Linhas do dataset (GET /linhas) com idade, altura e peso. */
export function linhasDados(inicio: number, fim: number): Esquemas['LinhaDados'][] {
  return linhasDe(inicio, fim).map((linha) => ({
    linha,
    valores: { sexo: linha % 2 ? 'F' : 'M', idade: 20 + (linha % 40), peso_kg: 60.5 + (linha % 9) },
  }));
}
