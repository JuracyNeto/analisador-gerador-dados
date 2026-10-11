import { useId } from 'react';
import Grafico from '../../../shared/graficos/Grafico';
import Botao from '../../../shared/ui/Botao';
import Card from '../../../shared/ui/Card';
import EstadoCarregando from '../../../shared/ui/EstadoCarregando';
import EstadoVazio from '../../../shared/ui/EstadoVazio';
import Icone from '../../../shared/ui/Icone';
import { useAcoesGeracao } from '../hooks/useAcoesGeracao';
import { TEXTOS_GERADOR } from '../textos';
import type { Gerado } from '../tipos';
import estilos from './Resultado.module.css';
import TabelaComparacao from './TabelaComparacao';

const T = TEXTOS_GERADOR;

interface PropsGerado {
  gerado: Gerado;
  aoExpirar: () => void;
}

function AcoesGeracao({ gerado, aoExpirar }: Readonly<PropsGerado>) {
  const acoes = useAcoesGeracao(gerado, aoExpirar);
  return (
    <div className={estilos.acoes}>
      <Botao
        variante="secundario"
        icone="download"
        carregando={acoes.baixando}
        onClick={acoes.baixar}
      >
        {T.acoes.baixar}
      </Botao>
      {acoes.podeAnexar ? (
        <Botao
          variante="secundario"
          icone="playlist_add"
          carregando={acoes.anexando}
          onClick={acoes.anexar}
        >
          {T.acoes.anexar}
        </Botao>
      ) : null}
      <Botao icone="table_view" carregando={acoes.usando} onClick={acoes.usarComoNovo}>
        {T.acoes.usar}
      </Botao>
    </div>
  );
}

function GraficoEExplicacao({ gerado }: Readonly<{ gerado: Gerado }>) {
  const [figura] = gerado.figuras;
  const idTitulo = useId();
  return (
    <Card>
      <div className={estilos.graficoExplicacao}>
        {figura ? (
          <Grafico titulo={figura.titulo} resumo={figura.resumo} figura={figura.dados} />
        ) : null}
        <section className={estilos.explicacao} aria-labelledby={idTitulo}>
          <h3 id={idTitulo} className={estilos.tituloExplicacao}>
            <Icone nome="menu_book" tamanho={20} />
            {T.resultado.comoGeramos}
          </h3>
          <p>{gerado.explicacao}</p>
        </section>
      </div>
    </Card>
  );
}

interface Props {
  gerado: Gerado | undefined;
  gerando: boolean;
  aoExpirar: () => void;
}

/** Coluna direita da tela 6: vazio, gerando ou o resultado com as ações. */
export default function ResultadoGeracao({ gerado, gerando, aoExpirar }: Readonly<Props>) {
  if (gerando) {
    return <EstadoCarregando forma={['tabela', 'grafico']} mensagem={T.resultado.gerandoDados} />;
  }
  if (gerado === undefined) {
    return (
      <EstadoVazio
        icone="auto_awesome"
        titulo={T.resultado.vazio.titulo}
        descricao={T.resultado.vazio.descricao}
      />
    );
  }
  return (
    <div className={estilos.resultado}>
      <TabelaComparacao gerado={gerado} />
      <GraficoEExplicacao gerado={gerado} />
      <AcoesGeracao gerado={gerado} aoExpirar={aoExpirar} />
    </div>
  );
}
