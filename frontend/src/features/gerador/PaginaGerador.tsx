import AcoesEtapa from '../../shared/navegacao/AcoesEtapa';
import { CAMINHOS } from '../../shared/navegacao/caminhos';
import { useSessao } from '../../shared/sessao/useSessao';
import Abas from '../../shared/ui/Abas';
import Card from '../../shared/ui/Card';
import PaginaEtapa from '../../shared/ui/PaginaEtapa';
import FormularioBivariado from './components/FormularioBivariado';
import FormularioUnivariado from './components/FormularioUnivariado';
import ResultadoGeracao from './components/ResultadoGeracao';
import { useAbaGerador } from './hooks/useAbaGerador';
import { useFormularioBivariado } from './hooks/useFormularioBivariado';
import { useFormularioUnivariado } from './hooks/useFormularioUnivariado';
import { useGeracao } from './hooks/useGeracao';
import { useResultadoGeracao } from './hooks/useResultadoGeracao';
import estilos from './PaginaGerador.module.css';
import { TEXTOS_GERADOR } from './textos';

const ETAPA_GERADOR = 6;
const T = TEXTOS_GERADOR;
const ABAS = (['univariado', 'bivariado'] as const).map((id) => ({ id, rotulo: T.abas[id] }));

const ACOES_GERADOR = (
  <AcoesEtapa
    voltar={{ para: CAMINHOS.bivariada, rotulo: T.navegacao.voltar }}
    continuar={{ para: CAMINHOS.detector, rotulo: T.navegacao.continuar }}
  />
);

/** Etapa 6 (telas 6a e 6b). Funciona também sem dataset, só com parâmetros manuais (D115). */
export default function PaginaGerador() {
  const { dataset } = useSessao();
  const datasetId = dataset?.id ?? null;
  const { aba, mudar } = useAbaGerador();
  const univariado = useFormularioUnivariado(datasetId);
  const bivariado = useFormularioBivariado(datasetId);
  const geracao = useGeracao();
  const resultado = useResultadoGeracao(aba, geracao);
  const gerarUnivariado = () => {
    const pedido = univariado.confirmar();
    if (pedido !== null) geracao.gerarUnivariado(pedido);
  };
  const gerarBivariado = () => {
    const pedido = bivariado.confirmar();
    if (pedido !== null) geracao.gerarBivariado(pedido);
  };
  const formulario =
    aba === 'univariado' ? (
      <FormularioUnivariado
        formulario={univariado}
        gerando={resultado.gerando}
        aoGerar={gerarUnivariado}
      />
    ) : (
      <FormularioBivariado
        formulario={bivariado}
        gerando={resultado.gerando}
        aoGerar={gerarBivariado}
      />
    );

  return (
    <PaginaEtapa etapa={ETAPA_GERADOR} titulo={T.titulo} ajuda={T.ajuda}>
      <Abas rotulo={T.rotuloAbas} abas={ABAS} ativa={aba} aoMudar={mudar}>
        <div className={estilos.grade}>
          <Card>{formulario}</Card>
          <ResultadoGeracao
            gerado={resultado.gerado}
            gerando={resultado.gerando}
            aoExpirar={resultado.expirar}
            aoGerarDeNovo={resultado.gerarDeNovo}
          />
        </div>
      </Abas>
      {ACOES_GERADOR}
    </PaginaEtapa>
  );
}
