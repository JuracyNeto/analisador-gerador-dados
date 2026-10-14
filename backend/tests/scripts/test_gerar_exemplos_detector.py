import importlib.util
from pathlib import Path
from types import ModuleType

import numpy as np

RAIZ = Path(__file__).resolve().parents[3]
SCRIPT = RAIZ / "backend" / "scripts" / "gerar_exemplos_detector.py"
EXEMPLOS = RAIZ / "dados-exemplo"


def _script() -> ModuleType:
    especificacao = importlib.util.spec_from_file_location("gerar_exemplos_detector", SCRIPT)
    assert especificacao is not None
    assert especificacao.loader is not None
    modulo = importlib.util.module_from_spec(especificacao)
    especificacao.loader.exec_module(modulo)
    return modulo


def test_script_gera_os_arquivos_versionados(tmp_path: Path) -> None:
    """Mesma semente → mesmos arquivos, byte a byte (LF, UTF-8, `;` e vírgula decimal)."""
    caminhos = _script().gravar(tmp_path)

    assert sorted(caminho.name for caminho in caminhos) == [
        "alturas_plantadas.txt",
        "alturas_reais.txt",
        "vendas_correlacao_puxada.txt",
    ]
    for caminho in caminhos:
        assert caminho.read_bytes() == (EXEMPLOS / caminho.name).read_bytes(), caminho.name


def test_bloco_alinhado_tem_a_media_e_o_desvio_do_conjunto() -> None:
    script = _script()
    resto, _ = script.pessoas(np.random.default_rng(1), 380)
    resto[0] += (19 - int(resto.sum()) % 19) % 19

    bloco = script.bloco_alinhado(resto, 20, 7)

    conjunto = np.concatenate([resto, bloco])
    assert bloco.sum() * 20 == conjunto.sum()
    assert abs(bloco.std(ddof=1) - conjunto.std(ddof=1)) / conjunto.std(ddof=1) < 0.001
