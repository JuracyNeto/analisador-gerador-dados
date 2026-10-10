import type { ReactNode } from 'react';
import Botao from '../../../shared/ui/Botao';
import { TEXTOS_GERADOR } from '../textos';
import estilos from './Formulario.module.css';

interface Props {
  gerando: boolean;
  aoGerar: () => void;
  children: ReactNode;
}

/** Moldura dos dois formulários: Enter ou o botão largo "Gerar dados" enviam. */
export default function FormularioGerador({ gerando, aoGerar, children }: Readonly<Props>) {
  return (
    <form
      className={estilos.formulario}
      noValidate
      onSubmit={(evento) => {
        evento.preventDefault();
        aoGerar();
      }}
    >
      {children}
      <Botao
        type="submit"
        tamanho="lg"
        icone="auto_awesome"
        carregando={gerando}
        textoCarregando={TEXTOS_GERADOR.gerando}
      >
        {TEXTOS_GERADOR.gerar}
      </Botao>
    </form>
  );
}
