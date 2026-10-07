import CampoNumero from '../../../shared/ui/CampoNumero';
import Card from '../../../shared/ui/Card';
import { LIMITE_VAZIO, type TextoLimite, validarLimite } from '../limites';
import { TEXTOS_LIMPEZA as T } from '../textos';
import estilos from './LimitesPorColuna.module.css';

type AoMudar = (coluna: string, campo: keyof TextoLimite, texto: string) => void;

interface PropsLimitesPorColuna {
  colunas: readonly string[];
  textos: Readonly<Record<string, TextoLimite>>;
  aoMudar: AoMudar;
}

function CamposLimite({
  coluna,
  texto,
  aoMudar,
}: Readonly<{ coluna: string; texto: TextoLimite; aoMudar: AoMudar }>) {
  const { erroMin, erroMax } = validarLimite(texto);
  return (
    <fieldset className={estilos.coluna}>
      <legend className={estilos.nome}>{coluna}</legend>
      <div className={estilos.campos}>
        <CampoNumero
          rotulo={T.limites.minimo}
          valor={texto.min}
          aoMudar={(valor) => {
            aoMudar(coluna, 'min', valor);
          }}
          {...(erroMin === null ? {} : { erro: erroMin })}
        />
        <CampoNumero
          rotulo={T.limites.maximo}
          valor={texto.max}
          aoMudar={(valor) => {
            aoMudar(coluna, 'max', valor);
          }}
          {...(erroMax === null ? {} : { erro: erroMax })}
        />
      </div>
    </fieldset>
  );
}

/** Limites opcionais por coluna numérica (3a); só limites válidos entram no diagnóstico (D74). */
export default function LimitesPorColuna({
  colunas,
  textos,
  aoMudar,
}: Readonly<PropsLimitesPorColuna>) {
  if (colunas.length === 0) return null;
  return (
    <Card titulo={T.limites.titulo} subtitulo={T.limites.subtitulo}>
      <div className={estilos.grade}>
        {colunas.map((coluna) => (
          <CamposLimite
            key={coluna}
            coluna={coluna}
            texto={textos[coluna] ?? LIMITE_VAZIO}
            aoMudar={aoMudar}
          />
        ))}
      </div>
    </Card>
  );
}
