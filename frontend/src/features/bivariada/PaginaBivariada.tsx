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
import { esperaAMatriz, parEscolhido } from './parametros';
import { TEXTOS_BIVARIADA } from './textos';

const ETAPA_BIVARIADA = 5;
const T = TEXTOS_BIVARIADA;

const ESPERANDO = { status: 'carregando-colunas' } as const;

const ACOES_BIVARIADA = (
  <AcoesEtapa
    voltar={{ para: CAMINHOS.analise, rotulo: T.navegacao.voltar }}
    continuar={{ para: CAMINHOS.gerador, rotulo: T.navegacao.continuar }}
  />
);

function BivariadaDoDataset({ datasetId }: Readonly<{ datasetId: string }>) {
  const colunas = useColunasNumericas(datasetId);
  const { pedido, escolher } = useParametrosBivariada();
  const matriz = useMatriz(datasetId);
  // Com o par na URL, bivariada e matriz saem juntas (§6); sem ele, o par vem da matriz.
  const esperando = esperaAMatriz(pedido, colunas.data ?? [], matriz.isPending);
  const par = esperando ? null : parEscolhido(pedido, colunas.data ?? [], matriz.data ?? null);
  const bivariada = useBivariada(datasetId, par);
  const seletores =
    colunas.data !== undefined && par !== null ? (
      <SeletoresPar colunas={colunas.data} par={par} aoMudar={escolher} />
    ) : null;

  return (
    <PaginaEtapa etapa={ETAPA_BIVARIADA} titulo={T.titulo} ajuda={T.ajuda} acoesTopo={seletores}>
      <CorpoBivariada
        estado={esperando ? ESPERANDO : estadoDaBivariada(colunas, bivariada, par)}
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
