import Accordion from '../../../shared/ui/Accordion';
import { TEXTOS_DETECTOR } from '../textos';
import type { RegraNaoAplicada } from '../tipos';
import estilos from './RegrasNaoVerificadas.module.css';

const T = TEXTOS_DETECTOR.naoVerificadas;

/** "Lei de Benford não verificada em idade: …" com o nome em 600 e a coluna em mono (7a). */
function FraseRegra({ item }: Readonly<{ item: RegraNaoAplicada }>) {
  const { frase, nome_regra: nome, coluna } = item;
  if (!frase.startsWith(nome)) return <>{frase}</>;
  const resto = frase.slice(nome.length);
  const posicao = coluna === null ? -1 : resto.indexOf(coluna);
  if (coluna === null || posicao < 0) {
    return (
      <>
        <strong className={estilos.nome}>{nome}</strong>
        {resto}
      </>
    );
  }
  return (
    <>
      <strong className={estilos.nome}>{nome}</strong>
      {resto.slice(0, posicao)}
      <span className={estilos.coluna}>{coluna}</span>
      {resto.slice(posicao + coluna.length)}
    </>
  );
}

interface PropsRegrasNaoVerificadas {
  itens: readonly RegraNaoAplicada[];
  /** Aberta no estado vazio (7c); com alertas começa fechada. */
  abertoInicial: boolean;
}

/** Seção recolhível com cada (regra, coluna) que não foi verificada e o motivo (spec 16). */
export default function RegrasNaoVerificadas({
  itens,
  abertoInicial,
}: Readonly<PropsRegrasNaoVerificadas>) {
  if (itens.length === 0) return null;
  const regras = new Set(itens.map((item) => item.regra));
  return (
    <section className={estilos.secao}>
      <Accordion
        titulo={T.titulo}
        complemento={T.complemento(regras.size)}
        abertoInicial={abertoInicial}
        variante="secao"
      >
        <ul className={estilos.lista}>
          {itens.map((item) => (
            <li key={`${item.regra}-${item.coluna ?? ''}`}>
              <FraseRegra item={item} />
            </li>
          ))}
        </ul>
      </Accordion>
    </section>
  );
}
