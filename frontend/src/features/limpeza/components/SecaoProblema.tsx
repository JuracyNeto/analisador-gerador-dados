import { useId } from 'react';
import Select from '../../../shared/ui/Select';
import { TEXTOS_LIMPEZA as T } from '../textos';
import type { EscolhasLimpeza, SecaoDiagnostico, TipoAcao } from '../tipos';

type LinhaSecao = SecaoDiagnostico['linhas'][number];
import estilos from './SecaoProblema.module.css';

interface PropsSecaoProblema {
  secao: SecaoDiagnostico;
  escolhas: EscolhasLimpeza;
  aoEscolher: (chave: string, acao: TipoAcao) => void;
}

interface PropsLinhaProblema {
  linha: LinhaSecao;
  secao: string;
  escolha: TipoAcao;
  aoEscolher: (chave: string, acao: TipoAcao) => void;
}

/** Uma linha da seção: rótulo (coluna ou linha do arquivo) · descrição · ação escolhida. */
function LinhaProblema({ linha, secao, escolha, aoEscolher }: Readonly<PropsLinhaProblema>) {
  return (
    <tr>
      <th scope="row" className={estilos.rotulo}>
        {linha.rotulo}
      </th>
      <td className={estilos.descricao}>
        {linha.descricao}
        {linha.detalhe === null ? null : <span className={estilos.detalhe}>{linha.detalhe}</span>}
      </td>
      <td>
        <Select
          rotulo={T.secoes.rotuloAcao(linha.rotulo, secao)}
          rotuloOculto
          altura={36}
          valor={escolha}
          opcoes={linha.opcoes}
          aoMudar={(acao) => {
            aoEscolher(linha.chave, acao);
          }}
        />
      </td>
    </tr>
  );
}

export default function SecaoProblema({
  secao,
  escolhas,
  aoEscolher,
}: Readonly<PropsSecaoProblema>) {
  const idTitulo = useId();
  return (
    <section className={estilos.secao} aria-labelledby={idTitulo}>
      <header className={estilos.cabecalho}>
        <h2 id={idTitulo} className={estilos.titulo}>
          {secao.titulo}
        </h2>
        <span className={estilos.subtitulo}>{secao.subtitulo}</span>
      </header>
      <table className={estilos.tabela} aria-labelledby={idTitulo}>
        <colgroup>
          <col className={estilos.colunaRotulo} />
          <col />
          <col className={estilos.colunaAcao} />
        </colgroup>
        <thead>
          <tr>
            <th scope="col">{secao.cabecalhos[0]}</th>
            <th scope="col">{secao.cabecalhos[1]}</th>
            <th scope="col">{T.secoes.cabecalhoAcao}</th>
          </tr>
        </thead>
        <tbody>
          {secao.linhas.map((linha) => (
            <LinhaProblema
              key={linha.chave}
              linha={linha}
              secao={secao.titulo}
              escolha={escolhas[linha.chave] ?? 'manter'}
              aoEscolher={aoEscolher}
            />
          ))}
        </tbody>
      </table>
    </section>
  );
}
