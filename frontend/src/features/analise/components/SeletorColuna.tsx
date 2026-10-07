import ChipTipo from '../../../shared/ui/ChipTipo';
import Select from '../../../shared/ui/Select';
import { TEXTOS_ANALISE } from '../textos';
import type { TipoColuna } from '../tipos';
import estilos from './SeletorColuna.module.css';

interface Props {
  colunas: readonly TipoColuna[];
  escolhida: TipoColuna;
  aoMudar: (coluna: string) => void;
}

export default function SeletorColuna({ colunas, escolhida, aoMudar }: Readonly<Props>) {
  const opcoes = colunas.map((coluna) => ({ valor: coluna.coluna, rotulo: coluna.coluna }));

  return (
    <div className={estilos.seletor}>
      <Select
        rotulo={TEXTOS_ANALISE.rotuloColuna}
        valor={escolhida.coluna}
        opcoes={opcoes}
        aoMudar={aoMudar}
        altura={44}
      />
      <span className={estilos.chip}>
        <ChipTipo tipo={escolhida.tipo} curto />
      </span>
    </div>
  );
}
