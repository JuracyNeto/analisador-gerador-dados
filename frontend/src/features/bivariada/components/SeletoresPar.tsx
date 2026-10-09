import Botao from '../../../shared/ui/Botao';
import Select from '../../../shared/ui/Select';
import { trocado } from '../parametros';
import { TEXTOS_BIVARIADA } from '../textos';
import type { Par, TipoColuna } from '../tipos';
import estilos from './SeletoresPar.module.css';

const S = TEXTOS_BIVARIADA.seletores;

interface Props {
  colunas: readonly TipoColuna[];
  par: Par;
  aoMudar: (par: Par) => void;
}

/** A coluna escolhida de um lado fica desabilitada do outro (X e Y sempre diferentes). */
function opcoes(colunas: readonly TipoColuna[], outra: string) {
  return colunas.map(({ coluna }) => ({
    valor: coluna,
    rotulo: coluna,
    desabilitada: coluna === outra,
  }));
}

/** Tela 5a: Selects "X (explica)" e "Y (é explicada)" com o botão "Trocar X e Y" no meio. */
export default function SeletoresPar({ colunas, par, aoMudar }: Readonly<Props>) {
  return (
    <div className={estilos.seletores}>
      <div className={estilos.campo}>
        <Select
          rotulo={S.x}
          valor={par.x}
          opcoes={opcoes(colunas, par.y)}
          aoMudar={(x) => {
            aoMudar({ ...par, x });
          }}
          altura={44}
        />
      </div>
      <Botao
        variante="secundario"
        tamanho="lg"
        icone="swap_horiz"
        aria-label={S.trocar}
        title={S.trocar}
        className={estilos.trocar}
        onClick={() => {
          aoMudar(trocado(par));
        }}
      />
      <div className={estilos.campo}>
        <Select
          rotulo={S.y}
          valor={par.y}
          opcoes={opcoes(colunas, par.x)}
          aoMudar={(y) => {
            aoMudar({ ...par, y });
          }}
          altura={44}
        />
      </div>
    </div>
  );
}
