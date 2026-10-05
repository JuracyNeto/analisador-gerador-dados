import { createContext } from 'react';
import type { ValorSessao } from './tipos';

export const ContextoSessao = createContext<ValorSessao | null>(null);
