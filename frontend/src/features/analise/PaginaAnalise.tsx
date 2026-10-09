import { useColunasAnalisaveis } from '../../shared/api/colunas';
import BotaoEtapa from '../../shared/navegacao/BotaoEtapa';
import { CAMINHOS } from '../../shared/navegacao/caminhos';
import SemDataset from '../../shared/sessao/SemDataset';
import { useSessao } from '../../shared/sessao/useSessao';
import BarraAcoes from '../../shared/ui/BarraAcoes';
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

const ACOES_ANALISE = (
  <BarraAcoes>
    <BotaoEtapa para={CAMINHOS.limpeza} sentido="voltar">
      {T.navegacao.voltar}
    </BotaoEtapa>
    <BotaoEtapa para={CAMINHOS.relatorio} sentido="avancar">
      {T.navegacao.continuar}
    </BotaoEtapa>
  </BarraAcoes>
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
        estado={estadoDaAnalise(colunas, analise, nomeColuna)}
        datasetId={datasetId}
        classes={classes}
        aoMudarClasses={parametros.mudarClasses}
        tentativas={tentativas}
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
