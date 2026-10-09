export const TEXTOS_BIVARIADA = {
  titulo: 'Análise bivariada',
  ajuda:
    'Veja se duas colunas numéricas andam juntas e use a reta para prever uma a partir da outra.',
  semDataset: 'Importe um arquivo para comparar duas colunas numéricas.',
  seletores: { x: 'X (explica)', y: 'Y (é explicada)', trocar: 'Trocar X e Y' },
  previsao: {
    titulo: 'Prever Y para X =',
    prever: 'Prever',
    prevendo: 'Calculando…',
    previsto: (y: string) => `${y} previsto`,
    dica: 'Digite um valor de X e clique em Prever.',
    erroValor: 'Digite um número, por exemplo 1,75.',
    foraTitulo: 'Fora da faixa observada.',
  },
  matriz: { carregando: 'Calculando a matriz de correlação…' },
  residuos: { comoLer: 'Como ler os resíduos' },
  cartoes: {
    pearson: 'Correlação de Pearson (r)',
    r2: 'Coeficiente de determinação (R²)',
    reta: 'Reta de regressão',
    seloFraca: 'Correlação fraca',
    selo: (sentido: 'positiva' | 'negativa', forca: 'moderada' | 'forte') =>
      `Correlação ${sentido} ${forca}`,
  },
  navegacao: { voltar: 'Voltar para Análise univariada', continuar: 'Continuar para Relatório' },
};
