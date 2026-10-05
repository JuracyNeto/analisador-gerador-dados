import { useQuery } from '@tanstack/react-query';
import { Suspense } from 'react';
import { Outlet } from 'react-router';
import { opcoesPrimeiraPagina } from '../../shared/api/dataset';
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
  const { data: resumo } = useQuery({
    ...opcoesPrimeiraPagina(dataset?.id ?? null),
    select: (pagina) => pagina.resumo,
  });
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
        <Cabecalho
          nomeArquivo={dataset?.nomeArquivo}
          nLinhas={resumo?.n_linhas}
          nColunas={resumo?.n_colunas}
        />
        <main id="conteudo" className={estilos.principal}>
          <Suspense fallback={<EstadoCarregando mensagem={TEXTOS_APP.abrindoEtapa} />}>
            <Outlet />
          </Suspense>
        </main>
      </div>
    </div>
  );
}
