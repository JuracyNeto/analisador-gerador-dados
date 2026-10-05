import EtapaEmBreve from '../../shared/ui/EtapaEmBreve';
import { TEXTOS_LIMPEZA } from './textos';

export default function PaginaLimpeza() {
  return <EtapaEmBreve etapa={3} titulo={TEXTOS_LIMPEZA.titulo} ajuda={TEXTOS_LIMPEZA.ajuda} />;
}
