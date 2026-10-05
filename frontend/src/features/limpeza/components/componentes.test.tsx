import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import { criarResumo } from '../../../testes/fixtures/datasets';
import { criarEntradaLog, DIAGNOSTICO_SAUDE } from '../../../testes/fixtures/limpeza';
import { montarSecoes } from '../secoes';
import CardsResumoLimpeza from './CardsResumoLimpeza';
import LimitesPorColuna from './LimitesPorColuna';
import PainelLog from './PainelLog';
import SecaoProblema from './SecaoProblema';

const [FALTANTES] = montarSecoes(DIAGNOSTICO_SAUDE);

describe('SecaoProblema', () => {
  it('lista as linhas com o Select em "Manter" e avisa a escolha', async () => {
    if (FALTANTES === undefined) throw new Error('fixture sem faltantes');
    const aoEscolher = vi.fn();
    render(<SecaoProblema secao={FALTANTES} escolhas={{}} aoEscolher={aoEscolher} />);

    const regiao = screen.getByRole('region', { name: 'Faltantes' });
    expect(within(regiao).getByText('5 células vazias')).toBeInTheDocument();
    const select = within(regiao).getByRole('combobox', { name: 'Ação para peso_kg' });
    expect(select).toHaveValue('manter');

    await userEvent.selectOptions(select, 'preencher_mediana');
    expect(aoEscolher).toHaveBeenCalledWith('faltantes:peso_kg', 'preencher_mediana');
  });
});

describe('CardsResumoLimpeza', () => {
  it('mostra os 4 cards', () => {
    render(<CardsResumoLimpeza diagnostico={DIAGNOSTICO_SAUDE} />);
    expect(screen.getByText('Cópias exatas da linha 44.')).toBeInTheDocument();
    expect(screen.getByText('Grafias diferentes')).toBeInTheDocument();
  });
});

describe('LimitesPorColuna', () => {
  it('um grupo por coluna numérica, com erro de ordem no mínimo', () => {
    render(
      <LimitesPorColuna
        colunas={['idade', 'peso_kg']}
        textos={{ idade: { min: '120', max: '110' } }}
        aoMudar={vi.fn()}
      />,
    );

    const idade = screen.getByRole('group', { name: 'idade' });
    expect(within(idade).getByLabelText('Mínimo')).toHaveValue('120');
    expect(
      within(idade).getByText('O mínimo precisa ser menor que o máximo (110). Ajuste um dos dois.'),
    ).toBeInTheDocument();
  });

  it('sem colunas numéricas não aparece', () => {
    const { container } = render(<LimitesPorColuna colunas={[]} textos={{}} aoMudar={vi.fn()} />);
    expect(container).toBeEmptyDOMElement();
  });
});

describe('PainelLog', () => {
  it('frases com detalhe e o resultado', () => {
    render(<PainelLog resumo={criarResumo({ n_linhas: 227, log_limpeza: [criarEntradaLog()] })} />);

    const painel = screen.getByRole('complementary', { name: 'Registro das ações' });
    expect(within(painel).getByText('Removemos 3 linhas duplicadas.')).toBeInTheDocument();
    expect(within(painel).getByText('linhas 45, 46, 47')).toBeInTheDocument();
    expect(painel).toHaveTextContent('Resultado: 227 linhas (eram 230).');
  });

  it('sem ações, explica onde elas vão aparecer', () => {
    render(<PainelLog resumo={criarResumo()} />);
    expect(
      screen.getByText('Nada aplicado ainda. As ações que você aplicar aparecem aqui.'),
    ).toBeInTheDocument();
  });
});
