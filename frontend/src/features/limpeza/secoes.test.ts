import { describe, expect, it } from 'vitest';
import { DIAGNOSTICO_SAUDE, DIAGNOSTICO_VAZIO } from '../../testes/fixtures/limpeza';
import { montarPedido, montarSecoes } from './secoes';

describe('montarSecoes', () => {
  const secoes = montarSecoes(DIAGNOSTICO_SAUDE);
  const porId = (id: string) => secoes.find((s) => s.id === id);

  it('só traz seções com problemas, na ordem do design', () => {
    expect(secoes.map((s) => s.id)).toEqual([
      'faltantes',
      'duplicados',
      'fora_de_faixa',
      'inconsistencia',
    ]);
    expect(montarSecoes(DIAGNOSTICO_VAZIO)).toEqual([]);
  });

  it('faltantes: valores sugeridos nos rótulos e moda para texto', () => {
    const [peso, cidade] = porId('faltantes')?.linhas ?? [];
    expect(porId('faltantes')?.subtitulo).toBe('5 células vazias');
    expect(peso?.descricao).toBe('3 · linhas 12, 141, 207');
    expect(peso?.opcoes.map((o) => o.rotulo)).toEqual([
      'Preencher com a mediana (69,8)',
      'Preencher com a média (70,3)',
      'Preencher com a moda (72)',
      'Remover a linha',
      'Manter como "não informado"',
    ]);
    expect(cidade?.opcoes.map((o) => o.valor)).toEqual([
      'preencher_moda',
      'remover_linhas',
      'manter',
    ]);
  });

  it('duplicados: uma linha só, com as cópias e a original', () => {
    const [linha] = porId('duplicados')?.linhas ?? [];
    expect(linha).toMatchObject({
      rotulo: '45, 46, 47',
      descricao: 'Linha 44 (todas as colunas iguais, exceto as de identificador)',
    });
  });

  it('fora de faixa: ocorrências, faixa usada e limites na ação', () => {
    const [idade, peso] = porId('fora_de_faixa')?.linhas ?? [];
    expect(idade?.descricao).toBe('Linhas 19 e 201: 0 e 230');
    expect(idade?.detalhe).toBe('Faixa aceita: 1 a 110 (seus limites)');
    expect(peso?.detalhe).toBe('Faixa aceita: 38,5 a 102,1 (regra do IQR)');
    expect(idade?.acaoBase.limites).toEqual({ min: 1, max: 110 });
  });

  it('grafias: variações sem a forma preferida', () => {
    const [goiania] = porId('inconsistencia')?.linhas ?? [];
    expect(porId('inconsistencia')?.subtitulo).toBe('2 grupos em cidade');
    expect(goiania?.descricao).toBe('"Goiania" (6), "goiânia" (2)');
    expect(goiania?.opcoes[0]?.rotulo).toBe("Unificar 'Goiania', 'goiânia' → 'Goiânia'");
  });
});

describe('montarPedido', () => {
  it('leva só as ações diferentes de "manter", completas', () => {
    const pedido = montarPedido(montarSecoes(DIAGNOSTICO_SAUDE), {
      'faltantes:peso_kg': 'preencher_mediana',
      duplicados: 'remover',
      'inconsistencia:cidade:Goiânia': 'unificar',
      'faltantes:cidade': 'manter',
    });

    expect(pedido.acoes).toEqual([
      {
        problema: 'faltantes',
        acao: 'preencher_mediana',
        coluna: 'peso_kg',
        valor: null,
        limites: null,
        grupo: null,
      },
      {
        problema: 'duplicados',
        acao: 'remover',
        coluna: null,
        valor: null,
        limites: null,
        grupo: null,
      },
      {
        problema: 'inconsistencia',
        acao: 'unificar',
        coluna: 'cidade',
        valor: null,
        limites: null,
        grupo: 'Goiânia',
      },
    ]);
  });
});
