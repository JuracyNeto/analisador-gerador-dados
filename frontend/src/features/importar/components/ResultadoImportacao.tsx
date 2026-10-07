import { keepPreviousData, useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router';
import { opcoesPrimeiraPagina } from '../../../shared/api/dataset';
import { CAMINHOS } from '../../../shared/navegacao/caminhos';
import Banner from '../../../shared/ui/Banner';
import BarraAcoes from '../../../shared/ui/BarraAcoes';
import Botao from '../../../shared/ui/Botao';
import ConteudoConsulta from '../../../shared/ui/ConteudoConsulta';
import type { Importacao } from '../hooks/useImportacao';
import { TEXTOS_IMPORTAR as T } from '../textos';
import CardDeteccoes from './CardDeteccoes';
import InicioArquivo from './InicioArquivo';
import PreviaDados from './PreviaDados';

interface PropsResultadoImportacao {
  datasetId: string;
  importacao: Importacao;
}

/** "Ler de novo" (só com o arquivo na memória da página) e "Continuar para Variáveis". */
function AcoesResultado({ importacao }: Readonly<{ importacao: Importacao }>) {
  const navegar = useNavigate();
  const { lerDeNovo } = importacao;
  return (
    <BarraAcoes>
      {lerDeNovo === null ? null : (
        <Botao
          variante="secundario"
          tamanho="lg"
          carregando={importacao.enviando}
          textoCarregando={T.acoes.lendo}
          onClick={lerDeNovo}
        >
          {T.acoes.lerDeNovo}
        </Botao>
      )}
      <Botao
        tamanho="lg"
        iconeFinal="arrow_forward"
        onClick={() => {
          void navegar(CAMINHOS.variaveis);
        }}
      >
        {T.acoes.continuar}
      </Botao>
    </BarraAcoes>
  );
}

/** Estado 1a. Lê da API (não da mutação) para funcionar também depois de recarregar a página. */
export default function ResultadoImportacao({
  datasetId,
  importacao,
}: Readonly<PropsResultadoImportacao>) {
  // keepPreviousData: ao reler com outra opção o id muda, mas a tela não pisca.
  const consulta = useQuery({
    ...opcoesPrimeiraPagina(datasetId),
    placeholderData: keepPreviousData,
  });
  return (
    <ConteudoConsulta consulta={consulta} carregando={T.previa.carregando} forma="tabela">
      {(pagina) => (
        <>
          {pagina.resumo.metadados.avisos.map((aviso) => (
            <Banner key={aviso.codigo} variante="atencao">
              {aviso.mensagem}
            </Banner>
          ))}
          <CardDeteccoes
            metadados={pagina.resumo.metadados}
            opcoes={importacao.opcoes}
            aoCorrigir={importacao.corrigir}
          />
          <InicioArquivo metadados={pagina.resumo.metadados} />
          <PreviaDados linhas={pagina.linhas} totalLinhas={pagina.resumo.n_linhas} />
          <AcoesResultado importacao={importacao} />
        </>
      )}
    </ConteudoConsulta>
  );
}
