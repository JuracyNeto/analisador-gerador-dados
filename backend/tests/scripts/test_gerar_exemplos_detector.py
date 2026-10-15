from pathlib import Path

import numpy as np

from tests.scripts.apoio import RAIZ, carregar_script

EXEMPLOS = RAIZ / "dados-exemplo"


def test_script_gera_os_arquivos_versionados(tmp_path: Path) -> None:
    """Mesma semente → mesmos arquivos, byte a byte (LF, UTF-8, `;` e vírgula decimal)."""
    caminhos = carregar_script("gerar_exemplos_detector").gravar(tmp_path)

    assert sorted(caminho.name for caminho in caminhos) == [
        "alturas_plantadas.txt",
        "alturas_reais.txt",
        "vendas_correlacao_puxada.txt",
    ]
    for caminho in caminhos:
        assert caminho.read_bytes() == (EXEMPLOS / caminho.name).read_bytes(), caminho.name


def test_bloco_alinhado_tem_a_media_e_o_desvio_do_restante() -> None:
    """Média exata e DP a menos de 0,05% do restante (no conjunto todo, o DP fica ~0,13% abaixo)."""
    script = carregar_script("gerar_exemplos_detector")
    resto, _ = script.pessoas(np.random.default_rng(1), 380)
    resto[0] += (19 - int(resto.sum()) % 19) % 19

    bloco = script.bloco_alinhado(resto, 20, 7)

    assert bloco.sum() * 380 == resto.sum() * 20
    assert abs(bloco.std(ddof=1) - resto.std(ddof=1)) / resto.std(ddof=1) < 0.0005
