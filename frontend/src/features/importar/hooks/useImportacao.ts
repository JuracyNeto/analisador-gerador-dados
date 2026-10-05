import { useState } from 'react';
import { useAbrirExemplo, useImportarArquivo } from '../api';
import { aplicarCorrecao, type CampoDeteccao, type OpcoesLeitura } from '../opcoesLeitura';
import { NOME_EXEMPLO } from '../textos';

type Origem = { tipo: 'arquivo'; arquivo: File; opcoes: OpcoesLeitura } | { tipo: 'exemplo' };

export interface Importacao {
  nomeArquivo: string;
  enviando: boolean;
  erro: Error | null;
  opcoes: OpcoesLeitura;
  enviar: (arquivo: File) => void;
  abrirExemplo: () => void;
  /** null quando não há arquivo na memória da página (exemplo ou página recarregada) — D70. */
  corrigir: ((campo: CampoDeteccao, valor: string) => void) | null;
  lerDeNovo: (() => void) | null;
}

/** Fluxo da tela 1: enviar, abrir exemplo, corrigir a leitura (relê o mesmo File) e "Ler de novo". */
export function useImportacao(): Importacao {
  const [origem, setOrigem] = useState<Origem | null>(null);
  const importar = useImportarArquivo();
  const exemplo = useAbrirExemplo();

  function lerArquivo(arquivo: File, opcoes: OpcoesLeitura): void {
    exemplo.reset();
    setOrigem({ tipo: 'arquivo', arquivo, opcoes });
    importar.mutate({ arquivo, opcoes });
  }

  function abrirExemplo(): void {
    importar.reset();
    setOrigem({ tipo: 'exemplo' });
    exemplo.mutate();
  }

  const atual = origem?.tipo === 'arquivo' ? origem : null;

  return {
    nomeArquivo: atual === null ? NOME_EXEMPLO : atual.arquivo.name,
    enviando: importar.isPending || exemplo.isPending,
    erro: importar.error ?? exemplo.error,
    opcoes: atual === null ? {} : atual.opcoes,
    enviar: (arquivo) => {
      lerArquivo(arquivo, {});
    },
    abrirExemplo,
    corrigir:
      atual === null
        ? null
        : (campo, valor) => {
            lerArquivo(atual.arquivo, aplicarCorrecao(atual.opcoes, campo, valor));
          },
    lerDeNovo:
      origem === null
        ? null
        : () => {
            if (atual === null) abrirExemplo();
            else lerArquivo(atual.arquivo, {});
          },
  };
}
