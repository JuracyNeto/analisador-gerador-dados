import type { UseQueryResult } from '@tanstack/react-query';
import { ErroApi } from '../../shared/api/cliente';
import { type Saude, useSaude } from './api';

function textoDoErro(erro: Error): string {
  return erro instanceof ErroApi ? `${erro.message} ${erro.sugestao}` : erro.message;
}

function textoDoStatus(saude: UseQueryResult<Saude>): string {
  if (saude.isPending) return 'Verificando a conexão com a API…';
  if (saude.isError) return textoDoErro(saude.error);
  return `API conectada (versão ${saude.data.versao}).`;
}

export default function PaginaInicio() {
  const saude = useSaude();

  return (
    <main>
      <h1>Analisador e Gerador de Dados</h1>
      <p role="status" aria-live="polite">
        {textoDoStatus(saude)}
      </p>
    </main>
  );
}
