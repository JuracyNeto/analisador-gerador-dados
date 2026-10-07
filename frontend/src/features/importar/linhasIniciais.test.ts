import { describe, expect, it } from 'vitest';
import { METADADOS_COM_TITULO, METADADOS_SAUDE } from '../../testes/fixtures/datasets';
import { descreverLinhasIniciais } from './linhasIniciais';

describe('descreverLinhasIniciais', () => {
  it('marca o que fica de fora, o cabeçalho e os dados, com a mesma largura', () => {
    const inicio = descreverLinhasIniciais(METADADOS_COM_TITULO);

    expect(inicio?.largura).toBe(2);
    expect(inicio?.linhas).toEqual([
      { numero: 1, celulas: ['Pesquisa de satisfação', ''], papel: 'fora' },
      { numero: 2, celulas: ['', ''], papel: 'fora' },
      { numero: 3, celulas: ['nome', 'nota'], papel: 'cabecalho' },
      { numero: 4, celulas: ['Ana', '8.5'], papel: 'dados' },
    ]);
  });

  it('sem cabeçalho, todas as linhas são dados', () => {
    const inicio = descreverLinhasIniciais({ ...METADADOS_SAUDE, linha_cabecalho: 0 });

    expect(inicio?.linhas.map((linha) => linha.papel)).toEqual(['dados', 'dados', 'dados']);
  });

  it('JSON (sem linhas do arquivo) não mostra o início', () => {
    expect(descreverLinhasIniciais({ ...METADADOS_SAUDE, linhas_iniciais: [] })).toBeNull();
    expect(descreverLinhasIniciais({ ...METADADOS_SAUDE, linha_cabecalho: null })).toBeNull();
  });
});
