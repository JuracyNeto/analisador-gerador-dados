import type { ReactNode } from 'react';
import { juntarClasses } from '../lib/classes';
import estilos from './Card.module.css';

type Preenchimento = 'normal' | 'nenhum';

interface PropsCard {
  titulo?: ReactNode;
  subtitulo?: ReactNode;
  acoes?: ReactNode;
  preenchimento?: Preenchimento;
  children: ReactNode;
}

export default function Card({
  titulo,
  subtitulo,
  acoes,
  preenchimento = 'normal',
  children,
}: Readonly<PropsCard>) {
  const temCabecalho = titulo !== undefined || acoes !== undefined;
  return (
    <section className={estilos.card}>
      {temCabecalho ? <CabecalhoCard titulo={titulo} subtitulo={subtitulo} acoes={acoes} /> : null}
      <div
        className={juntarClasses(estilos.corpo, preenchimento === 'nenhum' && estilos.semEspaco)}
      >
        {children}
      </div>
    </section>
  );
}

interface PropsCabecalhoCard {
  titulo: ReactNode;
  subtitulo: ReactNode;
  acoes: ReactNode;
}

function CabecalhoCard({ titulo, subtitulo, acoes }: Readonly<PropsCabecalhoCard>) {
  return (
    <header className={estilos.cabecalho}>
      <div className={estilos.textos}>
        {titulo === undefined ? null : <h2 className={estilos.titulo}>{titulo}</h2>}
        {subtitulo === undefined ? null : <p className={estilos.subtitulo}>{subtitulo}</p>}
      </div>
      {acoes === undefined ? null : <div className={estilos.acoes}>{acoes}</div>}
    </header>
  );
}
