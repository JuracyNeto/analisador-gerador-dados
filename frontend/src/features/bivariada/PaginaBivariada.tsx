import { useColunasNumericas } from '../../shared/api/colunas';
import AcoesEtapa from '../../shared/navegacao/AcoesEtapa';
import { CAMINHOS } from '../../shared/navegacao/caminhos';
import SemDataset from '../../shared/sessao/SemDataset';
import { useSessao } from '../../shared/sessao/useSessao';
import PaginaEtapa from '../../shared/ui/PaginaEtapa';
import { useBivariada, useMatriz } from './api';
import CorpoBivariada from './components/CorpoBivariada';
import SeletoresPar from './components/SeletoresPar';
import { estadoDaBivariada } from './estadoBivariada';
import { useParametrosBivariada } from './hooks/useParametrosBivariada';
import { parEscolhido } from './parametros';
import { TEXTOS_BIVARIADA } from './textos';

const ETAPA_BIVARIADA = 5;
const T = TEXTOS_BIVARIADA;

const ACOES_BIVARIADA = (
  <AcoesEtapa
    voltar={{ para: CAMINHOS.analise, rotulo: T.navegacao.voltar }}
    continuar={{ para: CAMINHOS.relatorio, rotulo: T.navegacao.continuar }}
  />
);

function BivariadaDoDataset({ datasetId }: Readonly<{ datasetId: string }>) {
  const colunas = useColunasNumericas(datasetId);
  const { pedido, escolher } = useParametrosBivariada();
  const par = parEscolhido(pedido, colunas.data ?? []);
  // Bivariada e matriz são independentes: as duas consultas saem juntas (§6).
  const bivariada = useBivariada(datasetId, par);
  const matriz = useMatriz(datasetId);
  const seletores =
    colunas.data !== undefined && par !== null ? (
      <SeletoresPar colunas={colunas.data} par={par} aoMudar={escolher} />
    ) : null;

  return (
    <PaginaEtapa etapa={ETAPA_BIVARIADA} titulo={T.titulo} ajuda={T.ajuda} acoesTopo={seletores}>
      <CorpoBivariada
        estado={estadoDaBivariada(colunas, bivariada, par)}
        datasetId={datasetId}
        matriz={matriz}
      />
      {ACOES_BIVARIADA}
    </PaginaEtapa>
  );
}

export default function PaginaBivariada() {
  const { dataset } = useSessao();
  return dataset === null ? (
    <PaginaEtapa etapa={ETAPA_BIVARIADA} titulo={T.titulo} ajuda={T.ajuda}>
      <SemDataset descricao={T.semDataset} />
    </PaginaEtapa>
  ) : (
    <BivariadaDoDataset datasetId={dataset.id} />
  );
}
