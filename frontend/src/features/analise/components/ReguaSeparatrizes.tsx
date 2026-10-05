import { descricaoDaRegua, montarRegua } from '../separatrizes';
import { TEXTOS_ANALISE } from '../textos';
import type { Posicao } from '../tipos';
import estilos from './ReguaSeparatrizes.module.css';

const P = TEXTOS_ANALISE.posicao;

const emPorcentagem = (valor: number) => `${valor.toFixed(2)}%`;

interface Props {
  posicao: Posicao;
}

type Regua = ReturnType<typeof montarRegua>;

/** Mínimo, rótulos das marcas e máximo, embaixo do trilho. */
function RotulosRegua({ regua }: Readonly<{ regua: Regua }>) {
  return (
    <div className={estilos.rotulos}>
      <span className={estilos.extremoEsquerdo}>
        {P.minimo}
        <br />
        {regua.minimo}
      </span>
      {regua.marcas.map((marca) => (
        <span
          key={marca.rotulo}
          className={estilos.rotulo}
          style={{ left: emPorcentagem(marca.percentual) }}
        >
          {marca.rotulo}
          <br />
          {marca.valor}
        </span>
      ))}
      <span className={estilos.extremoDireito}>
        {P.maximo}
        <br />
        {regua.maximo}
      </span>
    </div>
  );
}

export default function ReguaSeparatrizes({ posicao }: Readonly<Props>) {
  const regua = montarRegua(posicao);

  return (
    <div className={estilos.regua} role="img" aria-label={descricaoDaRegua(posicao)}>
      <div className={estilos.area}>
        <div className={estilos.trilho} />
        <div
          className={estilos.faixa}
          style={{
            left: emPorcentagem(regua.faixa.inicio),
            width: emPorcentagem(regua.faixa.largura),
          }}
        />
        {regua.marcas.map((marca) => (
          <div
            key={marca.rotulo}
            className={estilos.marca}
            style={{ left: emPorcentagem(marca.percentual) }}
          />
        ))}
        <div className={estilos.marcador} style={{ left: emPorcentagem(regua.marcador) }}>
          <span className={estilos.etiqueta}>{regua.valor}</span>
          <span className={estilos.ponto} />
        </div>
      </div>
      <RotulosRegua regua={regua} />
    </div>
  );
}
