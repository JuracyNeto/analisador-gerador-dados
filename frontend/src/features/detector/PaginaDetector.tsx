import AcoesEtapa from '../../shared/navegacao/AcoesEtapa';
import { CAMINHOS } from '../../shared/navegacao/caminhos';
import SemDataset from '../../shared/sessao/SemDataset';
import { useSessao } from '../../shared/sessao/useSessao';
import PaginaEtapa from '../../shared/ui/PaginaEtapa';
import { TEXTOS_DETECTOR } from './textos';

const ETAPA_DETECTOR = 7;
const T = TEXTOS_DETECTOR;

/** Etapa 7 (telas 7a–7d). */
export default function PaginaDetector() {
  const { dataset } = useSessao();
  return (
    <PaginaEtapa etapa={ETAPA_DETECTOR} titulo={T.titulo} ajuda={T.ajuda}>
      {dataset === null ? (
        <SemDataset descricao={T.semDataset} />
      ) : (
        <AcoesEtapa
          voltar={{ para: CAMINHOS.gerador, rotulo: T.navegacao.voltar }}
          continuar={{ para: CAMINHOS.relatorio, rotulo: T.navegacao.continuar }}
        />
      )}
    </PaginaEtapa>
  );
}
