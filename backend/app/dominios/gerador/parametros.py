"""Lista de parâmetros de uma geração, já em texto (tela 6 e relatório)."""

from dataclasses import dataclass

from app.compartilhado.numeros import formatar_inteiro
from app.dominios.gerador import textos
from app.dominios.gerador.resultados import Parametro


@dataclass(frozen=True, slots=True)
class DescricaoUnivariada:
    origem: str
    quantidade: int
    modo: str
    semente: int
    media: float | None = None
    desvio: float | None = None
    sucesso: str | None = None
    chance: float | None = None
    limitar_faixa: bool = False


def _opcionais(descricao: DescricaoUnivariada) -> list[Parametro]:
    itens: list[Parametro] = []
    if descricao.media is not None:
        itens.append(Parametro("Média", textos.numero(descricao.media)))
    if descricao.desvio is not None:
        itens.append(Parametro("Desvio", textos.numero(descricao.desvio)))
    if descricao.chance is not None:
        itens.append(Parametro(f"Chance de {descricao.sucesso}", textos.numero(descricao.chance)))
    if descricao.limitar_faixa:
        itens.append(Parametro("Limitar à faixa original", textos.SIM))
    return itens


def parametros_univariados(descricao: DescricaoUnivariada) -> tuple[Parametro, ...]:
    """Origem, quantidade, modo, medidas usadas, faixa e semente."""
    return (
        Parametro("Origem", descricao.origem),
        Parametro("Quantidade", formatar_inteiro(descricao.quantidade)),
        Parametro("Modo", textos.MODOS[descricao.modo]),
        *_opcionais(descricao),
        Parametro("Semente", str(descricao.semente)),
    )


@dataclass(frozen=True, slots=True)
class DescricaoBivariada:
    origem: str
    contexto: textos.ContextoPares


def parametros_bivariados(descricao: DescricaoBivariada) -> tuple[Parametro, ...]:
    pares = descricao.contexto
    return (
        Parametro("Origem", descricao.origem),
        Parametro("Pares", formatar_inteiro(pares.n)),
        Parametro(f"Média de {pares.x}", textos.numero(pares.media_x)),
        Parametro(f"Média de {pares.y}", textos.numero(pares.media_y)),
        Parametro(f"Desvio de {pares.x}", textos.numero(pares.desvio_x)),
        Parametro(f"Desvio de {pares.y}", textos.numero(pares.desvio_y)),
        Parametro("Correlação alvo (ρ)", textos.numero(pares.rho)),
        Parametro("Ajuste exato", textos.SIM if pares.exato else textos.NAO),
        Parametro("Semente", str(pares.semente)),
    )


def origem_coluna(colunas: tuple[str, ...], nome_arquivo: str) -> str:
    """Ex.: "peso_kg (pesquisa_saude.txt)" · "altura_m × peso_kg (pesquisa_saude.txt)"."""
    return f"{' × '.join(colunas)} ({nome_arquivo})"
