import { ErroApi } from './cliente';

export interface TextoErro {
  mensagem: string;
  sugestao: string;
}

const CODIGO_DATASET_NAO_ENCONTRADO = 'DATASET_NAO_ENCONTRADO';

/** Erro que não veio da API (falha inesperada no navegador). Spec 16: o que houve + o que fazer. */
const ERRO_GENERICO: TextoErro = {
  mensagem: 'Algo deu errado do nosso lado.',
  sugestao: 'Tente de novo. Se continuar, recarregue a página.',
};

/** A API perdeu o dataset (expirou ou o servidor reiniciou): a sessão do frontend acabou (D61). */
export function ehDatasetNaoEncontrado(erro: unknown): boolean {
  return erro instanceof ErroApi && erro.codigo === CODIGO_DATASET_NAO_ENCONTRADO;
}

/** Texto para EstadoErro e toasts: a mensagem da API ou um texto genérico amigável. */
export function textoDoErro(erro: unknown): TextoErro {
  if (!(erro instanceof ErroApi)) return ERRO_GENERICO;
  return {
    mensagem: erro.message,
    sugestao: erro.sugestao === '' ? ERRO_GENERICO.sugestao : erro.sugestao,
  };
}

/** Erros que não mudam ao repetir a requisição (entrada inválida) não ganham "Tentar de novo". */
export function podeRepetir(erro: unknown, definitivos: ReadonlySet<string>): boolean {
  return !(erro instanceof ErroApi && definitivos.has(erro.codigo));
}
