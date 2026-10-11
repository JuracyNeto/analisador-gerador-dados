import { formatarNumero } from '../../../shared/lib/formatar';
import CampoNumero from '../../../shared/ui/CampoNumero';
import Select from '../../../shared/ui/Select';
import type { FormularioUnivariado as Formulario } from '../hooks/useFormularioUnivariado';
import { ehNumerica, origemUnivariada, tipoUnivariado } from '../pedidos';
import { TEXTOS_GERADOR } from '../textos';
import type { TipoManual } from '../tipos';
import CaixaComAjuda from './CaixaComAjuda';
import CamposModo from './CamposModo';
import CamposParametros from './CamposParametros';
import FormularioGerador from './FormularioGerador';
import SeletorOrigem from './SeletorOrigem';

const T = TEXTOS_GERADOR;
const OPCOES_TIPO = (['continua', 'discreta', 'binaria'] as const).map((valor) => ({
  valor,
  rotulo: T.tipos[valor],
}));

interface PropsCampo {
  formulario: Formulario;
}

function CampoOrigem({ formulario }: Readonly<PropsCampo>) {
  const { estado, contexto, colunas, mudar, escolherColuna } = formulario;
  if (origemUnivariada(estado, contexto) === 'manual') {
    return (
      <Select<TipoManual>
        rotulo={T.tipo}
        valor={estado.tipoManual}
        opcoes={OPCOES_TIPO}
        aoMudar={(tipo) => {
          mudar('tipoManual', tipo);
        }}
      />
    );
  }
  const opcoes = (colunas.data ?? []).map(({ coluna }) => ({ valor: coluna, rotulo: coluna }));
  return (
    <Select
      rotulo={T.coluna}
      valor={contexto.coluna ?? ''}
      opcoes={opcoes}
      aoMudar={escolherColuna}
    />
  );
}

function LimitarFaixa({ formulario }: Readonly<PropsCampo>) {
  const { estado, contexto, mudar } = formulario;
  const { minimo, maximo } = contexto.resumo ?? {};
  const comOrigem = origemUnivariada(estado, contexto) === 'coluna';
  if (!comOrigem || !ehNumerica(tipoUnivariado(estado, contexto))) return null;
  if (minimo === null || minimo === undefined || maximo === null || maximo === undefined) {
    return null;
  }
  return (
    <CaixaComAjuda
      rotulo={T.limitar}
      ajuda={T.limitarAjuda(formatarNumero(minimo), formatarNumero(maximo))}
      marcada={estado.limitar}
      aoMudar={(marcada) => {
        mudar('limitar', marcada);
      }}
    />
  );
}

interface Props extends PropsCampo {
  gerando: boolean;
  aoGerar: () => void;
}

/** Formulário univariado (tela 6a). */
export default function FormularioUnivariado({ formulario, gerando, aoGerar }: Readonly<Props>) {
  const { estado, contexto, erros, mudar } = formulario;
  const manual = origemUnivariada(estado, contexto) === 'manual';
  const aoMudarTexto = (campo: 'quantidade' | 'semente') => (texto: string) => {
    mudar(campo, texto);
  };
  return (
    <FormularioGerador gerando={gerando} aoGerar={aoGerar}>
      <SeletorOrigem
        rotulos={T.origem.univariado}
        valor={estado.origem}
        aoMudar={(origem) => {
          mudar('origem', origem);
        }}
        temDataset={contexto.datasetId !== null}
      />
      <CampoOrigem formulario={formulario} />
      <CampoNumero
        rotulo={T.quantidade}
        valor={estado.quantidade}
        aoMudar={aoMudarTexto('quantidade')}
        erro={erros.quantidade}
      />
      {manual ? (
        <CamposParametros formulario={formulario} />
      ) : (
        <CamposModo formulario={formulario} />
      )}
      <CampoNumero
        rotulo={`${T.semente} ${T.sementeAjuda}`}
        valor={estado.semente}
        aoMudar={aoMudarTexto('semente')}
        erro={erros.semente}
      />
      <LimitarFaixa formulario={formulario} />
    </FormularioGerador>
  );
}
