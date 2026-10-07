import { useSessao } from '../../shared/sessao/useSessao';
import PaginaEtapa from '../../shared/ui/PaginaEtapa';
import AreaUpload from './components/AreaUpload';
import BannerErroImportacao from './components/BannerErroImportacao';
import BotaoLink from './components/BotaoLink';
import ResultadoImportacao from './components/ResultadoImportacao';
import { type Importacao, useImportacao } from './hooks/useImportacao';
import estilos from './PaginaImportar.module.css';
import { TEXTOS_IMPORTAR as T } from './textos';

function EnvioArquivo({ importacao }: Readonly<{ importacao: Importacao }>) {
  return (
    <>
      <AreaUpload
        enviando={importacao.enviando}
        nomeEnviando={importacao.nomeArquivo}
        comErro={importacao.erro !== null}
        aoEscolher={importacao.enviar}
      />
      <p className={estilos.exemplo}>
        {T.exemplo.pergunta}{' '}
        <BotaoLink onClick={importacao.abrirExemplo}>{T.exemplo.link}</BotaoLink>
      </p>
    </>
  );
}

/** Etapa 1: 1b (sem arquivo), 1c (erro, banner acima) e 1a (arquivo lido). */
export default function PaginaImportar() {
  const importacao = useImportacao();
  const sessao = useSessao();
  return (
    <PaginaEtapa etapa={1} titulo={T.titulo} ajuda={T.ajuda}>
      <div className={estilos.conteudo}>
        {importacao.erro === null ? null : (
          <BannerErroImportacao
            erro={importacao.erro}
            nomeArquivo={importacao.nomeArquivo}
            aoUsarExemplo={importacao.abrirExemplo}
          />
        )}
        {sessao.dataset === null ? (
          <EnvioArquivo importacao={importacao} />
        ) : (
          <ResultadoImportacao datasetId={sessao.dataset.id} />
        )}
      </div>
    </PaginaEtapa>
  );
}
