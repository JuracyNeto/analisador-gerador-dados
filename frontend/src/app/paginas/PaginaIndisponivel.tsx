import { Navigate, useLocation } from 'react-router';
import EtapaEmBreve from '../../shared/ui/EtapaEmBreve';
import { ETAPAS, ehEtapaFutura, etapaDoCaminho } from '../etapas';
import { TEXTOS_APP } from '../textos';

export default function PaginaIndisponivel() {
  const etapa = etapaDoCaminho(useLocation().pathname);
  if (etapa === undefined || !ehEtapaFutura(etapa))
    return <Navigate to={ETAPAS[0].caminho} replace />;
  return (
    <EtapaEmBreve
      etapa={etapa.numero}
      titulo={TEXTOS_APP.titulosFuturos[etapa.numero]}
      ajuda={TEXTOS_APP.ajudaFutura}
      descricao={TEXTOS_APP.disponivelNaVersao(etapa.disponivelEm)}
    />
  );
}
