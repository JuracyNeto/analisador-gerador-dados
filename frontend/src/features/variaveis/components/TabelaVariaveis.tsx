import type { TipoColuna } from '../../../shared/api/dataset';
import { formatarInteiro } from '../../../shared/lib/formatar';
import ChipTipo from '../../../shared/ui/ChipTipo';
import Select from '../../../shared/ui/Select';
import Tabela, { type ColunaTabela } from '../../../shared/ui/Tabela';
import { ORDEM_TIPOS, TIPOS_VARIAVEL, type TipoVariavel } from '../../../shared/ui/tiposVariavel';
import { juntarExemplos } from '../regras';
import { TEXTOS_VARIAVEIS as T } from '../textos';
import estilos from './TabelaVariaveis.module.css';

const OPCOES_TIPO = ORDEM_TIPOS.map((tipo) => ({
  valor: tipo,
  rotulo: TIPOS_VARIAVEL[tipo].rotuloCompleto,
}));

interface PropsTabelaVariaveis {
  colunas: readonly TipoColuna[];
  aoAlterarTipo: (coluna: string, tipo: TipoVariavel) => void;
}

function ValidosFaltantes({ coluna }: Readonly<{ coluna: TipoColuna }>) {
  return (
    <>
      {formatarInteiro(coluna.n_validos)}
      <span className={estilos.barra}> / </span>
      <span className={estilos.faltantes} data-zero={coluna.n_faltantes === 0}>
        {formatarInteiro(coluna.n_faltantes)}
      </span>
    </>
  );
}

/** Colunas da tela 2a: coluna · tipo · motivo · válidos/faltantes · exemplos · corrigir. */
function definirColunas(
  aoAlterarTipo: PropsTabelaVariaveis['aoAlterarTipo'],
): readonly ColunaTabela<TipoColuna>[] {
  return [
    { id: 'coluna', titulo: T.tabela.coluna, mono: true, celula: (c) => c.coluna },
    {
      id: 'tipo',
      titulo: T.tabela.tipo,
      celula: (c) => <ChipTipo tipo={c.tipo} curto corrigido={c.origem === 'manual'} />,
    },
    { id: 'motivo', titulo: T.tabela.motivo, celula: (c) => c.motivo },
    {
      id: 'validos',
      titulo: T.tabela.validos,
      alinhamento: 'direita',
      mono: true,
      celula: (c) => <ValidosFaltantes coluna={c} />,
    },
    {
      id: 'exemplos',
      titulo: T.tabela.exemplos,
      mono: true,
      celula: (c) => <span className={estilos.exemplos}>{juntarExemplos(c.exemplos)}</span>,
    },
    {
      id: 'corrigir',
      titulo: T.tabela.corrigir,
      celula: (c) => (
        <Select
          rotulo={T.tabela.rotuloSelect(c.coluna)}
          rotuloOculto
          altura={36}
          valor={c.tipo}
          opcoes={OPCOES_TIPO}
          aoMudar={(tipo) => {
            aoAlterarTipo(c.coluna, tipo);
          }}
        />
      ),
    },
  ];
}

export default function TabelaVariaveis({
  colunas,
  aoAlterarTipo,
}: Readonly<PropsTabelaVariaveis>) {
  return (
    <div className={estilos.envoltorio}>
      <Tabela
        legenda={T.tabela.legenda}
        colunas={definirColunas(aoAlterarTipo)}
        linhas={colunas}
        chave={(c) => c.coluna}
      />
    </div>
  );
}
