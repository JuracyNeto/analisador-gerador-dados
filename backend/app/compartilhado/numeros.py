"""Formatação de números no padrão pt-BR (vírgula decimal, ponto de milhar)."""

import math

CASAS_SIGNIFICATIVAS_PADRAO = 4


def _trocar_separadores(texto: str) -> str:
    """Converte '1,234.5' (formato do Python) em '1.234,5'."""
    return texto.replace(",", "_").replace(".", ",").replace("_", ".")


def casas_para_significativos(valor: float, casas_significativas: int) -> int:
    """Casas decimais que mantêm `casas_significativas` dígitos, sem cortar a parte inteira."""
    if valor == 0 or not math.isfinite(valor):
        return 0
    ordem = math.floor(math.log10(abs(valor)))
    return max(0, casas_significativas - 1 - ordem)


def formatar_numero(valor: float, casas_significativas: int = CASAS_SIGNIFICATIVAS_PADRAO) -> str:
    """Número com até 4 dígitos significativos, sem zeros à direita: 70,31 · 12.346 · 0,001235."""
    casas = casas_para_significativos(valor, casas_significativas)
    texto = f"{valor:,.{casas}f}"
    if "." in texto:
        texto = texto.rstrip("0").rstrip(".")
    return _trocar_separadores(texto)


def formatar_inteiro(valor: int) -> str:
    """Inteiro com ponto de milhar: 1.234."""
    return _trocar_separadores(f"{valor:,d}")


def formatar_percentual(valor: float, casas: int = 1) -> str:
    """Percentual já na escala 0–100: 21,6%."""
    return _trocar_separadores(f"{valor:,.{casas}f}") + "%"


def formatar_fixo(valor: float, casas: int) -> str:
    """Número com casas decimais fixas: 60,0 · 1.234,50 (limites de classe)."""
    return _trocar_separadores(f"{valor:,.{casas}f}")


P_VALOR_MINIMO = 0.001


def formatar_p_valor(p: float) -> str:
    """ "p < 0,001" para valores muito pequenos; senão "p = 0,213" (3 algarismos)."""
    if p < P_VALOR_MINIMO:
        return "p < 0,001"
    return f"p = {formatar_numero(p, 3)}"
