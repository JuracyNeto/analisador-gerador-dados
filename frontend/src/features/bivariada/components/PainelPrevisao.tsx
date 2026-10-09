import { textoDoErro } from '../../../shared/api/erros';
import { formatarNumero } from '../../../shared/lib/formatar';
import Banner from '../../../shared/ui/Banner';
import Botao from '../../../shared/ui/Botao';
import CampoNumero from '../../../shared/ui/CampoNumero';
import Card from '../../../shared/ui/Card';
import { usePrevisao } from '../hooks/usePrevisao';
import { TEXTOS_BIVARIADA } from '../textos';
import type { Par, Previsao } from '../tipos';
import estilos from './PainelPrevisao.module.css';

const P = TEXTOS_BIVARIADA.previsao;

function Resultado({ previsao, y }: Readonly<{ previsao: Previsao; y: string }>) {
  return (
    <>
      <div className={estilos.resultado}>
        <span className={estilos.rotulo}>{P.previsto(y)}</span>
        <span className={estilos.valor}>{formatarNumero(previsao.y_previsto)}</span>
      </div>
      {previsao.aviso === null ? null : (
        <Banner variante="atencao" titulo={P.foraTitulo}>
          {previsao.aviso}
        </Banner>
      )}
    </>
  );
}

interface Props {
  datasetId: string;
  par: Par;
}

/** Tela 5a: "Prever Y para X =" com o resultado e o aviso de extrapolação. */
export default function PainelPrevisao({ datasetId, par }: Readonly<Props>) {
  const { texto, mudarTexto, erro, prever, consulta } = usePrevisao(datasetId, par);
  const previsao = consulta.data;

  return (
    <Card titulo={P.titulo}>
      <div className={estilos.corpo}>
        <form
          className={estilos.controles}
          noValidate
          onSubmit={(evento) => {
            evento.preventDefault();
            prever();
          }}
        >
          <CampoNumero rotulo={par.x} valor={texto} aoMudar={mudarTexto} erro={erro} />
          <Botao type="submit" carregando={consulta.isFetching} textoCarregando={P.prevendo}>
            {P.prever}
          </Botao>
        </form>
        {consulta.isError ? (
          <Banner variante="erro">{textoDoErro(consulta.error).mensagem}</Banner>
        ) : null}
        {previsao === undefined ? null : <Resultado previsao={previsao} y={par.y} />}
        <p aria-live="polite" className={estilos.frase}>
          {previsao?.frase ?? P.dica}
        </p>
      </div>
    </Card>
  );
}
