import { juntarClasses } from '../../shared/lib/classes';
import type { Tema } from '../../shared/tema/tipos';
import { useTema } from '../../shared/tema/useTema';
import Icone from '../../shared/ui/Icone';
import { useNavegacaoPorSetas } from '../../shared/ui/useNavegacaoPorSetas';
import { TEXTOS_APP } from '../textos';
import estilos from './AlternanciaTema.module.css';

const OPCOES = [
  { valor: 'claro', icone: 'light_mode', rotulo: TEXTOS_APP.temaClaro },
  { valor: 'escuro', icone: 'dark_mode', rotulo: TEXTOS_APP.temaEscuro },
] as const satisfies readonly { valor: Tema; icone: string; rotulo: string }[];

const IDS: readonly Tema[] = OPCOES.map((opcao) => opcao.valor);

export default function AlternanciaTema() {
  const { tema, definirTema } = useTema();
  const propsItem = useNavegacaoPorSetas({ ids: IDS, ativo: tema, aoMudar: definirTema });
  return (
    <div role="radiogroup" aria-label={TEXTOS_APP.tema} className={estilos.grupo}>
      {OPCOES.map((opcao) => {
        const selecionada = opcao.valor === tema;
        return (
          <button
            key={opcao.valor}
            {...propsItem(opcao.valor)}
            type="button"
            role="radio"
            aria-checked={selecionada}
            aria-label={opcao.rotulo}
            className={juntarClasses(estilos.opcao, selecionada && estilos.selecionada)}
            onClick={() => {
              definirTema(opcao.valor);
            }}
          >
            <Icone nome={opcao.icone} tamanho={18} />
          </button>
        );
      })}
    </div>
  );
}
