"""Mede os tempos da spec 00 pela API (TestClient), com CSVs sintéticos de 8 colunas.

Metas: análise de uma coluna < 2 s; detector completo < 10 s com 10 mil linhas.
Fora do CI (o tempo depende da máquina). Uso, em backend/:
    python scripts/medir_desempenho.py                      # 10 mil e 100 mil linhas
    python scripts/medir_desempenho.py --linhas 10000 --perfil 1   # cProfile acima de 1 s
"""

import argparse
import cProfile
import io
import pstats
import sys
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any
from unittest import mock

import numpy as np
from fastapi import routing
from fastapi.testclient import TestClient
from httpx import Response

from app.main import create_app

SEMENTE = 2026
META_COLUNA_S = 2.0
META_DETECTOR_S = 10.0
LINHAS_META_DETECTOR = 10_000
TIPOS_FORA_DA_ANALISE = {"identificador", "data"}
CIDADES = ("Goiânia", "Anápolis", "Aparecida de Goiânia", "Rio Verde", "Luziânia")
SATISFACAO = ("ruim", "regular", "bom", "ótimo")
HTTP_SUCESSO = {200, 201}
ACIMA_DA_META = "ACIMA DA META"


@dataclass(frozen=True, slots=True)
class Medida:
    """Tempo de uma etapa; `meta` em segundos quando a spec 00 define uma."""

    etapa: str
    segundos: float
    meta: float | None = None

    @property
    def situacao(self) -> str:
        if self.meta is None:
            return ""
        return "ok" if self.segundos < self.meta else ACIMA_DA_META


def gerar_csv(n: int, semente: int) -> bytes:
    """CSV com id, data, binária, nominal, ordinal, discreta e duas contínuas correlacionadas."""
    rng = np.random.default_rng(semente)
    datas = np.datetime64("2020-01-01") + np.sort(rng.integers(0, 2_000, n))
    altura = rng.normal(1.70, 0.09, n).round(2)
    peso = (altura * 95 - 92 + rng.normal(0, 8, n)).round(1)
    colunas = {
        "id": np.arange(1, n + 1).astype(str),
        "data": [str(d) for d in datas],
        "sexo": rng.choice(["F", "M"], n),
        "cidade": rng.choice(CIDADES, n),
        "satisfacao": rng.choice(SATISFACAO, n),
        "filhos": rng.poisson(1.5, n).astype(str),
        "altura_m": altura.astype(str),
        "peso_kg": peso.astype(str),
    }
    linhas = [";".join(colunas)]
    linhas += [";".join(valores) for valores in zip(*colunas.values(), strict=True)]
    return ("\n".join(linhas) + "\n").encode("utf-8")


def cronometrar(chamada: Callable[[], Response]) -> tuple[float, Response]:
    """Executa a chamada e devolve (segundos, resposta); falha se a API não respondeu 200/201."""
    inicio = time.perf_counter()
    resposta = chamada()
    segundos = time.perf_counter() - inicio
    if resposta.status_code not in HTTP_SUCESSO:
        raise RuntimeError(f"{resposta.request.url} → {resposta.status_code}: {resposta.text}")
    return segundos, resposta


def perfilar(chamada: Callable[[], Response], linhas: int = 25) -> str:
    """Top das funções por tempo acumulado (cProfile) do endpoint chamado.

    O TestClient roda o endpoint em outra thread, que o cProfile não vê: o perfil entra pela
    função com que o FastAPI chama os endpoints síncronos.
    """
    perfil = cProfile.Profile()
    original = routing.run_in_threadpool

    async def com_perfil(funcao: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        return await original(perfil.runcall, funcao, *args, **kwargs)

    with mock.patch.object(routing, "run_in_threadpool", com_perfil):
        chamada()
    saida = io.StringIO()
    pstats.Stats(perfil, stream=saida).sort_stats("cumulative").print_stats(linhas)
    return saida.getvalue()


type Chamadas = dict[str, Callable[[], Response]]


def medir(cliente: TestClient, n: int, semente: int) -> tuple[list[Medida], Chamadas]:
    """Importa o CSV de n linhas e mede cada etapa; devolve as medidas e as chamadas (perfil)."""
    conteudo = gerar_csv(n, semente)
    arquivo = {"arquivo": (f"desempenho_{n}.csv", conteudo, "text/csv")}
    etapa_leitura = f"leitura ({decimal(len(conteudo) / 1e6, 1)} MB)"
    chamadas: Chamadas = {etapa_leitura: lambda: cliente.post("/api/datasets", files=arquivo)}
    segundos, resposta = cronometrar(chamadas[etapa_leitura])
    medidas = [Medida(etapa_leitura, segundos)]
    base = f"/api/datasets/{resposta.json()['dataset_id']}"
    analises: Chamadas = {
        f"análise de {c['coluna']} ({c['tipo']})": _get(
            cliente, f"{base}/colunas/{c['coluna']}/analise"
        )
        for c in cliente.get(f"{base}/colunas").json()
        if c["tipo"] not in TIPOS_FORA_DA_ANALISE
    }
    metas = dict.fromkeys(analises, META_COLUNA_S)
    if n <= LINHAS_META_DETECTOR:
        metas["detector completo"] = META_DETECTOR_S
    chamadas |= analises | {
        "bivariada (altura_m × peso_kg)": _get(cliente, f"{base}/bivariada?x=altura_m&y=peso_kg"),
        "matriz de correlação": _get(cliente, f"{base}/correlacoes"),
        "detector completo": _get(cliente, f"{base}/detector"),
        "relatório (com internet)": _get(cliente, f"{base}/relatorio?offline=false"),
        "relatório (funciona sem internet)": _get(cliente, f"{base}/relatorio?offline=true"),
    }
    medidas += [
        Medida(etapa, cronometrar(chamada)[0], metas.get(etapa))
        for etapa, chamada in chamadas.items()
        if etapa != etapa_leitura
    ]
    return medidas, chamadas


def _get(cliente: TestClient, url: str) -> Callable[[], Response]:
    return lambda: cliente.get(url)


def decimal(valor: float, casas: int) -> str:
    """Número com vírgula decimal (pt-BR)."""
    return f"{valor:.{casas}f}".replace(".", ",")


def imprimir(n: int, medidas: list[Medida]) -> None:
    print(f"\n## {n:,} linhas × 8 colunas".replace(",", "."))
    print(f"{'etapa':<44} {'tempo':>9}  {'meta':>6}  situação")
    for m in medidas:
        meta = f"< {m.meta:.0f} s" if m.meta is not None else ""
        print(f"{m.etapa:<44} {decimal(m.segundos, 2):>7} s  {meta:>6}  {m.situacao}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--linhas", type=int, nargs="+", default=[10_000, 100_000])
    parser.add_argument("--semente", type=int, default=SEMENTE)
    parser.add_argument(
        "--perfil",
        type=float,
        metavar="SEGUNDOS",
        help="mostra o cProfile das etapas acima da meta ou mais lentas que SEGUNDOS",
    )
    args = parser.parse_args()
    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(encoding="utf-8")  # o console do Windows não é UTF-8
    cliente = TestClient(create_app())
    for n in args.linhas:
        medidas, chamadas = medir(cliente, n, args.semente)
        imprimir(n, medidas)
        limite = float("inf") if args.perfil is None else args.perfil
        lentas = [m.etapa for m in medidas if m.situacao == ACIMA_DA_META or m.segundos > limite]
        for etapa in lentas if args.perfil is not None else []:
            print(f"\n### Perfil: {etapa}\n{perfilar(chamadas[etapa])}")


if __name__ == "__main__":
    main()
