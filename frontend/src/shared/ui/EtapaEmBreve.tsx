import EstadoVazio from './EstadoVazio';
import PaginaEtapa from './PaginaEtapa';
import { TEXTOS_UI } from './textos';

interface PropsEtapaEmBreve {
  etapa: number;
  titulo: string;
  ajuda: string;
  descricao?: string;
}

/** Página de etapa sem conteúdo ainda (provisórias do M1 e etapas futuras, D60). */
export default function EtapaEmBreve({
  etapa,
  titulo,
  ajuda,
  descricao = TEXTOS_UI.telaEmConstrucao,
}: Readonly<PropsEtapaEmBreve>) {
  return (
    <PaginaEtapa etapa={etapa} titulo={titulo} ajuda={ajuda}>
      <EstadoVazio icone="construction" titulo={TEXTOS_UI.etapaEmBreve} descricao={descricao} />
    </PaginaEtapa>
  );
}
