"""Textos do gerador (spec 11 e 16): métodos, estatísticas, parâmetros e "Como geramos"."""

from collections.abc import Callable
from dataclasses import dataclass

from app.compartilhado.numeros import formatar_numero, formatar_percentual
from app.compartilhado.textos import quantidade

NOMES_METODOS = {
    "normal": "Normal com reescala",
    "kde": "KDE com reescala",
    "poisson": "Poisson",
    "empirica": "Empírica",
    "normal_inteira": "Normal arredondada",
    "bernoulli": "Bernoulli",
    "frequencias": "Sorteio pelas frequências",
    "cholesky": "Cholesky",
}
ESTATISTICA_N = "n"
ESTATISTICAS_NUMERICAS = (
    (ESTATISTICA_N, "n"),
    ("Média", "media"),
    ("Mediana", "mediana"),
    ("Desvio padrão", "desvio_padrao"),
    ("Mínimo", "minimo"),
    ("Máximo", "maximo"),
    ("Assimetria", "assimetria"),
    ("Curtose", "curtose"),
)
SIM, NAO = "Sim", "Não"
COLUNA_SEM_ORIGEM = "valor"
NOMES_SEM_ORIGEM = ("x", "y")
MODOS = {"preservar": "Preservar estatísticas", "parametros": "Novos parâmetros"}
PARAMETROS_MANUAIS = "Parâmetros manuais"


def estatistica_frequencia(categoria: str) -> str:
    return f"fr% · {categoria}"


def estatisticas_par(x: str, y: str) -> tuple[str, ...]:
    return (
        ESTATISTICA_N,
        f"Média de {x}",
        f"Média de {y}",
        f"Desvio padrão de {x}",
        f"Desvio padrão de {y}",
        "Correlação (r)",
    )


def numero(valor: float) -> str:
    return formatar_numero(valor)


@dataclass(frozen=True, slots=True)
class ContextoExplicacao:
    """O que a frase "Como geramos" precisa saber de uma geração univariada."""

    metodo: str
    quantidade: int
    semente: int
    coluna: str | None = None
    media: float | None = None
    desvio: float | None = None
    chance: float | None = None
    sucesso: str | None = None
    fracasso: str | None = None
    casas: int | None = None
    faixa: tuple[float, float] | None = None
    sem_negativos: bool = False
    preservar: bool = False


def _de_coluna(contexto: ContextoExplicacao) -> str:
    return f" de {contexto.coluna}" if contexto.coluna else ""


def _em_coluna(contexto: ContextoExplicacao) -> str:
    return f" em {contexto.coluna}" if contexto.coluna else ""


def _semente(contexto: ContextoExplicacao) -> str:
    return f"usando a semente {contexto.semente}"


def _quantos(contexto: ContextoExplicacao) -> str:
    return quantidade(contexto.quantidade, "valor", "valores")


def _medidas(contexto: ContextoExplicacao) -> str:
    media, desvio = numero(contexto.media or 0.0), numero(contexto.desvio or 0.0)
    if contexto.preservar:
        return f"a mesma média ({media}) e desvio padrão ({desvio}){_de_coluna(contexto)}"
    return f"média {media} e desvio padrão {desvio}"


def _normal(contexto: ContextoExplicacao) -> str:
    return (
        f"Sorteamos {_quantos(contexto)} de uma curva Normal com {_medidas(contexto)}, "
        f"{_semente(contexto)}. Depois, ajustamos os valores para bater exatamente essas medidas."
    )


def _kde(contexto: ContextoExplicacao) -> str:
    return (
        f"Os dados{_de_coluna(contexto)} não seguem uma curva Normal. Sorteamos "
        f"{_quantos(contexto)} parecidos com os originais (estimativa de densidade, KDE), "
        f"{_semente(contexto)}, e ajustamos a média ({numero(contexto.media or 0.0)}) "
        f"e o desvio padrão ({numero(contexto.desvio or 0.0)})."
    )


def _poisson(contexto: ContextoExplicacao) -> str:
    media = numero(contexto.media or 0.0)
    return (
        f"A média ({media}) e a variância{_de_coluna(contexto)} são parecidas, como numa "
        f"distribuição de Poisson. Sorteamos {_quantos(contexto)} de uma Poisson com média "
        f"{media}, {_semente(contexto)}."
    )


def _empirica(contexto: ContextoExplicacao) -> str:
    return (
        f"Sorteamos {_quantos(contexto)} entre os que aparecem{_em_coluna(contexto)}, cada um "
        f"com a mesma frequência relativa do original, {_semente(contexto)}."
    )


def _normal_inteira(contexto: ContextoExplicacao) -> str:
    final = ", sem valores negativos, como no original" if contexto.sem_negativos else ""
    return (
        f"Sorteamos {_quantos(contexto)} de uma curva Normal com {_medidas(contexto)}, "
        f"{_semente(contexto)}. Depois, arredondamos para inteiros{final}."
    )


def _bernoulli(contexto: ContextoExplicacao) -> str:
    chance = formatar_percentual((contexto.chance or 0.0) * 100)
    origem = " (a mesma proporção do original)" if contexto.preservar else ""
    return (
        f"Sorteamos {_quantos(contexto)}: cada um é {contexto.sucesso} com chance de "
        f"{chance}{origem} ou {contexto.fracasso} nos demais casos, {_semente(contexto)}."
    )


def _frequencias(contexto: ContextoExplicacao) -> str:
    return (
        f"Sorteamos {_quantos(contexto)} entre as categorias{_de_coluna(contexto)}, cada uma "
        f"com a mesma frequência relativa do original, {_semente(contexto)}."
    )


FRASES: dict[str, Callable[[ContextoExplicacao], str]] = {
    "normal": _normal,
    "kde": _kde,
    "poisson": _poisson,
    "empirica": _empirica,
    "normal_inteira": _normal_inteira,
    "bernoulli": _bernoulli,
    "frequencias": _frequencias,
}
METODOS_COM_CASAS = frozenset({"normal", "kde"})


def frase_casas(casas: int | None, preservar: bool) -> str:
    """Frase do arredondamento; vazia quando não houve arredondamento."""
    if casas is None:
        return ""
    como = ", como no original" if preservar else ""
    if casas == 0:
        return f"Arredondamos para inteiros{como}."
    return f"Arredondamos com {quantidade(casas, 'casa decimal', 'casas decimais')}{como}."


def frase_faixa(faixa: tuple[float, float] | None) -> str:
    if faixa is None:
        return ""
    return f"Sorteamos de novo os valores fora de {numero(faixa[0])} a {numero(faixa[1])}."


def explicacao_univariada(contexto: ContextoExplicacao) -> str:
    """Até 3 frases curtas: método, arredondamento e faixa (spec 11, print 6a)."""
    partes = [FRASES[contexto.metodo](contexto)]
    if contexto.metodo in METODOS_COM_CASAS:
        partes.append(frase_casas(contexto.casas, contexto.preservar))
    partes.append(frase_faixa(contexto.faixa))
    return " ".join(parte for parte in partes if parte)


@dataclass(frozen=True, slots=True)
class ContextoPares:
    n: int
    x: str
    y: str
    media_x: float
    media_y: float
    desvio_x: float
    desvio_y: float
    rho: float
    semente: int
    exato: bool


AJUSTE_EXATO = (
    "Com o ajuste exato, as médias, os desvios e a correlação dos dados gerados ficam "
    "exatamente iguais aos pedidos; por isso, não arredondamos os valores."
)


def explicacao_bivariada(contexto: ContextoPares) -> str:
    """Cholesky em linguagem simples, com o efeito do ajuste exato."""
    x, y = contexto.x, contexto.y
    inicio = (
        f"Sorteamos {quantidade(contexto.n, 'par', 'pares')} de duas curvas Normais e as "
        f"combinamos (método de Cholesky), usando a semente {contexto.semente}. Assim, {y} "
        f"acompanha {x} com correlação {numero(contexto.rho)}; {x} tem média "
        f"{numero(contexto.media_x)} e desvio padrão {numero(contexto.desvio_x)}, e {y}, "
        f"média {numero(contexto.media_y)} e desvio padrão {numero(contexto.desvio_y)}."
    )
    if contexto.exato:
        return f"{inicio} {AJUSTE_EXATO}"
    return (
        f"{inicio} Sem o ajuste exato, a correlação obtida varia um pouco em torno de "
        f"{numero(contexto.rho)}, como numa amostra real."
    )
