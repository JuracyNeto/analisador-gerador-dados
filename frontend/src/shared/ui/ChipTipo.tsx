import estilos from './ChipTipo.module.css';
import Icone from './Icone';
import {
  DICA_CORRIGIDO,
  estiloDoTipo,
  ROTULO_CORRIGIDO,
  TIPOS_VARIAVEL,
  type TipoVariavel,
} from './tiposVariavel';
import Tooltip from './Tooltip';

interface PropsChipTipo {
  tipo: TipoVariavel;
  curto?: boolean;
  corrigido?: boolean;
}

/** Tipo de variável sempre com ícone + palavra + cor (princípio 4 do design). */
export default function ChipTipo({
  tipo,
  curto = false,
  corrigido = false,
}: Readonly<PropsChipTipo>) {
  const config = TIPOS_VARIAVEL[tipo];
  const chip = (
    <span className={estilos.chip} data-tipo={tipo} style={estiloDoTipo(tipo)}>
      <Icone nome={config.icone} tamanho={17} />
      {curto ? config.rotuloCurto : config.rotuloCompleto}
      {corrigido ? <span className={estilos.selo}>{ROTULO_CORRIGIDO}</span> : null}
    </span>
  );
  // Tooltip só quando acrescenta algo ao que já está escrito no chip.
  if (!curto && !corrigido) return chip;
  const dica = corrigido ? `${config.rotuloCompleto} (${DICA_CORRIGIDO})` : config.rotuloCompleto;
  return <Tooltip texto={dica}>{chip}</Tooltip>;
}
