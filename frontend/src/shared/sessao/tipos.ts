export interface DatasetSessao {
  id: string;
  nomeArquivo: string;
}

export interface ValorSessao {
  dataset: DatasetSessao | null;
  definirDataset: (dataset: DatasetSessao) => void;
  encerrar: () => void;
  etapasVisitadas: ReadonlySet<number>;
  marcarVisitada: (etapa: number) => void;
}
