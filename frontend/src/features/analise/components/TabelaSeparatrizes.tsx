import Card from '../../../shared/ui/Card';
import { percentisVisiveis } from '../separatrizes';
import { TEXTOS_ANALISE } from '../textos';
import type { Separatrizes } from '../tipos';
import ListaSeparatrizes from './ListaSeparatrizes';
import estilos from './TabelaSeparatrizes.module.css';

const S = TEXTOS_ANALISE.separatrizes;

interface Props {
  coluna: string;
  separatrizes: Separatrizes;
  destaque: string | null;
}

export default function TabelaSeparatrizes({ coluna, separatrizes, destaque }: Readonly<Props>) {
  const grupos = [
    { titulo: S.quartis, itens: separatrizes.quartis },
    { titulo: S.decis, itens: separatrizes.decis },
    { titulo: S.percentis, itens: percentisVisiveis(separatrizes, destaque) },
  ];

  return (
    <Card titulo={S.titulo(coluna)}>
      <div className={estilos.grupos}>
        {grupos.map((grupo) => (
          <ListaSeparatrizes
            key={grupo.titulo}
            titulo={grupo.titulo}
            itens={grupo.itens}
            destaque={destaque}
          />
        ))}
      </div>
      <details className={estilos.todos}>
        <summary className={estilos.resumo}>{S.verTodos}</summary>
        <ListaSeparatrizes
          titulo={S.todosPercentis}
          itens={separatrizes.percentis}
          destaque={destaque}
        />
      </details>
    </Card>
  );
}
