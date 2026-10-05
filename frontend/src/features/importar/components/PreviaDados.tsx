import type { LinhaDados } from '../../../shared/api/dataset';
import { formatarCelula } from '../../../shared/lib/formatarCelula';
import Card from '../../../shared/ui/Card';
import Tabela, { type ColunaTabela } from '../../../shared/ui/Tabela';
import { colunasDaPrevia } from '../apresentacao';
import { TEXTOS_IMPORTAR as T } from '../textos';

const ALTURA_MAXIMA = 520;

interface PropsPreviaDados {
  linhas: readonly LinhaDados[];
  totalLinhas: number;
}

export default function PreviaDados({ linhas, totalLinhas }: Readonly<PropsPreviaDados>) {
  const colunas = colunasDaPrevia(linhas).map((coluna): ColunaTabela<LinhaDados> => ({
    id: coluna.nome,
    titulo: coluna.nome,
    celula: (linha) => formatarCelula(linha.valores[coluna.nome]),
    alinhamento: coluna.numerica ? 'direita' : 'esquerda',
  }));
  return (
    <Card titulo={T.previa.titulo} subtitulo={T.previa.subtitulo(linhas.length, totalLinhas)}>
      <Tabela
        legenda={T.previa.legenda}
        colunas={colunas}
        linhas={linhas}
        chave={(linha) => String(linha.linha)}
        alturaMaxima={ALTURA_MAXIMA}
      />
    </Card>
  );
}
