import type { ComponentType } from 'react';
import Abas from '../../../shared/ui/Abas';
import SecaoTituloOculto from '../../../shared/ui/SecaoTituloOculto';
import { abaEfetiva, abasDaAnalise } from '../abas';
import { TEXTOS_ANALISE } from '../textos';
import type { IdAba, PropsPainel } from '../tipos';
import AbaDispersao from './AbaDispersao';
import AbaForma from './AbaForma';
import AbaFrequencias from './AbaFrequencias';
import AbaGraficos from './AbaGraficos';
import AbaSeparatrizes from './AbaSeparatrizes';
import AbaTendencia from './AbaTendencia';

const PAINEIS: Record<IdAba, ComponentType<PropsPainel>> = {
  frequencias: AbaFrequencias,
  tendencia: AbaTendencia,
  separatrizes: AbaSeparatrizes,
  dispersao: AbaDispersao,
  forma: AbaForma,
  graficos: AbaGraficos,
};

interface Props extends PropsPainel {
  /** A aba da URL (`?aba=`); null ou desabilitada para a coluna = Frequências. */
  aba: IdAba | null;
  aoMudarAba: (aba: IdAba) => void;
}

export default function ConteudoAnalise({ aba, aoMudarAba, ...props }: Readonly<Props>) {
  const abas = abasDaAnalise(props.analise);
  const ativa = abaEfetiva(aba ?? 'frequencias', abas);
  const Painel = PAINEIS[ativa];

  return (
    <Abas rotulo={TEXTOS_ANALISE.rotuloAbas} abas={abas} ativa={ativa} aoMudar={aoMudarAba}>
      <SecaoTituloOculto titulo={TEXTOS_ANALISE.abas[ativa]}>
        <Painel key={props.analise.coluna} {...props} />
      </SecaoTituloOculto>
    </Abas>
  );
}
