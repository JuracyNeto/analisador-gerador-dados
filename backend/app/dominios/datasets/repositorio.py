"""Repositório em memória: dataset_id → Dataset (ADR 0004)."""

from collections import OrderedDict

from app.dominios.datasets import erros
from app.dominios.datasets.modelos import Dataset


class RepositorioDatasets:
    """Guarda até `limite` datasets; ao passar do limite, o mais antigo é descartado."""

    def __init__(self, limite: int) -> None:
        self._limite = limite
        self._itens: OrderedDict[str, Dataset] = OrderedDict()

    def __len__(self) -> int:
        return len(self._itens)

    def adicionar(self, dataset: Dataset) -> None:
        self._itens[dataset.id] = dataset
        while len(self._itens) > self._limite:
            self._itens.popitem(last=False)

    def obter(self, dataset_id: str) -> Dataset:
        dataset = self._itens.get(dataset_id)
        if dataset is None:
            raise erros.dataset_nao_encontrado()
        return dataset

    def remover(self, dataset_id: str) -> None:
        self.obter(dataset_id)
        del self._itens[dataset_id]
