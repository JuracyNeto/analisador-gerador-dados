import type { UseQueryResult } from '@tanstack/react-query';
import Grafico from '../../../shared/graficos/Grafico';
import Card from '../../../shared/ui/Card';
import EstadoCarregando from '../../../shared/ui/EstadoCarregando';
import EstadoErro from '../../../shared/ui/EstadoErro';
import { TEXTOS_BIVARIADA } from '../textos';
import type { MatrizCorrelacao } from '../tipos';
import estilos from './CardMatriz.module.css';

const M = TEXTOS_BIVARIADA.matriz;
const ALTURA_MATRIZ = 320;

function ConteudoMatriz({ matriz }: Readonly<{ matriz: MatrizCorrelacao }>) {
  const { figura } = matriz;
  if (figura === null) return <p className={estilos.resumo}>{matriz.resumo}</p>;
  return (
    <Grafico
      titulo={figura.titulo}
      resumo={matriz.resumo}
      figura={figura.dados}
      altura={ALTURA_MATRIZ}
    />
  );
}

/** Heatmap da matriz de correlação; carrega e falha sem derrubar o resto da tela (D105). */
export default function CardMatriz({
  consulta,
}: Readonly<{ consulta: UseQueryResult<MatrizCorrelacao> }>) {
  if (consulta.isPending) return <EstadoCarregando forma="grafico" mensagem={M.carregando} />;
  if (consulta.isError)
    return (
      <EstadoErro
        erro={consulta.error}
        aoTentarDeNovo={() => {
          void consulta.refetch();
        }}
      />
    );
  return (
    <Card>
      <ConteudoMatriz matriz={consulta.data} />
    </Card>
  );
}
