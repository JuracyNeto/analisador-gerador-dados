import { type ReactNode, useCallback, useEffect, useMemo, useState } from 'react';
import { ContextoSessao } from './contextoSessao';
import {
  SESSAO_VAZIA,
  carregarSessao,
  comEtapaVisitada,
  comGerado,
  salvarSessao,
} from './persistencia';
import type { DatasetSessao, GeradoSessao, ValorSessao } from './tipos';

interface PropsSessaoProvider {
  children: ReactNode;
}

export default function SessaoProvider({ children }: Readonly<PropsSessaoProvider>) {
  const [estado, setEstado] = useState(carregarSessao);

  useEffect(() => {
    salvarSessao(estado);
  }, [estado]);

  // Trocar de dataset (inclusive "Usar como novo dataset") mantém a última geração.
  const definirDataset = useCallback((dataset: DatasetSessao) => {
    setEstado((anterior) =>
      comGerado({ dataset, etapasVisitadas: [] }, anterior.ultimoGerado ?? null),
    );
  }, []);
  const definirUltimoGerado = useCallback((gerado: GeradoSessao) => {
    setEstado((anterior) => comGerado(anterior, gerado));
  }, []);
  const encerrar = useCallback(() => {
    setEstado(SESSAO_VAZIA);
  }, []);
  const marcarVisitada = useCallback((etapa: number) => {
    setEstado((anterior) => comEtapaVisitada(anterior, etapa));
  }, []);

  const etapasVisitadas = useMemo(() => new Set(estado.etapasVisitadas), [estado.etapasVisitadas]);
  const ultimoGerado = estado.ultimoGerado ?? null;
  const valor = useMemo<ValorSessao>(
    () => ({
      dataset: estado.dataset,
      definirDataset,
      ultimoGerado,
      definirUltimoGerado,
      encerrar,
      etapasVisitadas,
      marcarVisitada,
    }),
    [
      estado.dataset,
      definirDataset,
      ultimoGerado,
      definirUltimoGerado,
      encerrar,
      etapasVisitadas,
      marcarVisitada,
    ],
  );

  return <ContextoSessao value={valor}>{children}</ContextoSessao>;
}
