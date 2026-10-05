import { type ChangeEvent, useId } from 'react';
import { VISUALMENTE_OCULTO, juntarClasses } from '../lib/classes';
import campo from './Campo.module.css';
import Icone from './Icone';
import MensagemCampo from './MensagemCampo';

interface OpcaoSelect<T extends string> {
  valor: T;
  rotulo: string;
  desabilitada?: boolean | undefined;
}

interface PropsSelect<T extends string> {
  rotulo: string;
  valor: T;
  opcoes: readonly OpcaoSelect<T>[];
  aoMudar: (valor: T) => void;
  ajuda?: string | undefined;
  rotuloOculto?: boolean;
  altura?: 36 | 40 | 44;
}

const CLASSE_ALTURA = { 36: campo.altura36, 40: undefined, 44: campo.altura44 } as const;

export default function Select<T extends string>({
  rotulo,
  valor,
  opcoes,
  aoMudar,
  ajuda,
  rotuloOculto = false,
  altura = 40,
}: Readonly<PropsSelect<T>>) {
  const id = useId();
  const idAjuda = `${id}-ajuda`;
  // Recupera o valor tipado T a partir da string do DOM, sem `as`.
  const aoAlterar = (evento: ChangeEvent<HTMLSelectElement>): void => {
    const escolhida = opcoes.find((opcao) => opcao.valor === evento.target.value);
    if (escolhida) aoMudar(escolhida.valor);
  };
  return (
    <div className={campo.campo}>
      <label htmlFor={id} className={rotuloOculto ? VISUALMENTE_OCULTO : campo.rotulo}>
        {rotulo}
      </label>
      <div className={campo.caixa}>
        <select
          id={id}
          value={valor}
          onChange={aoAlterar}
          aria-describedby={ajuda ? idAjuda : undefined}
          className={juntarClasses(campo.entrada, campo.select, CLASSE_ALTURA[altura])}
        >
          {opcoes.map((opcao) => (
            <option key={opcao.valor} value={opcao.valor} disabled={opcao.desabilitada}>
              {opcao.rotulo}
            </option>
          ))}
        </select>
        <Icone nome="expand_more" tamanho={20} className={campo.seta} />
      </div>
      <MensagemCampo id={idAjuda} ajuda={ajuda} />
    </div>
  );
}
