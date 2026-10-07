import { describe, expect, it } from 'vitest';
import { caminhoRelatorio, nomeArquivoRelatorio, SECOES_RELATORIO } from './api';

describe('caminhoRelatorio', () => {
  it('repete secoes e colunas e manda offline', () => {
    const caminho = caminhoRelatorio('ds1', {
      secoes: SECOES_RELATORIO,
      colunas: ['sexo', 'peso_kg'],
      offline: true,
    });

    expect(caminho).toBe(
      '/datasets/ds1/relatorio?secoes=leitura&secoes=tipos&secoes=limpeza&secoes=analises&colunas=sexo&colunas=peso_kg&offline=true',
    );
  });

  it('codifica nomes de coluna com espaço e acento', () => {
    expect(
      caminhoRelatorio('ds1', { secoes: ['analises'], colunas: ['renda média'], offline: false }),
    ).toBe('/datasets/ds1/relatorio?secoes=analises&colunas=renda+m%C3%A9dia&offline=false');
  });
});

describe('nomeArquivoRelatorio', () => {
  it.each([
    ['pesquisa_saude.txt', 'relatorio-pesquisa_saude.html'],
    ['notas.turma.csv', 'relatorio-notas.turma.html'],
    ['sem_extensao', 'relatorio-sem_extensao.html'],
  ])('%s → %s', (arquivo, esperado) => {
    expect(nomeArquivoRelatorio(arquivo)).toBe(esperado);
  });
});
