import { Suspense } from 'react';
import { Outlet } from 'react-router';
import { juntarClasses } from '../../shared/lib/classes';
import { useSessao } from '../../shared/sessao/useSessao';
import EstadoCarregando from '../../shared/ui/EstadoCarregando';
import { TEXTOS_APP } from '../textos';
import BarraEtapas from './BarraEtapas';
import Cabecalho from './Cabecalho';
import estilos from './LayoutApp.module.css';
import { useBarraRecolhivel } from './useBarraRecolhivel';
import { useSessaoExpirada } from './useSessaoExpirada';

export default function LayoutApp() {
  const { dataset } = useSessao();
  const barra = useBarraRecolhivel();
  useSessaoExpirada();

  return (
    <div
      className={juntarClasses(
        estilos.app,
        (barra.recolhida || barra.sobreposta) && estilos.estreita,
      )}
    >
      <a href="#conteudo" className={estilos.pular}>
        {TEXTOS_APP.pularParaConteudo}
      </a>
      <BarraEtapas
        recolhida={barra.recolhida}
        sobreposta={barra.sobreposta}
        aoAlternar={barra.alternar}
      />
      {barra.sobreposta ? (
        <button
          type="button"
          tabIndex={-1}
          className={estilos.fundo}
          aria-label={TEXTOS_APP.fecharBarra}
          onClick={barra.recolher}
        />
      ) : null}
      <div className={estilos.coluna}>
        {/* M1.6: passar nLinhas/nColunas do resumo do dataset (react-query). */}
        <Cabecalho nomeArquivo={dataset?.nomeArquivo} />
        <main id="conteudo" className={estilos.principal}>
          <Suspense fallback={<EstadoCarregando mensagem={TEXTOS_APP.abrindoEtapa} />}>
            <Outlet />
          </Suspense>
        </main>
      </div>
    </div>
  );
}
