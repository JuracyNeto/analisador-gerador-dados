import type { ResumoDataset } from '../../../shared/api/dataset';
import { contarLinhas } from '../../../shared/lib/pluralizar';
import Icone from '../../../shared/ui/Icone';
import { chaveDoLog, detalheDoLog } from '../descricoes';
import { TEXTOS_LIMPEZA as T } from '../textos';
import type { EntradaLog } from '../tipos';
import estilos from './PainelLog.module.css';

function ListaLog({ log }: Readonly<{ log: readonly EntradaLog[] }>) {
  return (
    <ol className={estilos.lista}>
      {log.map((entrada) => {
        const detalhe = detalheDoLog(entrada);
        return (
          <li key={chaveDoLog(entrada)} className={estilos.item}>
            <span className={estilos.marca}>
              <Icone nome="check" tamanho={18} />
            </span>
            <span>
              {entrada.frase}
              {detalhe === '' ? null : <span className={estilos.detalhe}>{detalhe}</span>}
            </span>
          </li>
        );
      })}
    </ol>
  );
}

/** "O que fizemos" (3a): log acumulado vindo do resumo do dataset. */
export default function PainelLog({ resumo }: Readonly<{ resumo: ResumoDataset }>) {
  const log = resumo.log_limpeza;
  const mudou = resumo.n_linhas !== resumo.n_linhas_original;
  return (
    <aside className={estilos.painel} aria-label={T.log.rotulo}>
      <div className={estilos.topo}>
        <Icone nome="history" tamanho={20} />
        <h2 className={estilos.titulo}>{T.log.titulo}</h2>
      </div>
      {log.length === 0 ? <p className={estilos.vazio}>{T.log.vazio}</p> : <ListaLog log={log} />}
      <p className={estilos.resultado}>
        {T.log.resultado} <strong>{contarLinhas(resumo.n_linhas)}</strong>
        {mudou ? T.log.eram(resumo.n_linhas_original) : '.'}
      </p>
    </aside>
  );
}
