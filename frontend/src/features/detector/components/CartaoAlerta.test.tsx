import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import type { ReactElement } from 'react';
import { describe, expect, it, vi } from 'vitest';
import { avisoR1, avisoR4, avisoR5, criarAviso } from '../../../testes/fixtures/detector';
import { ContextoVerNaTabela } from '../hooks/contextoVerNaTabela';
import type { Aviso } from '../tipos';
import CartaoAlerta from './CartaoAlerta';

vi.mock('../../../shared/graficos/Grafico', () => import('../../../testes/graficoFalso'));

function renderizar(elemento: ReactElement, verNaTabela: (aviso: Aviso) => void = vi.fn()) {
  const usuario = userEvent.setup();
  const resultado = render(
    <ContextoVerNaTabela value={verNaTabela}>{elemento}</ContextoVerNaTabela>,
  );
  return { ...resultado, usuario };
}

function posicoes(texto: string, partes: readonly string[]): number[] {
  return partes.map((parte) => texto.indexOf(parte));
}

describe('CartaoAlerta', () => {
  it('aberto mostra as 8 partes na ordem da spec 16', () => {
    const { container } = renderizar(<CartaoAlerta aviso={avisoR4} abertoInicial />);

    const ordem = posicoes(container.textContent, [
      'Atenção',
      'R4 · Valores redondos',
      'peso_kg',
      avisoR4.titulo,
      avisoR4.resumo,
      'Por que chama atenção',
      avisoR4.por_que,
      'Pode ser normal se…',
      avisoR4.pode_ser_normal,
      'Exemplo',
      'Linhas 120 a 122: 70, 75, 80',
      'Ver na tabela',
      'O que fazer:',
      avisoR4.o_que_fazer,
      'Detalhes técnicos',
    ]);
    expect(ordem.every((posicao) => posicao >= 0)).toBe(true);
    expect(ordem).toEqual(ordem.toSorted((a, b) => a - b));
    expect(screen.getByRole('article', { name: avisoR4.titulo })).toBeInTheDocument();
    expect(screen.getByRole('heading', { level: 3, name: avisoR4.titulo })).toBeInTheDocument();
  });

  it('recolhido mostra só severidade, título e resumo até pedir a explicação', async () => {
    const { usuario } = renderizar(<CartaoAlerta aviso={avisoR4} abertoInicial={false} />);

    expect(screen.getByText(avisoR4.resumo)).toBeInTheDocument();
    expect(screen.queryByText(avisoR4.por_que)).not.toBeInTheDocument();
    const botao = screen.getByRole('button', { name: 'Ver explicação' });
    expect(botao).toHaveAttribute('aria-expanded', 'false');

    await usuario.click(botao);

    expect(screen.getByText(avisoR4.por_que)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Ocultar explicação' })).toHaveAttribute(
      'aria-expanded',
      'true',
    );
  });

  it('detalhes técnicos começam fechados e trazem o p-valor com a tradução', async () => {
    const { usuario } = renderizar(<CartaoAlerta aviso={avisoR4} abertoInicial />);
    expect(screen.queryByText('Binomial unilateral')).not.toBeInTheDocument();

    await usuario.click(screen.getByRole('button', { name: 'Detalhes técnicos' }));

    const detalhes = screen;
    expect(detalhes.getByText('Binomial unilateral')).toBeInTheDocument();
    expect(detalhes.getByText('p < 0,001')).toBeInTheDocument();
    expect(
      detalhes.getByText('· chance de acontecer por acaso: menos de 1 em 1.000'),
    ).toBeInTheDocument();
    expect(detalhes.getByText(avisoR4.detalhes.formula ?? '')).toBeInTheDocument();
    expect(screen.queryByRole('figure')).not.toBeInTheDocument();
  });

  it('sem teste, p-valor e fórmula, essas linhas não aparecem', async () => {
    const semP = criarAviso({ regra: 'R7', nome_regra: 'Valores distantes', severidade: 'info' });
    const sem = { ...semP, detalhes: { ...semP.detalhes, formula: null } };
    const { usuario } = renderizar(<CartaoAlerta aviso={sem} abertoInicial />);

    await usuario.click(screen.getByRole('button', { name: 'Detalhes técnicos' }));

    expect(screen.getByText('Medida')).toBeInTheDocument();
    for (const rotulo of ['Teste', 'p-valor', 'Fórmula']) {
      expect(screen.queryByText(rotulo)).not.toBeInTheDocument();
    }
  });

  it('a figura da regra aparece dentro dos detalhes técnicos (R1)', async () => {
    const { usuario } = renderizar(<CartaoAlerta aviso={avisoR1} abertoInicial />);

    await usuario.click(screen.getByRole('button', { name: 'Detalhes técnicos' }));

    expect(screen.getByRole('figure', { name: 'Média por bloco' })).toBeInTheDocument();
  });

  it('"Ver na tabela" pede o drawer com o aviso; linhas inteiras no topo (R5)', async () => {
    const verNaTabela = vi.fn();
    const { usuario } = renderizar(<CartaoAlerta aviso={avisoR5} abertoInicial />, verNaTabela);

    expect(screen.getByText('Linhas inteiras')).toBeInTheDocument();
    await usuario.click(screen.getByRole('button', { name: 'Ver na tabela' }));

    expect(verNaTabela).toHaveBeenCalledWith(avisoR5);
  });

  it('sem exemplo não há "Ver na tabela"', () => {
    renderizar(
      <CartaoAlerta aviso={criarAviso({ regra: 'R10', nome_regra: 'Normal' })} abertoInicial />,
    );

    expect(screen.queryByText('Exemplo')).not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'Ver na tabela' })).not.toBeInTheDocument();
  });
});
