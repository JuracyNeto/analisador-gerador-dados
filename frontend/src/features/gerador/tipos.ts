import type { components } from '../../shared/api/schema';

type Schemas = components['schemas'];

export type Gerado = Schemas['Gerado'];
export type LinhaComparacao = Schemas['LinhaComparacao'];
export type PedidoUnivariado = Schemas['PedidoUnivariado'];
export type PedidoBivariado = Schemas['PedidoBivariado'];
export type ResumoOrigem = Schemas['ResumoOrigem'];
export type ResumoOrigemPar = Schemas['ResumoOrigemPar'];
export type Adotado = Schemas['Adotado'];

export type IdAba = 'univariado' | 'bivariado';
export type Origem = 'coluna' | 'manual';
export type Modo = 'preservar' | 'parametros';
export type TipoManual = 'continua' | 'discreta' | 'binaria';
