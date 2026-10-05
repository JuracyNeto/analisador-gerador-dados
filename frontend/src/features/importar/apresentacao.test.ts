import { describe, expect, it } from 'vitest';
import { ErroApi } from '../../shared/api/cliente';
import { LINHAS_SAUDE } from '../../testes/fixtures/datasets';
import { colunasDaPrevia, descreverErroImportacao } from './apresentacao';

describe('colunasDaPrevia', () => {
  it('mantém a ordem do arquivo e alinha à direita colunas com números', () => {
    const colunas = colunasDaPrevia(LINHAS_SAUDE);

    expect(colunas.map((c) => c.nome)).toEqual([
      'id',
      'sexo',
      'idade',
      'altura_m',
      'peso_kg',
      'escolaridade',
      'cidade',
      'satisfacao',
    ]);
    expect(colunas.filter((c) => c.numerica).map((c) => c.nome)).toEqual([
      'id',
      'idade',
      'altura_m',
      'peso_kg',
    ]);
  });

  it('sem linhas, sem colunas', () => {
    expect(colunasDaPrevia([])).toEqual([]);
  });
});

describe('descreverErroImportacao', () => {
  it('erro de leitura (4xx) cita o arquivo no título', () => {
    const erro = new ErroApi(400, {
      codigo: 'FORMATO_NAO_SUPORTADO',
      mensagem: 'Este tipo de arquivo não é aceito. Use TXT, CSV, TSV, XLSX ou JSON.',
      sugestao: 'Salve como CSV e envie de novo.',
    });

    expect(descreverErroImportacao(erro, 'relatorio_final.pdf')).toEqual({
      titulo: 'Não conseguimos ler este arquivo: relatorio_final.pdf',
      texto:
        'Este tipo de arquivo não é aceito. Use TXT, CSV, TSV, XLSX ou JSON. Salve como CSV e envie de novo.',
    });
  });

  it('sem conexão usa a mensagem como título', () => {
    const erro = new ErroApi(0, {
      codigo: 'SEM_CONEXAO',
      mensagem: 'Não conseguimos falar com o servidor.',
      sugestao: 'Verifique se o backend está rodando e tente novamente.',
    });

    expect(descreverErroImportacao(erro, 'a.csv').titulo).toBe(
      'Não conseguimos falar com o servidor.',
    );
  });
});
