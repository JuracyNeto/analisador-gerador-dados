import { type ReactNode, type RefObject, useEffect, useId, useRef } from 'react';
import { createPortal } from 'react-dom';
import { useTeclaEsc } from '../lib/useTeclaEsc';
import estilos from './Drawer.module.css';
import Icone from './Icone';
import { TEXTOS_UI } from './textos';

const SELETOR_FOCAVEL = [
  'a[href]',
  'button:not([disabled])',
  'input:not([disabled])',
  'select:not([disabled])',
  'textarea:not([disabled])',
  '[tabindex]:not([tabindex="-1"])',
].join(',');

/** Tab e Shift+Tab circulam dentro do painel (foco preso). */
function prenderFoco(evento: KeyboardEvent, painel: HTMLElement | null): void {
  if (evento.key !== 'Tab' || painel === null) return;
  const focaveis = Array.from(painel.querySelectorAll<HTMLElement>(SELETOR_FOCAVEL));
  const primeiro = focaveis[0];
  const ultimo = focaveis.at(-1);
  if (primeiro === undefined || ultimo === undefined) return;
  const limite = evento.shiftKey ? primeiro : ultimo;
  if (document.activeElement !== limite) return;
  evento.preventDefault();
  (evento.shiftKey ? ultimo : primeiro).focus();
}

interface RefsDrawer {
  painel: RefObject<HTMLElement | null>;
  fechar: RefObject<HTMLButtonElement | null>;
}

/** Ao abrir: foco no Fechar, Tab preso e página sem rolar; ao fechar, o foco volta a quem abriu. */
function useFocoDoDrawer(aberto: boolean, { painel, fechar }: RefsDrawer): void {
  useEffect(() => {
    if (!aberto) return undefined;
    const anterior = document.activeElement instanceof HTMLElement ? document.activeElement : null;
    const rolagem = document.body.style.overflow;
    const aoTeclar = (evento: KeyboardEvent): void => {
      prenderFoco(evento, painel.current);
    };
    document.body.style.overflow = 'hidden';
    document.addEventListener('keydown', aoTeclar);
    fechar.current?.focus();
    return () => {
      document.removeEventListener('keydown', aoTeclar);
      document.body.style.overflow = rolagem;
      anterior?.focus();
    };
  }, [aberto, painel, fechar]);
}

interface PropsCabecalho {
  idTitulo: string;
  titulo: ReactNode;
  topo?: ReactNode;
  subtitulo?: ReactNode;
  aoFechar: () => void;
  ref: RefObject<HTMLButtonElement | null>;
}

function CabecalhoDrawer({
  idTitulo,
  titulo,
  topo,
  subtitulo,
  aoFechar,
  ref,
}: Readonly<PropsCabecalho>) {
  return (
    <header className={estilos.cabecalho}>
      <div className={estilos.textos}>
        {topo}
        <h2 id={idTitulo} className={estilos.titulo}>
          {titulo}
        </h2>
        {subtitulo === undefined ? null : <p className={estilos.subtitulo}>{subtitulo}</p>}
      </div>
      <button
        ref={ref}
        type="button"
        className={estilos.fechar}
        aria-label={TEXTOS_UI.fechar}
        onClick={aoFechar}
      >
        <Icone nome="close" tamanho={22} />
      </button>
    </header>
  );
}

interface PropsDrawer extends Omit<PropsCabecalho, 'idTitulo' | 'ref'> {
  aberto: boolean;
  /** Nome da região rolável do corpo (fica focável para rolar pelo teclado). */
  rotuloCorpo?: string;
  rodape?: ReactNode;
  children: ReactNode;
}

/** Painel lateral direito com fundo escurecido (componentes.md §Drawer, tela 7b). */
export default function Drawer({
  aberto,
  rotuloCorpo,
  rodape,
  children,
  ...cabecalho
}: Readonly<PropsDrawer>) {
  const idTitulo = useId();
  const painel = useRef<HTMLElement>(null);
  const fechar = useRef<HTMLButtonElement>(null);
  useFocoDoDrawer(aberto, { painel, fechar });
  useTeclaEsc(aberto, cabecalho.aoFechar);
  if (!aberto) return null;
  return createPortal(
    <>
      {/* Clicar fora fecha; fora da ordem do Tab e escondido dos leitores (o Fechar e o Esc bastam). */}
      <button
        type="button"
        tabIndex={-1}
        aria-hidden="true"
        className={estilos.fundo}
        data-testid="fundo-drawer"
        onClick={cabecalho.aoFechar}
      />
      <aside
        ref={painel}
        role="dialog"
        aria-modal="true"
        aria-labelledby={idTitulo}
        className={estilos.drawer}
      >
        <CabecalhoDrawer {...cabecalho} idTitulo={idTitulo} ref={fechar} />
        <div
          className={estilos.corpo}
          role={rotuloCorpo === undefined ? undefined : 'region'}
          aria-label={rotuloCorpo}
          tabIndex={rotuloCorpo === undefined ? undefined : 0}
        >
          {children}
        </div>
        {rodape === undefined ? null : <footer className={estilos.rodape}>{rodape}</footer>}
      </aside>
    </>,
    document.body,
  );
}
