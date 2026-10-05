import Card from '../../../shared/ui/Card';
import Icone from '../../../shared/ui/Icone';
import Select from '../../../shared/ui/Select';
import {
  type CampoDeteccao as Campo,
  descreverDeteccoes,
  type DescricaoCampo,
  type MetadadosLeitura,
  type OpcoesLeitura,
} from '../opcoesLeitura';
import { TEXTOS_IMPORTAR as T } from '../textos';
import estilos from './CardDeteccoes.module.css';

type AoCorrigir = ((campo: Campo, valor: string) => void) | null;

interface PropsCardDeteccoes {
  metadados: MetadadosLeitura;
  opcoes: OpcoesLeitura;
  aoCorrigir: AoCorrigir;
}

function CampoDeteccao({
  descricao,
  aoCorrigir,
}: Readonly<{ descricao: DescricaoCampo; aoCorrigir: AoCorrigir }>) {
  if (aoCorrigir === null || !descricao.corrigivel) {
    return (
      <div className={estilos.campo}>
        <span className={estilos.rotulo}>{descricao.rotulo}</span>
        <span className={estilos.valorFixo}>{descricao.rotuloValor}</span>
        <span className={estilos.motivo}>{descricao.motivo}</span>
      </div>
    );
  }
  return (
    <div className={estilos.campo}>
      <Select
        rotulo={descricao.rotulo}
        valor={descricao.valor}
        opcoes={descricao.opcoes}
        ajuda={descricao.motivo}
        aoMudar={(valor) => {
          aoCorrigir(descricao.campo, valor);
        }}
      />
    </div>
  );
}

/** Card "O que detectamos" (1a): mudar um Select relê o arquivo. */
export default function CardDeteccoes({
  metadados,
  opcoes,
  aoCorrigir,
}: Readonly<PropsCardDeteccoes>) {
  const campos = descreverDeteccoes(metadados, opcoes);
  const complemento = aoCorrigir === null ? T.deteccoes.semArquivo : T.deteccoes.corrijaAbaixo;
  const titulo = (
    <span className={estilos.titulo}>
      <span className={estilos.icone}>
        <Icone nome="check_circle" preenchido tamanho={22} />
      </span>
      {T.deteccoes.titulo}
    </span>
  );
  return (
    <Card
      titulo={titulo}
      subtitulo={`${T.deteccoes.lemos(metadados.n_linhas, metadados.n_colunas)} ${complemento}`}
    >
      <div
        className={estilos.grade}
        style={{ gridTemplateColumns: `repeat(${String(campos.length)}, minmax(0, 1fr))` }}
      >
        {campos.map((descricao) => (
          <CampoDeteccao key={descricao.campo} descricao={descricao} aoCorrigir={aoCorrigir} />
        ))}
      </div>
    </Card>
  );
}
