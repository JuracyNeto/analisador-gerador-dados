from pathlib import Path

from app.dominios.analise import servico as analise
from app.dominios.detector import servico as detector
from app.dominios.gerador import servico as gerador
from tests.scripts.apoio import RAIZ, carregar_script

VERSIONADO = RAIZ / "docs" / "relatorio-final" / "formulas.md"


def test_script_gera_o_arquivo_versionado(tmp_path: Path) -> None:
    """Mesmos catálogos → mesmo arquivo, byte a byte (LF, UTF-8), como os exemplos (D124)."""
    caminho = carregar_script("exportar_formulas").gravar(tmp_path / "formulas.md")

    assert caminho.read_bytes() == VERSIONADO.read_bytes()


def test_todas_as_formulas_dos_catalogos_aparecem() -> None:
    """Em blocos ```math: com $$…$$, o Markdown do GitHub tira a barra de \\#, \\, e \\%."""
    texto = carregar_script("exportar_formulas").texto_das_formulas()

    for formula in [*analise.FORMULAS.values(), *gerador.FORMULAS.values()]:
        bloco = f"```math\n{formula.latex}\n```\n\nEm texto: `{formula.texto}`"
        assert bloco in texto, formula.chave
    for regra in detector.formulas_das_regras():
        assert f"### {regra.codigo} · {regra.nome}" in texto
        assert all(f"- `{formula}`" in texto for formula in regra.formulas), regra.codigo


def test_grupos_da_analise_na_ordem_das_specs() -> None:
    grupos = carregar_script("exportar_formulas").grupos_da_analise()

    assert [titulo for titulo, _ in grupos] == [
        "Frequências",
        "Tendência central",
        "Separatrizes",
        "Dispersão",
        "Forma e distribuições",
        "Correlação e regressão",
    ]
    forma = next(formulas for titulo, formulas in grupos if titulo == "Forma e distribuições")
    assert {formula.chave for formula in forma} == analise.CHAVES_FORMA
