"""Gerações em memória (ADR 0004): gerado_id → Gerado, com limite e descarte do mais antigo."""

from collections import OrderedDict
from typing import Protocol

from app.dominios.gerador import erros


class ComId(Protocol):
    @property
    def gerado_id(self) -> str: ...


class RepositorioGerados[T: ComId]:
    """Guarda até `limite` gerações; ao passar do limite, a mais antiga é descartada."""

    def __init__(self, limite: int) -> None:
        self._limite = limite
        self._itens: OrderedDict[str, T] = OrderedDict()

    def __len__(self) -> int:
        return len(self._itens)

    def adicionar(self, gerado: T) -> None:
        self._itens[gerado.gerado_id] = gerado
        while len(self._itens) > self._limite:
            self._itens.popitem(last=False)

    def obter(self, gerado_id: str) -> T:
        gerado = self._itens.get(gerado_id)
        if gerado is None:
            raise erros.gerado_nao_encontrado()
        return gerado
