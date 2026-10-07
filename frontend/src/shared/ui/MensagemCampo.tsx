import campo from './Campo.module.css';
import Icone from './Icone';

interface PropsMensagemCampo {
  id: string;
  erro?: string | undefined;
  ajuda?: string | undefined;
}

/** Erro tem prioridade sobre a ajuda; formato do erro: "{o que}. {como resolver}." (spec 16). */
export default function MensagemCampo({ id, erro, ajuda }: Readonly<PropsMensagemCampo>) {
  if (erro) {
    return (
      <p id={id} className={campo.erro}>
        <Icone nome="error" tamanho={16} />
        {erro}
      </p>
    );
  }
  return ajuda ? (
    <p id={id} className={campo.ajuda}>
      {ajuda}
    </p>
  ) : null;
}
