import CaixaSelecao from '../../../shared/ui/CaixaSelecao';
import estilos from './Formulario.module.css';

interface Props {
  rotulo: string;
  ajuda: string;
  marcada: boolean;
  aoMudar: (marcada: boolean) => void;
}

/** Checkbox com uma linha de explicação ("Limitar à faixa original", "Ajuste exato"). */
export default function CaixaComAjuda({ rotulo, ajuda, marcada, aoMudar }: Readonly<Props>) {
  return (
    <CaixaSelecao
      rotulo={
        <span className={estilos.caixaTexto}>
          <span>{rotulo}</span>
          <span className={estilos.ajuda}>{ajuda}</span>
        </span>
      }
      marcada={marcada}
      aoMudar={aoMudar}
    />
  );
}
