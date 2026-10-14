from app.compartilhado.tipos import Severidade
from app.dominios.detector.regras.base import ResultadoRegra
from app.dominios.detector.resultados import Aviso, DetalhesAviso, RegraNaoAplicada
from app.dominios.detector.resumo import montar_resultado

ALTA, ATENCAO, INFO = Severidade.ALTA, Severidade.ATENCAO, Severidade.INFO


def _aviso(regra: str, severidade: Severidade, *colunas: str) -> Aviso:
    detalhes = DetalhesAviso("m", "v", "l")
    return Aviso(regra, regra, severidade, colunas, "t", "r", "p", None, "…n", "o", detalhes)


def _nao_aplicada(regra: str) -> RegraNaoAplicada:
    return RegraNaoAplicada(regra, regra, "idade", "motivo", "frase")


def _resultado(*avisos: Aviso, verificada: bool = True) -> ResultadoRegra:
    return ResultadoRegra(avisos, (), verificada)


def test_avisos_em_ordem_de_severidade_regra_e_coluna() -> None:
    resultados = [
        _resultado(_aviso("R4", ATENCAO, "peso")),
        _resultado(_aviso("R7", INFO, "idade"), _aviso("R7", ATENCAO, "altura")),
        _resultado(_aviso("R9", ATENCAO, "idade")),
        _resultado(_aviso("R5", ALTA)),
    ]

    resultado = montar_resultado(resultados)

    ordem = [(a.regra, a.colunas) for a in resultado.avisos]
    assert ordem == [
        ("R5", ()),
        ("R4", ("peso",)),
        ("R7", ("altura",)),
        ("R9", ("idade",)),
        ("R7", ("idade",)),
    ]


def test_resumo_conta_alertas_colunas_e_regras() -> None:
    resultados = [
        _resultado(_aviso("R4", ATENCAO, "peso_kg")),
        _resultado(_aviso("R5", ALTA)),
        _resultado(_aviso("R7", INFO, "altura_m"), _aviso("R7", INFO, "idade")),
        ResultadoRegra((), (_nao_aplicada("R8"),), verificada=False),
        _resultado(),
    ]

    resumo = montar_resultado(resultados).resumo

    assert resumo.total == 4
    assert (resumo.por_severidade.alta, resumo.por_severidade.atencao) == (1, 1)
    assert resumo.por_severidade.info == 2
    assert resumo.colunas_afetadas == ("peso_kg", "altura_m", "idade")
    assert (resumo.regras_verificadas, resumo.regras_nao_aplicadas) == (4, 1)
    assert resumo.frase == "Encontramos 4 alertas em 3 colunas"
    assert resumo.detalhe == (
        "peso_kg, altura_m e idade · 4 regras verificadas, 1 não se aplica a este arquivo"
    )
    assert resumo.vazio is None


def test_um_alerta_numa_coluna_usa_o_singular() -> None:
    resumo = montar_resultado([_resultado(_aviso("R9", ATENCAO, "idade"))]).resumo

    assert resumo.frase == "Encontramos 1 alerta em 1 coluna"
    assert resumo.detalhe == "idade · 1 regra verificada"


def test_alerta_so_de_linhas_inteiras_nao_conta_colunas() -> None:
    resumo = montar_resultado([_resultado(_aviso("R5", ALTA)), _resultado()]).resumo

    assert resumo.frase == "Encontramos 1 alerta"
    assert resumo.colunas_afetadas == ()


def test_sem_alertas_traz_o_texto_de_vazio() -> None:
    resultados = [_resultado(), _resultado(), _resultado(verificada=False)]

    resultado = montar_resultado(resultados)

    assert resultado.resumo.total == 0
    assert resultado.resumo.frase == "Nenhum alerta"
    assert resultado.resumo.detalhe == "2 regras verificadas, 1 não se aplica a este arquivo"
    assert resultado.resumo.vazio == (
        "Nenhuma das 3 regras encontrou suspeitas. Isso não garante que os dados sejam reais, "
        "mas não vimos sinais comuns de dados artificiais."
    )


def test_vazio_com_uma_regra_so() -> None:
    vazio = montar_resultado([_resultado()]).resumo.vazio

    assert vazio is not None
    assert vazio.startswith("A regra pedida não encontrou suspeitas.")


def test_vazio_sem_nenhuma_regra_aplicavel() -> None:
    resultados = [_resultado(verificada=False), _resultado(verificada=False)]

    resumo = montar_resultado(resultados).resumo

    assert resumo.vazio == (
        "Nenhuma das regras se aplica a este arquivo; os motivos estão em Regras não verificadas."
    )
    assert resumo.detalhe == "0 regras verificadas, 2 não se aplicam a este arquivo"


def test_nao_aplicadas_vem_na_ordem_das_regras() -> None:
    resultados = [
        ResultadoRegra((), (_nao_aplicada("R4"),), verificada=True),
        ResultadoRegra((), (_nao_aplicada("R8"),), verificada=False),
    ]

    resultado = montar_resultado(resultados)

    assert [n.regra for n in resultado.nao_aplicadas] == ["R4", "R8"]
