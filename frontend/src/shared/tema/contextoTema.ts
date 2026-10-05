import { createContext } from 'react';
import type { ValorTema } from './tipos';

export const ContextoTema = createContext<ValorTema | null>(null);
