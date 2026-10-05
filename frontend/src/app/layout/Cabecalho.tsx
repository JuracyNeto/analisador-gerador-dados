import { useNavigate } from 'react-router';
import { CAMINHOS } from '../../shared/navegacao/caminhos';
import { useSessao } from '../../shared/sessao/useSessao';
import Botao from '../../shared/ui/Botao';
import Icone from '../../shared/ui/Icone';
import { TEXTOS_APP } from '../textos';
import AlternanciaTema from './AlternanciaTema';
import estilos from './Cabecalho.module.css';

interface PropsCabecalho {
  nomeArquivo?: string | undefined;
  nLinhas?: number | undefined;
  nColunas?: number | undefined;
}

export default function Cabecalho({ nomeArquivo, nLinhas, nColunas }: Readonly<PropsCabecalho>) {
  const navegar = useNavigate();
  const { encerrar } = useSessao();
  return (
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
          onClick={() => {
            // Encerra a sessão para Importar mostrar a área de envio (D73).
            encerrar();
            void navegar(CAMINHOS.importar);
          }}
        >
          {TEXTOS_APP.trocarArquivo}
        </Botao>
      )}
      <AlternanciaTema />
    </header>
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
