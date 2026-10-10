import type { TipoColuna } from '../../../shared/api/dataset';
import CaixaSelecao from '../../../shared/ui/CaixaSelecao';
import ChipTipo from '../../../shared/ui/ChipTipo';
import EstadoCarregando from '../../../shared/ui/EstadoCarregando';
import { SECOES_RELATORIO } from '../api';
import type { SelecaoNaTela } from '../hooks/useSelecaoRelatorio';
import { usaColunas } from '../selecao';
import { TEXTOS_RELATORIO } from '../textos';
import GrupoCaixas from './GrupoCaixas';
import estilos from './OpcoesRelatorio.module.css';

const T = TEXTOS_RELATORIO;
const ITENS_SECOES = SECOES_RELATORIO.map((id) => ({ id, rotulo: T.rotulosSecoes[id] }));
const NOTA_SEM_ANALISES = <p className={estilos.nota}>{T.colunasSemAnalises}</p>;

function itemColuna(coluna: TipoColuna) {
  return {
    id: coluna.coluna,
    rotulo: (
      <span className={estilos.coluna}>
        <span className={estilos.nome}>{coluna.coluna}</span>
        <ChipTipo tipo={coluna.tipo} curto />
      </span>
    ),
  };
}

interface Props {
  colunas: readonly TipoColuna[] | undefined;
  selecao: SelecaoNaTela;
  offline: boolean;
  aoMudarOffline: (offline: boolean) => void;
}

export default function OpcoesRelatorio({
  colunas,
  selecao,
  offline,
  aoMudarOffline,
}: Readonly<Props>) {
  const semAnalises = !usaColunas(selecao.secoes);

  return (
    <div className={estilos.opcoes}>
      <GrupoCaixas
        legenda={T.secoes}
        itens={ITENS_SECOES}
        marcados={selecao.secoes}
        aoAlternar={selecao.alternarSecao}
      />
      {colunas === undefined ? (
        <EstadoCarregando forma="tabela" mensagem={T.carregandoColunas} />
      ) : (
        <GrupoCaixas
          legenda={T.colunas}
          itens={colunas.map(itemColuna)}
          marcados={selecao.colunas}
          aoAlternar={selecao.alternarColuna}
          desabilitado={semAnalises}
          nota={semAnalises ? NOTA_SEM_ANALISES : null}
        />
      )}
      <div className={estilos.offline}>
        <CaixaSelecao rotulo={T.offline} marcada={offline} aoMudar={aoMudarOffline} />
        <p className={estilos.nota}>{T.offlineAjuda}</p>
      </div>
    </div>
  );
}
