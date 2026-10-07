import { describe, expect, it } from 'vitest';
import { METADADOS_COM_TITULO, METADADOS_SAUDE } from '../../testes/fixtures/datasets';
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
    expect(campos[4]).toMatchObject({ valor: '1', rotuloValor: 'Linha 1' });
  });

  it('cabeçalho oferece as linhas não vazias do início do arquivo e "Sem cabeçalho"', () => {
    const cabecalho = descreverDeteccoes(METADADOS_COM_TITULO, {}).at(-1);

    expect(cabecalho).toMatchObject({ campo: 'cabecalho', valor: '3', rotuloValor: 'Linha 3' });
    expect(cabecalho?.opcoes).toEqual([
      { valor: '1', rotulo: 'Linha 1' },
      { valor: '3', rotulo: 'Linha 3' },
      { valor: '4', rotulo: 'Linha 4' },
      { valor: '0', rotulo: 'Sem cabeçalho (só dados)' },
    ]);
  });

  it('JSON não tem linha de cabeçalho para escolher', () => {
    const json = { ...METADADOS_SAUDE, formato: 'json' as const, linha_cabecalho: null };

    expect(descreverDeteccoes(json, {}).map((c) => c.campo)).not.toContain('cabecalho');
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
  it('cabeçalho vira o número da linha e mantém as correções anteriores', () => {
    expect(aplicarCorrecao({ separador: ',' }, 'cabecalho', '3')).toEqual({
      separador: ',',
      linha_cabecalho: 3,
    });
    expect(aplicarCorrecao({}, 'cabecalho', '0')).toEqual({ linha_cabecalho: 0 });
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
      linha_cabecalho: 0,
    });

    expect(formulario.get('arquivo')).toBe(arquivo);
    expect(formulario.get('separador')).toBe(',');
    expect(formulario.has('decimal')).toBe(false);
    expect(formulario.get('linha_cabecalho')).toBe('0');
  });
});
