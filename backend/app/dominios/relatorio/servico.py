"""Fachada do domínio relatorio: junta leitura, tipos, limpeza e análises num HTML (spec 13)."""

from dataclasses import dataclass
from datetime import datetime

from app.compartilhado.numeros import formatar_numero, formatar_percentual
from app.compartilhado.tipos import TIPOS_AUXILIARES, TipoVariavel
from app.core.erros import EntradaInvalida
from app.dominios.analise.servico import Analise, ServicoAnalise
from app.dominios.datasets.servico import Resumo, ServicoDatasets
from app.dominios.graficos.servico import codigo_plotlyjs, endereco_plotlyjs_cdn, figura_html
from app.dominios.relatorio import textos
from app.dominios.relatorio.conteudo import (
    SECOES_M1,
    ConteudoRelatorio,
    DadosLeitura,
    FiguraRelatorio,
    FormulaTexto,
    ItemMedida,
    LinhaTipo,
    Secao,
    SecaoColuna,
)
from app.dominios.relatorio.montagem import renderizar

__all__ = ["SECOES_M1", "PedidoRelatorio", "Secao", "ServicoRelatorio"]

FORMATO_DATA = "%d/%m/%Y %H:%M"
ESCAPE_FECHAMENTO = r"<\/script"
CABECALHOS_PRIMEIRA_COLUNA = {
    TipoVariavel.CONTINUA: "Classe",
    TipoVariavel.DISCRETA: "Valor",
}


@dataclass(frozen=True, slots=True)
class PedidoRelatorio:
    """O que entra no relatório; sem colunas = todas as analisáveis."""

    secoes: tuple[Secao, ...] = SECOES_M1
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


def _valor(valor: float | str | None, sufixo: str = "") -> str:
    return f"{formatar_numero(valor)}{sufixo}" if isinstance(valor, float) else str(valor)


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
    itens = [ItemMedida(r, _valor(m.valor, s)) for r, m, s in candidatas if m.aplicavel]
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


def _figura(analise: Analise, ordem: int) -> FiguraRelatorio | None:
    if not analise.figuras:
        return None
    principal = analise.figuras[0]
    html = figura_html(f"figura-{ordem}", principal.dados)
    return FiguraRelatorio(principal.titulo, principal.resumo, html)


def _secao_coluna(analise: Analise, ordem: int) -> SecaoColuna:
    cabecalho, linhas = _tabela(analise)
    return SecaoColuna(
        coluna=analise.coluna,
        tipo=textos.TIPOS_LEGIVEIS[analise.tipo],
        n=analise.n,
        n_faltantes=analise.n_faltantes,
        cabecalho_tabela=cabecalho,
        linhas_tabela=linhas,
        medidas=_medidas(analise),
        separatrizes=_separatrizes(analise),
        interpretacoes=analise.interpretacoes,
        figura=_figura(analise, ordem),
        formulas=tuple(FormulaTexto(f.nome, f.latex, f.texto) for f in analise.formulas),
    )


class ServicoRelatorio:
    """Mini relatório do M1 (spec 13): leitura, tipos, limpeza e análise por coluna."""

    def __init__(self, datasets: ServicoDatasets, analise: ServicoAnalise) -> None:
        self._datasets = datasets
        self._analise = analise

    def _colunas(self, dataset_id: str, pedido: PedidoRelatorio) -> tuple[SecaoColuna, ...]:
        tipos = self._datasets.colunas(dataset_id)
        nomes = pedido.colunas or tuple(t.coluna for t in tipos if t.tipo not in TIPOS_AUXILIARES)
        secoes: list[SecaoColuna] = []
        for nome in nomes:
            try:
                analise = self._analise.analisar(dataset_id, nome)
            except EntradaInvalida:
                continue  # tipo auxiliar ou coluna vazia: fica fora, como na tela
            secoes.append(_secao_coluna(analise, len(secoes) + 1))
        return tuple(secoes)

    def gerar(self, dataset_id: str, pedido: PedidoRelatorio) -> str:
        """HTML autocontido; `offline` embute o plotly.js (cerca de 4,8 MB)."""
        resumo = self._datasets.resumo(dataset_id)
        secoes = set(pedido.secoes)
        tipos = self._datasets.colunas(dataset_id)
        conteudo = ConteudoRelatorio(
            nome_arquivo=resumo.nome_arquivo,
            gerado_em=datetime.now().strftime(FORMATO_DATA),
            subtitulo=textos.subtitulo(
                resumo.nome_arquivo, resumo.n_linhas, resumo.n_linhas_original, resumo.n_colunas
            ),
            script_plotly=_script_plotly(pedido.offline),
            leitura=_leitura(resumo) if "leitura" in secoes else None,
            tipos=tuple(LinhaTipo(t.coluna, textos.TIPOS_LEGIVEIS[t.tipo], t.motivo) for t in tipos)
            if "tipos" in secoes
            else None,
            limpeza=(tuple(e.frase for e in resumo.log_limpeza) or (textos.SEM_LIMPEZA,))
            if "limpeza" in secoes
            else None,
            colunas=self._colunas(dataset_id, pedido) if "analises" in secoes else None,
        )
        return renderizar(conteudo)
