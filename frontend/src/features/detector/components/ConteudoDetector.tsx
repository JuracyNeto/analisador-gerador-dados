import type { UseQueryResult } from '@tanstack/react-query';
import AcoesEtapa from '../../../shared/navegacao/AcoesEtapa';
import { CAMINHOS } from '../../../shared/navegacao/caminhos';
import EstadoCarregando from '../../../shared/ui/EstadoCarregando';
import EstadoErro from '../../../shared/ui/EstadoErro';
import type { FiltrosNaUrl } from '../hooks/useFiltrosDetector';
import { TEXTOS_DETECTOR as T } from '../textos';
import type { ResultadoDetector } from '../tipos';
import BarraFiltros from './BarraFiltros';
import DetectorVazio from './DetectorVazio';
import ListaAlertas from './ListaAlertas';
import RegrasNaoVerificadas from './RegrasNaoVerificadas';
import ResumoDetector from './ResumoDetector';

const ACOES_DETECTOR = (
  <AcoesEtapa
    voltar={{ para: CAMINHOS.gerador, rotulo: T.navegacao.voltar }}
    continuar={{ para: CAMINHOS.relatorio, rotulo: T.navegacao.continuar }}
  />
);

function ComAlertas({
  resultado,
  filtros,
}: Readonly<{ resultado: ResultadoDetector; filtros: FiltrosNaUrl }>) {
  return (
    <>
      <ResumoDetector resumo={resultado.resumo} />
      <BarraFiltros
        porSeveridade={resultado.resumo.por_severidade}
        filtros={filtros}
        aoAlternar={filtros.alternarSeveridade}
        aoAgrupar={filtros.mudarAgrupamento}
      />
      <ListaAlertas avisos={resultado.avisos} filtros={filtros} />
      <RegrasNaoVerificadas itens={resultado.nao_aplicadas} abertoInicial={false} />
      {ACOES_DETECTOR}
    </>
  );
}

interface PropsConteudoDetector {
  consulta: UseQueryResult<ResultadoDetector>;
  filtros: FiltrosNaUrl;
  nomeArquivo: string;
}

/** Estados da tela 7: carregando, erro, nenhum alerta (7c) ou a lista (7a). */
export default function ConteudoDetector({
  consulta,
  filtros,
  nomeArquivo,
}: Readonly<PropsConteudoDetector>) {
  if (consulta.isPending) {
    return <EstadoCarregando forma={['cards', 'tabela']} mensagem={T.carregando(nomeArquivo)} />;
  }
  if (consulta.isError) {
    return (
      <EstadoErro
        erro={consulta.error}
        aoTentarDeNovo={() => {
          void consulta.refetch();
        }}
      />
    );
  }
  const resultado = consulta.data;
  if (resultado.avisos.length > 0) return <ComAlertas resultado={resultado} filtros={filtros} />;
  // Sem alertas, o "Continuar" fica no estado vazio (como na Limpeza) e as regras abrem (7c).
  return (
    <>
      <DetectorVazio texto={resultado.resumo.vazio} />
      <RegrasNaoVerificadas itens={resultado.nao_aplicadas} abertoInicial />
    </>
  );
}
