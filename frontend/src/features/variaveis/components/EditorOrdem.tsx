import { useEffect, useId, useRef, useState } from 'react';
import type { TipoColuna } from '../../../shared/api/dataset';
import Card from '../../../shared/ui/Card';
import ChipTipo from '../../../shared/ui/ChipTipo';
import { moverItem } from '../regras';
import { TEXTOS_VARIAVEIS as T } from '../textos';
import estilos from './EditorOrdem.module.css';
import ItemOrdem, { type Controle } from './ItemOrdem';

interface PropsEditorOrdem {
  coluna: TipoColuna;
  aoReordenar: (categorias: string[]) => void;
}

interface Foco {
  nome: string;
  controle: Controle;
}

/** Ordem, arraste, foco depois de mover e anúncio da nova posição (D62). */
function useEditorOrdem(
  categorias: readonly string[],
  aoReordenar: (categorias: string[]) => void,
) {
  const [arrastando, setArrastando] = useState<string | null>(null);
  const [anuncio, setAnuncio] = useState('');
  const controles = useRef(new Map<string, HTMLButtonElement>());
  const focoPendente = useRef<Foco | null>(null);

  // Reordenar move nós do DOM e o foco se perde; devolve ao controle usado quando a nova ordem chega.
  useEffect(() => {
    const alvo = focoPendente.current;
    focoPendente.current = null;
    if (alvo === null) return;
    const botao = controles.current.get(`${alvo.nome}:${alvo.controle}`);
    const destino = botao && !botao.disabled ? botao : controles.current.get(`${alvo.nome}:alca`);
    destino?.focus();
  }, [categorias]);

  function mover(de: number, para: number, controle: Controle): void {
    const nova = moverItem(categorias, de, para);
    const nome = categorias[de];
    if (nova === null || nome === undefined) return;
    focoPendente.current = { nome, controle };
    setAnuncio(T.ordem.anuncio(nome, para + 1, categorias.length));
    aoReordenar(nova);
  }

  function soltarEm(alvo: number): void {
    const de = arrastando === null ? -1 : categorias.indexOf(arrastando);
    setArrastando(null);
    mover(de, alvo, 'alca');
  }

  const registrar = (nome: string) => (controle: Controle, elemento: HTMLButtonElement | null) => {
    const chave = `${nome}:${controle}`;
    if (elemento === null) controles.current.delete(chave);
    else controles.current.set(chave, elemento);
  };

  return { arrastando, setArrastando, anuncio, mover, soltarEm, registrar };
}

/** Card "Ordem das categorias · {coluna}" (2a, D62). */
export default function EditorOrdem({ coluna, aoReordenar }: Readonly<PropsEditorOrdem>) {
  const categorias = coluna.categorias_ordem;
  const idInstrucao = useId();
  const { arrastando, setArrastando, anuncio, mover, soltarEm, registrar } = useEditorOrdem(
    categorias,
    aoReordenar,
  );

  const titulo = (
    <>
      {T.ordem.titulo} · <span className={estilos.mono}>{coluna.coluna}</span>
    </>
  );

  return (
    <Card titulo={titulo} acoes={<ChipTipo tipo="ordinal" curto />}>
      <p id={idInstrucao} className={estilos.instrucao}>
        {T.ordem.instrucao}
      </p>
      <ol className={estilos.lista} aria-label={T.ordem.rotuloLista(coluna.coluna)}>
        {categorias.map((nome, indice) => (
          <ItemOrdem
            key={nome}
            nome={nome}
            posicao={indice + 1}
            total={categorias.length}
            quantidade={coluna.contagens[nome] ?? 0}
            arrastando={arrastando === nome}
            idInstrucao={idInstrucao}
            registrar={registrar(nome)}
            aoMover={(passo, controle) => {
              mover(indice, indice + passo, controle);
            }}
            aoIniciarArraste={() => {
              setArrastando(nome);
            }}
            aoSoltar={() => {
              soltarEm(indice);
            }}
            aoTerminarArraste={() => {
              setArrastando(null);
            }}
          />
        ))}
      </ol>
      <p className={estilos.escala}>{categorias.join(' < ')}</p>
      <p className={estilos.somenteLeitor} aria-live="polite">
        {anuncio}
      </p>
    </Card>
  );
}
