import { useCallback, useEffect, useState } from 'react';
import { juntarClasses } from '../lib/classes';
import Botao from './Botao';
import type { ToastAtivo } from './contextoToast';
import Icone from './Icone';
import { TEXTOS_UI } from './textos';
import estilos from './Toast.module.css';

const DURACAO_MS = 6000;

function useTemporizador(duracaoMs: number, aoTerminar: () => void) {
  const [pausado, setPausado] = useState(false);
  useEffect(() => {
    if (pausado) return undefined;
    const temporizador = window.setTimeout(aoTerminar, duracaoMs);
    return () => {
      window.clearTimeout(temporizador);
    };
  }, [pausado, duracaoMs, aoTerminar]);
  const pausar = useCallback(() => {
    setPausado(true);
  }, []);
  const retomar = useCallback(() => {
    setPausado(false);
  }, []);
  return { pausar, retomar };
}

interface PropsItemToast {
  toast: ToastAtivo;
  aoRemover: (id: number) => void;
}

export default function ItemToast({ toast, aoRemover }: Readonly<PropsItemToast>) {
  const { id, tipo, titulo, descricao, acao } = toast;
  const fechar = useCallback(() => {
    aoRemover(id);
  }, [aoRemover, id]);
  const { pausar, retomar } = useTemporizador(DURACAO_MS, fechar);

  return (
    <div
      role={tipo === 'erro' ? 'alert' : 'status'}
      className={juntarClasses(estilos.toast, estilos[tipo])}
      onMouseEnter={pausar}
      onMouseLeave={retomar}
      onFocus={pausar}
      onBlur={retomar}
    >
      <Icone
        nome={tipo === 'erro' ? 'error' : 'check_circle'}
        preenchido
        tamanho={22}
        className={estilos.icone}
      />
      <div className={estilos.texto}>
        <p className={estilos.titulo}>{titulo}</p>
        {descricao ? <p className={estilos.descricao}>{descricao}</p> : null}
        {acao ? (
          <Botao
            variante="fantasma"
            tamanho="sm"
            className={estilos.acao}
            onClick={() => {
              acao.aoClicar();
              fechar();
            }}
          >
            {acao.rotulo}
          </Botao>
        ) : null}
      </div>
      <button
        type="button"
        className={estilos.fechar}
        aria-label={TEXTOS_UI.fecharAviso}
        onClick={fechar}
      >
        <Icone nome="close" tamanho={20} />
      </button>
    </div>
  );
}
