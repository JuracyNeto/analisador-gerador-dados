import { useQuery } from '@tanstack/react-query';
import { screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { requisitar } from '../api/cliente';
import { simularApi } from '../../testes/api';
import { renderizarComProvedores } from '../../testes/renderizar';
import ConteudoConsulta from './ConteudoConsulta';

function Exemplo() {
  const consulta = useQuery({
    queryKey: ['exemplo'],
    queryFn: () => requisitar<{ nome: string }>('/exemplo'),
  });
  return (
    <ConteudoConsulta consulta={consulta} carregando="Carregando o exemplo…" forma="cards">
      {(dados) => <p>Olá, {dados.nome}</p>}
    </ConteudoConsulta>
  );
}

describe('ConteudoConsulta', () => {
  it('mostra o carregando e depois os dados', async () => {
    simularApi([{ caminho: '/exemplo', corpo: { nome: 'mundo' } }]);
    renderizarComProvedores(<Exemplo />);

    // O ToastProvider também tem região role="status"; por isso a busca é pelo texto.
    expect(screen.getByText('Carregando o exemplo…')).toBeInTheDocument();
    expect(await screen.findByText('Olá, mundo')).toBeInTheDocument();
  });

  it('mostra o erro da API com "tentar de novo"', async () => {
    simularApi([
      {
        caminho: '/exemplo',
        status: 400,
        corpo: { codigo: 'X', mensagem: 'Deu errado.', sugestao: 'Tente outra coisa.' },
      },
    ]);
    renderizarComProvedores(<Exemplo />);

    expect(await screen.findByText('Deu errado.')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /tentar de novo/i })).toBeInTheDocument();
  });
});
