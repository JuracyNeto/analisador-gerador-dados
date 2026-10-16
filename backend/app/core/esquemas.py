"""Modelos de contrato usados por mais de um domínio (OpenAPI com um nome só)."""

from typing import Any

from pydantic import BaseModel, ConfigDict


class Figura(BaseModel):
    """Figura Plotly pronta (ADR 0003): análise, bivariada e gerador usam o mesmo contrato."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    rotulo: str
    titulo: str
    resumo: str
    porque: str
    recomendado: bool
    dados: dict[str, Any]
