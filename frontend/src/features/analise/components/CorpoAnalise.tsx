import { useNavigate } from 'react-router';
import { CAMINHOS } from '../../../shared/navegacao/caminhos';
import Botao from '../../../shared/ui/Botao';
import EstadoCarregando from '../../../shared/ui/EstadoCarregando';
import EstadoErro from '../../../shared/ui/EstadoErro';
import EstadoVazio from '../../../shared/ui/EstadoVazio';
import type { EstadoAnalise } from '../estadoAnalise';
import { TEXTOS_ANALISE } from '../textos';
import ConteudoAnalise from './ConteudoAnalise';

const T = TEXTOS_ANALISE;
const FORMAS_CALCULANDO = ['cards', 'grafico'] as const;

function SemColunas() {
  const navegar = useNavigate();
  const acao = (
    <Botao
      variante="secundario"
      onClick={() => {
        void navegar(CAMINHOS.variaveis);
      }}
    >
      {T.semColunas.acao}
    </Botao>
  );
  return (
    <EstadoVazio
      icone="dataset"
      titulo={T.semColunas.titulo}
      descricao={T.semColunas.descricao}
      acao={acao}
    />
  );
}

interface Props {
  estado: EstadoAnalise;
  datasetId: string;
  classes: number | null;
  aoMudarClasses: (k: number) => void;
  aoMudarTentativas: (n: number) => void;
}

export default function CorpoAnalise({ estado, ...resto }: Readonly<Props>) {
  switch (estado.status) {
    case 'carregando-colunas':
      return <EstadoCarregando forma="tabela" mensagem={T.carregandoColunas} />;
    case 'sem-colunas':
      return <SemColunas />;
    case 'calculando':
      return <EstadoCarregando forma={FORMAS_CALCULANDO} mensagem={T.calculando(estado.coluna)} />;
    case 'erro':
      return (
        <EstadoErro
          erro={estado.erro}
          {...(estado.tentarDeNovo === null ? {} : { aoTentarDeNovo: estado.tentarDeNovo })}
        />
      );
    case 'pronta':
      return (
        <ConteudoAnalise analise={estado.analise} atualizando={estado.atualizando} {...resto} />
      );
  }
}
