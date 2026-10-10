import Card from '../../../shared/ui/Card';
import Tabela, { type ColunaTabela } from '../../../shared/ui/Tabela';
import {
  formatarDiferenca,
  formatarValor,
  quantidadeGerada,
  subtituloResultado,
} from '../comparacao';
import { TEXTOS_GERADOR } from '../textos';
import type { Gerado, LinhaComparacao } from '../tipos';
import estilos from './Resultado.module.css';

const T = TEXTOS_GERADOR.resultado;

function colunas(gerado: Gerado): ColunaTabela<LinhaComparacao>[] {
  return [
    { id: 'medida', titulo: T.medida, celula: (linha) => linha.estatistica, cabecalhoLinha: true },
    {
      id: 'original',
      titulo: T.original,
      celula: (linha) => formatarValor(linha, linha.original),
      alinhamento: 'direita',
      mono: true,
    },
    {
      id: 'gerado',
      titulo: T.gerado(quantidadeGerada(gerado)),
      celula: (linha) => <strong>{formatarValor(linha, linha.gerado)}</strong>,
      alinhamento: 'direita',
      mono: true,
    },
    {
      id: 'diferenca',
      titulo: T.diferenca,
      celula: (linha) => <span className={estilos.diferenca}>{formatarDiferenca(linha)}</span>,
      alinhamento: 'direita',
      mono: true,
    },
  ];
}

/** Card "Original × Gerado" (print 6a). */
export default function TabelaComparacao({ gerado }: Readonly<{ gerado: Gerado }>) {
  return (
    <Card titulo={T.titulo} subtitulo={subtituloResultado(gerado)} preenchimento="nenhum">
      <Tabela
        legenda={T.legenda}
        colunas={colunas(gerado)}
        linhas={gerado.comparacao}
        chave={(linha) => linha.estatistica}
      />
    </Card>
  );
}
