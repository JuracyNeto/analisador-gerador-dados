import { useState } from 'react';
import { useColunasGeraveis, useOrigemPar } from '../api';
import {
  type CampoBivariado,
  type ContextoBivariado,
  ESTADO_INICIAL_BIVARIADO,
  type EstadoBivariado,
  ehNumerica,
  montarPedidoBivariado,
} from '../pedidos';
import type { PedidoBivariado } from '../tipos';

/** X e Y escolhidos, se ainda forem numéricas; padrão = as duas primeiras (como na tela 5). */
function escolherXY(estado: EstadoBivariado, nomes: readonly string[]) {
  const valida = (escolhida: string | null) =>
    escolhida !== null && nomes.includes(escolhida) ? escolhida : null;
  const x = valida(estado.x) ?? nomes[0] ?? null;
  const y = valida(estado.y) ?? nomes.find((nome) => nome !== x) ?? null;
  return { x, y };
}

/** Estado do formulário 6b. */
export function useFormularioBivariado(datasetId: string | null) {
  const [estado, setEstado] = useState<EstadoBivariado>(ESTADO_INICIAL_BIVARIADO);
  const [tentou, setTentou] = useState(false);
  const colunas = useColunasGeraveis(datasetId);
  const numericas = (colunas.data ?? []).filter((coluna) => ehNumerica(coluna.tipo));
  const nomes = numericas.map((coluna) => coluna.coluna);
  const { x, y } = escolherXY(estado, nomes);
  // Como na tela 5: com menos de duas numéricas não há par do dataset (só parâmetros manuais).
  const parPossivel = !(colunas.isSuccess && nomes.length < 2);
  const usaOrigem = datasetId !== null && parPossivel && estado.origem === 'coluna';
  const par = useOrigemPar(usaOrigem ? datasetId : null, x, y);
  const contexto: ContextoBivariado = { datasetId, x, y, par: par.data, parPossivel };
  const resultado = montarPedidoBivariado(estado, contexto);
  const erros: Partial<Record<CampoBivariado, string>> =
    tentou && !resultado.ok ? resultado.erros : {};

  return {
    estado,
    contexto,
    numericas,
    par,
    erros,
    mudar: <K extends keyof EstadoBivariado>(campo: K, valor: EstadoBivariado[K]) => {
      setEstado((atual) => ({ ...atual, [campo]: valor }));
    },
    confirmar: (): PedidoBivariado | null => {
      setTentou(true);
      return resultado.ok ? resultado.pedido : null;
    },
  };
}

export type FormularioBivariado = ReturnType<typeof useFormularioBivariado>;
