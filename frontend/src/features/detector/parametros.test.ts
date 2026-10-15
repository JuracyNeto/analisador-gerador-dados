import { describe, expect, it } from 'vitest';
import { escreverParametros, lerParametros, TODAS_SEVERIDADES } from './parametros';

describe('lerParametros', () => {
  it('sem nada na URL: todas as severidades e agrupado por coluna', () => {
    expect(lerParametros(new URLSearchParams())).toEqual({
      severidades: TODAS_SEVERIDADES,
      agrupar: 'coluna',
    });
  });

  it('lê as severidades marcadas e o agrupamento', () => {
    const lidos = lerParametros(new URLSearchParams('sev=alta&sev=atencao&agrupar=regra'));

    expect([...lidos.severidades]).toEqual(['alta', 'atencao']);
    expect(lidos.agrupar).toBe('regra');
  });

  it('"sev=" vazio quer dizer nenhuma severidade marcada', () => {
    expect(lerParametros(new URLSearchParams('sev=')).severidades.size).toBe(0);
  });

  it.each([
    ['sev=xyz&agrupar=tabela', ['alta', 'atencao', 'info'], 'coluna'],
    ['sev=info&sev=xyz', ['info'], 'coluna'],
  ])('valores inválidos caem no padrão: %s', (busca, severidades, agrupar) => {
    const lidos = lerParametros(new URLSearchParams(busca));

    expect([...lidos.severidades]).toEqual(severidades);
    expect(lidos.agrupar).toBe(agrupar);
  });
});

describe('escreverParametros', () => {
  it('o padrão não aparece na URL e os outros parâmetros ficam', () => {
    const busca = escreverParametros(new URLSearchParams('sev=alta&agrupar=regra&x=1'), {
      severidades: TODAS_SEVERIDADES,
      agrupar: 'coluna',
    });

    expect(busca.toString()).toBe('x=1');
  });

  it('grava as marcadas na ordem das severidades, ou "sev=" sem nenhuma', () => {
    const algumas = escreverParametros(new URLSearchParams(), {
      severidades: new Set(['info', 'alta'] as const),
      agrupar: 'regra',
    });
    const nenhuma = escreverParametros(new URLSearchParams(), {
      severidades: new Set(),
      agrupar: 'coluna',
    });

    expect(algumas.toString()).toBe('sev=alta&sev=info&agrupar=regra');
    expect(nenhuma.toString()).toBe('sev=');
  });

  it('ler o que foi escrito devolve o mesmo filtro', () => {
    const filtros = { severidades: new Set(['atencao'] as const), agrupar: 'regra' as const };

    expect(lerParametros(escreverParametros(new URLSearchParams(), filtros))).toEqual(filtros);
  });
});
