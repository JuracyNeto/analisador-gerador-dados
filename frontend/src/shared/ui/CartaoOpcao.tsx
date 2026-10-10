import { type ReactNode, useId } from 'react';
import { juntarClasses } from '../lib/classes';
import estilos from './CartaoOpcao.module.css';

interface PropsCartaoOpcao {
  /** Mesmo `nome` para os cartões do grupo (input radio nativo: setas trocam a opção). */
  nome: string;
  titulo: string;
  descricao?: ReactNode;
  selecionado: boolean;
  aoSelecionar: () => void;
  desabilitado?: boolean;
  /** Campos do cartão (ex.: média e desvio); quem usa os desabilita quando não selecionado. */
  children?: ReactNode;
}

/** Rádio em cartão (tela 6a, Modo): selecionado com borda 2 primária e fundo primária-suave. */
export default function CartaoOpcao({
  nome,
  titulo,
  descricao,
  selecionado,
  aoSelecionar,
  desabilitado = false,
  children,
}: Readonly<PropsCartaoOpcao>) {
  const id = useId();
  const idDescricao = `${id}-descricao`;
  return (
    <div
      className={juntarClasses(
        estilos.cartao,
        selecionado && estilos.selecionado,
        desabilitado && estilos.desabilitado,
      )}
    >
      <label className={estilos.cabecalho}>
        <input
          type="radio"
          name={nome}
          className={estilos.entrada}
          checked={selecionado}
          disabled={desabilitado}
          aria-describedby={descricao ? idDescricao : undefined}
          onChange={aoSelecionar}
        />
        <span className={estilos.marca} aria-hidden="true" />
        <span className={estilos.titulo}>{titulo}</span>
      </label>
      {descricao ? (
        <p id={idDescricao} className={estilos.descricao}>
          {descricao}
        </p>
      ) : null}
      {children ? <div className={estilos.campos}>{children}</div> : null}
    </div>
  );
}
