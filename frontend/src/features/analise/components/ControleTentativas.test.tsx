import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import { analiseDiscreta, analiseNominal } from '../../../testes/fixturesAnalise';
import { maiorValorObservado, validarTentativas } from '../tentativas';
import { TEXTOS_ANALISE } from '../textos';
import ControleTentativas from './ControleTentativas';

const T = TEXTOS_ANALISE.forma.tentativas;

describe('ControleTentativas', () => {
  it('aplica um número válido pelo botão', async () => {
    const usuario = userEvent.setup();
    const aoAplicar = vi.fn();
    render(<ControleTentativas tentativas={8} maximo={8} aoAplicar={aoAplicar} />);

    const campo = screen.getByRole('textbox', { name: T.rotulo });
    await usuario.clear(campo);
    await usuario.type(campo, '10');
    await usuario.click(screen.getByRole('button', { name: T.aplicar }));

    expect(aoAplicar).toHaveBeenCalledWith(10);
  });

  it('aplica com Enter', async () => {
    const usuario = userEvent.setup();
    const aoAplicar = vi.fn();
    render(<ControleTentativas tentativas={8} maximo={8} aoAplicar={aoAplicar} />);

    await usuario.type(screen.getByRole('textbox', { name: T.rotulo }), '0{Enter}');

    expect(aoAplicar).toHaveBeenCalledWith(80);
  });

  it('recusa valor menor que o máximo, sem chamar a API', async () => {
    const usuario = userEvent.setup();
    const aoAplicar = vi.fn();
    render(<ControleTentativas tentativas={8} maximo={8} aoAplicar={aoAplicar} />);

    const campo = screen.getByRole('textbox', { name: T.rotulo });
    await usuario.clear(campo);
    await usuario.type(campo, '2');
    await usuario.click(screen.getByRole('button', { name: T.aplicar }));

    expect(aoAplicar).not.toHaveBeenCalled();
    expect(screen.getByText(T.erroMinimo('8'))).toBeInTheDocument();
    expect(campo).toHaveAttribute('aria-invalid', 'true');
  });

  it('mostra o padrão na ajuda', () => {
    render(<ControleTentativas tentativas={8} maximo={8} aoAplicar={vi.fn()} />);

    expect(screen.getByText(T.ajuda('8'))).toBeInTheDocument();
  });
});

describe('validarTentativas', () => {
  it.each([
    ['10', 8, { status: 'ok', n: 10 }],
    ['8', 8, { status: 'ok', n: 8 }],
    ['2,5', 2, { status: 'erro', mensagem: T.erroInteiro }],
    ['abc', 2, { status: 'erro', mensagem: T.erroInteiro }],
    ['3', 8, { status: 'erro', mensagem: T.erroMinimo('8') }],
  ])('%s com máximo %s', (texto, maximo, esperado) => {
    expect(validarTentativas(texto, maximo)).toEqual(esperado);
  });
});

describe('maiorValorObservado', () => {
  it('na discreta é o último valor da tabela; sem números, null', () => {
    expect(maiorValorObservado(analiseNominal)).toBeNull();
    expect(maiorValorObservado(analiseDiscreta)).toBe(8);
  });
});
