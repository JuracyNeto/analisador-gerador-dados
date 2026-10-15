import { useState } from 'react';
import { useAbrirExemplo, useImportarArquivo } from '../api';
import { NOME_EXEMPLO } from '../textos';

export interface Importacao {
  nomeArquivo: string;
  enviando: boolean;
  erro: Error | null;
  enviar: (arquivo: File) => void;
  /** Um dos exemplos de `GET /datasets/exemplos` (o principal é `pesquisa_saude.txt`). */
  abrirExemplo: (arquivo: string) => void;
}

/** Fluxo da tela 1 antes de ter um dataset: enviar um arquivo ou abrir um exemplo. */
export function useImportacao(): Importacao {
  const [nomeArquivo, setNomeArquivo] = useState(NOME_EXEMPLO);
  const importar = useImportarArquivo();
  const exemplo = useAbrirExemplo();

  return {
    nomeArquivo,
    enviando: importar.isPending || exemplo.isPending,
    erro: importar.error ?? exemplo.error,
    enviar: (escolhido) => {
      exemplo.reset();
      setNomeArquivo(escolhido.name);
      importar.mutate(escolhido);
    },
    abrirExemplo: (arquivo) => {
      importar.reset();
      setNomeArquivo(arquivo);
      exemplo.mutate(arquivo);
    },
  };
}
