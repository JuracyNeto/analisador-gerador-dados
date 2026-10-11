import CampoNumero from '../../../shared/ui/CampoNumero';
import type { FormularioUnivariado } from '../hooks/useFormularioUnivariado';
import { modoUnivariado, textoCampo, tipoUnivariado } from '../pedidos';
import { TEXTOS_GERADOR } from '../textos';
import estilos from './Formulario.module.css';

const T = TEXTOS_GERADOR;

interface Props {
  formulario: FormularioUnivariado;
}

/** Média e desvio, ou a chance de sucesso na binária; habilitados só em "Novos parâmetros". */
export default function CamposParametros({ formulario }: Readonly<Props>) {
  const { estado, contexto, erros, mudar } = formulario;
  const resumo = contexto.resumo;
  const desabilitado = modoUnivariado(estado, contexto) !== 'parametros';
  if (tipoUnivariado(estado, contexto) === 'binaria') {
    const rotulo = resumo?.sucesso ? T.chance(resumo.sucesso) : T.chanceSemOrigem;
    return (
      <CampoNumero
        rotulo={rotulo}
        valor={textoCampo(estado.chance, resumo?.chance)}
        aoMudar={(texto) => {
          mudar('chance', texto);
        }}
        erro={erros.chance}
        desabilitado={desabilitado}
      />
    );
  }
  return (
    <div className={estilos.par}>
      <CampoNumero
        rotulo={T.media}
        valor={textoCampo(estado.media, resumo?.media)}
        aoMudar={(texto) => {
          mudar('media', texto);
        }}
        erro={erros.media}
        desabilitado={desabilitado}
      />
      <CampoNumero
        rotulo={T.desvio}
        valor={textoCampo(estado.desvio, resumo?.desvio)}
        aoMudar={(texto) => {
          mudar('desvio', texto);
        }}
        erro={erros.desvio}
        desabilitado={desabilitado}
      />
    </div>
  );
}
