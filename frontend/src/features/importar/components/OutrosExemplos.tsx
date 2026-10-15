import { useId } from 'react';
import { useExemplos } from '../api';
import { NOME_EXEMPLO, TEXTOS_IMPORTAR as T } from '../textos';
import BotaoLink from './BotaoLink';
import estilos from './OutrosExemplos.module.css';

/** Demais arquivos de demonstração (detector, M3.4); sem resposta da API, a lista não aparece. */
export default function OutrosExemplos({
  aoEscolher,
}: Readonly<{ aoEscolher: (arquivo: string) => void }>) {
  const idTitulo = useId();
  const outros = (useExemplos().data ?? []).filter((exemplo) => exemplo.arquivo !== NOME_EXEMPLO);
  if (outros.length === 0) return null;
  return (
    <div className={estilos.outros}>
      <p id={idTitulo} className={estilos.titulo}>
        {T.exemplo.outros}
      </p>
      <ul aria-labelledby={idTitulo} className={estilos.lista}>
        {outros.map((exemplo) => (
          <li key={exemplo.arquivo}>
            <BotaoLink
              onClick={() => {
                aoEscolher(exemplo.arquivo);
              }}
            >
              <span className={estilos.arquivo}>{exemplo.arquivo}</span>
            </BotaoLink>
            {T.exemplo.separador}
            {exemplo.descricao}
          </li>
        ))}
      </ul>
    </div>
  );
}
