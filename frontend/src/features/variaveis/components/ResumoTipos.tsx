import type { TipoColuna } from '../../../shared/api/dataset';
import { formatarInteiro } from '../../../shared/lib/formatar';
import { escolherForma } from '../../../shared/lib/pluralizar';
import { corDoTipo } from '../../../shared/ui/tiposVariavel';
import { contarPorTipo } from '../regras';
import { NOMES_RESUMO, TEXTOS_VARIAVEIS as T } from '../textos';
import estilos from './ResumoTipos.module.css';

export default function ResumoTipos({ colunas }: Readonly<{ colunas: readonly TipoColuna[] }>) {
  return (
    <ul className={estilos.resumo} aria-label={T.resumo}>
      {contarPorTipo(colunas).map(({ tipo, quantidade }) => (
        <li key={tipo} className={estilos.item}>
          <span className={estilos.numero} style={{ color: corDoTipo(tipo) }}>
            {formatarInteiro(quantidade)}
          </span>{' '}
          {escolherForma(quantidade, NOMES_RESUMO[tipo][0], NOMES_RESUMO[tipo][1])}
        </li>
      ))}
    </ul>
  );
}
