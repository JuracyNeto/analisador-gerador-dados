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


class Formula(BaseModel):
    """Fórmula em LaTeX e em texto de reserva: análise e gerador usam o mesmo contrato (D152)."""

    model_config = ConfigDict(from_attributes=True)

    chave: str
    nome: str
    latex: str
    texto: str
