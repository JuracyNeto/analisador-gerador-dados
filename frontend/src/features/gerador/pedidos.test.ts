import { describe, expect, it } from 'vitest';
import {
  type ContextoBivariado,
  type ContextoUnivariado,
  ESTADO_INICIAL_BIVARIADO,
  ESTADO_INICIAL_UNIVARIADO,
  modoUnivariado,
  montarPedidoBivariado,
  montarPedidoUnivariado,
  textoCampo,
} from './pedidos';
import { TEXTOS_GERADOR } from './textos';
import type { ResumoOrigem, ResumoOrigemPar } from './tipos';

const PESO: ResumoOrigem = {
  coluna: 'peso_kg',
  tipo: 'continua',
  n: 222,
  media: 70.2079,
  desvio: 11.397,
  minimo: 42.3,
  maximo: 98.2,
  sucesso: null,
  fracasso: null,
  chance: null,
  so_preservar: false,
};
const COM_PESO: ContextoUnivariado = { datasetId: 'ds-1', coluna: 'peso_kg', resumo: PESO };

describe('montarPedidoUnivariado', () => {
  it('preservar com origem manda só a coluna, a quantidade e a semente', () => {
    const resultado = montarPedidoUnivariado(
      { ...ESTADO_INICIAL_UNIVARIADO, semente: '42', limitar: true },
      COM_PESO,
    );

    expect(resultado).toEqual({
      ok: true,
      pedido: {
        origem: { dataset_id: 'ds-1', coluna: 'peso_kg' },
        tipo: null,
        x: 500,
        modo: 'preservar',
        media: null,
        desvio: null,
        p: null,
        semente: 42,
        limitar_faixa: true,
      },
    });
  });

  it('novos parâmetros sem edição usam os valores exatos da origem', () => {
    const resultado = montarPedidoUnivariado(
      { ...ESTADO_INICIAL_UNIVARIADO, modo: 'parametros' },
      COM_PESO,
    );

    expect(resultado.ok && resultado.pedido).toMatchObject({ media: 70.2079, desvio: 11.397 });
  });

  it('erros por campo', () => {
    const resultado = montarPedidoUnivariado(
      { ...ESTADO_INICIAL_UNIVARIADO, modo: 'parametros', quantidade: '0', desvio: '0' },
      COM_PESO,
    );

    expect(resultado).toEqual({
      ok: false,
      erros: { quantidade: TEXTOS_GERADOR.erros.quantidade, desvio: TEXTOS_GERADOR.erros.desvio },
    });
  });

  it('sem dataset, só parâmetros manuais com o tipo escolhido', () => {
    const contexto: ContextoUnivariado = { datasetId: null, coluna: null, resumo: undefined };
    const estado = { ...ESTADO_INICIAL_UNIVARIADO, tipoManual: 'binaria' as const, chance: '0,3' };

    expect(modoUnivariado(estado, contexto)).toBe('parametros');
    expect(montarPedidoUnivariado(estado, contexto)).toMatchObject({
      ok: true,
      pedido: { origem: null, tipo: 'binaria', modo: 'parametros', p: 0.3, limitar_faixa: false },
    });
  });

  it('coluna que só preserva força o modo preservar', () => {
    const cidade = { ...PESO, tipo: 'nominal' as const, so_preservar: true, media: null };
    const contexto = { ...COM_PESO, resumo: cidade };

    expect(modoUnivariado({ ...ESTADO_INICIAL_UNIVARIADO, modo: 'parametros' }, contexto)).toBe(
      'preservar',
    );
  });
});

const PAR: ResumoOrigemPar = {
  x: 'altura_m',
  y: 'peso_kg',
  n: 218,
  media_x: 1.686,
  media_y: 70.167,
  desvio_x: 0.0931,
  desvio_y: 11.41,
  r: 0.7019,
};
const COM_PAR: ContextoBivariado = { datasetId: 'ds-1', x: 'altura_m', y: 'peso_kg', par: PAR };

describe('montarPedidoBivariado', () => {
  it('com origem, só o que foi editado vai no pedido', () => {
    const resultado = montarPedidoBivariado(
      { ...ESTADO_INICIAL_BIVARIADO, mediaX: '1,7', rho: 0.5 },
      COM_PAR,
    );

    expect(resultado).toEqual({
      ok: true,
      pedido: {
        origem: { dataset_id: 'ds-1', x: 'altura_m', y: 'peso_kg' },
        n: 500,
        media_x: 1.7,
        media_y: null,
        desvio_x: null,
        desvio_y: null,
        rho: 0.5,
        ajuste_exato: true,
        semente: null,
      },
    });
  });

  it('sem origem, médias e desvios são obrigatórios e ρ começa em 0', () => {
    const contexto: ContextoBivariado = { datasetId: 'ds-1', x: null, y: null, par: undefined };
    const estado = { ...ESTADO_INICIAL_BIVARIADO, origem: 'manual' as const };

    expect(montarPedidoBivariado(estado, contexto)).toEqual({
      ok: false,
      erros: {
        mediaX: TEXTOS_GERADOR.erros.numero,
        mediaY: TEXTOS_GERADOR.erros.numero,
        desvioX: TEXTOS_GERADOR.erros.numero,
        desvioY: TEXTOS_GERADOR.erros.numero,
      },
    });
    const preenchido = { ...estado, mediaX: '0', mediaY: '0', desvioX: '1', desvioY: '1' };
    expect(montarPedidoBivariado(preenchido, contexto)).toMatchObject({
      ok: true,
      pedido: { origem: null, rho: 0 },
    });
  });
});

describe('textoCampo', () => {
  it('mostra o digitado ou o valor da origem formatado', () => {
    expect(textoCampo(null, -0.5)).toBe('−0,5');
    expect(textoCampo('7', 1)).toBe('7');
    expect(textoCampo(null, null)).toBe('');
  });
});
