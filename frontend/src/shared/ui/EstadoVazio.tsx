import type { ReactNode } from 'react';
import estilos from './EstadoVazio.module.css';
import Icone from './Icone';

interface PropsEstadoVazio {
  icone: string;
  titulo: string;
  /** Frase com o próximo passo (spec 15). */
  descricao: string;
  acao?: ReactNode;
}

export default function EstadoVazio({
  icone,
  titulo,
  descricao,
  acao,
}: Readonly<PropsEstadoVazio>) {
  return (
    <div className={estilos.vazio}>
      <span className={estilos.circulo}>
        <Icone nome={icone} tamanho={28} />
      </span>
      <h2 className={estilos.titulo}>{titulo}</h2>
      <p className={estilos.descricao}>{descricao}</p>
      {acao === undefined ? null : <div className={estilos.acao}>{acao}</div>}
    </div>
  );
}
