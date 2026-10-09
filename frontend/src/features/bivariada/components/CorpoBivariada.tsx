import type { UseQueryResult } from '@tanstack/react-query';
import { useNavigate } from 'react-router';
import { CAMINHOS } from '../../../shared/navegacao/caminhos';
import Botao from '../../../shared/ui/Botao';
import EstadoCarregando from '../../../shared/ui/EstadoCarregando';
import EstadoErro from '../../../shared/ui/EstadoErro';
import EstadoVazio from '../../../shared/ui/EstadoVazio';
import type { EstadoBivariada } from '../estadoBivariada';
import { TEXTOS_BIVARIADA } from '../textos';
import type { MatrizCorrelacao } from '../tipos';
import ConteudoBivariada from './ConteudoBivariada';

const T = TEXTOS_BIVARIADA;
const FORMAS_CALCULANDO = ['cards', 'grafico'] as const;

function PoucasColunas() {
  const navegar = useNavigate();
  const acao = (
    <Botao
      variante="secundario"
      onClick={() => {
        void navegar(CAMINHOS.variaveis);
      }}
    >
      {T.vazio.acao}
    </Botao>
  );
  return (
    <EstadoVazio
      icone="scatter_plot"
      titulo={T.vazio.titulo}
      descricao={T.vazio.descricao}
      acao={acao}
    />
  );
}

interface Props {
  estado: EstadoBivariada;
  datasetId: string;
  matriz: UseQueryResult<MatrizCorrelacao>;
}

export default function CorpoBivariada({ estado, datasetId, matriz }: Readonly<Props>) {
  switch (estado.status) {
    case 'carregando-colunas':
      return <EstadoCarregando forma="tabela" mensagem={T.carregandoColunas} />;
    case 'poucas-colunas':
      return <PoucasColunas />;
    case 'calculando':
      return (
        <EstadoCarregando
          forma={FORMAS_CALCULANDO}
          mensagem={T.calculando(estado.par.x, estado.par.y)}
        />
      );
    case 'erro':
      return (
        <EstadoErro
          erro={estado.erro}
          {...(estado.tentarDeNovo === null ? {} : { aoTentarDeNovo: estado.tentarDeNovo })}
        />
      );
    case 'pronta':
      return (
        <ConteudoBivariada bivariada={estado.bivariada} datasetId={datasetId} matriz={matriz} />
      );
  }
}
