import { describe, expect, it } from 'vitest';
import { METADADOS_SAUDE } from '../../testes/fixtures/datasets';
import { aplicarCorrecao, descreverDeteccoes, montarFormulario } from './opcoesLeitura';

const XLSX = {
  ...METADADOS_SAUDE,
  formato: 'xlsx' as const,
  separador: null,
  decimal: null,
  codificacao: null,
  abas: ['Dados', 'Resumo'],
};

describe('descreverDeteccoes', () => {
  it('TXT mostra os 5 campos do design, com rótulo e motivo', () => {
    const campos = descreverDeteccoes(METADADOS_SAUDE, {});

    expect(campos.map((c) => c.campo)).toEqual([
      'formato',
      'separador',
      'decimal',
      'codificacao',
      'cabecalho',
    ]);
    expect(campos[1]).toMatchObject({
      rotulo: 'Separador',
      valor: ';',
      rotuloValor: 'Ponto e vírgula ( ; )',
      motivo: 'Aparece 7 vezes em todas as linhas.',
      corrigivel: true,
    });
    expect(campos[0]).toMatchObject({ rotuloValor: 'Texto (TXT)', corrigivel: false });
    expect(campos[4]).toMatchObject({ valor: 'sim', rotuloValor: 'Sim, 1ª linha' });
  });

  it('XLSX troca separador, decimal e codificação pela aba', () => {
    const campos = descreverDeteccoes(XLSX, { aba: 'Resumo' });

    expect(campos.map((c) => c.campo)).toEqual(['formato', 'aba', 'cabecalho']);
    expect(campos[1]?.valor).toBe('Resumo');
  });

  it('valor detectado fora da lista vira uma opção extra', () => {
    const [, separador] = descreverDeteccoes({ ...METADADOS_SAUDE, separador: '#' }, {});

    expect(separador?.opcoes.at(-1)).toEqual({ valor: '#', rotulo: 'Outro ( # )' });
  });
});

describe('aplicarCorrecao', () => {
  it('cabeçalho vira booleano e mantém as correções anteriores', () => {
    expect(aplicarCorrecao({ separador: ',' }, 'cabecalho', 'nao')).toEqual({
      separador: ',',
      tem_cabecalho: false,
    });
  });

  it('formato não é corrigível', () => {
    expect(aplicarCorrecao({}, 'formato', 'csv')).toEqual({});
  });
});

describe('montarFormulario', () => {
  it('envia o arquivo e só as opções definidas', () => {
    const arquivo = new File(['a;b'], 'dados.txt', { type: 'text/plain' });

    const formulario = montarFormulario(arquivo, {
      separador: ',',
      decimal: null,
      tem_cabecalho: false,
    });

    expect(formulario.get('arquivo')).toBe(arquivo);
    expect(formulario.get('separador')).toBe(',');
    expect(formulario.has('decimal')).toBe(false);
    expect(formulario.get('tem_cabecalho')).toBe('false');
  });
});
