import { ehErroDeEntrada } from '../../shared/api/classificarErro';
import type { LinhaDados } from '../../shared/api/dataset';
import { textoDoErro } from '../../shared/api/erros';
import { TEXTOS_IMPORTAR as T } from './textos';

export interface ColunaPrevia {
  nome: string;
  numerica: boolean;
}

/** Ordem das colunas = ordem das chaves da 1ª linha (a API preserva a ordem do arquivo). */
export function colunasDaPrevia(linhas: readonly LinhaDados[]): ColunaPrevia[] {
  const primeira = linhas[0];
  if (primeira === undefined) return [];
  return Object.keys(primeira.valores).map((nome) => ({
    nome,
    numerica: linhas.some((linha) => typeof linha.valores[nome] === 'number'),
  }));
}

export interface ErroImportacao {
  titulo: string;
  texto: string;
}

/** Banner 1c: erro do arquivo cita o nome; falha de rede/servidor usa a mensagem do cliente HTTP. */
export function descreverErroImportacao(erro: unknown, nomeArquivo: string): ErroImportacao {
  const { mensagem, sugestao } = textoDoErro(erro);
  if (ehErroDeEntrada(erro)) {
    return { titulo: T.erro.titulo(nomeArquivo), texto: `${mensagem} ${sugestao}`.trim() };
  }
  return { titulo: mensagem, texto: sugestao };
}
