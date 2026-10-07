import { useId } from 'react';
import { juntarClasses } from '../lib/classes';
import campo from './Campo.module.css';
import MensagemCampo from './MensagemCampo';

interface PropsCampoNumero {
  rotulo: string;
  /** Texto digitado; quem usa converte com lerNumeroPtBr (shared/lib/formatar). */
  valor: string;
  aoMudar: (texto: string) => void;
  erro?: string | undefined;
  ajuda?: string | undefined;
}

export default function CampoNumero({
  rotulo,
  valor,
  aoMudar,
  erro,
  ajuda,
}: Readonly<PropsCampoNumero>) {
  const id = useId();
  const idMensagem = `${id}-mensagem`;
  const temMensagem = Boolean(erro ?? ajuda);
  return (
    <div className={campo.campo}>
      <label htmlFor={id} className={campo.rotulo}>
        {rotulo}
      </label>
      <input
        id={id}
        type="text"
        inputMode="decimal"
        autoComplete="off"
        value={valor}
        onChange={(evento) => {
          aoMudar(evento.target.value);
        }}
        aria-invalid={erro ? true : undefined}
        aria-describedby={temMensagem ? idMensagem : undefined}
        className={juntarClasses(campo.entrada, campo.mono, erro ? campo.comErro : undefined)}
      />
      <MensagemCampo id={idMensagem} erro={erro} ajuda={ajuda} />
    </div>
  );
}
