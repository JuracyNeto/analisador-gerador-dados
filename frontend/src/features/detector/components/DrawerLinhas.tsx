import { baixarArquivo } from '../../../shared/lib/baixarArquivo';
import BadgeSeveridade from '../../../shared/ui/BadgeSeveridade';
import Botao from '../../../shared/ui/Botao';
import Drawer from '../../../shared/ui/Drawer';
import EstadoCarregando from '../../../shared/ui/EstadoCarregando';
import EstadoErro from '../../../shared/ui/EstadoErro';
import { exportarLinhas, nomeDoCsv } from '../exportarLinhas';
import { type EstadoLinhas, useLinhasDoAviso } from '../hooks/useLinhasDoAviso';
import { TEXTOS_DETECTOR } from '../textos';
import { descreverLinhas, descreverTrechos } from '../trechos';
import type { Aviso } from '../tipos';
import estilos from './DrawerLinhas.module.css';
import TabelaLinhas from './TabelaLinhas';

const T = TEXTOS_DETECTOR;
const TIPO_CSV = 'text/csv;charset=utf-8';

function TituloDrawer({ aviso }: Readonly<{ aviso: Aviso }>) {
  const linhas = descreverLinhas(aviso.exemplo?.linhas ?? []);
  if (aviso.colunas.length === 0) return <>{linhas}</>;
  return (
    <>
      {linhas}
      {T.separadorTitulo}
      <span className={estilos.colunas}>{aviso.colunas.join(T.separadorPar)}</span>
    </>
  );
}

interface PropsCorpo {
  aviso: Aviso;
  estado: EstadoLinhas;
  destacadas: ReadonlySet<number>;
}

function CorpoDrawer({ aviso, estado, destacadas }: Readonly<PropsCorpo>) {
  if (estado.status === 'carregando') {
    return <EstadoCarregando forma="tabela" mensagem={T.drawer.carregando} />;
  }
  if (estado.status === 'erro') {
    return (
      <div className={estilos.erro}>
        <EstadoErro erro={estado.erro} aoTentarDeNovo={estado.tentarDeNovo} />
      </div>
    );
  }
  return (
    <TabelaLinhas
      legenda={T.drawer.legenda(aviso.titulo)}
      trechos={estado.trechos}
      destacadas={destacadas}
      afetadas={aviso.colunas}
      severidade={aviso.severidade}
    />
  );
}

function exportar(aviso: Aviso, estado: EstadoLinhas, destacadas: ReadonlySet<number>): void {
  if (estado.status !== 'pronto') return;
  const linhas = estado.trechos.flatMap((trecho) => trecho.linhas);
  const colunas = Object.keys(linhas[0]?.valores ?? {});
  const csv = exportarLinhas(linhas, colunas, destacadas);
  baixarArquivo(new Blob([csv], { type: TIPO_CSV }), nomeDoCsv(aviso));
}

interface PropsDrawerLinhas {
  datasetId: string;
  /** O aviso cujo exemplo é mostrado; `null` com o drawer fechado. */
  aviso: Aviso | null;
  aoFechar: () => void;
}

/** "Ver na tabela" (tela 7b): as linhas do exemplo com ±3 de contexto e "Exportar estas linhas". */
export default function DrawerLinhas({ datasetId, aviso, aoFechar }: Readonly<PropsDrawerLinhas>) {
  const { trechos, destacadas, estado } = useLinhasDoAviso(datasetId, aviso);
  if (aviso === null) return null;
  const total = aviso.exemplo?.total_linhas ?? destacadas.size;
  return (
    <Drawer
      aberto
      aoFechar={aoFechar}
      topo={<BadgeSeveridade severidade={aviso.severidade} tamanho="sm" />}
      titulo={<TituloDrawer aviso={aviso} />}
      subtitulo={T.drawer.destacadas(destacadas.size, total)}
      rotuloCorpo={T.drawer.rotuloCorpo}
      rodape={
        <>
          <span className={estilos.contagem}>{T.drawer.rodape(descreverTrechos(trechos))}</span>
          <Botao
            variante="secundario"
            tamanho="sm"
            icone="download"
            disabled={estado.status !== 'pronto'}
            onClick={() => {
              exportar(aviso, estado, destacadas);
            }}
          >
            {T.drawer.exportar}
          </Botao>
        </>
      }
    >
      <CorpoDrawer aviso={aviso} estado={estado} destacadas={destacadas} />
    </Drawer>
  );
}
