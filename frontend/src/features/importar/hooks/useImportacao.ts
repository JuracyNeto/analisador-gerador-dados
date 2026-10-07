import { useState } from 'react';
import { useAbrirExemplo, useImportarArquivo } from '../api';
import { NOME_EXEMPLO } from '../textos';

export interface Importacao {
  nomeArquivo: string;
  enviando: boolean;
  erro: Error | null;
  enviar: (arquivo: File) => void;
  abrirExemplo: () => void;
}

/** Fluxo da tela 1 antes de ter um dataset: enviar um arquivo ou abrir o exemplo. */
export function useImportacao(): Importacao {
  const [arquivo, setArquivo] = useState<File | null>(null);
  const importar = useImportarArquivo();
  const exemplo = useAbrirExemplo();

  return {
    nomeArquivo: arquivo === null ? NOME_EXEMPLO : arquivo.name,
    enviando: importar.isPending || exemplo.isPending,
    erro: importar.error ?? exemplo.error,
    enviar: (escolhido) => {
      exemplo.reset();
      setArquivo(escolhido);
      importar.mutate(escolhido);
    },
    abrirExemplo: () => {
      importar.reset();
      setArquivo(null);
      exemplo.mutate();
    },
  };
}
