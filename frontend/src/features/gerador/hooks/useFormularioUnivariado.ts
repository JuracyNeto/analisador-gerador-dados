import { useState } from 'react';
import { useColunasGeraveis, useOrigem } from '../api';
import {
  type CampoUnivariado,
  type ContextoUnivariado,
  ESTADO_INICIAL_UNIVARIADO,
  type EstadoUnivariado,
  montarPedidoUnivariado,
} from '../pedidos';
import type { PedidoUnivariado } from '../tipos';

/** Estado do formulário 6a; os derivados (coluna padrão, pedido, erros) são calculados. */
export function useFormularioUnivariado(datasetId: string | null) {
  const [estado, setEstado] = useState<EstadoUnivariado>(ESTADO_INICIAL_UNIVARIADO);
  const [tentou, setTentou] = useState(false);
  const colunas = useColunasGeraveis(datasetId);
  const nomes = (colunas.data ?? []).map((item) => item.coluna);
  // Depois de trocar de dataset, a coluna escolhida pode não existir mais: volta para a 1ª.
  const coluna =
    estado.coluna !== null && nomes.includes(estado.coluna) ? estado.coluna : (nomes[0] ?? null);
  const usaOrigem = datasetId !== null && estado.origem === 'coluna';
  const resumo = useOrigem(datasetId, usaOrigem ? coluna : null);
  const contexto: ContextoUnivariado = { datasetId, coluna, resumo: resumo.data };
  const resultado = montarPedidoUnivariado(estado, contexto);
  const erros: Partial<Record<CampoUnivariado, string>> =
    tentou && !resultado.ok ? resultado.erros : {};

  return {
    estado,
    contexto,
    colunas,
    resumo,
    erros,
    mudar: <K extends keyof EstadoUnivariado>(campo: K, valor: EstadoUnivariado[K]) => {
      setEstado((atual) => ({ ...atual, [campo]: valor }));
    },
    /** Trocar de coluna volta os parâmetros para os da nova origem. */
    escolherColuna: (nova: string) => {
      setEstado((atual) => ({ ...atual, coluna: nova, media: null, desvio: null, chance: null }));
    },
    /** Marca a tentativa (mostra os erros) e devolve o pedido, se estiver válido. */
    confirmar: (): PedidoUnivariado | null => {
      setTentou(true);
      return resultado.ok ? resultado.pedido : null;
    },
  };
}

export type FormularioUnivariado = ReturnType<typeof useFormularioUnivariado>;
