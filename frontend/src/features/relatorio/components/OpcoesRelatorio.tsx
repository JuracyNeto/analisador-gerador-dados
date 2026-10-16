import type { TipoColuna } from '../../../shared/api/dataset';
import CaixaSelecao from '../../../shared/ui/CaixaSelecao';
import ChipTipo from '../../../shared/ui/ChipTipo';
import EstadoCarregando from '../../../shared/ui/EstadoCarregando';
import { SECOES_RELATORIO, type SecaoRelatorio } from '../api';
import type { SelecaoNaTela } from '../hooks/useSelecaoRelatorio';
import { secaoDisponivel, usaColunas } from '../selecao';
import { TEXTOS_RELATORIO } from '../textos';
import GrupoCaixas, { type ItemCaixa } from './GrupoCaixas';
import estilos from './OpcoesRelatorio.module.css';

const T = TEXTOS_RELATORIO;
const NOTA_SEM_ANALISES = <p className={estilos.nota}>{T.colunasSemAnalises}</p>;
const NOTA_SEM_GERACAO = <p className={estilos.nota}>{T.semGeracao}</p>;

function itensSecoes(temGeracao: boolean): ItemCaixa<SecaoRelatorio>[] {
  return SECOES_RELATORIO.map((id) =>
    secaoDisponivel(id, temGeracao)
      ? { id, rotulo: T.rotulosSecoes[id] }
      : { id, rotulo: T.rotulosSecoes[id], desabilitada: true, nota: NOTA_SEM_GERACAO },
  );
}

const ITENS_COM_GERACAO = itensSecoes(true);
const ITENS_SEM_GERACAO = itensSecoes(false);

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
        itens={selecao.gerado === null ? ITENS_SEM_GERACAO : ITENS_COM_GERACAO}
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
