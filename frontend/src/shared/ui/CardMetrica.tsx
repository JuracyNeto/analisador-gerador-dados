import { useId, useState } from 'react';
import { juntarClasses } from '../lib/classes';
import Botao from './Botao';
import estilos from './CardMetrica.module.css';
import { TEXTOS_UI } from './textos';

interface FormulaMetrica {
  expressao: string;
  calculo?: string | undefined;
}

interface PropsCardMetrica {
  rotulo: string;
  valor: string;
  /** `menor` (26 px) para valores longos, como a equação da reta (print 5a). */
  tamanhoValor?: 'normal' | 'menor' | undefined;
  unidade?: string | undefined;
  interpretacao?: string | undefined;
  selo?: string | undefined;
  formula?: FormulaMetrica | undefined;
  /** Motivo já no formato da spec 16: "{medida} não se aplica a {tipo}: {motivo}." */
  naoAplicavel?: { motivo: string } | undefined;
}

export default function CardMetrica({ naoAplicavel, ...props }: Readonly<PropsCardMetrica>) {
  if (naoAplicavel) return <CardNaoAplicavel rotulo={props.rotulo} motivo={naoAplicavel.motivo} />;
  return <CardAplicavel {...props} />;
}

function CardAplicavel({
  rotulo,
  valor,
  tamanhoValor = 'normal',
  unidade,
  interpretacao,
  selo,
  formula,
}: Readonly<Omit<PropsCardMetrica, 'naoAplicavel'>>) {
  return (
    <article className={estilos.card}>
      <h3 className={estilos.rotulo}>{rotulo}</h3>
      <p className={estilos.valor} data-tamanho={tamanhoValor}>
        {valor}
        {unidade ? <span className={estilos.unidade}>{unidade}</span> : null}
      </p>
      {selo ? <span className={estilos.selo}>{selo}</span> : null}
      {interpretacao ? <p className={estilos.interpretacao}>{interpretacao}</p> : null}
      {formula ? <FormulaRecolhivel formula={formula} /> : null}
    </article>
  );
}

function FormulaRecolhivel({ formula }: Readonly<{ formula: FormulaMetrica }>) {
  const [aberta, setAberta] = useState(false);
  const id = useId();
  return (
    <>
      <Botao
        variante="fantasma"
        tamanho="sm"
        className={estilos.botaoFormula}
        iconeFinal={aberta ? 'expand_less' : 'expand_more'}
        aria-expanded={aberta}
        aria-controls={id}
        onClick={() => {
          setAberta((atual) => !atual);
        }}
      >
        {aberta ? TEXTOS_UI.ocultarFormula : TEXTOS_UI.verFormula}
      </Botao>
      <div id={id} className={estilos.formula} hidden={!aberta}>
        <p className={estilos.expressao}>{formula.expressao}</p>
        {formula.calculo ? <p className={estilos.calculo}>{formula.calculo}</p> : null}
      </div>
    </>
  );
}

function CardNaoAplicavel({ rotulo, motivo }: Readonly<{ rotulo: string; motivo: string }>) {
  return (
    <article className={juntarClasses(estilos.card, estilos.naoAplicavel)}>
      <div className={estilos.topo}>
        <h3 className={estilos.rotulo}>{rotulo}</h3>
        <span className={estilos.seloNaoAplica}>{TEXTOS_UI.naoSeAplica}</span>
      </div>
      <p className={juntarClasses(estilos.valor, estilos.ausente)} aria-hidden="true">
        {TEXTOS_UI.valorAusente}
      </p>
      <p className={estilos.motivo}>{motivo}</p>
    </article>
  );
}
