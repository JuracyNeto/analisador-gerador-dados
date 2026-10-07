import type { DragEvent, KeyboardEvent } from 'react';
import { contarLinhas } from '../../../shared/lib/pluralizar';
import Icone from '../../../shared/ui/Icone';
import { TEXTOS_VARIAVEIS as T } from '../textos';
import estilos from './EditorOrdem.module.css';

export type Controle = 'alca' | 'subir' | 'descer';
type Passo = -1 | 1;

export interface PropsItemOrdem {
  nome: string;
  posicao: number;
  total: number;
  quantidade: number;
  arrastando: boolean;
  idInstrucao: string;
  registrar: (controle: Controle, elemento: HTMLButtonElement | null) => void;
  aoMover: (passo: Passo, controle: Controle) => void;
  aoIniciarArraste: () => void;
  aoSoltar: () => void;
  aoTerminarArraste: () => void;
}

const PASSO_POR_TECLA: Partial<Record<string, Passo>> = { ArrowUp: -1, ArrowDown: 1 };

function permitirSoltar(evento: DragEvent<HTMLLIElement>): void {
  evento.preventDefault();
}

function BotoesMover({ nome, posicao, total, registrar, aoMover }: Readonly<PropsItemOrdem>) {
  return (
    <span className={estilos.botoes}>
      <button
        type="button"
        className={estilos.botaoIcone}
        ref={(el) => {
          registrar('subir', el);
        }}
        aria-label={T.ordem.subir(nome)}
        disabled={posicao === 1}
        onClick={() => {
          aoMover(-1, 'subir');
        }}
      >
        <Icone nome="arrow_upward" tamanho={18} />
      </button>
      <button
        type="button"
        className={estilos.botaoIcone}
        ref={(el) => {
          registrar('descer', el);
        }}
        aria-label={T.ordem.descer(nome)}
        disabled={posicao === total}
        onClick={() => {
          aoMover(1, 'descer');
        }}
      >
        <Icone nome="arrow_downward" tamanho={18} />
      </button>
    </span>
  );
}

export default function ItemOrdem(props: Readonly<PropsItemOrdem>) {
  const { nome, posicao, quantidade, arrastando, idInstrucao, registrar, aoMover } = props;

  function aoIniciar(evento: DragEvent<HTMLLIElement>): void {
    evento.dataTransfer.effectAllowed = 'move';
    evento.dataTransfer.setData('text/plain', nome); // Firefox só arrasta com dado
    props.aoIniciarArraste();
  }

  function aoSoltarAqui(evento: DragEvent<HTMLLIElement>): void {
    evento.preventDefault();
    props.aoSoltar();
  }

  function aoTeclar(evento: KeyboardEvent<HTMLButtonElement>): void {
    const passo = PASSO_POR_TECLA[evento.key];
    if (passo === undefined) return;
    evento.preventDefault();
    aoMover(passo, 'alca');
  }

  return (
    <li
      className={estilos.item}
      data-arrastando={arrastando}
      draggable
      onDragStart={aoIniciar}
      onDragOver={permitirSoltar}
      onDrop={aoSoltarAqui}
      onDragEnd={props.aoTerminarArraste}
    >
      <button
        type="button"
        className={estilos.alca}
        ref={(el) => {
          registrar('alca', el);
        }}
        aria-label={T.ordem.mover(nome)}
        aria-describedby={idInstrucao}
        onKeyDown={aoTeclar}
      >
        <Icone nome="drag_indicator" tamanho={20} />
      </button>
      <span className={estilos.posicao}>{posicao}</span>
      <span className={estilos.nome}>{nome}</span>
      {arrastando ? (
        <span className={estilos.movendo}>{T.ordem.movendo}</span>
      ) : (
        <span className={estilos.quantidade}>{contarLinhas(quantidade)}</span>
      )}
      <BotoesMover {...props} />
    </li>
  );
}
