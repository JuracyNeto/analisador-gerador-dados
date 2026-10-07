import BotaoEtapa from '../../../shared/navegacao/BotaoEtapa';
import { CAMINHOS } from '../../../shared/navegacao/caminhos';
import BarraAcoes from '../../../shared/ui/BarraAcoes';
import ConteudoConsulta from '../../../shared/ui/ConteudoConsulta';
import { TIPOS_VARIAVEL, type TipoVariavel } from '../../../shared/ui/tiposVariavel';
import { useToast } from '../../../shared/ui/useToast';
import { useAlterarTipo, useColunas } from '../api';
import { TEXTOS_VARIAVEIS as T } from '../textos';
import estilos from './ConteudoVariaveis.module.css';
import EditorOrdem from './EditorOrdem';
import TabelaVariaveis from './TabelaVariaveis';

const ACOES_VARIAVEIS = (
  <BarraAcoes>
    <BotaoEtapa para={CAMINHOS.importar} sentido="voltar">
      {T.voltar}
    </BotaoEtapa>
    <BotaoEtapa para={CAMINHOS.limpeza} sentido="avancar">
      {T.continuar}
    </BotaoEtapa>
  </BarraAcoes>
);

export default function ConteudoVariaveis({ datasetId }: Readonly<{ datasetId: string }>) {
  const consulta = useColunas(datasetId);
  const alterar = useAlterarTipo(datasetId);
  const toast = useToast();

  function alterarTipo(coluna: string, tipo: TipoVariavel): void {
    alterar.mutate(
      { coluna, alteracao: { tipo } },
      {
        onSuccess: () => {
          toast.mostrar({
            tipo: 'sucesso',
            titulo: T.toastTipo(coluna, TIPOS_VARIAVEL[tipo].rotuloCompleto),
          });
        },
      },
    );
  }

  function reordenar(coluna: string, categorias: string[]): void {
    alterar.mutate({ coluna, alteracao: { tipo: 'ordinal', categorias_ordem: categorias } });
  }

  return (
    <ConteudoConsulta consulta={consulta} carregando={T.carregando} forma="tabela">
      {(colunas) => (
        <div className={estilos.conteudo}>
          <TabelaVariaveis colunas={colunas} aoAlterarTipo={alterarTipo} />
          <div className={estilos.ordinais}>
            {colunas
              .filter((c) => c.tipo === 'ordinal' && c.categorias_ordem.length > 0)
              .map((c) => (
                <EditorOrdem
                  key={c.coluna}
                  coluna={c}
                  aoReordenar={(ordem) => {
                    reordenar(c.coluna, ordem);
                  }}
                />
              ))}
          </div>
          {ACOES_VARIAVEIS}
        </div>
      )}
    </ConteudoConsulta>
  );
}
