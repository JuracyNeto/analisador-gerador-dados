import type { ReactNode } from 'react';
import CaixaSelecao from '../../../shared/ui/CaixaSelecao';
import { TEXTOS_RELATORIO } from '../textos';
import estilos from './GrupoCaixas.module.css';

export interface ItemCaixa<T extends string> {
  id: T;
  rotulo: ReactNode;
}

interface Props<T extends string> {
  legenda: string;
  itens: readonly ItemCaixa<T>[];
  marcados: readonly T[];
  aoAlternar: (id: T) => void;
  desabilitado?: boolean;
  nota?: ReactNode;
}

export default function GrupoCaixas<T extends string>({
  legenda,
  itens,
  marcados,
  aoAlternar,
  desabilitado = false,
  nota = null,
}: Readonly<Props<T>>) {
  const conjuntoMarcados = new Set(marcados);

  return (
    <fieldset className={estilos.grupo} disabled={desabilitado}>
      <legend className={estilos.legenda}>
        <span className={estilos.titulo}>{legenda}</span>
        <span className={estilos.contador}>
          {TEXTOS_RELATORIO.contador(marcados.length, itens.length)}
        </span>
      </legend>
      {itens.map((item) => (
        <CaixaSelecao
          key={item.id}
          rotulo={item.rotulo}
          marcada={conjuntoMarcados.has(item.id)}
          desabilitada={desabilitado}
          aoMudar={() => {
            aoAlternar(item.id);
          }}
        />
      ))}
      {nota}
    </fieldset>
  );
}
