import BarraAcoes from '../ui/BarraAcoes';
import BotaoEtapa from './BotaoEtapa';

interface Destino {
  para: string;
  rotulo: string;
}

interface PropsAcoesEtapa {
  voltar: Destino;
  continuar: Destino;
}

/** Barra de ações do fim da etapa: "Voltar para …" e "Continuar para …" (D89). */
export default function AcoesEtapa({ voltar, continuar }: Readonly<PropsAcoesEtapa>) {
  return (
    <BarraAcoes>
      <BotaoEtapa para={voltar.para} sentido="voltar">
        {voltar.rotulo}
      </BotaoEtapa>
      <BotaoEtapa para={continuar.para} sentido="avancar">
        {continuar.rotulo}
      </BotaoEtapa>
    </BarraAcoes>
  );
}
