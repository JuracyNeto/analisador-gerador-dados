import type { ReactNode } from 'react';
import { useNavigate } from 'react-router';
import Botao from '../ui/Botao';
import estilos from './BotaoEtapa.module.css';

type Sentido = 'voltar' | 'avancar';

/** Voltar: secundário à esquerda da barra de ações; avançar: primário à direita (D89). */
const APARENCIA = {
  voltar: {
    variante: 'secundario',
    icone: 'arrow_back',
    iconeFinal: undefined,
    classe: estilos.voltar,
  },
  avancar: {
    variante: 'primario',
    icone: undefined,
    iconeFinal: 'arrow_forward',
    classe: undefined,
  },
} as const satisfies Record<Sentido, object>;

interface PropsBotaoEtapa {
  para: string;
  sentido: Sentido;
  children: ReactNode;
}

/** Botão da barra de ações que leva à etapa anterior ou à seguinte. */
export default function BotaoEtapa({ para, sentido, children }: Readonly<PropsBotaoEtapa>) {
  const navegar = useNavigate();
  const aparencia = APARENCIA[sentido];
  return (
    <Botao
      tamanho="lg"
      variante={aparencia.variante}
      icone={aparencia.icone}
      iconeFinal={aparencia.iconeFinal}
      className={aparencia.classe}
      onClick={() => {
        void navegar(para);
      }}
    >
      {children}
    </Botao>
  );
}
