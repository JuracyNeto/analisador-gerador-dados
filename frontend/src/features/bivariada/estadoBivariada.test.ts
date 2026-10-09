import { describe, expect, it } from 'vitest';
import { ErroApi } from '../../shared/api/cliente';
import { consultaFalsa } from '../../testes/consultaFalsa';
import { bivariadaAlturaPeso, colunasBivariada } from '../../testes/fixtures/bivariada';
import { estadoDaBivariada } from './estadoBivariada';
import type { Bivariada, TipoColuna } from './tipos';

const COLUNAS = consultaFalsa<TipoColuna[]>({ status: 'success', data: colunasBivariada });
const PAR = { x: 'altura_m', y: 'peso_kg' };

describe('estadoDaBivariada', () => {
  it('carrega as colunas, depois calcula o par, depois mostra', () => {
    expect(estadoDaBivariada(consultaFalsa({}), consultaFalsa({}), null).status).toBe(
      'carregando-colunas',
    );
    expect(estadoDaBivariada(COLUNAS, consultaFalsa({}), PAR)).toEqual({
      status: 'calculando',
      par: PAR,
    });
    expect(
      estadoDaBivariada(
        COLUNAS,
        consultaFalsa<Bivariada>({ status: 'success', data: bivariadaAlturaPeso }),
        PAR,
      ),
    ).toEqual({ status: 'pronta', bivariada: bivariadaAlturaPeso });
  });

  it('sem par (menos de 2 numéricas) mostra o vazio', () => {
    expect(estadoDaBivariada(COLUNAS, consultaFalsa({}), null).status).toBe('poucas-colunas');
  });

  it('erro definitivo da API não oferece "Tentar de novo"; erro de rede oferece', () => {
    const poucos = new ErroApi(400, { codigo: 'POUCOS_PARES', mensagem: 'x', sugestao: 'y' });
    const rede = new ErroApi(0, { codigo: 'SEM_CONEXAO', mensagem: 'x', sugestao: 'y' });

    const definitivo = estadoDaBivariada(
      COLUNAS,
      consultaFalsa({ status: 'error', error: poucos }),
      PAR,
    );
    const repetivel = estadoDaBivariada(
      COLUNAS,
      consultaFalsa({ status: 'error', error: rede }),
      PAR,
    );

    expect(definitivo.status === 'erro' && definitivo.tentarDeNovo).toBeNull();
    expect(repetivel.status === 'erro' && typeof repetivel.tentarDeNovo).toBe('function');
  });
});
