import Card from '../../../shared/ui/Card';
import Tabela, { type ColunaTabela } from '../../../shared/ui/Tabela';
import { descreverLinhasIniciais, type LinhaInicial } from '../linhasIniciais';
import type { MetadadosLeitura } from '../opcoesLeitura';
import { TEXTOS_IMPORTAR as T } from '../textos';
import estilos from './InicioArquivo.module.css';

const COLUNA_NUMERO: ColunaTabela<LinhaInicial> = {
  id: 'numero',
  titulo: T.inicio.linha,
  celula: (linha) => linha.numero,
  mono: true,
  cabecalhoLinha: true,
};

const COLUNA_PAPEL: ColunaTabela<LinhaInicial> = {
  id: 'papel',
  titulo: T.inicio.papel,
  celula: (linha) => <span className={estilos[linha.papel]}>{T.inicio.papeis[linha.papel]}</span>,
};

function colunasDasCelulas(largura: number): ColunaTabela<LinhaInicial>[] {
  return Array.from({ length: largura }, (_, i) => ({
    id: `c${String(i)}`,
    titulo: T.inicio.coluna(i + 1),
    celula: (linha: LinhaInicial) => linha.celulas[i],
  }));
}

/** As primeiras linhas como estão no arquivo, para conferir (e escolher) a linha do cabeçalho. */
export default function InicioArquivo({ metadados }: Readonly<{ metadados: MetadadosLeitura }>) {
  const inicio = descreverLinhasIniciais(metadados);
  if (inicio === null) return null;
  return (
    <Card titulo={T.inicio.titulo} subtitulo={T.inicio.subtitulo}>
      <Tabela
        legenda={T.inicio.legenda}
        colunas={[COLUNA_NUMERO, COLUNA_PAPEL, ...colunasDasCelulas(inicio.largura)]}
        linhas={inicio.linhas}
        chave={(linha) => String(linha.numero)}
        destacada={(linha) => linha.papel === 'cabecalho'}
      />
    </Card>
  );
}
