"""Forma e distribuição de uma coluna, por tipo (spec 09); nominal e ordinal ficam sem forma."""

from collections.abc import Callable
from dataclasses import dataclass

import numpy as np

from app.compartilhado.tipos import TipoVariavel
from app.dominios.analise import textos_forma
from app.dominios.analise.distribuicoes import (
    ajuste_bernoulli,
    ajuste_binomial,
    ajuste_normal,
)
from app.dominios.analise.forma import (
    assimetria,
    classificar_assimetria,
    classificar_curtose,
    curtose,
    curtose_percentilica,
    pearson,
)
from app.dominios.analise.resultados import (
    Ajuste,
    Amostra,
    Forma,
    Medida,
    NaoAplicavel,
    Separatrizes,
    TabelaFrequencia,
    Tendencia,
    TesteAderencia,
    ajuste_nao_aplicavel,
    nao_aplicavel,
)

MIN_NORMAL_DISCRETA = 30
MEDIDAS_FORMA = (
    "assimetria",
    "assimetria_pearson_1",
    "assimetria_pearson_2",
    "curtose",
    "curtose_percentilica",
)
TESTE_QUI_QUADRADO = textos_forma.TESTE_QUI_QUADRADO


@dataclass(frozen=True, slots=True)
class ContextoForma:
    """O que a forma reaproveita da análise já feita (classes, moda, mediana, separatrizes)."""

    tabela: TabelaFrequencia
    tendencia: Tendencia
    separatrizes: Separatrizes | None


@dataclass(frozen=True, slots=True)
class _Medidas:
    assimetria: Medida
    pearson_1: Medida
    pearson_2: Medida
    curtose: Medida
    percentilica: Medida


def _numero(medida: Medida) -> float | None:
    return medida.valor if medida.aplicavel and isinstance(medida.valor, float) else None


def _moda_para_pearson(amostra: Amostra, tendencia: Tendencia) -> float | None:
    """D98: Czuber na contínua (sempre única); moda bruta na discreta, só se unimodal."""
    if amostra.tipo == TipoVariavel.CONTINUA:
        return _numero(tendencia.moda_czuber)
    moda = tendencia.moda
    unica = moda.classificacao == "unimodal" and isinstance(moda.valores[0], float)
    return float(moda.valores[0]) if unica else None


def _medidas_numericas(valores: np.ndarray, amostra: Amostra, contexto: ContextoForma) -> _Medidas:
    mediana = _numero(contexto.tendencia.mediana)
    if mediana is None:
        mediana = float(np.median(valores))
    as1, as2 = pearson(valores, _moda_para_pearson(amostra, contexto.tendencia), mediana)
    seps = contexto.separatrizes
    motivo_k = textos_forma.nao_calculavel("curtose_percentilica", "poucos_4")
    return _Medidas(
        assimetria=assimetria(valores),
        pearson_1=as1,
        pearson_2=as2,
        curtose=curtose(valores),
        percentilica=curtose_percentilica(seps) if seps else nao_aplicavel(motivo_k),
    )


def _aderencia(normal: Ajuste, binomial: Ajuste) -> tuple[str, TesteAderencia] | None:
    """A frase conjunta cita a Normal quando houver teste; senão a Binomial."""
    if normal.teste is not None:
        return "Normal", normal.teste
    if binomial.teste is not None and binomial.distribuicao == "binomial":
        return "Binomial", binomial.teste
    return None


def _montar(medidas: _Medidas, normal: Ajuste, binomial: Ajuste) -> Forma:
    g1, g2 = _numero(medidas.assimetria), _numero(medidas.curtose)
    classe_assimetria = classificar_assimetria(g1) if g1 is not None else None
    classe_curtose = classificar_curtose(g2) if g2 is not None else None
    tentativas = next((int(p.valor) for p in binomial.parametros if p.simbolo == "n"), None)
    return Forma(
        assimetria=medidas.assimetria,
        assimetria_pearson_1=medidas.pearson_1,
        assimetria_pearson_2=medidas.pearson_2,
        curtose=medidas.curtose,
        curtose_percentilica=medidas.percentilica,
        normal=normal,
        binomial=binomial,
        classificacao_assimetria=classe_assimetria[0] if classe_assimetria else None,
        sentido_assimetria=classe_assimetria[1] if classe_assimetria else None,
        classificacao_curtose=classe_curtose,
        tentativas=tentativas,
        interpretacao=textos_forma.frase_conjunta(
            classe_assimetria, classe_curtose, _aderencia(normal, binomial)
        ),
    )


def _valores(amostra: Amostra) -> np.ndarray:
    return amostra.valores.to_numpy(dtype="float64")


def _continua(amostra: Amostra, contexto: ContextoForma, _tentativas: int | None) -> Forma:
    valores = _valores(amostra)
    motivo = textos_forma.nao_se_aplica_ao_tipo("binomial", amostra.tipo, "binomial_continua")
    return _montar(
        _medidas_numericas(valores, amostra, contexto),
        ajuste_normal(valores, contexto.tabela),
        ajuste_nao_aplicavel("binomial", motivo),
    )


def _normal_discreta(valores: np.ndarray) -> Ajuste:
    if len(valores) < MIN_NORMAL_DISCRETA:
        motivo = textos_forma.nao_calculavel("normal", "normal_discreta")
        return ajuste_nao_aplicavel("normal", motivo)
    return ajuste_normal(valores, None)


def _discreta(amostra: Amostra, contexto: ContextoForma, tentativas: int | None) -> Forma:
    valores = _valores(amostra)
    return _montar(
        _medidas_numericas(valores, amostra, contexto),
        _normal_discreta(valores),
        ajuste_binomial(valores, tentativas),
    )


def _binaria(amostra: Amostra, contexto: ContextoForma, _tentativas: int | None) -> Forma:
    """Valores são categorias: só a Bernoulli com a proporção da spec 05 (D95)."""
    tipo = amostra.tipo
    medidas = {
        item: nao_aplicavel(textos_forma.nao_se_aplica_ao_tipo(item, tipo, "categorias"))
        for item in MEDIDAS_FORMA
    }
    motivo_normal = textos_forma.nao_se_aplica_ao_tipo("normal", tipo, "normal_binaria")
    p = _numero(contexto.tendencia.proporcao) or 0.0
    return _montar(
        _Medidas(*medidas.values()),
        ajuste_nao_aplicavel("normal", motivo_normal),
        ajuste_bernoulli(p),
    )


type Montador = Callable[[Amostra, ContextoForma, int | None], Forma]

FORMAS: dict[TipoVariavel, Montador] = {
    TipoVariavel.CONTINUA: _continua,
    TipoVariavel.DISCRETA: _discreta,
    TipoVariavel.BINARIA: _binaria,
}


def forma_da_amostra(
    amostra: Amostra, contexto: ContextoForma, tentativas: int | None = None
) -> Forma | None:
    """Forma por tipo (tabela de despacho); nominal e ordinal → None."""
    montar = FORMAS.get(amostra.tipo)
    return montar(amostra, contexto, tentativas) if montar else None


def _medidas_da_forma(forma: Forma) -> dict[str, Medida]:
    return {item: getattr(forma, item) for item in MEDIDAS_FORMA}


def aplicavel_forma(forma: Forma | None) -> dict[str, bool]:
    """Chaves novas de `Analise.aplicavel` (contrato do M2)."""
    if forma is None:
        return dict.fromkeys(("forma", "assimetria", "curtose", "normal", "binomial"), False)
    return {
        "forma": True,
        "assimetria": forma.assimetria.aplicavel,
        "curtose": forma.curtose.aplicavel,
        "normal": forma.normal.aplicavel,
        "binomial": forma.binomial.aplicavel,
    }


def nao_aplicaveis_forma(amostra: Amostra, forma: Forma | None) -> list[NaoAplicavel]:
    """Sem forma: o item `forma` com o motivo da spec 09; com forma: cada medida ou ajuste."""
    if forma is None:
        motivo = textos_forma.nao_se_aplica_ao_tipo("forma", amostra.tipo, "exige_numeros")
        return [NaoAplicavel("forma", motivo)]
    medidas = _medidas_da_forma(forma).items()
    itens = [NaoAplicavel(nome, m.motivo or "") for nome, m in medidas if not m.aplicavel]
    ajustes = (forma.normal, forma.binomial)
    return itens + [
        NaoAplicavel(a.distribuicao, a.motivo or "") for a in ajustes if not a.aplicavel
    ]


def _usa_qui_quadrado(ajuste: Ajuste) -> bool:
    testes = (ajuste.teste, ajuste.complementar)
    return any(t is not None and t.nome == TESTE_QUI_QUADRADO for t in testes)


def formulas_forma(forma: Forma | None) -> list[str | None]:
    """Chaves das fórmulas das medidas e ajustes aplicáveis (e do χ² quando usado)."""
    if forma is None:
        return []
    chaves = [m.formula for m in _medidas_da_forma(forma).values() if m.aplicavel]
    ajustes = [a for a in (forma.normal, forma.binomial) if a.aplicavel]
    chaves += [a.formula for a in ajustes]
    if any(_usa_qui_quadrado(a) for a in ajustes):
        chaves.append("qui_quadrado")
    return chaves
