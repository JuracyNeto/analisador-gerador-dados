"""Barras de exemplo compartilhadas pelos testes de figuras."""

from app.dominios.graficos.entradas import Barra

VALORES = (
    Barra("1", 2, 20.0, 20.0, valor=1.0),
    Barra("2", 5, 50.0, 70.0, valor=2.0),
    Barra("3", 3, 30.0, 100.0, valor=3.0),
)
CLASSES = (
    Barra("2,0 ⊢ 3,9", 2, 40.0, 40.0, inferior=2.0, superior=3.9),
    Barra("3,9 ⊢ 5,8", 3, 60.0, 100.0, inferior=3.9, superior=5.8),
)
