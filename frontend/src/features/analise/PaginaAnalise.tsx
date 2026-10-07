import { useColunasAnalisaveis } from '../../shared/api/colunas';
import SemDataset from '../../shared/sessao/SemDataset';
import { useSessao } from '../../shared/sessao/useSessao';
import PaginaEtapa from '../../shared/ui/PaginaEtapa';
import { useAnalise } from './api';
import CorpoAnalise from './components/CorpoAnalise';
import SeletorColuna from './components/SeletorColuna';
import { estadoDaAnalise } from './estadoAnalise';
import { useParametrosAnalise } from './hooks/useParametrosAnalise';
import { colunaEscolhida } from './parametros';
import { TEXTOS_ANALISE } from './textos';

const ETAPA_ANALISE = 4;
const T = TEXTOS_ANALISE;

function AnaliseDoDataset({ datasetId }: Readonly<{ datasetId: string }>) {
  const colunas = useColunasAnalisaveis(datasetId);
  const parametros = useParametrosAnalise();
  const escolhida = colunaEscolhida(parametros.coluna, colunas.data ?? []);
  const nomeColuna = escolhida?.coluna ?? null;
  const analise = useAnalise(datasetId, nomeColuna, parametros.classes);
  const seletor =
    colunas.data !== undefined && escolhida !== null ? (
      <SeletorColuna
        colunas={colunas.data}
        escolhida={escolhida}
        aoMudar={parametros.escolherColuna}
      />
    ) : null;

  return (
    <PaginaEtapa etapa={ETAPA_ANALISE} titulo={T.titulo} ajuda={T.ajuda} acoesTopo={seletor}>
      <CorpoAnalise
        estado={estadoDaAnalise(colunas, analise, nomeColuna)}
        datasetId={datasetId}
        classes={parametros.classes}
        aoMudarClasses={parametros.mudarClasses}
      />
    </PaginaEtapa>
  );
}

export default function PaginaAnalise() {
  const { dataset } = useSessao();
  return dataset === null ? (
    <PaginaEtapa etapa={ETAPA_ANALISE} titulo={T.titulo} ajuda={T.ajuda}>
      <SemDataset descricao={T.semDataset} />
    </PaginaEtapa>
  ) : (
    <AnaliseDoDataset datasetId={dataset.id} />
  );
}
