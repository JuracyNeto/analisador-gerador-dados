import { useId } from 'react';
import { formatadorDaColuna } from '../../../shared/lib/formatar';
import { formatarValorMedida } from '../../../shared/metricas/formatacao';
import type { ValorSeparatriz } from '../tipos';
import estilos from './ListaSeparatrizes.module.css';

interface Props {
  titulo: string;
  itens: readonly ValorSeparatriz[];
  destaque: string | null;
}

/** Separatrizes numéricas com as mesmas casas na lista (62,30 · 77,95); categorias como vêm. */
function formatadorDaLista(itens: readonly ValorSeparatriz[]): (item: ValorSeparatriz) => string {
  const numeros = itens.flatMap((item) => (typeof item.valor === 'number' ? [item.valor] : []));
  const formatar = formatadorDaColuna(numeros);
  return (item) =>
    typeof item.valor === 'number' ? formatar(item.valor) : formatarValorMedida(item.valor);
}

export default function ListaSeparatrizes({ titulo, itens, destaque }: Readonly<Props>) {
  const idTitulo = useId();
  const formatar = formatadorDaLista(itens);

  return (
    <section className={estilos.lista} aria-labelledby={idTitulo}>
      <h3 id={idTitulo} className={estilos.titulo}>
        {titulo}
      </h3>
      <dl className={estilos.itens}>
        {itens.map((item) => (
          <div key={item.rotulo} className={estilos.item} data-destaque={item.rotulo === destaque}>
            <dt className={estilos.rotulo}>{item.rotulo}</dt>
            <dd className={estilos.valor}>{formatar(item)}</dd>
          </div>
        ))}
      </dl>
    </section>
  );
}
