import { useState } from 'react';
import { useNavigate } from 'react-router';
import { CAMINHOS } from '../../shared/navegacao/caminhos';
import { useSessao } from '../../shared/sessao/useSessao';
import Banner from '../../shared/ui/Banner';
import Botao from '../../shared/ui/Botao';
import Icone from '../../shared/ui/Icone';
import { TEXTOS_APP } from '../textos';
import AlternanciaTema from './AlternanciaTema';
import estilos from './Cabecalho.module.css';

const C = TEXTOS_APP.trocaComAjustes;

interface PropsCabecalho {
  nomeArquivo?: string | undefined;
  nLinhas?: number | undefined;
  nColunas?: number | undefined;
  /** Tipos corrigidos, limpeza ou dados gerados: trocar de arquivo pede confirmação. */
  temAjustes?: boolean;
}

/** Encerra a sessão para Importar mostrar a área de envio (D73); com ajustes, confirma antes. */
function useTrocarArquivo() {
  const navegar = useNavigate();
  const { encerrar } = useSessao();
  const [confirmando, setConfirmando] = useState(false);
  const trocar = () => {
    setConfirmando(false);
    encerrar();
    void navegar(CAMINHOS.importar);
  };
  return {
    confirmando,
    pedirConfirmacao: () => {
      setConfirmando(true);
    },
    trocar,
    cancelar: () => {
      setConfirmando(false);
    },
  };
}

function ConfirmarTroca({
  aoTrocar,
  aoCancelar,
}: Readonly<{ aoTrocar: () => void; aoCancelar: () => void }>) {
  const acoes = (
    <>
      <Botao tamanho="sm" onClick={aoTrocar}>
        {C.confirmar}
      </Botao>
      <Botao variante="secundario" tamanho="sm" onClick={aoCancelar}>
        {C.cancelar}
      </Botao>
    </>
  );
  return (
    <div role="alert" className={estilos.confirmacao}>
      <Banner variante="atencao" titulo={C.aviso} acoes={acoes}>
        {C.detalhe}
      </Banner>
    </div>
  );
}

export default function Cabecalho({
  nomeArquivo,
  nLinhas,
  nColunas,
  temAjustes = false,
}: Readonly<PropsCabecalho>) {
  const troca = useTrocarArquivo();
  return (
    <>
      <header className={estilos.cabecalho}>
        {nomeArquivo === undefined ? (
          <span className={estilos.vazio}>{TEXTOS_APP.nenhumArquivo}</span>
        ) : (
          <ArquivoAtual nomeArquivo={nomeArquivo} nLinhas={nLinhas} nColunas={nColunas} />
        )}
        {nomeArquivo === undefined ? null : (
          <Botao
            variante="secundario"
            tamanho="sm"
            icone="swap_horiz"
            onClick={temAjustes ? troca.pedirConfirmacao : troca.trocar}
          >
            {TEXTOS_APP.trocarArquivo}
          </Botao>
        )}
        <AlternanciaTema />
      </header>
      {troca.confirmando ? (
        <ConfirmarTroca aoTrocar={troca.trocar} aoCancelar={troca.cancelar} />
      ) : null}
    </>
  );
}

interface PropsArquivoAtual {
  nomeArquivo: string;
  nLinhas: number | undefined;
  nColunas: number | undefined;
}

function ArquivoAtual({ nomeArquivo, nLinhas, nColunas }: Readonly<PropsArquivoAtual>) {
  return (
    <div className={estilos.arquivo}>
      <Icone nome="description" tamanho={22} className={estilos.icone} />
      <div className={estilos.textos}>
        <span className={estilos.nome}>{nomeArquivo}</span>
        {nLinhas === undefined || nColunas === undefined ? null : (
          <span className={estilos.dimensoes}>{TEXTOS_APP.dimensoes(nLinhas, nColunas)}</span>
        )}
      </div>
    </div>
  );
}
