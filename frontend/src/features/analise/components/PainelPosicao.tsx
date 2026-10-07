import { textoDoErro } from '../../../shared/api/erros';
import Banner from '../../../shared/ui/Banner';
import CampoNumero from '../../../shared/ui/CampoNumero';
import Card from '../../../shared/ui/Card';
import Segmented from '../../../shared/ui/Segmented';
import type { ConsultaPosicaoNaTela } from '../hooks/useConsultaPosicao';
import { textoForaDaFaixa } from '../separatrizes';
import { TEXTOS_ANALISE } from '../textos';
import type { Posicao, TipoSeparatriz } from '../tipos';
import estilos from './PainelPosicao.module.css';
import ReguaSeparatrizes from './ReguaSeparatrizes';

const P = TEXTOS_ANALISE.posicao;
const TIPOS: readonly TipoSeparatriz[] = ['quartil', 'decil', 'percentil'];
const OPCOES_TIPO = TIPOS.map((valor) => ({ valor, rotulo: P.tipos[valor] }));

function ResultadoPosicao({ posicao }: Readonly<{ posicao: Posicao }>) {
  const fora = textoForaDaFaixa(posicao);
  return (
    <>
      {fora === null ? null : (
        <Banner variante="atencao" titulo={P.foraTitulo}>
          {fora}
        </Banner>
      )}
      <ReguaSeparatrizes posicao={posicao} />
    </>
  );
}

interface Props {
  coluna: string;
  consulta: ConsultaPosicaoNaTela;
}

export default function PainelPosicao({ coluna, consulta }: Readonly<Props>) {
  const { posicaoAtual, posicao } = consulta;

  return (
    <Card titulo={P.titulo}>
      <div className={estilos.corpo}>
        <div className={estilos.controles}>
          <CampoNumero
            rotulo={P.campo(coluna)}
            valor={consulta.texto}
            aoMudar={consulta.setTexto}
            {...(consulta.invalido ? { erro: P.erroValor } : {})}
          />
          <Segmented
            rotulo={P.comparar}
            opcoes={OPCOES_TIPO}
            valor={consulta.tipo}
            aoMudar={consulta.setTipo}
          />
        </div>
        {posicao.isError ? (
          <Banner variante="erro">{textoDoErro(posicao.error).mensagem}</Banner>
        ) : null}
        {posicaoAtual === undefined ? null : <ResultadoPosicao posicao={posicaoAtual} />}
        <p aria-live="polite" className={posicaoAtual === undefined ? estilos.dica : estilos.frase}>
          {posicaoAtual?.frase ?? P.dica}
        </p>
      </div>
    </Card>
  );
}
