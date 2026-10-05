import EtapaEmBreve from '../../shared/ui/EtapaEmBreve';
import { TEXTOS_ANALISE } from './textos';

export default function PaginaAnalise() {
  return <EtapaEmBreve etapa={4} titulo={TEXTOS_ANALISE.titulo} ajuda={TEXTOS_ANALISE.ajuda} />;
}
