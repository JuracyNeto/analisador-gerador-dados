import { useState } from 'react';
import SemDataset from '../../shared/sessao/SemDataset';
import { useSessao } from '../../shared/sessao/useSessao';
import Botao from '../../shared/ui/Botao';
import PaginaEtapa from '../../shared/ui/PaginaEtapa';
import { useDetector } from './api';
import ConteudoDetector from './components/ConteudoDetector';
import DrawerLinhas from './components/DrawerLinhas';
import { ContextoVerNaTabela } from './hooks/contextoVerNaTabela';
import { useFiltrosDetector } from './hooks/useFiltrosDetector';
import { TEXTOS_DETECTOR } from './textos';
import type { Aviso } from './tipos';

const ETAPA_DETECTOR = 7;
const T = TEXTOS_DETECTOR;

interface Props {
  datasetId: string;
  nomeArquivo: string;
}

function DetectorDoDataset({ datasetId, nomeArquivo }: Readonly<Props>) {
  const consulta = useDetector(datasetId);
  const filtros = useFiltrosDetector();
  const [avisoNaTabela, setAvisoNaTabela] = useState<Aviso | null>(null);
  const analisarDeNovo = (
    <Botao
      variante="secundario"
      icone="refresh"
      carregando={consulta.isFetching}
      textoCarregando={T.analisando}
      onClick={() => {
        void consulta.refetch();
      }}
    >
      {T.analisarDeNovo}
    </Botao>
  );
  return (
    <ContextoVerNaTabela value={setAvisoNaTabela}>
      <PaginaEtapa
        etapa={ETAPA_DETECTOR}
        titulo={T.titulo}
        ajuda={T.ajuda}
        acoesTopo={analisarDeNovo}
      >
        <ConteudoDetector consulta={consulta} filtros={filtros} nomeArquivo={nomeArquivo} />
        <DrawerLinhas
          datasetId={datasetId}
          aviso={avisoNaTabela}
          aoFechar={() => {
            setAvisoNaTabela(null);
          }}
        />
      </PaginaEtapa>
    </ContextoVerNaTabela>
  );
}

/** Etapa 7 (telas 7a–7d). */
export default function PaginaDetector() {
  const { dataset } = useSessao();
  return dataset === null ? (
    <PaginaEtapa etapa={ETAPA_DETECTOR} titulo={T.titulo} ajuda={T.ajuda}>
      <SemDataset descricao={T.semDataset} />
    </PaginaEtapa>
  ) : (
    <DetectorDoDataset datasetId={dataset.id} nomeArquivo={dataset.nomeArquivo} />
  );
}
