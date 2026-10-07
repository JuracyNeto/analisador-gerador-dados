import type { ReactNode } from 'react';
import { textoDoErro } from '../api/erros';
import Banner from './Banner';
import Botao from './Botao';
import { TEXTOS_UI } from './textos';

interface PropsEstadoErro {
  erro: unknown;
  aoTentarDeNovo?: (() => void) | undefined;
  acoes?: ReactNode;
}

export default function EstadoErro({ erro, aoTentarDeNovo, acoes }: Readonly<PropsEstadoErro>) {
  const { mensagem, sugestao } = textoDoErro(erro);
  const temAcoes = aoTentarDeNovo !== undefined || acoes !== undefined;
  const botaoTentar = aoTentarDeNovo ? (
    <Botao variante="secundario" tamanho="sm" icone="refresh" onClick={aoTentarDeNovo}>
      {TEXTOS_UI.tentarDeNovo}
    </Botao>
  ) : null;
  return (
    <Banner
      variante="erro"
      titulo={mensagem}
      acoes={
        temAcoes ? (
          <>
            {botaoTentar}
            {acoes}
          </>
        ) : undefined
      }
    >
      {sugestao}
    </Banner>
  );
}
