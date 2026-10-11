import { useSearchParams } from 'react-router';
import type { IdAba } from '../tipos';

const ABAS: readonly IdAba[] = ['univariado', 'bivariado'];

/** Aba na URL (`?aba=`), como a coluna da tela 4 (D78): recarregar mantém a aba. */
export function lerAba(busca: URLSearchParams): IdAba {
  const valor = busca.get('aba');
  return ABAS.find((aba) => aba === valor) ?? 'univariado';
}

export function useAbaGerador() {
  const [busca, definirBusca] = useSearchParams();
  return {
    aba: lerAba(busca),
    mudar: (aba: IdAba) => {
      definirBusca((atual) => {
        const nova = new URLSearchParams(atual);
        nova.set('aba', aba);
        return nova;
      });
    },
  };
}
