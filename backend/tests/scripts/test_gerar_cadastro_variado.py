from pathlib import Path

from tests.scripts.apoio import RAIZ, carregar_script

VERSIONADO = RAIZ / "backend" / "tests" / "fixtures" / "cadastro_variado.txt"


def test_script_gera_o_cadastro_versionado(tmp_path: Path) -> None:
    caminho = carregar_script("gerar_cadastro_variado").gravar(tmp_path / "cadastro.txt")

    assert caminho.read_bytes() == VERSIONADO.read_bytes()


def test_cada_coluna_tem_o_seu_sorteio() -> None:
    """Tirar (ou acrescentar) uma coluna não muda as outras."""
    script = carregar_script("gerar_cadastro_variado")
    completo = [linha.split(";") for linha in script.texto_do_cadastro().splitlines()]
    script.COLUNAS.pop("celular")

    sem_celular = [linha.split(";") for linha in script.texto_do_cadastro().splitlines()]

    indice = completo[0].index("saldo")
    assert [linha[indice] for linha in completo] == [linha[indice - 1] for linha in sem_celular]
