/** Mensagens do cliente HTTP quando a API não responde no formato {codigo, mensagem, sugestao}. */
export const TEXTOS_API = {
  semConexao: {
    mensagem: 'Não conseguimos falar com o servidor.',
    sugestao: 'Confira se o servidor está ligado e tente de novo.',
  },
  desconhecido: {
    mensagem: 'O servidor respondeu de um jeito inesperado.',
    sugestao: 'Tente de novo em instantes.',
  },
  /** Falha no navegador (não veio da API); a mesma sugestão do erro 500 da API. */
  generico: {
    mensagem: 'Não conseguimos concluir esta ação.',
    sugestao: 'Tente de novo. Se continuar, reinicie o servidor e recarregue a página.',
  },
} as const;
