import ExigeDataset from '../../shared/sessao/ExigeDataset';
import PaginaEtapa from '../../shared/ui/PaginaEtapa';
import ConteudoLimpeza from './components/ConteudoLimpeza';
import { TEXTOS_LIMPEZA as T } from './textos';

export default function PaginaLimpeza() {
  return (
    <PaginaEtapa etapa={3} titulo={T.titulo} ajuda={T.ajuda}>
      <ExigeDataset>{(id) => <ConteudoLimpeza datasetId={id} />}</ExigeDataset>
    </PaginaEtapa>
  );
}
