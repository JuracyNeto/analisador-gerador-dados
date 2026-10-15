import Icone from '../../../shared/ui/Icone';
import { ORDEM_SEVERIDADES, SEVERIDADES, corDaSeveridade } from '../../../shared/ui/severidades';
import { TEXTOS_DETECTOR as T } from '../textos';
import type { ResumoDetector as Resumo } from '../tipos';
import estilos from './ResumoDetector.module.css';

/** Card do topo (7a): frase da API, detalhe e contadores mono 28 na cor de cada severidade. */
export default function ResumoDetector({ resumo }: Readonly<{ resumo: Resumo }>) {
  return (
    <section className={estilos.resumo}>
      <div className={estilos.textos}>
        <h2 className={estilos.frase}>{resumo.frase}</h2>
        <p className={estilos.detalhe}>{resumo.detalhe}</p>
      </div>
      <ul className={estilos.contadores} aria-label={T.alertasPorSeveridade}>
        {ORDEM_SEVERIDADES.map((severidade) => (
          <li
            key={severidade}
            className={estilos.contador}
            style={{ color: corDaSeveridade(severidade) }}
          >
            <span className={estilos.numero}>{resumo.por_severidade[severidade]}</span>
            <span className={estilos.palavra}>
              <Icone nome={SEVERIDADES[severidade].icone} preenchido tamanho={17} />
              {SEVERIDADES[severidade].palavra}
            </span>
          </li>
        ))}
      </ul>
    </section>
  );
}
