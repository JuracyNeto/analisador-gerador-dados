import { juntarClasses } from '../lib/classes';
import estilos from './Segmented.module.css';
import { useNavegacaoPorSetas } from './useNavegacaoPorSetas';

interface OpcaoSegmented<T extends string> {
  valor: T;
  rotulo: string;
  selo?: string | undefined;
}

interface PropsSegmented<T extends string> {
  rotulo: string;
  opcoes: readonly OpcaoSegmented<T>[];
  valor: T;
  aoMudar: (valor: T) => void;
}

export default function Segmented<T extends string>({
  rotulo,
  opcoes,
  valor,
  aoMudar,
}: Readonly<PropsSegmented<T>>) {
  const propsItem = useNavegacaoPorSetas({
    ids: opcoes.map((opcao) => opcao.valor),
    ativo: valor,
    aoMudar,
  });
  return (
    <div role="radiogroup" aria-label={rotulo} className={estilos.grupo}>
      {opcoes.map((opcao) => (
        <button
          key={opcao.valor}
          {...propsItem(opcao.valor)}
          type="button"
          role="radio"
          aria-checked={opcao.valor === valor}
          className={juntarClasses(estilos.opcao, opcao.valor === valor && estilos.selecionada)}
          onClick={() => {
            aoMudar(opcao.valor);
          }}
        >
          {opcao.rotulo}
          {opcao.selo ? <span className={estilos.selo}>{opcao.selo}</span> : null}
        </button>
      ))}
    </div>
  );
}
