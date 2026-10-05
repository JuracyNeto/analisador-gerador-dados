import EtapaEmBreve from '../../shared/ui/EtapaEmBreve';
import { TEXTOS_IMPORTAR } from './textos';

export default function PaginaImportar() {
  return <EtapaEmBreve etapa={1} titulo={TEXTOS_IMPORTAR.titulo} ajuda={TEXTOS_IMPORTAR.ajuda} />;
}
