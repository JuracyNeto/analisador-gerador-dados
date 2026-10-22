"""Fachada do domínio relatorio: junta leitura, tipos, limpeza e análises num HTML (spec 13)."""

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, replace
from datetime import datetime
from itertools import combinations
from typing import Any, Protocol

from app.compartilhado.numeros import (
    formatar_inteiro,
    formatar_numero,
    formatar_p_valor,
    formatar_percentual,
)
from app.compartilhado.tipos import TIPOS_AUXILIARES, Formula, TipoVariavel
from app.core.erros import EntradaInvalida, NaoEncontrado
from app.dominios.analise.servico import (
    CHAVES_FORMA,
    ORDEM_FORMULAS,
    Ajuste,
    Analise,
    Bivariada,
    Forma,
    Medida,
    ServicoAnalise,
)
from app.dominios.datasets.servico import Resumo, ServicoDatasets
from app.dominios.detector.servico import Aviso, ResultadoDetector, ServicoDetector
from app.dominios.gerador.servico import Gerado, ServicoGerador
from app.dominios.graficos.servico import codigo_plotlyjs, endereco_plotlyjs_cdn, figura_html
from app.dominios.relatorio import textos
from app.dominios.relatorio.apendice import montar_apendice
from app.dominios.relatorio.comparacao import linha_comparacao
from app.dominios.relatorio.conteudo import (
    SECOES_PADRAO,
    AvisoRelatorio,
    BlocoAnalises,
    ConteudoRelatorio,
    DadosLeitura,
    FiguraRelatorio,
    FormulaApendice,
    ItemMedida,
    LinhaTipo,
    ParRelatorio,
    Secao,
    SecaoBivariada,
    SecaoColuna,
    SecaoDetector,
    SecaoForma,
    SecaoGerador,
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
    """O que entra no relatório; sem colunas = todas as analisáveis; sem `gerado`, sem Gerador."""

    secoes: tuple[Secao, ...] = SECOES_PADRAO
    colunas: tuple[str, ...] | None = None
    offline: bool = False
    gerado: str | None = None


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
    return f"{formatar_numero(valor)}{sufixo}" if isinstance(valor, float) else str(valor)


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
            ("Coeficiente de variação", disp.cv, "%"),
            ("Amplitude interquartil (IQR)", disp.iqr, ""),
            ("Amplitude", disp.amplitude, ""),
        ]
    itens = _itens(candidatas)
    modas = ", ".join(_valor(v) for v in tend.moda.valores) or "Sem moda"
    return (*itens[:2], ItemMedida("Moda", modas), *itens[2:])


def _tabela(analise: Analise) -> tuple[tuple[str, ...], tuple[tuple[str, ...], ...]]:
    tabela = analise.frequencias
    primeira = CABECALHOS_PRIMEIRA_COLUNA.get(analise.tipo, "Categoria")
    cabecalho = (primeira, "fᵢ", "fr%") + (("Fr%",) if tabela.acumulada_aplicavel else ())
    acumular = tabela.acumulada_aplicavel
    linhas = tuple(
        (linha.rotulo, formatar_inteiro(linha.fi), formatar_percentual(linha.fr_pct))
        + ((formatar_percentual(linha.fr_acum_pct or 0.0),) if acumular else ())
        for linha in tabela.linhas
    )
    return cabecalho, linhas


def _separatrizes(analise: Analise) -> str | None:
    if analise.separatrizes is None:
        return None
    return " · ".join(f"{q.rotulo} = {_valor(q.valor)}" for q in analise.separatrizes.quartis)


class FiguraDesenhavel(Protocol):
    """Figura de qualquer domínio (análise, gerador, detector): título, resumo e JSON do Plotly."""

    @property
    def titulo(self) -> str: ...

    @property
    def resumo(self) -> str: ...

    @property
    def dados(self) -> Mapping[str, Any]: ...


def _figura(
    figuras: Iterable[FiguraDesenhavel | None], identificador: str
) -> FiguraRelatorio | None:
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
        formulas=tuple(f for f in analise.formulas if f.chave not in CHAVES_FORMA),
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
        formulas=tuple(f for f in analise.formulas if f.chave in CHAVES_FORMA),
    )


def _secao_coluna(analise: Analise, ordem: int, secoes: frozenset[Secao]) -> SecaoColuna:
    return SecaoColuna(
        coluna=analise.coluna,
        tipo=textos.TIPOS_LEGIVEIS[analise.tipo],
        contagem=textos.contagem_coluna(analise.n, analise.n_faltantes),
        analises=_bloco_analises(analise, ordem) if "analises" in secoes else None,
        forma=_secao_forma(analise, ordem) if "distribuicoes" in secoes else None,
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
    pearson = ItemMedida("Correlação de Pearson (r)", _valor(bivariada.pearson.valor), selo)
    p_valor = bivariada.teste_t.valor
    teste = ItemMedida("Teste t", formatar_p_valor(p_valor) if isinstance(p_valor, float) else "")
    candidatas = [("ρ de Spearman", bivariada.spearman, ""), ("R²", reta.r2, "%")]
    candidatas += [("Sₑ", reta.se, "")]
    pares = ItemMedida("Pares (n)", formatar_inteiro(bivariada.n))
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


def _formulas_bivariada(analises: Iterable[Bivariada]) -> tuple[Formula, ...]:
    unicas = {f.chave: f for bivariada in analises for f in bivariada.formulas}
    return tuple(unicas.values())


def _secao_gerador(gerado: Gerado) -> SecaoGerador:
    linhas = tuple(
        linha_comparacao(linha.estatistica, linha.original, linha.gerado, linha.diferenca)
        for linha in gerado.comparacao
    )
    return SecaoGerador(
        subtitulo=textos.subtitulo_gerador(gerado.tipo, gerado.n, gerado.semente),
        parametros=tuple(ItemMedida(p.nome, p.valor) for p in gerado.parametros),
        metodo=gerado.metodo,
        explicacao=gerado.explicacao,
        cabecalho_comparacao=textos.cabecalho_comparacao(gerado.n),
        linhas_comparacao=linhas,
        figura=_figura(gerado.figuras, "gerador"),
        formulas=gerado.formulas,
    )


def _detalhes(aviso: Aviso) -> tuple[ItemMedida, ...]:
    """Parte 8 da spec 16: medida, valor, limiar, teste, p traduzido e fórmula (só os que há)."""
    d = aviso.detalhes
    p_valor = None if d.p_valor is None else formatar_p_valor(d.p_valor)
    partes = {"medida": d.medida, "valor": d.valor, "limiar": d.limiar, "teste": d.teste}
    partes |= {"p_valor": p_valor, "formula": d.formula}
    notas = {"p_valor": d.p_em_palavras}
    return tuple(
        ItemMedida(textos.ROTULOS_DETALHES[chave], valor, notas.get(chave))
        for chave, valor in partes.items()
        if valor
    )


def _formula_do_aviso(aviso: Aviso) -> FormulaApendice | None:
    """A fórmula em texto dos detalhes, para o apêndice (os alertas não têm LaTeX)."""
    formula = aviso.detalhes.formula
    if not formula:
        return None
    return FormulaApendice(textos.nome_formula_regra(aviso.regra, aviso.nome_regra), formula)


def _aviso_relatorio(aviso: Aviso, ordem: int) -> AvisoRelatorio:
    return AvisoRelatorio(
        severidade=aviso.severidade,
        selo=textos.SELOS_SEVERIDADE[aviso.severidade],
        titulo=textos.titulo_aviso(aviso.regra, aviso.titulo),
        resumo=aviso.resumo,
        por_que=aviso.por_que,
        exemplo=aviso.exemplo.texto if aviso.exemplo else None,
        pode_ser_normal=aviso.pode_ser_normal,
        o_que_fazer=aviso.o_que_fazer,
        detalhes=_detalhes(aviso),
        figura=_figura((aviso.figura,), f"aviso-{ordem}"),
        formula=_formula_do_aviso(aviso),
        colunas=aviso.colunas,
    )


def _secao_detector(resultado: ResultadoDetector) -> SecaoDetector:
    resumo, contagem = resultado.resumo, resultado.resumo.por_severidade
    return SecaoDetector(
        frase=resumo.frase,
        detalhe=resumo.detalhe,
        contadores=textos.contadores_severidade(contagem.alta, contagem.atencao, contagem.info),
        avisos=tuple(_aviso_relatorio(a, ordem) for ordem, a in enumerate(resultado.avisos, 1)),
        nao_verificadas=tuple(regra.frase for regra in resultado.nao_aplicadas),
        vazio=resumo.vazio,
    )


class ServicoRelatorio:
    """Relatório da spec 13: leitura, tipos, limpeza, colunas, bivariada, gerador e detector."""

    def __init__(
        self,
        datasets: ServicoDatasets,
        analise: ServicoAnalise,
        gerador: ServicoGerador,
        detector: ServicoDetector,
    ) -> None:
        self._datasets = datasets
        self._analise = analise
        self._gerador = gerador
        self._detector = detector

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

    def _secao_do_gerado(self, gerado_id: str | None) -> SecaoGerador | None:
        """Sem geração (ou com a geração já descartada) a seção sai e o relatório segue (D141)."""
        if gerado_id is None:
            return None
        try:
            return _secao_gerador(self._gerador.obter(gerado_id))
        except NaoEncontrado:
            return None

    def _secao_detector(self, dataset_id: str) -> SecaoDetector:
        """Todas as regras na versão atual, como na tela 7."""
        return _secao_detector(self._detector.analisar(dataset_id))

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
            gerador=self._secao_do_gerado(pedido.gerado) if "gerador" in secoes else None,
            detector=self._secao_detector(dataset_id) if "detector" in secoes else None,
        )
        if "formulas" in secoes:
            conteudo = replace(conteudo, formulas=montar_apendice(conteudo, ORDEM_FORMULAS))
        return renderizar(conteudo)
