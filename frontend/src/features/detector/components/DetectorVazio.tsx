import { useState } from 'react';
import { useNavigate } from 'react-router';
import { CAMINHOS } from '../../../shared/navegacao/caminhos';
import Botao from '../../../shared/ui/Botao';
import Drawer from '../../../shared/ui/Drawer';
import Icone from '../../../shared/ui/Icone';
import { REGRAS_DETECTOR, TEXTOS_DETECTOR } from '../textos';
import estilos from './DetectorVazio.module.css';

const T = TEXTOS_DETECTOR;

function DrawerRegras({ aberto, aoFechar }: Readonly<{ aberto: boolean; aoFechar: () => void }>) {
  return (
    <Drawer
      aberto={aberto}
      aoFechar={aoFechar}
      titulo={T.regras.titulo}
      subtitulo={T.regras.subtitulo}
      rotuloCorpo={T.regras.rotuloCorpo}
    >
      <ol className={estilos.regras}>
        {REGRAS_DETECTOR.map((regra) => (
          <li key={regra.regra}>
            <strong className={estilos.nome}>
              {T.regra({ regra: regra.regra, nome_regra: regra.nome })}
            </strong>
            <p className={estilos.intuicao}>{regra.intuicao}</p>
          </li>
        ))}
      </ol>
    </Drawer>
  );
}

/** Estado vazio (7c): nenhum alerta, com o texto da API, "Ver as 11 regras" e o próximo passo. */
export default function DetectorVazio({ texto }: Readonly<{ texto: string | null }>) {
  const navegar = useNavigate();
  const [regrasAbertas, setRegrasAbertas] = useState(false);
  return (
    <section className={estilos.vazio}>
      <span className={estilos.circulo}>
        <Icone nome="verified" tamanho={34} />
      </span>
      <h2 className={estilos.titulo}>{T.vazio.titulo}</h2>
      <p className={estilos.texto}>{texto ?? T.vazio.textoPadrao}</p>
      <div className={estilos.acoes}>
        <Botao
          variante="secundario"
          onClick={() => {
            setRegrasAbertas(true);
          }}
        >
          {T.vazio.verRegras}
        </Botao>
        <Botao
          iconeFinal="arrow_forward"
          onClick={() => {
            void navegar(CAMINHOS.relatorio);
          }}
        >
          {T.navegacao.continuar}
        </Botao>
      </div>
      <DrawerRegras
        aberto={regrasAbertas}
        aoFechar={() => {
          setRegrasAbertas(false);
        }}
      />
    </section>
  );
}
