import { useNavigate } from 'react-router';
import { CAMINHOS } from '../navegacao/caminhos';
import Botao from '../ui/Botao';
import EstadoVazio from '../ui/EstadoVazio';
import { TEXTOS_SESSAO as T } from './textos';

interface PropsSemDataset {
  descricao?: string;
}

/** Estado vazio das etapas 2–8 quando se chega sem arquivo (URL direta ou sessão encerrada). */
export default function SemDataset({
  descricao = T.semDatasetDescricao,
}: Readonly<PropsSemDataset>) {
  const navegar = useNavigate();
  return (
    <EstadoVazio
      icone="upload_file"
      titulo={T.semDatasetTitulo}
      descricao={descricao}
      acao={
        <Botao
          onClick={() => {
            void navegar(CAMINHOS.importar);
          }}
        >
          {T.irParaImportar}
        </Botao>
      }
    />
  );
}
