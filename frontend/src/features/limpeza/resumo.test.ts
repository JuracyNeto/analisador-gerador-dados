import { describe, expect, it } from 'vitest';
import {
  criarResultado,
  DIAGNOSTICO_SAUDE,
  DIAGNOSTICO_VAZIO,
} from '../../testes/fixtures/limpeza';
import {
  avisoLimpezaAplicada,
  avisoLimpezaDesfeita,
  resumirDiagnostico,
  temProblemas,
} from './resumo';

describe('resumirDiagnostico', () => {
  it('monta os 4 cards do design', () => {
    expect(resumirDiagnostico(DIAGNOSTICO_SAUDE)).toEqual([
      {
        id: 'faltantes',
        rotulo: 'Faltantes',
        valor: '5',
        unidade: 'células',
        frase: 'Em 2 colunas; peso_kg tem 3.',
      },
      {
        id: 'duplicados',
        rotulo: 'Duplicados',
        valor: '3',
        unidade: 'linhas',
        frase: 'Cópias exatas da linha 44.',
      },
      {
        id: 'fora_de_faixa',
        rotulo: 'Fora de faixa',
        valor: '4',
        unidade: 'valores',
        frase: 'Fora dos limites que você definiu.',
      },
      {
        id: 'grafias',
        rotulo: 'Grafias diferentes',
        valor: '2',
        unidade: 'grupos',
        frase: 'Mesmo texto escrito de jeitos diferentes.',
      },
    ]);
  });

  it('sem problemas, frases de "nenhum"', () => {
    expect(resumirDiagnostico(DIAGNOSTICO_VAZIO)[0]).toMatchObject({
      valor: '0',
      unidade: 'células',
      frase: 'Nenhum valor faltando.',
    });
    expect(temProblemas(DIAGNOSTICO_VAZIO)).toBe(false);
    expect(temProblemas(DIAGNOSTICO_SAUDE)).toBe(true);
  });
});

describe('avisos', () => {
  it('toast de limpeza aplicada: verbo no passado + quantidade', () => {
    expect(avisoLimpezaAplicada(230, criarResultado({ n_linhas: 227 }), 3)).toEqual({
      tipo: 'sucesso',
      titulo: 'Limpeza aplicada: 3 linhas removidas.',
      descricao: '3 ações aplicadas.',
    });
    expect(avisoLimpezaAplicada(230, criarResultado({ n_linhas: 230 }), 1).titulo).toBe(
      'Limpeza aplicada: nenhuma linha removida.',
    );
  });

  it('toast de desfazer', () => {
    expect(avisoLimpezaDesfeita(criarResultado({ n_linhas: 230 })).titulo).toBe(
      'Limpeza desfeita: voltamos às 230 linhas do arquivo.',
    );
  });
});
