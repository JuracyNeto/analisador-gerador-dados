"""Fachada do domínio relatorio: junta leitura, tipos, limpeza e análises num HTML (spec 13)."""

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime
from itertools import combinations

from app.compartilhado.numeros import formatar_com_sinal, formatar_p_valor, formatar_percentual
from app.compartilhado.tipos import TIPOS_AUXILIARES, TipoVariavel
from app.core.erros import EntradaInvalida
from app.dominios.analise.servico import (
    CHAVES_FORMA,
    Ajuste,
    Analise,
    Bivariada,
    Figura,
    Forma,
    Formula,
    Medida,
    ServicoAnalise,
)
from app.dominios.datasets.servico import Resumo, ServicoDatasets
from app.dominios.graficos.servico import codigo_plotlyjs, endereco_plotlyjs_cdn, figura_html
from app.dominios.relatorio import textos
from app.dominios.relatorio.conteudo import (
    SECOES_PADRAO,
    BlocoAnalises,
    ConteudoRelatorio,
    DadosLeitura,
    FiguraRelatorio,
    FormulaTexto,
    ItemMedida,
    LinhaTipo,
    ParRelatorio,
    Secao,
    SecaoBivariada,
    SecaoColuna,
    SecaoForma,
)
from app.dominios.relatorio.montagem import renderizar

__all__ = ["SECOES_PADRAO", "PedidoRelatorio", "Secao", "ServicoRelatorio", "pares_mais_fortes"]

FORMATO_DATA = "%d/%m/%Y %H:%M"
ESCAPE_FECHAMENTO = r"<\/script"
CABECALHOS_PRIMEIRA_COLUNA = {
    TipoVariavel.CONTINUA: "Classe",
    TipoVariavel.DISCRETA: "Valor",
}
# A seção da coluna aparece com qualquer uma das duas caixas (D106).
SECOES_POR_COLUNA: frozenset[Secao] = frozenset({"analises", "distribuicoes"})
# Spec 10: a partir de |r| = 0,3 a correlação é moderada; só esses pares entram (D106).
CORRELACAO_MINIMA = 0.3
PARES_NO_RELATORIO = 3
# Par sem dados suficientes fica de fora, como as colunas vazias na seção de análises.
ERROS_DO_PAR = frozenset({"POUCOS_PARES", "SEM_VARIACAO"})


@dataclass(frozen=True, slots=True)
class PedidoRelatorio:
    """O que entra no relatório; sem colunas = todas as analisáveis."""

    secoes: tuple[Secao, ...] = SECOES_PADRAO
    colunas: tuple[str, ...] | None = None
    offline: bool = False


def _script_plotly(offline: bool) -> str:
    if offline:
        return f"<script>{codigo_plotlyjs().replace('</script', ESCAPE_FECHAMENTO)}</script>"
    return f'<script src="{endereco_plotlyjs_cdn()}"></script>'


def _leitura(resumo: Resumo) -> str:
    m = resumo.metadados
    dados = DadosLeitura(
        m.formato, m.separador, m.decimal, m.codificacao, m.linha_cabecalho, m.n_linhas, m.n_colunas
    )
    return textos.descrever_leitura(dados)


def _limpeza(resumo: Resumo) -> tuple[str, ...]:
    return tuple(e.frase for e in resumo.log_limpeza) or (textos.SEM_LIMPEZA,)


def _valor(valor: float | str | None, sufixo: str = "") -> str:
    return f"{formatar_com_sinal(valor)}{sufixo}" if isinstance(valor, float) else str(valor)


def _itens(candidatas: Iterable[tuple[str, Medida, str]]) -> list[ItemMedida]:
    return [ItemMedida(r, _valor(m.valor, s)) for r, m, s in candidatas if m.aplicavel]


def _medidas(analise: Analise) -> tuple[ItemMedida, ...]:
    tend, disp = analise.tendencia, analise.dispersao
    candidatas = [("Média", tend.media, ""), ("Mediana", tend.mediana, "")]
    candidatas += [("Moda de Czuber", tend.moda_czuber, ""), ("Proporção", tend.proporcao, "")]
    if disp is not None:
        candidatas += [
            ("Desvio padrão", disp.desvio_padrao, ""),
            ("Variância", disp.variancia, ""),
            ("CV", disp.cv, "%"),
            ("IQR", disp.iqr, ""),
            ("Amplitude", disp.amplitude, ""),
        ]
    itens = _itens(candidatas)
    modas = ", ".join(_valor(v) for v in tend.moda.valores) or "não há (amodal)"
    return (*itens[:2], ItemMedida("Moda", modas), *itens[2:])


def _tabela(analise: Analise) -> tuple[tuple[str, ...], tuple[tuple[str, ...], ...]]:
    tabela = analise.frequencias
    primeira = CABECALHOS_PRIMEIRA_COLUNA.get(analise.tipo, "Categoria")
    cabecalho = (primeira, "fᵢ", "fr%") + (("Fr%",) if tabela.acumulada_aplicavel else ())
    acumular = tabela.acumulada_aplicavel
    linhas = tuple(
        (linha.rotulo, str(linha.fi), formatar_percentual(linha.fr_pct))
        + ((formatar_percentual(linha.fr_acum_pct or 0.0),) if acumular else ())
        for linha in tabela.linhas
    )
    return cabecalho, linhas


def _separatrizes(analise: Analise) -> str | None:
    if analise.separatrizes is None:
        return None
    return " · ".join(f"{q.rotulo} = {_valor(q.valor)}" for q in analise.separatrizes.quartis)


def _figura(figuras: Iterable[Figura | None], identificador: str) -> FiguraRelatorio | None:
    """A primeira figura da lista, desenhada no tema claro (D47)."""
    principal = next(iter(figuras), None)
    if principal is None:
        return None
    html = figura_html(identificador, principal.dados)
    return FiguraRelatorio(principal.titulo, principal.resumo, html)


def _bloco_analises(analise: Analise, ordem: int) -> BlocoAnalises:
    cabecalho, linhas = _tabela(analise)
    return BlocoAnalises(
        cabecalho_tabela=cabecalho,
        linhas_tabela=linhas,
        medidas=_medidas(analise),
        separatrizes=_separatrizes(analise),
        interpretacoes=analise.interpretacoes,
        figura=_figura(analise.figuras, f"figura-{ordem}"),
    )


def _selo_assimetria(forma: Forma) -> str | None:
    classe = forma.classificacao_assimetria
    return None if classe is None else textos.selo_assimetria(classe, forma.sentido_assimetria)


def _selo_curtose(forma: Forma) -> str | None:
    classe = forma.classificacao_curtose
    return None if classe is None else textos.SELOS_CURTOSE[classe]


def _medidas_forma(forma: Forma) -> tuple[ItemMedida, ...]:
    """G₁ e G₂ com a classificação; As₁, As₂ e K só com o valor (spec 09)."""
    notas = {"assimetria": _selo_assimetria(forma), "curtose": _selo_curtose(forma)}
    medidas: dict[str, Medida] = {chave: getattr(forma, chave) for chave in textos.ROTULOS_FORMA}
    return tuple(
        ItemMedida(textos.ROTULOS_FORMA[chave], _valor(medida.valor), notas.get(chave))
        for chave, medida in medidas.items()
        if medida.aplicavel
    )


def _frase_ajuste(ajuste: Ajuste) -> str | None:
    """Ex.: "Shapiro-Wilk: W = 0,9933 · p = 0,399 ≥ 0,05. Os dados são compatíveis…"."""
    if not ajuste.aplicavel:
        return ajuste.motivo
    if ajuste.calculo and ajuste.frase:
        return f"{ajuste.calculo}. {ajuste.frase}"
    return ajuste.frase or ajuste.calculo


def _motivo_forma(analise: Analise) -> str | None:
    return next((n.motivo for n in analise.nao_aplicavel if n.item == "forma"), None)


def _secao_forma(analise: Analise, ordem: int) -> SecaoForma:
    forma = analise.forma
    if forma is None:
        return SecaoForma(motivo=_motivo_forma(analise))
    ajustes = (_frase_ajuste(forma.normal), _frase_ajuste(forma.binomial))
    return SecaoForma(
        medidas=_medidas_forma(forma),
        ajustes=tuple(frase for frase in ajustes if frase),
        interpretacao=forma.interpretacao,
        figura=_figura(forma.figuras, f"forma-{ordem}"),
    )


def _como_texto(formulas: Iterable[Formula]) -> tuple[FormulaTexto, ...]:
    return tuple(FormulaTexto(f.nome, f.latex, f.texto) for f in formulas)


def _secao_da_formula(formula: Formula) -> Secao:
    return "distribuicoes" if formula.chave in CHAVES_FORMA else "analises"


def _secao_coluna(analise: Analise, ordem: int, secoes: frozenset[Secao]) -> SecaoColuna:
    return SecaoColuna(
        coluna=analise.coluna,
        tipo=textos.TIPOS_LEGIVEIS[analise.tipo],
        n=analise.n,
        n_faltantes=analise.n_faltantes,
        analises=_bloco_analises(analise, ordem) if "analises" in secoes else None,
        forma=_secao_forma(analise, ordem) if "distribuicoes" in secoes else None,
        formulas=_como_texto(f for f in analise.formulas if _secao_da_formula(f) in secoes),
    )


def pares_mais_fortes(
    colunas: tuple[str, ...],
    valores: tuple[tuple[float | None, ...], ...],
    limite: int = PARES_NO_RELATORIO,
) -> tuple[tuple[str, str], ...]:
    """Pares com |r| ≥ 0,3, do mais forte ao mais fraco; empate fica na ordem das colunas."""
    candidatos = [
        (abs(r), (colunas[i], colunas[j]))
        for i, j in combinations(range(len(colunas)), 2)
        if (r := valores[i][j]) is not None and abs(r) >= CORRELACAO_MINIMA
    ]
    ordenados = sorted(candidatos, key=lambda candidato: -candidato[0])
    return tuple(par for _, par in ordenados[:limite])


def _medidas_par(bivariada: Bivariada) -> tuple[ItemMedida, ...]:
    reta = bivariada.regressao
    selo = textos.selo_correlacao(bivariada.forca, bivariada.sentido)
    pearson = ItemMedida("r de Pearson", _valor(bivariada.pearson.valor), selo)
    p_valor = bivariada.teste_t.valor
    teste = ItemMedida("Teste t", formatar_p_valor(p_valor) if isinstance(p_valor, float) else "")
    candidatas = [("ρ de Spearman", bivariada.spearman, ""), ("R²", reta.r2, "%")]
    candidatas += [("Sₑ", reta.se, "")]
    pares = ItemMedida("Pares (n)", str(bivariada.n))
    return (pearson, teste, *_itens(candidatas), pares)


def _par_relatorio(bivariada: Bivariada, ordem: int) -> ParRelatorio:
    return ParRelatorio(
        x=bivariada.x,
        y=bivariada.y,
        medidas=_medidas_par(bivariada),
        equacao=bivariada.regressao.equacao,
        interpretacoes=bivariada.interpretacoes,
        figura=_figura(bivariada.figuras, f"par-{ordem}"),
    )


def _formulas_bivariada(analises: Iterable[Bivariada]) -> tuple[FormulaTexto, ...]:
    unicas = {f.chave: f for bivariada in analises for f in bivariada.formulas}
    return _como_texto(unicas.values())


class ServicoRelatorio:
    """Relatório da spec 13: leitura, tipos, limpeza, colunas (análises e forma) e bivariada."""

    def __init__(self, datasets: ServicoDatasets, analise: ServicoAnalise) -> None:
        self._datasets = datasets
        self._analise = analise

    def _tipos(self, dataset_id: str) -> tuple[LinhaTipo, ...]:
        return tuple(
            LinhaTipo(t.coluna, textos.TIPOS_LEGIVEIS[t.tipo], t.motivo)
            for t in self._datasets.colunas(dataset_id)
        )

    def _colunas(self, dataset_id: str, pedido: PedidoRelatorio) -> tuple[SecaoColuna, ...]:
        tipos = self._datasets.colunas(dataset_id)
        nomes = pedido.colunas or tuple(t.coluna for t in tipos if t.tipo not in TIPOS_AUXILIARES)
        secoes = frozenset(pedido.secoes)
        colunas: list[SecaoColuna] = []
        for nome in nomes:
            try:
                analise = self._analise.analisar(dataset_id, nome)
            except EntradaInvalida:
                continue  # tipo auxiliar ou coluna vazia: fica fora, como na tela
            colunas.append(_secao_coluna(analise, len(colunas) + 1, secoes))
        return tuple(colunas)

    def _par(self, dataset_id: str, x: str, y: str) -> Bivariada | None:
        try:
            return self._analise.bivariada(dataset_id, x, y)
        except EntradaInvalida as erro:
            if erro.codigo not in ERROS_DO_PAR:
                raise
            return None

    def _bivariada(self, dataset_id: str) -> SecaoBivariada:
        matriz = self._analise.correlacoes(dataset_id)
        candidatos = pares_mais_fortes(matriz.colunas, matriz.valores)
        analises = [b for x, y in candidatos if (b := self._par(dataset_id, x, y)) is not None]
        pares = tuple(_par_relatorio(b, ordem) for ordem, b in enumerate(analises, start=1))
        sem_pares = matriz.figura is not None and not pares
        return SecaoBivariada(
            matriz=_figura((matriz.figura,), "matriz"),
            resumo=matriz.resumo,
            pares=pares,
            vazio=textos.SEM_PAR_FORTE if sem_pares else None,
            formulas=_formulas_bivariada(analises),
        )

    def gerar(self, dataset_id: str, pedido: PedidoRelatorio) -> str:
        """HTML autocontido; `offline` embute o plotly.js (cerca de 4,8 MB)."""
        resumo = self._datasets.resumo(dataset_id)
        secoes = frozenset(pedido.secoes)
        conteudo = ConteudoRelatorio(
            nome_arquivo=resumo.nome_arquivo,
            gerado_em=datetime.now().strftime(FORMATO_DATA),
            subtitulo=textos.subtitulo(
                resumo.nome_arquivo, resumo.n_linhas, resumo.n_linhas_original, resumo.n_colunas
            ),
            script_plotly=_script_plotly(pedido.offline),
            leitura=_leitura(resumo) if "leitura" in secoes else None,
            tipos=self._tipos(dataset_id) if "tipos" in secoes else None,
            limpeza=_limpeza(resumo) if "limpeza" in secoes else None,
            colunas=self._colunas(dataset_id, pedido) if secoes & SECOES_POR_COLUNA else None,
            bivariada=self._bivariada(dataset_id) if "bivariada" in secoes else None,
        )
        return renderizar(conteudo)
