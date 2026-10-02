from pathlib import Path

import pytest

from tests.arquitetura.verificador import LIMITE_LINHAS, verificar

RAIZ_BACKEND = Path(__file__).resolve().parents[2]


def _criar(raiz: Path, caminho: str, conteudo: str = "") -> None:
    arquivo = raiz / caminho
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    arquivo.write_text(conteudo, encoding="utf-8")


def test_projeto_real_respeita_a_arquitetura() -> None:
    assert verificar(RAIZ_BACKEND) == []


@pytest.mark.parametrize(
    ("caminho", "conteudo", "regra"),
    [
        ("app/dominios/analise/frequencias.py", "import fastapi\n", "violacao_framework"),
        (
            "app/dominios/analise/servico.py",
            "from pydantic import BaseModel\n",
            "violacao_framework",
        ),
        (
            "app/dominios/gerador/servico.py",
            "from app.dominios.analise import frequencias\n",
            "violacao_entre_dominios",
        ),
        (
            "app/compartilhado/numeros.py",
            "from app.dominios.analise.servico import calcular\n",
            "violacao_compartilhado",
        ),
    ],
)
def test_importacoes_proibidas_sao_apontadas(
    tmp_path: Path, caminho: str, conteudo: str, regra: str
) -> None:
    _criar(tmp_path, caminho, conteudo)

    violacoes = verificar(tmp_path)

    assert [v.regra for v in violacoes] == [regra]


@pytest.mark.parametrize(
    ("caminho", "conteudo"),
    [
        ("app/dominios/analise/router.py", "from fastapi import APIRouter\n"),
        ("app/dominios/analise/schemas.py", "from pydantic import BaseModel\n"),
        ("app/dominios/gerador/servico.py", "from app.dominios.analise.servico import calcular\n"),
        (
            "app/dominios/analise/servico.py",
            "from app.dominios.analise.frequencias import tabela\n",
        ),
    ],
)
def test_importacoes_permitidas_passam(tmp_path: Path, caminho: str, conteudo: str) -> None:
    _criar(tmp_path, caminho, conteudo)

    assert verificar(tmp_path) == []


def test_arquivo_acima_do_limite_de_linhas(tmp_path: Path) -> None:
    _criar(tmp_path, "app/dominios/analise/grande.py", "x = 1\n" * (LIMITE_LINHAS + 1))

    assert [v.regra for v in verificar(tmp_path)] == ["tamanho"]
