import { describe, expect, it, vi } from 'vitest';
import { ErroApi } from '../../shared/api/cliente';
import { analiseContinua, colunasPesquisa } from '../../testes/fixturesAnalise';
import { comPadraoDeTentativas, estadoDaAnalise, type ConsultaSimples } from './estadoAnalise';
import type { Analise, TipoColuna } from './tipos';

function consulta<T>(parcial: Partial<ConsultaSimples<T>>): ConsultaSimples<T> {
  return {
    status: 'pending',
    data: undefined,
    error: null,
    isPlaceholderData: false,
    refetch: vi.fn(),
    ...parcial,
  };
}

const colunasProntas = consulta<TipoColuna[]>({ status: 'success', data: colunasPesquisa });
const analisePendente = consulta<Analise>({});

describe('estadoDaAnalise', () => {
  it('carrega as colunas primeiro', () => {
    expect(estadoDaAnalise(consulta({}), analisePendente, null).status).toBe('carregando-colunas');
  });

  it('erro nas colunas pode ser tentado de novo', () => {
    const colunas = consulta<TipoColuna[]>({ status: 'error', error: new Error('rede') });
    const estado = estadoDaAnalise(colunas, analisePendente, null);

    expect(estado.status).toBe('erro');
    if (estado.status !== 'erro') return;
    estado.tentarDeNovo?.();
    expect(colunas.refetch).toHaveBeenCalled();
  });

  it('sem coluna analisável mostra o estado vazio', () => {
    expect(estadoDaAnalise(colunasProntas, analisePendente, null).status).toBe('sem-colunas');
  });

  it('enquanto a análise não chega, mostra "Calculando…" com o nome da coluna', () => {
    expect(estadoDaAnalise(colunasProntas, analisePendente, 'peso_kg')).toEqual({
      status: 'calculando',
      coluna: 'peso_kg',
    });
  });

  it('COLUNA_IGNORADA não oferece "Tentar de novo"', () => {
    const erro = new ErroApi(400, {
      codigo: 'COLUNA_IGNORADA',
      mensagem: 'A coluna id é um identificador.',
      sugestao: '',
    });
    const estado = estadoDaAnalise(
      colunasProntas,
      consulta<Analise>({ status: 'error', error: erro }),
      'id',
    );

    expect(estado).toEqual({ status: 'erro', erro, tentarDeNovo: null });
  });

  it('com dados de outro nº de classes (placeholder), fica pronta e marcada como atualizando', () => {
    const analise = consulta<Analise>({
      status: 'success',
      data: analiseContinua,
      isPlaceholderData: true,
    });

    expect(estadoDaAnalise(colunasProntas, analise, 'peso_kg')).toEqual({
      status: 'pronta',
      analise: analiseContinua,
      atualizando: true,
    });
  });
});

describe('comPadraoDeTentativas', () => {
  const erro = (codigo: string) => new ErroApi(400, { codigo, mensagem: 'x', sugestao: 'y' });

  it('troca o "Tentar de novo" por voltar ao padrão quando as tentativas são inválidas', () => {
    const usarPadrao = vi.fn();
    const estado = comPadraoDeTentativas(
      { status: 'erro', erro: erro('TENTATIVAS_INVALIDAS'), tentarDeNovo: null },
      usarPadrao,
    );

    expect(estado.status === 'erro' && estado.tentarDeNovo).toBe(usarPadrao);
  });

  it('não mexe nos outros estados', () => {
    const estado = { status: 'erro' as const, erro: erro('COLUNA_VAZIA'), tentarDeNovo: null };

    expect(comPadraoDeTentativas(estado, vi.fn())).toBe(estado);
    expect(comPadraoDeTentativas({ status: 'sem-colunas' }, vi.fn())).toEqual({
      status: 'sem-colunas',
    });
  });
});
