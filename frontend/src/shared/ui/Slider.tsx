import { useId } from 'react';
import { formatarDecimal } from '../lib/formatar';
import estilos from './Slider.module.css';

interface PropsSlider {
  rotulo: string;
  valor: number;
  aoMudar: (valor: number) => void;
  min: number;
  max: number;
  passo: number;
  /** Casas decimais do valor mostrado ao lado (padrão: 2, como "0,70"). */
  casas?: number;
}

const MENOS = '−';

/** Casas fixas ("0,70", "−0,35"), com o sinal de menos tipográfico (D107). */
function exibir(valor: number, casas: number): string {
  const texto = formatarDecimal(valor, casas);
  return texto.startsWith('-') ? `${MENOS}${texto.slice(1)}` : texto;
}

function Limites({ min, max }: Readonly<{ min: number; max: number }>) {
  return (
    <div className={estilos.limites} aria-hidden="true">
      <span>{exibir(min, 0)}</span>
      <span>{exibir(max, 0)}</span>
    </div>
  );
}

/** Range nativo com marca no zero e o valor em mono (tela 6b, correlação alvo). */
export default function Slider({
  rotulo,
  valor,
  aoMudar,
  min,
  max,
  passo,
  casas = 2,
}: Readonly<PropsSlider>) {
  const id = useId();
  const texto = exibir(valor, casas);
  const posicaoZero = ((0 - min) / (max - min)) * 100;
  return (
    <div className={estilos.slider}>
      <div className={estilos.topo}>
        <label htmlFor={id} className={estilos.rotulo}>
          {rotulo}
        </label>
        <output htmlFor={id} className={estilos.valor}>
          {texto}
        </output>
      </div>
      <div className={estilos.trilho}>
        {min < 0 && max > 0 ? (
          <span
            className={estilos.zero}
            style={{ left: `${String(posicaoZero)}%` }}
            aria-hidden="true"
          />
        ) : null}
        <input
          id={id}
          type="range"
          min={min}
          max={max}
          step={passo}
          value={valor}
          aria-valuetext={texto}
          className={estilos.entrada}
          onChange={(evento) => {
            aoMudar(Number(evento.target.value));
          }}
        />
      </div>
      <Limites min={min} max={max} />
    </div>
  );
}
