import { describe, expect, it } from 'vitest';
import { criarEntradaLog } from '../../testes/fixtures/limpeza';
import {
  descreverLinhas,
  descreverOcorrencias,
  detalheDoLog,
  listarNumeros,
  primeiraMaiuscula,
} from './descricoes';

describe('descricoes', () => {
  it('lista até 5 números e resume o resto', () => {
    expect(listarNumeros([12, 141, 207])).toBe('12, 141, 207');
    expect(listarNumeros([1, 2, 3, 4, 5, 6, 7])).toBe('1, 2, 3, 4, 5 e mais 2');
  });

  it('descreve linhas no singular e no plural', () => {
    expect(descreverLinhas([88])).toBe('linha 88');
    expect(descreverLinhas([45, 46, 47])).toBe('linhas 45, 46, 47');
    expect(primeiraMaiuscula('linha 44')).toBe('Linha 44');
  });

  it('descreve ocorrências com linhas e valores em pt-BR', () => {
    expect(descreverOcorrencias([{ linha: 77, valor: 17.2 }])).toBe('Linha 77: 17,2');
    expect(
      descreverOcorrencias([
        { linha: 19, valor: 0 },
        { linha: 201, valor: 230 },
      ]),
    ).toBe('Linhas 19 e 201: 0 e 230');
  });

  it('separa valores decimais com ponto e vírgula (a vírgula já é o decimal)', () => {
    expect(
      descreverOcorrencias([
        { linha: 99, valor: 6.8 },
        { linha: 106, valor: 106.4 },
        { linha: 160, valor: 712 },
        { linha: 161, valor: 800 },
      ]),
    ).toBe('Linhas 99, 106 e 160: 6,8; 106,4 e 712 e mais 1');
  });

  it('detalhe do log junta linhas e antes → depois', () => {
    expect(detalheDoLog(criarEntradaLog())).toBe('linhas 45, 46, 47');
    expect(
      detalheDoLog(
        criarEntradaLog({ linhas_afetadas: [77], antes_exemplo: '17,2', depois_exemplo: '1,72' }),
      ),
    ).toBe('linha 77 · 17,2 → 1,72');
  });
});
