import { type ReactNode, useId } from 'react';
import { juntarClasses } from '../lib/classes';
import estilos from './Abas.module.css';
import Icone from './Icone';
import Tooltip from './Tooltip';
import { type PropsItemNavegavel, useNavegacaoPorSetas } from './useNavegacaoPorSetas';

export interface DefinicaoAba<T extends string> {
  id: T;
  rotulo: string;
  desabilitada?: boolean | undefined;
  /** Texto do tooltip da aba desabilitada (D46): "{medida} não se aplica a {tipo}: {motivo}." */
  motivo?: string | undefined;
}

interface PropsAbas<T extends string> {
  rotulo: string;
  abas: readonly DefinicaoAba<T>[];
  ativa: T;
  aoMudar: (id: T) => void;
  children: ReactNode;
}

export default function Abas<T extends string>({
  rotulo,
  abas,
  ativa,
  aoMudar,
  children,
}: Readonly<PropsAbas<T>>) {
  const prefixo = useId();
  const propsItem = useNavegacaoPorSetas({
    ids: abas.map((aba) => aba.id),
    ativo: ativa,
    aoMudar,
    habilitado: (id) => abas.find((aba) => aba.id === id)?.desabilitada !== true,
  });
  return (
    <div>
      <div role="tablist" aria-label={rotulo} className={estilos.lista}>
        {abas.map((aba) => (
          <ItemAba
            key={aba.id}
            aba={aba}
            ativa={aba.id === ativa}
            prefixo={prefixo}
            propsNavegacao={propsItem(aba.id)}
            aoAtivar={aoMudar}
          />
        ))}
      </div>
      <div
        role="tabpanel"
        id={`${prefixo}painel`}
        aria-labelledby={`${prefixo}${ativa}`}
        tabIndex={0}
        className={estilos.painel}
      >
        {children}
      </div>
    </div>
  );
}

interface PropsItemAba<T extends string> {
  aba: DefinicaoAba<T>;
  ativa: boolean;
  prefixo: string;
  propsNavegacao: PropsItemNavegavel;
  aoAtivar: (id: T) => void;
}

function ItemAba<T extends string>({
  aba,
  ativa,
  prefixo,
  propsNavegacao,
  aoAtivar,
}: Readonly<PropsItemAba<T>>) {
  const desabilitada = aba.desabilitada === true;
  const botao = (
    <button
      {...propsNavegacao}
      type="button"
      role="tab"
      id={`${prefixo}${aba.id}`}
      aria-selected={ativa}
      aria-controls={ativa ? `${prefixo}painel` : undefined}
      aria-disabled={desabilitada}
      className={juntarClasses(
        estilos.aba,
        ativa && estilos.ativa,
        desabilitada && estilos.desabilitada,
      )}
      onClick={() => {
        if (!desabilitada) aoAtivar(aba.id);
      }}
    >
      {desabilitada ? <Icone nome="block" tamanho={16} /> : null}
      {aba.rotulo}
    </button>
  );
  return desabilitada && aba.motivo ? <Tooltip texto={aba.motivo}>{botao}</Tooltip> : botao;
}
