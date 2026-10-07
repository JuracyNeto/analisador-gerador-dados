import { keepPreviousData, useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router';
import { opcoesPrimeiraPagina, type PaginaDataset } from '../../../shared/api/dataset';
import { CAMINHOS } from '../../../shared/navegacao/caminhos';
import Banner from '../../../shared/ui/Banner';
import BarraAcoes from '../../../shared/ui/BarraAcoes';
import Botao from '../../../shared/ui/Botao';
import ConteudoConsulta from '../../../shared/ui/ConteudoConsulta';
import { type Releitura, useReleitura } from '../hooks/useReleitura';
import { TEXTOS_IMPORTAR as T } from '../textos';
import CardDeteccoes from './CardDeteccoes';
import InicioArquivo from './InicioArquivo';
import PreviaDados from './PreviaDados';

/** "Ler de novo" (detecta tudo outra vez) e "Continuar para Variáveis". */
function AcoesResultado({ releitura }: Readonly<{ releitura: Releitura }>) {
  const navegar = useNavigate();
  return (
    <BarraAcoes>
      <Botao
        variante="secundario"
        tamanho="lg"
        carregando={releitura.lendo}
        textoCarregando={T.acoes.lendo}
        onClick={releitura.lerDeNovo}
      >
        {T.acoes.lerDeNovo}
      </Botao>
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

/** Aviso antes de reler quando há tipos corrigidos ou limpeza aplicada (D88). */
function ConfirmarReleitura({ releitura }: Readonly<{ releitura: Releitura }>) {
  const acoes = (
    <>
      <Botao tamanho="sm" onClick={releitura.confirmar}>
        {T.releitura.confirmar}
      </Botao>
      <Botao variante="secundario" tamanho="sm" onClick={releitura.cancelar}>
        {T.releitura.cancelar}
      </Botao>
    </>
  );
  return (
    <Banner variante="atencao" titulo={T.releitura.aviso} acoes={acoes}>
      {T.releitura.detalhe}
    </Banner>
  );
}

function ConteudoResultado({ pagina }: Readonly<{ pagina: PaginaDataset }>) {
  const { metadados, opcoes_leitura: opcoes } = pagina.resumo;
  const releitura = useReleitura(pagina.resumo);
  return (
    <>
      {metadados.avisos.map((aviso) => (
        <Banner key={aviso.codigo} variante="atencao">
          {aviso.mensagem}
        </Banner>
      ))}
      {releitura.aguardandoConfirmacao ? <ConfirmarReleitura releitura={releitura} /> : null}
      <CardDeteccoes metadados={metadados} opcoes={opcoes} aoCorrigir={releitura.corrigir} />
      <InicioArquivo metadados={metadados} />
      <PreviaDados linhas={pagina.linhas} totalLinhas={pagina.resumo.n_linhas} />
      <AcoesResultado releitura={releitura} />
    </>
  );
}

/** Estado 1a. Lê da API (não da mutação) para funcionar também depois de recarregar a página. */
export default function ResultadoImportacao({ datasetId }: Readonly<{ datasetId: string }>) {
  // keepPreviousData: ao trocar de arquivo ou reler, a tela não pisca.
  const consulta = useQuery({
    ...opcoesPrimeiraPagina(datasetId),
    placeholderData: keepPreviousData,
  });
  return (
    <ConteudoConsulta consulta={consulta} carregando={T.previa.carregando} forma="tabela">
      {(pagina) => <ConteudoResultado pagina={pagina} />}
    </ConteudoConsulta>
  );
}
