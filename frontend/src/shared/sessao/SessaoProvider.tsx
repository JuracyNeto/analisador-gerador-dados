import { type ReactNode, useCallback, useEffect, useMemo, useState } from 'react';
import { ContextoSessao } from './contextoSessao';
import { SESSAO_VAZIA, carregarSessao, comEtapaVisitada, salvarSessao } from './persistencia';
import type { DatasetSessao, ValorSessao } from './tipos';

interface PropsSessaoProvider {
  children: ReactNode;
}

export default function SessaoProvider({ children }: Readonly<PropsSessaoProvider>) {
  const [estado, setEstado] = useState(carregarSessao);

  useEffect(() => {
    salvarSessao(estado);
  }, [estado]);

  const definirDataset = useCallback((dataset: DatasetSessao) => {
    setEstado({ dataset, etapasVisitadas: [] });
  }, []);
  const encerrar = useCallback(() => {
    setEstado(SESSAO_VAZIA);
  }, []);
  const marcarVisitada = useCallback((etapa: number) => {
    setEstado((anterior) => comEtapaVisitada(anterior, etapa));
  }, []);

  const etapasVisitadas = useMemo(() => new Set(estado.etapasVisitadas), [estado.etapasVisitadas]);
  const valor = useMemo<ValorSessao>(
    () => ({ dataset: estado.dataset, definirDataset, encerrar, etapasVisitadas, marcarVisitada }),
    [estado.dataset, definirDataset, encerrar, etapasVisitadas, marcarVisitada],
  );

  return <ContextoSessao value={valor}>{children}</ContextoSessao>;
}
