import CartaoOpcao from '../../../shared/ui/CartaoOpcao';
import { formatarNumero, formatarPercentual } from '../../../shared/lib/formatar';
import type { FormularioUnivariado } from '../hooks/useFormularioUnivariado';
import { modoUnivariado } from '../pedidos';
import { TEXTOS_GERADOR } from '../textos';
import type { ResumoOrigem } from '../tipos';
import CamposParametros from './CamposParametros';
import estilos from './Formulario.module.css';

const T = TEXTOS_GERADOR;

interface Props {
  formulario: FormularioUnivariado;
}

function descricaoPreservar(resumo: ResumoOrigem | undefined): string {
  if (resumo === undefined) return T.carregandoOrigem;
  if (resumo.media !== null && resumo.desvio !== null) {
    return T.descricaoPreservar(formatarNumero(resumo.media), formatarNumero(resumo.desvio));
  }
  if (resumo.sucesso !== null && resumo.chance !== null) {
    return T.descricaoPreservarBinaria(resumo.sucesso, formatarPercentual(resumo.chance * 100));
  }
  return T.descricaoPreservarCategorias;
}

/** "Modo" (tela 6a): dois cartões de rádio; nominal e ordinal só preservam. */
export default function CamposModo({ formulario }: Readonly<Props>) {
  const { estado, contexto, mudar } = formulario;
  const resumo = contexto.resumo;
  const modo = modoUnivariado(estado, contexto);
  const soPreservar = resumo?.so_preservar === true;
  const descricaoParametros = soPreservar ? T.soPreservar(T.tipoNoPlural(resumo.tipo)) : undefined;
  return (
    <fieldset className={estilos.grupo}>
      <legend className={estilos.legenda}>{T.modo}</legend>
      <CartaoOpcao
        nome="modo-univariado"
        titulo={T.modos.preservar}
        descricao={descricaoPreservar(resumo)}
        selecionado={modo === 'preservar'}
        aoSelecionar={() => {
          mudar('modo', 'preservar');
        }}
      />
      <CartaoOpcao
        nome="modo-univariado"
        titulo={T.modos.parametros}
        descricao={descricaoParametros}
        selecionado={modo === 'parametros'}
        desabilitado={soPreservar}
        aoSelecionar={() => {
          mudar('modo', 'parametros');
        }}
      >
        {soPreservar ? null : <CamposParametros formulario={formulario} />}
      </CartaoOpcao>
    </fieldset>
  );
}
