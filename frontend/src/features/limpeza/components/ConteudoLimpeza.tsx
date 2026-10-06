import { useId } from 'react';
import { useNavigate } from 'react-router';
import { CAMINHOS } from '../../../shared/navegacao/caminhos';
import BarraAcoes from '../../../shared/ui/BarraAcoes';
import Botao from '../../../shared/ui/Botao';
import ConteudoConsulta from '../../../shared/ui/ConteudoConsulta';
import EstadoVazio from '../../../shared/ui/EstadoVazio';
import { type Limpeza, useLimpeza } from '../hooks/useLimpeza';
import { TEXTOS_LIMPEZA as T } from '../textos';
import CardsResumoLimpeza from './CardsResumoLimpeza';
import estilos from './ConteudoLimpeza.module.css';
import LimitesPorColuna from './LimitesPorColuna';
import PainelLog from './PainelLog';
import SecaoProblema from './SecaoProblema';

function AcoesLimpeza({ limpeza }: Readonly<{ limpeza: Limpeza }>) {
  const idAjuda = useId();
  const semAcoes = limpeza.pedido.acoes.length === 0;
  const temSecoes = limpeza.secoes.length > 0;
  return (
    <BarraAcoes>
      {semAcoes && temSecoes ? (
        <p id={idAjuda} className={estilos.ajuda}>
          {T.botoes.semAcoes}
        </p>
      ) : null}
      <Botao
        variante="perigo"
        tamanho="lg"
        icone="undo"
        disabled={!limpeza.podeDesfazer}
        carregando={limpeza.desfazendo}
        textoCarregando={T.botoes.desfazendo}
        onClick={limpeza.desfazerTudo}
      >
        {T.botoes.desfazer}
      </Botao>
      {temSecoes ? (
        <Botao
          tamanho="lg"
          icone="cleaning_services"
          disabled={semAcoes}
          aria-describedby={semAcoes ? idAjuda : undefined}
          carregando={limpeza.aplicando}
          textoCarregando={T.botoes.aplicando}
          onClick={limpeza.aplicarLimpeza}
        >
          {T.botoes.aplicar}
        </Botao>
      ) : null}
    </BarraAcoes>
  );
}

function SemProblemas() {
  const navegar = useNavigate();
  return (
    <EstadoVazio
      icone="verified"
      titulo={T.vazio.titulo}
      descricao={T.vazio.descricao}
      acao={
        <Botao
          iconeFinal="arrow_forward"
          onClick={() => {
            void navegar(CAMINHOS.analise);
          }}
        >
          {T.vazio.continuar}
        </Botao>
      }
    />
  );
}

export default function ConteudoLimpeza({ datasetId }: Readonly<{ datasetId: string }>) {
  const limpeza = useLimpeza(datasetId);
  return (
    <ConteudoConsulta consulta={limpeza.diagnostico} carregando={T.carregando} forma="cards">
      {(diagnostico) => (
        <div className={estilos.conteudo} aria-busy={limpeza.diagnostico.isPlaceholderData}>
          {limpeza.secoes.length > 0 ? <CardsResumoLimpeza diagnostico={diagnostico} /> : null}
          <div className={estilos.grade}>
            <div className={estilos.principal}>
              {limpeza.secoes.length > 0 ? (
                limpeza.secoes.map((s) => (
                  <SecaoProblema
                    key={s.id}
                    secao={s}
                    escolhas={limpeza.escolhas.valores}
                    aoEscolher={limpeza.escolhas.escolher}
                  />
                ))
              ) : (
                <SemProblemas />
              )}
              <LimitesPorColuna
                colunas={limpeza.colunasNumericas}
                textos={limpeza.limites.textos}
                aoMudar={limpeza.limites.alterar}
              />
              <AcoesLimpeza limpeza={limpeza} />
            </div>
            <ConteudoConsulta consulta={limpeza.resumo} carregando={T.log.carregando} forma="cards">
              {(resumo) => <PainelLog resumo={resumo} />}
            </ConteudoConsulta>
          </div>
        </div>
      )}
    </ConteudoConsulta>
  );
}
