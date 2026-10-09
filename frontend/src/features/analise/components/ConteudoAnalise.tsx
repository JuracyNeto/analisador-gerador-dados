import { useState, type ComponentType } from 'react';
import Abas from '../../../shared/ui/Abas';
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

export default function ConteudoAnalise(props: Readonly<PropsPainel>) {
  const [pedida, setPedida] = useState<IdAba>('frequencias');
  const abas = abasDaAnalise(props.analise);
  const ativa = abaEfetiva(pedida, abas);
  const Painel = PAINEIS[ativa];

  return (
    <Abas rotulo={TEXTOS_ANALISE.rotuloAbas} abas={abas} ativa={ativa} aoMudar={setPedida}>
      <Painel key={props.analise.coluna} {...props} />
    </Abas>
  );
}
