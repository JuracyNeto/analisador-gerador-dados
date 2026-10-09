import { useState } from 'react';
import { formatarInteiro } from '../../../shared/lib/formatar';
import Botao from '../../../shared/ui/Botao';
import CampoNumero from '../../../shared/ui/CampoNumero';
import { validarTentativas } from '../tentativas';
import { TEXTOS_ANALISE } from '../textos';
import estilos from './ControleTentativas.module.css';

const T = TEXTOS_ANALISE.forma.tentativas;

interface Props {
  tentativas: number;
  maximo: number;
  aoAplicar: (n: number) => void;
}

/** Campo "Número de tentativas (n)" da Binomial; Enter ou "Aplicar" pede a análise de novo. */
export default function ControleTentativas({ tentativas, maximo, aoAplicar }: Readonly<Props>) {
  const [texto, setTexto] = useState(() => String(tentativas));
  const [erro, setErro] = useState<string | undefined>(undefined);

  return (
    <form
      className={estilos.controle}
      noValidate
      onSubmit={(evento) => {
        evento.preventDefault();
        const resultado = validarTentativas(texto, maximo);
        if (resultado.status === 'erro') {
          setErro(resultado.mensagem);
          return;
        }
        setErro(undefined);
        aoAplicar(resultado.n);
      }}
    >
      <CampoNumero
        rotulo={T.rotulo}
        valor={texto}
        aoMudar={setTexto}
        erro={erro}
        ajuda={T.ajuda(formatarInteiro(maximo))}
      />
      <Botao type="submit" variante="secundario" className={estilos.botao}>
        {T.aplicar}
      </Botao>
    </form>
  );
}
