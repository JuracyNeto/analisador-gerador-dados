export interface DatasetSessao {
  id: string;
  nomeArquivo: string;
}

/** Última geração (etapa 6), para o relatório incluir a seção Gerador (M3.5). */
export interface GeradoSessao {
  id: string;
  descricao: string;
}

export interface ValorSessao {
  dataset: DatasetSessao | null;
  definirDataset: (dataset: DatasetSessao) => void;
  ultimoGerado: GeradoSessao | null;
  definirUltimoGerado: (gerado: GeradoSessao) => void;
  encerrar: () => void;
  etapasVisitadas: ReadonlySet<number>;
  marcarVisitada: (etapa: number) => void;
}
