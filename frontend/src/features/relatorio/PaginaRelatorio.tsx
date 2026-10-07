import { useState } from 'react';
import { useColunasAnalisaveis } from '../../shared/api/colunas';
import BotaoEtapa from '../../shared/navegacao/BotaoEtapa';
import { CAMINHOS } from '../../shared/navegacao/caminhos';
import SemDataset from '../../shared/sessao/SemDataset';
import { useSessao } from '../../shared/sessao/useSessao';
import BarraAcoes from '../../shared/ui/BarraAcoes';
import Botao from '../../shared/ui/Botao';
import EstadoErro from '../../shared/ui/EstadoErro';
import PaginaEtapa from '../../shared/ui/PaginaEtapa';
import OpcoesRelatorio from './components/OpcoesRelatorio';
import PreviaRelatorio from './components/PreviaRelatorio';
import { useAcaoBaixar } from './hooks/useAcaoBaixar';
import { usePreviaRelatorio } from './hooks/usePreviaRelatorio';
import { useSelecaoRelatorio } from './hooks/useSelecaoRelatorio';
import estilos from './PaginaRelatorio.module.css';
import { selecaoEfetiva } from './selecao';
import { TEXTOS_RELATORIO } from './textos';

const ETAPA_RELATORIO = 8;
const T = TEXTOS_RELATORIO;

const ACOES_RODAPE = (
  <BarraAcoes>
    <BotaoEtapa para={CAMINHOS.analise} sentido="voltar">
      {T.voltar}
    </BotaoEtapa>
  </BarraAcoes>
);

interface PropsAcoes {
  baixando: boolean;
  podeBaixar: boolean;
  podeImprimir: boolean;
  aoBaixar: () => void;
  aoImprimir: () => void;
}

function AcoesRelatorio({
  baixando,
  podeBaixar,
  podeImprimir,
  aoBaixar,
  aoImprimir,
}: Readonly<PropsAcoes>) {
  return (
    <>
      <Botao
        variante="secundario"
        tamanho="lg"
        icone="code"
        carregando={baixando}
        textoCarregando={T.baixando}
        disabled={!podeBaixar}
        onClick={aoBaixar}
      >
        {T.baixar}
      </Botao>
      <Botao tamanho="lg" icone="print" disabled={!podeImprimir} onClick={aoImprimir}>
        {T.imprimir}
      </Botao>
    </>
  );
}

interface Props {
  datasetId: string;
  nomeArquivo: string;
}

function RelatorioDoDataset({ datasetId, nomeArquivo }: Readonly<Props>) {
  const colunas = useColunasAnalisaveis(datasetId);
  const selecao = useSelecaoRelatorio((colunas.data ?? []).map((coluna) => coluna.coluna));
  const [offline, setOffline] = useState(true);
  const efetiva = selecaoEfetiva(selecao);
  const previa = usePreviaRelatorio(datasetId, efetiva);
  const download = useAcaoBaixar(datasetId, nomeArquivo);

  const acoes = (
    <AcoesRelatorio
      baixando={download.baixando}
      podeBaixar={efetiva !== null}
      podeImprimir={previa.pronta}
      aoBaixar={() => {
        if (efetiva !== null) download.baixar(efetiva, offline);
      }}
      aoImprimir={previa.imprimir}
    />
  );

  return (
    <PaginaEtapa etapa={ETAPA_RELATORIO} titulo={T.titulo} ajuda={T.ajuda} acoesTopo={acoes}>
      {colunas.isError ? (
        <EstadoErro
          erro={colunas.error}
          aoTentarDeNovo={() => {
            void colunas.refetch();
          }}
        />
      ) : (
        <div className={estilos.grade}>
          <OpcoesRelatorio
            colunas={colunas.data}
            selecao={selecao}
            offline={offline}
            aoMudarOffline={setOffline}
          />
          <PreviaRelatorio
            src={previa.src}
            carregando={previa.carregando}
            aoCarregar={previa.aoCarregar}
          />
        </div>
      )}
      {ACOES_RODAPE}
    </PaginaEtapa>
  );
}

export default function PaginaRelatorio() {
  const { dataset } = useSessao();
  return dataset === null ? (
    <PaginaEtapa etapa={ETAPA_RELATORIO} titulo={T.titulo} ajuda={T.ajuda}>
      <SemDataset descricao={T.semDataset} />
    </PaginaEtapa>
  ) : (
    <RelatorioDoDataset datasetId={dataset.id} nomeArquivo={dataset.nomeArquivo} />
  );
}
