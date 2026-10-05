import type { ButtonHTMLAttributes, ReactNode } from 'react';
import { juntarClasses } from '../lib/classes';
import estilos from './Botao.module.css';
import Icone from './Icone';

type VarianteBotao = 'primario' | 'secundario' | 'fantasma' | 'perigo';
type TamanhoBotao = 'sm' | 'md' | 'lg';

const TAMANHO_ICONE = { sm: 18, md: 18, lg: 20 } as const satisfies Record<TamanhoBotao, number>;

interface PropsBotao extends ButtonHTMLAttributes<HTMLButtonElement> {
  variante?: VarianteBotao;
  tamanho?: TamanhoBotao;
  icone?: string | undefined;
  iconeFinal?: string | undefined;
  carregando?: boolean;
  textoCarregando?: string | undefined;
}

export default function Botao({
  variante = 'primario',
  tamanho = 'md',
  icone,
  iconeFinal,
  carregando = false,
  textoCarregando,
  className,
  disabled,
  children,
  ...resto
}: Readonly<PropsBotao>) {
  return (
    <button
      type="button"
      {...resto}
      className={juntarClasses(estilos.botao, estilos[tamanho], estilos[variante], className)}
      disabled={disabled === true || carregando}
      aria-busy={carregando}
    >
      <ConteudoBotao
        carregando={carregando}
        textoCarregando={textoCarregando}
        icone={icone}
        iconeFinal={iconeFinal}
        tamanhoIcone={TAMANHO_ICONE[tamanho]}
      >
        {children}
      </ConteudoBotao>
    </button>
  );
}

interface PropsConteudoBotao {
  carregando: boolean;
  textoCarregando: string | undefined;
  icone: string | undefined;
  iconeFinal: string | undefined;
  tamanhoIcone: number;
  children: ReactNode;
}

function ConteudoBotao({
  carregando,
  textoCarregando,
  icone,
  iconeFinal,
  tamanhoIcone,
  children,
}: Readonly<PropsConteudoBotao>) {
  if (carregando) {
    return (
      <>
        <span className={estilos.spinner} aria-hidden="true" />
        {textoCarregando ?? children}
      </>
    );
  }
  return (
    <>
      {icone ? <Icone nome={icone} tamanho={tamanhoIcone} /> : null}
      {children}
      {iconeFinal ? <Icone nome={iconeFinal} tamanho={tamanhoIcone} /> : null}
    </>
  );
}
