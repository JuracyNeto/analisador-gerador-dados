import { useId } from 'react';
import { formatarValorMedida } from '../formatacao';
import type { ValorSeparatriz } from '../tipos';
import estilos from './ListaSeparatrizes.module.css';

interface Props {
  titulo: string;
  itens: readonly ValorSeparatriz[];
  destaque: string | null;
}

export default function ListaSeparatrizes({ titulo, itens, destaque }: Readonly<Props>) {
  const idTitulo = useId();

  return (
    <section className={estilos.lista} aria-labelledby={idTitulo}>
      <h3 id={idTitulo} className={estilos.titulo}>
        {titulo}
      </h3>
      <dl className={estilos.itens}>
        {itens.map((item) => (
          <div key={item.rotulo} className={estilos.item} data-destaque={item.rotulo === destaque}>
            <dt className={estilos.rotulo}>{item.rotulo}</dt>
            <dd className={estilos.valor}>{formatarValorMedida(item.valor)}</dd>
          </div>
        ))}
      </dl>
    </section>
  );
}
