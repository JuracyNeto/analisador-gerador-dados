import type { ReactNode } from 'react';
import Grafico from '../../../shared/graficos/Grafico';
import { formatarPValor } from '../../../shared/lib/formatar';
import Accordion from '../../../shared/ui/Accordion';
import { TEXTOS_DETECTOR } from '../textos';
import type { Aviso, DetalhesAviso } from '../tipos';
import estilos from './CartaoAlerta.module.css';

const T = TEXTOS_DETECTOR.detalhes;
const ALTURA_FIGURA = 280;

interface PropsLinha {
  rotulo: string;
  mono?: boolean;
  children: ReactNode;
}

function Linha({ rotulo, mono = false, children }: Readonly<PropsLinha>) {
  return (
    <>
      <dt>{rotulo}</dt>
      <dd className={mono ? estilos.mono : undefined}>{children}</dd>
    </>
  );
}

function PValor({ detalhes }: Readonly<{ detalhes: DetalhesAviso }>) {
  if (detalhes.p_valor === null) return null;
  return (
    <Linha rotulo={T.pValor}>
      <span className={estilos.mono}>{formatarPValor(detalhes.p_valor)}</span>{' '}
      {detalhes.p_em_palavras === null ? null : (
        <span className={estilos.secundario}>{T.traducao(detalhes.p_em_palavras)}</span>
      )}
    </Linha>
  );
}

function ListaDetalhes({ detalhes }: Readonly<{ detalhes: DetalhesAviso }>) {
  return (
    <dl className={estilos.lista}>
      <Linha rotulo={T.medida}>{detalhes.medida}</Linha>
      <Linha rotulo={T.valor} mono>
        {detalhes.valor}
      </Linha>
      <Linha rotulo={T.limiar} mono>
        {detalhes.limiar}
      </Linha>
      {detalhes.teste === null ? null : <Linha rotulo={T.teste}>{detalhes.teste}</Linha>}
      <PValor detalhes={detalhes} />
      {detalhes.formula === null ? null : (
        <>
          <dt>{T.formula}</dt>
          <dd className={estilos.formula}>{detalhes.formula}</dd>
        </>
      )}
    </dl>
  );
}

/** Parte 8, recolhida: medida, valor, limiar, teste, p-valor traduzido, fórmula e a figura (D123). */
export default function DetalhesTecnicos({ aviso }: Readonly<{ aviso: Aviso }>) {
  const { figura } = aviso;
  return (
    <div className={estilos.detalhes}>
      <Accordion titulo={T.titulo}>
        <ListaDetalhes detalhes={aviso.detalhes} />
        {figura === null ? null : (
          <div className={estilos.figura}>
            <Grafico
              titulo={figura.titulo}
              resumo={figura.resumo}
              figura={figura.dados}
              altura={ALTURA_FIGURA}
            />
            <p className={estilos.secundario}>{figura.porque}</p>
          </div>
        )}
      </Accordion>
    </div>
  );
}
