"""Carrega os scripts de backend/scripts/ (não são pacote) para os testes."""

import importlib.util
from pathlib import Path
from types import ModuleType

RAIZ = Path(__file__).resolve().parents[3]
SCRIPTS = RAIZ / "backend" / "scripts"


def carregar_script(nome: str) -> ModuleType:
    especificacao = importlib.util.spec_from_file_location(nome, SCRIPTS / f"{nome}.py")
    assert especificacao is not None
    assert especificacao.loader is not None
    modulo = importlib.util.module_from_spec(especificacao)
    especificacao.loader.exec_module(modulo)
    return modulo
