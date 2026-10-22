import { type ReactNode, useEffect, useRef } from 'react';
import { NavigationType, useNavigationType } from 'react-router';
import { useSessao } from '../sessao/useSessao';
import estilos from './PaginaEtapa.module.css';
import { TEXTOS_UI } from './textos';

interface PropsPaginaEtapa {
  etapa: number;
  titulo: string;
  ajuda: string;
  acoesTopo?: ReactNode;
  children: ReactNode;
}

export default function PaginaEtapa({
  etapa,
  titulo,
  ajuda,
  acoesTopo,
  children,
}: Readonly<PropsPaginaEtapa>) {
  const { dataset, marcarVisitada } = useSessao();
  const idDataset = dataset?.id;
  const refTitulo = useRef<HTMLHeadingElement>(null);
  const navegacaoNaMontagem = useRef(useNavigationType());

  useEffect(() => {
    // idDataset entra nas dependências de propósito: trocar de arquivo zera as visitadas e a etapa atual é remarcada.
    marcarVisitada(etapa);
  }, [etapa, idDataset, marcarVisitada]);

  useEffect(() => {
    document.title = `${titulo} · ${TEXTOS_UI.nomeApp}`;
  }, [titulo]);

  useEffect(() => {
    // Trocar de etapa por link ou botão leva o foco ao título: o leitor de tela anuncia a etapa
    // nova. Na primeira carga (POP), o foco fica onde está, com o link "Pular para o conteúdo" (D154).
    if (navegacaoNaMontagem.current !== NavigationType.Pop) refTitulo.current?.focus();
  }, []);

  return (
    <div className={estilos.pagina}>
      <header className={estilos.topo}>
        <div className={estilos.textos}>
          <p className={estilos.sobrelinha}>{TEXTOS_UI.etapaDeTotal(etapa)}</p>
          <h1 ref={refTitulo} tabIndex={-1} className={estilos.titulo}>
            {titulo}
          </h1>
          <p className={estilos.ajuda}>{ajuda}</p>
        </div>
        {acoesTopo === undefined ? null : <div className={estilos.acoesTopo}>{acoesTopo}</div>}
      </header>
      {children}
    </div>
  );
}
