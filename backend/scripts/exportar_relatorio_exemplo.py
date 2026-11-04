"""Gera o exemplo do relatório HTML do relatório final (D169), sem servidor (TestClient).

Importa `pesquisa_saude.txt`, aplica a limpeza sugerida (a primeira opção de cada linha da
tela Limpeza: mediana ou moda nos faltantes, remover os duplicados, tirar os valores fora de
faixa e unificar as grafias), gera 500 valores de peso_kg preservando as medidas (semente 42)
e pede o relatório com as 9 seções, com o Plotly e o KaTeX pelo CDN (arquivo pequeno). A data
do cabeçalho vem de --data, para o arquivo se repetir.

Uso (em backend/): python scripts/exportar_relatorio_exemplo.py --data "20/11/2026 10:00"
"""

import argparse
import re
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient

from app.main import create_app

SAIDA = Path(__file__).resolve().parents[2] / "docs" / "relatorio-final" / "exemplo-relatorio.html"
COLUNA_GERADA = "peso_kg"
VALORES_GERADOS = 500
SEMENTE = 42
DATA_DO_CABECALHO = re.compile(
    r'(<div class="marca"><span>Analisador e Gerador de Dados</span><span>)[^<]*(</span>)'
)


def _primeiro_valor_sugerido(sugeridos: dict[str, Any]) -> str:
    """Como na tela: mediana; sem mediana (texto), moda."""
    return "preencher_mediana" if sugeridos["mediana"] is not None else "preencher_moda"


def acoes_sugeridas(diagnostico: dict[str, Any]) -> list[dict[str, Any]]:
    """A primeira opção de cada linha da tela Limpeza, na ordem das seções."""
    faltantes = [
        {
            "problema": "faltantes",
            "acao": _primeiro_valor_sugerido(f["sugeridos"]),
            "coluna": f["coluna"],
        }
        for f in diagnostico["faltantes"]
    ]
    duplicados = (
        [{"problema": "duplicados", "acao": "remover"}] if diagnostico["duplicados"] else []
    )
    fora_de_faixa = [
        {
            "problema": "fora_de_faixa",
            "acao": "marcar_faltante",
            "coluna": item["coluna"],
            "limites": {"min": item["limite_inferior"], "max": item["limite_superior"]},
        }
        for item in diagnostico["fora_de_faixa"]
    ]
    grafias = [
        {
            "problema": "inconsistencia",
            "acao": "unificar",
            "coluna": item["coluna"],
            "grupo": g["forma_preferida"],
        }
        for item in diagnostico["inconsistencias"]
        for g in item["grupos"]
    ]
    return [*faltantes, *duplicados, *fora_de_faixa, *grafias]


def relatorio(data: str) -> str:
    """O HTML do relatório do exemplo, com `data` no cabeçalho."""
    cliente = TestClient(create_app())
    dataset_id = cliente.post("/api/datasets/exemplo").json()["dataset_id"]
    diagnostico = cliente.get(f"/api/datasets/{dataset_id}/diagnostico").json()
    acoes = acoes_sugeridas(diagnostico)
    cliente.post(f"/api/datasets/{dataset_id}/limpeza", json={"acoes": acoes}).raise_for_status()
    pedido = {
        "origem": {"dataset_id": dataset_id, "coluna": COLUNA_GERADA},
        "x": VALORES_GERADOS,
        "semente": SEMENTE,
    }
    gerado = cliente.post("/api/gerador/univariado", json=pedido).json()
    resposta = cliente.get(
        f"/api/datasets/{dataset_id}/relatorio", params={"gerado": gerado["gerado_id"]}
    )
    resposta.raise_for_status()
    return DATA_DO_CABECALHO.sub(rf"\g<1>{data}\g<2>", resposta.text, count=1)


def gravar(saida: Path, data: str) -> Path:
    saida.parent.mkdir(parents=True, exist_ok=True)
    with saida.open("w", encoding="utf-8", newline="\n") as arquivo:
        arquivo.write(relatorio(data))
    return saida


def main() -> None:
    parser = argparse.ArgumentParser(description="Gera o exemplo do relatório HTML.")
    parser.add_argument("--data", required=True, help='Data do cabeçalho, ex.: "20/11/2026 10:00"')
    parser.add_argument("--saida", type=Path, default=SAIDA)
    argumentos = parser.parse_args()
    print(f"Gravado {gravar(argumentos.saida, argumentos.data)}")


if __name__ == "__main__":
    main()
