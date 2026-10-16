import CampoNumero from '../../../shared/ui/CampoNumero';
import Select from '../../../shared/ui/Select';
import Slider from '../../../shared/ui/Slider';
import type { FormularioBivariado as Formulario } from '../hooks/useFormularioBivariado';
import { origemBivariada, textoCampo } from '../pedidos';
import { TEXTOS_GERADOR } from '../textos';
import type { ResumoOrigemPar } from '../tipos';
import CaixaComAjuda from './CaixaComAjuda';
import FormularioGerador from './FormularioGerador';
import estilos from './Formulario.module.css';
import SeletorOrigem from './SeletorOrigem';

const T = TEXTOS_GERADOR;

type CampoTexto = 'mediaX' | 'mediaY' | 'desvioX' | 'desvioY';

/** Campo do formulário → valor do par de origem que ele mostra sem edição. */
const VALOR_DO_PAR: Record<CampoTexto, (par: ResumoOrigemPar) => number> = {
  mediaX: (par) => par.media_x,
  mediaY: (par) => par.media_y,
  desvioX: (par) => par.desvio_x,
  desvioY: (par) => par.desvio_y,
};

interface PropsCampo {
  formulario: Formulario;
}

function SeletoresXY({ formulario }: Readonly<PropsCampo>) {
  const { contexto, numericas, mudar } = formulario;
  const opcoes = (outra: string | null) =>
    numericas.map(({ coluna }) => ({
      valor: coluna,
      rotulo: coluna,
      desabilitada: coluna === outra,
    }));
  return (
    <div className={estilos.par}>
      <Select
        rotulo={T.x}
        valor={contexto.x ?? ''}
        opcoes={opcoes(contexto.y)}
        aoMudar={(x) => {
          mudar('x', x);
        }}
      />
      <Select
        rotulo={T.y}
        valor={contexto.y ?? ''}
        opcoes={opcoes(contexto.x)}
        aoMudar={(y) => {
          mudar('y', y);
        }}
      />
    </div>
  );
}

function CamposDoPar({ formulario }: Readonly<PropsCampo>) {
  const { estado, contexto, par, erros, mudar } = formulario;
  const comOrigem = origemBivariada(estado, contexto) === 'coluna';
  const nomeX = comOrigem ? (contexto.x ?? T.x) : T.x;
  const nomeY = comOrigem ? (contexto.y ?? T.y) : T.y;
  const rotulos: Record<CampoTexto, string> = {
    mediaX: T.mediaDe(nomeX),
    mediaY: T.mediaDe(nomeY),
    desvioX: T.desvioDe(nomeX),
    desvioY: T.desvioDe(nomeY),
  };
  const campos: readonly CampoTexto[] = ['mediaX', 'mediaY', 'desvioX', 'desvioY'];
  return (
    <div className={estilos.par}>
      {campos.map((campo) => (
        <CampoNumero
          key={campo}
          rotulo={rotulos[campo]}
          valor={textoCampo(estado[campo], par.data ? VALOR_DO_PAR[campo](par.data) : undefined)}
          aoMudar={(texto) => {
            mudar(campo, texto);
          }}
          erro={erros[campo]}
        />
      ))}
    </div>
  );
}

function CampoRho({ formulario }: Readonly<PropsCampo>) {
  const { estado, contexto, par, mudar } = formulario;
  const doPar = origemBivariada(estado, contexto) === 'coluna' ? par.data?.r : undefined;
  return (
    <Slider
      rotulo={T.rho}
      valor={estado.rho ?? doPar ?? 0}
      aoMudar={(rho) => {
        mudar('rho', rho);
      }}
      min={-1}
      max={1}
      passo={0.01}
    />
  );
}

interface Props extends PropsCampo {
  gerando: boolean;
  aoGerar: () => void;
}

/** Formulário bivariado (tela 6b): X, Y, médias e desvios, ρ, pares, ajuste exato e semente. */
export default function FormularioBivariado({ formulario, gerando, aoGerar }: Readonly<Props>) {
  const { estado, contexto, erros, mudar } = formulario;
  const aoMudarTexto = (campo: 'quantidade' | 'semente') => (texto: string) => {
    mudar(campo, texto);
  };
  return (
    <FormularioGerador gerando={gerando} aoGerar={aoGerar}>
      <SeletorOrigem
        rotulos={T.origem.bivariado}
        valor={estado.origem}
        aoMudar={(origem) => {
          mudar('origem', origem);
        }}
        temDataset={contexto.datasetId !== null}
      />
      {origemBivariada(estado, contexto) === 'coluna' ? (
        <SeletoresXY formulario={formulario} />
      ) : null}
      <CamposDoPar formulario={formulario} />
      <CampoRho formulario={formulario} />
      <CampoNumero
        rotulo={T.quantidadePares}
        valor={estado.quantidade}
        aoMudar={aoMudarTexto('quantidade')}
        erro={erros.quantidade}
      />
      <CaixaComAjuda
        rotulo={T.exato}
        ajuda={T.exatoAjuda}
        marcada={estado.exato}
        aoMudar={(marcada) => {
          mudar('exato', marcada);
        }}
      />
      <CampoNumero
        rotulo={`${T.semente} ${T.sementeAjuda}`}
        valor={estado.semente}
        aoMudar={aoMudarTexto('semente')}
        erro={erros.semente}
      />
    </FormularioGerador>
  );
}
