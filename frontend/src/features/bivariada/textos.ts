export const TEXTOS_BIVARIADA = {
  titulo: 'Análise bivariada',
  ajuda:
    'Veja se duas colunas numéricas andam juntas e use a reta para prever uma a partir da outra.',
  semDataset: 'Importe um arquivo para comparar duas colunas numéricas.',
  seletores: { x: 'X (explica)', y: 'Y (é explicada)', trocar: 'Trocar X e Y' },
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
