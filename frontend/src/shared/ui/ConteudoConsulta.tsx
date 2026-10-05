import type { UseQueryResult } from '@tanstack/react-query';
import type { ReactNode } from 'react';
import EstadoCarregando from './EstadoCarregando';
import EstadoErro from './EstadoErro';

interface PropsConteudoConsulta<T> {
  consulta: UseQueryResult<T>;
  carregando: string;
  forma: 'cards' | 'tabela' | 'grafico';
  children: (dados: T) => ReactNode;
}

/** Estados obrigatórios (spec 15) de uma consulta: carregando → erro com "tentar de novo" → dados. */
export default function ConteudoConsulta<T>({
  consulta,
  carregando,
  forma,
  children,
}: Readonly<PropsConteudoConsulta<T>>) {
  if (consulta.isPending) return <EstadoCarregando mensagem={carregando} forma={forma} />;
  if (consulta.isError) {
    return (
      <EstadoErro
        erro={consulta.error}
        aoTentarDeNovo={() => {
          void consulta.refetch();
        }}
      />
    );
  }
  return <>{children(consulta.data)}</>;
}
