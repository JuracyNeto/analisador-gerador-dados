from pathlib import Path

from tests.scripts.apoio import RAIZ, carregar_script

VERSIONADO = RAIZ / "docs" / "relatorio-final" / "exemplo-relatorio.html"


def test_mesma_data_gera_o_mesmo_arquivo(tmp_path: Path) -> None:
    """Data fixa no cabeçalho, semente fixa no gerador e no detector: o arquivo se repete."""
    script = carregar_script("exportar_relatorio_exemplo")

    primeiro = script.gravar(tmp_path / "a.html", "20/11/2026 10:00").read_bytes()
    segundo = script.gravar(tmp_path / "b.html", "20/11/2026 10:00").read_bytes()

    assert primeiro == segundo
    assert b"<span>20/11/2026 10:00</span>" in primeiro


def test_relatorio_tem_as_9_secoes_e_a_geracao() -> None:
    html = carregar_script("exportar_relatorio_exemplo").relatorio("20/11/2026 10:00")

    titulos = (
        "Leitura do arquivo",
        "Tipos de variável",
        "Limpeza",
        "Bivariada",
        "Gerador de dados",
    )
    for titulo in (*titulos, "Detector de dados artificiais", "Fórmulas usadas"):
        assert f". {titulo}</h2>" in html, titulo
    assert "Univariado · 500 valores · semente 42" in html
    assert "cdn.plot.ly" in html


def test_versionado_veio_do_script() -> None:
    """O arquivo da pasta do relatório final é o do script, com a data em que foi gerado."""
    html = VERSIONADO.read_text(encoding="utf-8")
    data = html.split('<div class="marca"><span>Analisador e Gerador de Dados</span><span>')[1]

    assert html == carregar_script("exportar_relatorio_exemplo").relatorio(data[:16])
