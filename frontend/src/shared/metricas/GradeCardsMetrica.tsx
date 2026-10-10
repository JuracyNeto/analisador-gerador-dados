import CardMetrica from '../ui/CardMetrica';
import { propsDoCartao, type DefinicaoCartao, type Formula } from './cartoes';
import estilos from './GradeCardsMetrica.module.css';

interface Props {
  cartoes: readonly DefinicaoCartao[];
  formulas: readonly Formula[];
  colunas?: 3 | 4;
}

export default function GradeCardsMetrica({ cartoes, formulas, colunas = 3 }: Readonly<Props>) {
  return (
    <div className={estilos.grade} data-colunas={colunas}>
      {cartoes.map((cartao) => (
        <CardMetrica key={cartao.id} {...propsDoCartao(cartao, formulas)} />
      ))}
    </div>
  );
}
