import '@fontsource/inter/400.css';
import '@fontsource/inter/500.css';
import '@fontsource/inter/600.css';
import '@fontsource/inter/700.css';
import '@fontsource/jetbrains-mono/400.css';
import '@fontsource/jetbrains-mono/500.css';
import '@fontsource/jetbrains-mono/600.css';
import '@fontsource-variable/material-symbols-rounded/full.css';
import './shared/ui/tokens.css';
import './shared/ui/base.css';
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './app/App';
import { aplicarTemaInicial } from './shared/tema/preferencia';

aplicarTemaInicial();

const raiz = document.getElementById('root');
if (!raiz) throw new Error('Elemento #root não encontrado em index.html');

createRoot(raiz).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
