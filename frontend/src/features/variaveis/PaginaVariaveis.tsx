import EtapaEmBreve from '../../shared/ui/EtapaEmBreve';
import { TEXTOS_VARIAVEIS } from './textos';

export default function PaginaVariaveis() {
  return <EtapaEmBreve etapa={2} titulo={TEXTOS_VARIAVEIS.titulo} ajuda={TEXTOS_VARIAVEIS.ajuda} />;
}
