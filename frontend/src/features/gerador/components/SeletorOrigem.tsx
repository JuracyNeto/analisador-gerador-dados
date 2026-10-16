import Segmented from '../../../shared/ui/Segmented';
import { TEXTOS_GERADOR } from '../textos';
import type { Origem } from '../tipos';

const ORIGENS = ['coluna', 'manual'] as const;

interface Props {
  rotulos: Readonly<Record<Origem, string>>;
  valor: Origem;
  aoMudar: (origem: Origem) => void;
  /** Sem dataset na sessão, só há parâmetros manuais e o seletor some. */
  temDataset: boolean;
}

export default function SeletorOrigem({ rotulos, valor, aoMudar, temDataset }: Readonly<Props>) {
  if (!temDataset) return null;
  return (
    <Segmented<Origem>
      rotulo={TEXTOS_GERADOR.origem.rotulo}
      opcoes={ORIGENS.map((origem) => ({ valor: origem, rotulo: rotulos[origem] }))}
      valor={valor}
      aoMudar={aoMudar}
    />
  );
}
