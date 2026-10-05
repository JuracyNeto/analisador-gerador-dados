import EtapaEmBreve from '../../shared/ui/EtapaEmBreve';
import { TEXTOS_RELATORIO } from './textos';

export default function PaginaRelatorio() {
  return <EtapaEmBreve etapa={8} titulo={TEXTOS_RELATORIO.titulo} ajuda={TEXTOS_RELATORIO.ajuda} />;
}
