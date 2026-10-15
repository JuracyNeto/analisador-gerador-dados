import Botao from '../../../shared/ui/Botao';
import Icone from '../../../shared/ui/Icone';
import { useVerNaTabela } from '../hooks/contextoVerNaTabela';
import { TEXTOS_DETECTOR } from '../textos';
import type { Aviso } from '../tipos';
import estilos from './CartaoAlerta.module.css';
import DetalhesTecnicos from './DetalhesTecnicos';

const T = TEXTOS_DETECTOR.cartao;

/** Parte 5: linhas e valores concretos + "Ver na tabela" (abre o drawer da página). */
function ExemploAlerta({ aviso }: Readonly<{ aviso: Aviso }>) {
  const verNaTabela = useVerNaTabela();
  if (aviso.exemplo === null) return null;
  return (
    <div className={estilos.exemplo}>
      <div className={estilos.textoExemplo}>
        <span className={estilos.sobrelinha}>{T.exemplo}</span>
        <span className={estilos.valoresExemplo}>{aviso.exemplo.texto}</span>
      </div>
      {verNaTabela === null ? null : (
        <Botao
          variante="secundario"
          tamanho="sm"
          icone="table_view"
          onClick={() => {
            verNaTabela(aviso);
          }}
        >
          {T.verNaTabela}
        </Botao>
      )}
    </div>
  );
}

/** Partes 4 a 8: por que chama atenção, pode ser normal, exemplo, o que fazer e detalhes. */
export default function ExplicacaoAlerta({ aviso }: Readonly<{ aviso: Aviso }>) {
  return (
    <>
      <div className={estilos.grade}>
        <div className={estilos.bloco}>
          <span className={estilos.sobrelinha}>{T.porQue}</span>
          <p>{aviso.por_que}</p>
        </div>
        <div className={estilos.bloco}>
          <span className={estilos.sobrelinha}>{T.podeSerNormal}</span>
          <p>{aviso.pode_ser_normal}</p>
        </div>
      </div>
      <ExemploAlerta aviso={aviso} />
      <p className={estilos.fazer}>
        <Icone nome="arrow_forward" className={estilos.seta} />
        <span>
          <strong>{T.oQueFazer}</strong> {aviso.o_que_fazer}
        </span>
      </p>
      <DetalhesTecnicos aviso={aviso} />
    </>
  );
}
