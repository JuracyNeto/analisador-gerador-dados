from dataclasses import replace

from app.compartilhado.tipos import Formula
from app.dominios.relatorio.apendice import montar_apendice
from app.dominios.relatorio.conteudo import (
    AvisoRelatorio,
    BlocoAnalises,
    ConteudoRelatorio,
    FormulaApendice,
    SecaoBivariada,
    SecaoColuna,
    SecaoDetector,
    SecaoForma,
    SecaoGerador,
)

MEDIA = Formula("media", "Média", r"\bar{x}", "x̄ = Σxᵢ / n")
MEDIANA = Formula("mediana", "Mediana", "Md", "Md = valor central")
CZUBER = Formula("moda_czuber", "Moda de Czuber", "Mo", "Mo = Lᵢ + …")
PROPORCAO = Formula("proporcao", "Proporção", "p", "p = sucessos / n")
ASSIMETRIA = Formula("assimetria", "Assimetria (Fisher)", "G_1", "G₁ = …")
PEARSON = Formula("pearson", "Correlação de Pearson", "r", "r = …")
CHOLESKY = Formula("cholesky", "Pares com correlação (Cholesky)", "X", "X = μx + σx·Z₁")
ORDEM = ("proporcao", "media", "mediana", "moda_czuber", "assimetria")
VAZIO = ConteudoRelatorio("a.csv", "18/10/2026", "a.csv", "")


def _bloco(*formulas: Formula) -> BlocoAnalises:
    return BlocoAnalises((), (), (), None, (), None, formulas)


def _coluna(nome: str, analises: BlocoAnalises | None, forma: SecaoForma | None) -> SecaoColuna:
    return SecaoColuna(nome, "Quantitativa contínua", 10, 0, analises, forma)


def _aviso(formula: FormulaApendice | None, colunas: tuple[str, ...] = ()) -> AvisoRelatorio:
    return AvisoRelatorio(
        "info", "ℹ️ Informativo", "R4 · …", "", "", None, "", "", (), None, formula, colunas
    )


def test_grupos_na_ordem_do_documento_e_sem_repetir() -> None:
    colunas = (
        _coluna("sexo", _bloco(PROPORCAO), None),
        _coluna("peso", _bloco(MEDIA, MEDIANA, CZUBER), SecaoForma(formulas=(ASSIMETRIA,))),
        _coluna("idade", _bloco(MEDIANA, MEDIA), SecaoForma(formulas=(ASSIMETRIA,))),
    )
    bivariada = SecaoBivariada(None, "", (), None, (PEARSON,))
    gerador = SecaoGerador("", (), "", "", (), (), None, (CHOLESKY,))
    r4 = FormulaApendice("R4 · Valores redondos", "P(X ≥ k)")
    r5 = FormulaApendice("R5 · Duplicatas", "P(X ≥ k | λ)")
    avisos = (_aviso(r4, ("peso",)), _aviso(r5), _aviso(r4, ("idade", "peso")), _aviso(None))
    detector = SecaoDetector("", "", "", avisos, (), None)

    apendice = montar_apendice(
        replace(VAZIO, colunas=colunas, bivariada=bivariada, gerador=gerador, detector=detector),
        ORDEM,
    )

    assert apendice is not None
    assert [g.titulo for g in apendice.grupos] == [
        "Análise por coluna",
        "Forma e distribuição",
        "Bivariada",
        "Gerador",
        "Detector",
    ]
    analise, forma, par, geracao, alertas = apendice.grupos
    assert [(f.nome, f.onde) for f in analise.formulas] == [
        ("Proporção", "em sexo"),
        ("Média", "em peso e idade"),
        ("Mediana", "em peso e idade"),
        ("Moda de Czuber", "em peso"),
    ]
    assert [(f.nome, f.onde) for f in forma.formulas] == [
        ("Assimetria (Fisher)", "em todas as colunas")
    ]
    assert [(f.nome, f.latex, f.onde) for f in par.formulas] == [
        ("Correlação de Pearson", "r", None)
    ]
    assert [f.texto for f in geracao.formulas] == ["X = μx + σx·Z₁"]
    assert alertas.formulas == (
        FormulaApendice("R4 · Valores redondos", "P(X ≥ k)", onde="em peso e idade"),
        r5,
    )


def test_formula_em_todas_as_colunas_diz_todas() -> None:
    colunas = (_coluna("a", _bloco(MEDIA), None), _coluna("b", _bloco(MEDIA), None))

    apendice = montar_apendice(replace(VAZIO, colunas=colunas), ORDEM)

    assert apendice is not None
    assert apendice.grupos[0].formulas[0].onde == "em todas as colunas"


def test_chave_fora_do_catalogo_vai_para_o_fim() -> None:
    estranha = Formula("outra", "Outra", "o", "o")
    colunas = (_coluna("a", _bloco(estranha, MEDIA), None),)

    apendice = montar_apendice(replace(VAZIO, colunas=colunas), ORDEM)

    assert apendice is not None
    assert [f.nome for f in apendice.grupos[0].formulas] == ["Média", "Outra"]


def test_sem_formulas_nas_secoes_nao_ha_apendice() -> None:
    colunas = (_coluna("cidade", _bloco(), SecaoForma(motivo="Não se aplica.")),)

    assert montar_apendice(replace(VAZIO, leitura="Arquivo CSV.", colunas=colunas), ORDEM) is None
