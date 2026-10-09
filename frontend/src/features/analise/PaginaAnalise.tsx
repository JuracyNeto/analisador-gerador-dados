import { useColunasAnalisaveis } from '../../shared/api/colunas';
import AcoesEtapa from '../../shared/navegacao/AcoesEtapa';
import { CAMINHOS } from '../../shared/navegacao/caminhos';
import SemDataset from '../../shared/sessao/SemDataset';
import { useSessao } from '../../shared/sessao/useSessao';
import PaginaEtapa from '../../shared/ui/PaginaEtapa';
import { useAnalise } from './api';
import CorpoAnalise from './components/CorpoAnalise';
import SeletorColuna from './components/SeletorColuna';
import { comPadraoDeTentativas, estadoDaAnalise } from './estadoAnalise';
import { useParametrosAnalise } from './hooks/useParametrosAnalise';
import { colunaEscolhida } from './parametros';
import { TEXTOS_ANALISE } from './textos';

const ETAPA_ANALISE = 4;
const T = TEXTOS_ANALISE;

const ACOES_ANALISE = (
  <AcoesEtapa
    voltar={{ para: CAMINHOS.limpeza, rotulo: T.navegacao.voltar }}
    continuar={{ para: CAMINHOS.bivariada, rotulo: T.navegacao.continuar }}
  />
);

function AnaliseDoDataset({ datasetId }: Readonly<{ datasetId: string }>) {
  const colunas = useColunasAnalisaveis(datasetId);
  const parametros = useParametrosAnalise();
  const escolhida = colunaEscolhida(parametros.coluna, colunas.data ?? []);
  const nomeColuna = escolhida?.coluna ?? null;
  const { classes, tentativas } = parametros;
  const analise = useAnalise(datasetId, nomeColuna, { classes, tentativas });
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
        estado={comPadraoDeTentativas(
          estadoDaAnalise(colunas, analise, nomeColuna),
          parametros.usarTentativasPadrao,
        )}
        datasetId={datasetId}
        classes={classes}
        aoMudarClasses={parametros.mudarClasses}
        aoMudarTentativas={parametros.mudarTentativas}
      />
      {ACOES_ANALISE}
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
