import CardMetrica from '../../../shared/ui/CardMetrica';
import { resumirDiagnostico } from '../resumo';
import type { Diagnostico } from '../tipos';
import estilos from './CardsResumoLimpeza.module.css';

export default function CardsResumoLimpeza({
  diagnostico,
}: Readonly<{ diagnostico: Diagnostico }>) {
  return (
    <div className={estilos.grade}>
      {resumirDiagnostico(diagnostico).map((card) => (
        <CardMetrica
          key={card.id}
          rotulo={card.rotulo}
          valor={card.valor}
          unidade={card.unidade}
          interpretacao={card.frase}
        />
      ))}
    </div>
  );
}
