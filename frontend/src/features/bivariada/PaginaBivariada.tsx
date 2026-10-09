import BotaoEtapa from '../../shared/navegacao/BotaoEtapa';
import { CAMINHOS } from '../../shared/navegacao/caminhos';
import SemDataset from '../../shared/sessao/SemDataset';
import { useSessao } from '../../shared/sessao/useSessao';
import BarraAcoes from '../../shared/ui/BarraAcoes';
import PaginaEtapa from '../../shared/ui/PaginaEtapa';
import { TEXTOS_BIVARIADA } from './textos';

const ETAPA_BIVARIADA = 5;
const T = TEXTOS_BIVARIADA;

const ACOES_BIVARIADA = (
  <BarraAcoes>
    <BotaoEtapa para={CAMINHOS.analise} sentido="voltar">
      {T.navegacao.voltar}
    </BotaoEtapa>
    <BotaoEtapa para={CAMINHOS.relatorio} sentido="avancar">
      {T.navegacao.continuar}
    </BotaoEtapa>
  </BarraAcoes>
);

export default function PaginaBivariada() {
  const { dataset } = useSessao();
  return (
    <PaginaEtapa etapa={ETAPA_BIVARIADA} titulo={T.titulo} ajuda={T.ajuda}>
      {dataset === null ? <SemDataset descricao={T.semDataset} /> : ACOES_BIVARIADA}
    </PaginaEtapa>
  );
}
