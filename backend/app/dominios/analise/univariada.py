"""Monta a análise univariada de uma coluna: tabela, medidas, aplicabilidade e fórmulas."""

from dataclasses import fields

from app.compartilhado.tipos import TIPOS_NUMERICOS, TipoVariavel
from app.dominios.analise import textos
from app.dominios.analise.dispersao import dispersao
from app.dominios.analise.formulas import formulas_usadas
from app.dominios.analise.frequencias import tabela_frequencia
from app.dominios.analise.montagem_forma import (
    ContextoForma,
    aplicavel_forma,
    forma_da_amostra,
    formulas_forma,
    nao_aplicaveis_forma,
)
from app.dominios.analise.resultados import (
    Amostra,
    Analise,
    Dispersao,
    Medida,
    NaoAplicavel,
    Separatrizes,
    TabelaFrequencia,
    Tendencia,
)
from app.dominios.analise.separatrizes import separatrizes
from app.dominios.analise.tendencia import tendencia

FORMULAS_DE_CLASSES = ("sturges", "amplitude_classe", "ponto_medio")
INTERPRETACOES_DE_MEDIDAS = ("proporcao", "desvio_padrao", "cv")


def _medidas(tend: Tendencia, disp: Dispersao | None) -> dict[str, Medida]:
    """Medidas com nome; as de dispersão só entram se a dispersão se aplica ao tipo."""
    medidas = {
        "media": tend.media,
        "mediana": tend.mediana,
        "moda_czuber": tend.moda_czuber,
        "proporcao": tend.proporcao,
    }
    if disp is None:
        return medidas
    for campo in fields(disp):
        valor = getattr(disp, campo.name)
        if isinstance(valor, Medida):
            medidas[campo.name] = valor
    return medidas


def _secao(item: str, tipo: TipoVariavel) -> NaoAplicavel:
    return NaoAplicavel(item, textos.nao_se_aplica(item, tipo, item))


def _nao_aplicaveis(
    amostra: Amostra,
    tabela: TabelaFrequencia,
    medidas: dict[str, Medida],
    seps: Separatrizes | None,
) -> tuple[NaoAplicavel, ...]:
    """Tudo que não se aplica aparece com motivo (princípio 3 do design, D46)."""
    itens = [NaoAplicavel(nome, m.motivo or "") for nome, m in medidas.items() if not m.aplicavel]
    if tabela.motivo_acumulada:
        itens.insert(0, NaoAplicavel("acumulada", tabela.motivo_acumulada))
    if seps is None:
        itens.append(_secao("separatrizes", amostra.tipo))
    if amostra.tipo not in TIPOS_NUMERICOS:
        itens.append(_secao("posicao", amostra.tipo))
    if "amplitude" not in medidas:
        itens.append(_secao("dispersao", amostra.tipo))
    return tuple(itens)


def _aplicavel(
    amostra: Amostra,
    tabela: TabelaFrequencia,
    medidas: dict[str, Medida],
    seps: Separatrizes | None,
) -> dict[str, bool]:
    def ok(item: str) -> bool:
        return item in medidas and medidas[item].aplicavel

    return {
        "acumulada": tabela.acumulada_aplicavel,
        "media": ok("media"),
        "mediana": ok("mediana"),
        "moda_czuber": ok("moda_czuber"),
        "proporcao": ok("proporcao"),
        "separatrizes": seps is not None,
        "posicao": amostra.tipo in TIPOS_NUMERICOS,
        "dispersao": "amplitude" in medidas,
        "variancia": ok("variancia"),
        "cv": ok("cv"),
    }


def _numero(medida: Medida | None) -> float | None:
    return medida.valor if medida is not None and isinstance(medida.valor, float) else None


def _interpretacoes(medidas: dict[str, Medida]) -> tuple[str, ...]:
    """Frases automáticas das specs 05 e 07."""
    frases: list[str | None] = []
    media, mediana, desvio = (
        _numero(medidas.get(i)) for i in ("media", "mediana", "desvio_padrao")
    )
    if media is not None and mediana is not None and desvio is not None:
        frases.append(textos.interpretar_media_mediana(media, mediana, desvio))
    frases += [medidas[i].interpretacao for i in INTERPRETACOES_DE_MEDIDAS if i in medidas]
    return tuple(f for f in frases if f)


def _chaves_de_formulas(
    amostra: Amostra, tabela: TabelaFrequencia, medidas: dict[str, Medida]
) -> list[str | None]:
    chaves: list[str | None] = ["frequencia_relativa", "moda"]
    if tabela.acumulada_aplicavel:
        chaves.append("frequencia_acumulada")
    if amostra.tipo == TipoVariavel.CONTINUA:
        chaves += FORMULAS_DE_CLASSES
    if amostra.tipo in TIPOS_NUMERICOS:
        chaves += ["quantil", "posicao_percentil"]
    return chaves + [m.formula for m in medidas.values() if m.aplicavel]


def analisar_amostra(
    amostra: Amostra,
    classes: int | None = None,
    sucesso: str | None = None,
    tentativas: int | None = None,
) -> Analise:
    """Frequências, tendência, separatrizes, dispersão e forma, com motivos e fórmulas."""
    tabela = tabela_frequencia(amostra, classes)
    tend = tendencia(amostra, tabela, sucesso)
    seps = separatrizes(amostra)
    disp = dispersao(amostra, seps, tend.proporcao)
    forma = forma_da_amostra(amostra, ContextoForma(tabela, tend, seps), tentativas)
    medidas = _medidas(tend, disp)
    nao_aplicaveis = _nao_aplicaveis(amostra, tabela, medidas, seps)
    chaves = _chaves_de_formulas(amostra, tabela, medidas) + formulas_forma(forma)
    return Analise(
        coluna=amostra.coluna,
        tipo=amostra.tipo,
        n=amostra.n,
        n_faltantes=amostra.n_faltantes,
        aplicavel=_aplicavel(amostra, tabela, medidas, seps) | aplicavel_forma(forma),
        nao_aplicavel=nao_aplicaveis + tuple(nao_aplicaveis_forma(amostra, forma)),
        frequencias=tabela,
        tendencia=tend,
        separatrizes=seps,
        dispersao=disp,
        interpretacoes=_interpretacoes(medidas),
        formulas=formulas_usadas(chaves),
        forma=forma,
    )
