import ExigeDataset from '../../shared/sessao/ExigeDataset';
import { useSessao } from '../../shared/sessao/useSessao';
import PaginaEtapa from '../../shared/ui/PaginaEtapa';
import { useColunas } from './api';
import ConteudoVariaveis from './components/ConteudoVariaveis';
import ResumoTipos from './components/ResumoTipos';
import { TEXTOS_VARIAVEIS as T } from './textos';

/** Resumo no topo à direita (2a); usa a mesma consulta do conteúdo (react-query deduplica). */
function ResumoDoDataset() {
  const sessao = useSessao();
  const { data: colunas } = useColunas(sessao.dataset?.id ?? null);
  return colunas ? <ResumoTipos colunas={colunas} /> : null;
}

export default function PaginaVariaveis() {
  return (
    <PaginaEtapa etapa={2} titulo={T.titulo} ajuda={T.ajuda} acoesTopo={<ResumoDoDataset />}>
      <ExigeDataset>{(id) => <ConteudoVariaveis datasetId={id} />}</ExigeDataset>
    </PaginaEtapa>
  );
}
