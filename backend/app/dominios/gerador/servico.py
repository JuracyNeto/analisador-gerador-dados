"""Fachada do domínio gerador (spec 11): univariado, bivariado, CSV e adotar."""

import uuid
from dataclasses import dataclass
from functools import lru_cache

import numpy as np
import pandas as pd

from app.compartilhado.textos import juntar_lista
from app.compartilhado.tipos import TIPOS_AUXILIARES, TIPOS_NUMERICOS, TipoVariavel
from app.core.config import Configuracao, obter_configuracao
from app.dominios.analise.servico import Amostra, ServicoAnalise
from app.dominios.datasets.servico import OpcoesLeitura, ServicoDatasets
from app.dominios.gerador import erros, textos
from app.dominios.gerador.bivariado import ParametrosBivariado, gerar_pares, gerar_pares_exatos
from app.dominios.gerador.comparacao import (
    MedidasPar,
    comparar_categoricos,
    comparar_numericos,
    comparar_pares,
)
from app.dominios.gerador.estrategias.base import EntradaEstrategia, Modo, ResultadoEstrategia
from app.dominios.gerador.parametros import (
    DescricaoBivariada,
    origem_coluna,
    parametros_bivariados,
    parametros_univariados,
)
from app.dominios.gerador.pedidos import (
    Adotado,
    ModoAdotar,
    Origem,
    OrigemPar,
    PedidoBivariado,
    PedidoUnivariado,
    ResumoOrigem,
    ResumoOrigemPar,
)
from app.dominios.gerador.preparo import (
    BaseBivariada,
    Preparo,
    base_com_origem,
    base_sem_origem,
    casas_da_coluna,
    contexto_univariado,
    descricao_univariada,
    medidas_par,
    preparo_sem_origem,
    resumo_origem,
    resumo_origem_par,
    validar_parametros,
)
from app.dominios.gerador.reescala import arredondar
from app.dominios.gerador.repositorio import RepositorioGerados
from app.dominios.gerador.resultados import (
    LinhaComparacao,
    OrigemGeracao,
    Parametro,
    TipoGeracao,
)
from app.dominios.gerador.univariado import gerar_univariado
from app.dominios.graficos.servico import (
    DadosParesGerados,
    DadosSobreposicao,
    FiguraPronta,
    figura_pares_gerados,
    figura_sobreposicao_categorica,
    figura_sobreposicao_numerica,
)

__all__ = [
    "Adotado",
    "Gerado",
    "Origem",
    "OrigemPar",
    "PedidoBivariado",
    "PedidoUnivariado",
    "RepositorioGerados",
    "ResumoOrigem",
    "ResumoOrigemPar",
    "ServicoGerador",
    "obter_repositorio_gerados",
]

MAX_SEMENTE = 2**32

type Celula = float | int | str | None


def _celula(valor: object) -> Celula:
    if isinstance(valor, np.generic):
        valor = valor.item()
    if isinstance(valor, float) and np.isnan(valor):
        return None
    return valor if isinstance(valor, int | float | str) else str(valor)


@dataclass(frozen=True, slots=True, eq=False)
class Gerado:
    """Uma geração guardada em memória (CSV, adotar e relatório usam a mesma)."""

    gerado_id: str
    tipo: TipoGeracao
    colunas: tuple[str, ...]
    dados: pd.DataFrame
    semente: int
    origem: OrigemGeracao | None
    metodo: str
    explicacao: str
    parametros: tuple[Parametro, ...]
    comparacao: tuple[LinhaComparacao, ...]
    figuras: tuple[FiguraPronta, ...]
    tamanho_amostra: int = 50

    @property
    def n(self) -> int:
        return len(self.dados)

    @property
    def amostra(self) -> list[dict[str, Celula]]:
        registros = self.dados.head(self.tamanho_amostra).to_dict(orient="records")
        return [{str(c): _celula(v) for c, v in linha.items()} for linha in registros]

    @property
    def nome_csv(self) -> str:
        return f"gerado-{'-'.join(self.colunas)}.csv"

    def csv(self) -> bytes:
        """`;`, vírgula decimal e fim de linha LF (igual em qualquer sistema), como o app lê."""
        texto = self.dados.to_csv(sep=";", decimal=",", index=False, lineterminator="\n")
        return texto.encode("utf-8")


def sortear_semente(semente: int | None) -> int:
    """Sem semente, sorteia uma e devolve, para o usuário repetir o resultado (D109)."""
    if semente is not None:
        return semente
    return int(np.random.default_rng().integers(0, MAX_SEMENTE))


def _figura_univariada(preparo: Preparo, gerados: pd.Series) -> FiguraPronta:
    originais = preparo.entrada.originais
    n_original = len(originais) if originais is not None else 0
    dados = DadosSobreposicao(preparo.coluna, gerados, originais, n_original)
    if preparo.tipo in TIPOS_NUMERICOS:
        return figura_sobreposicao_numerica(dados)
    return figura_sobreposicao_categorica(dados)


def _alvo(parametros: ParametrosBivariado) -> MedidasPar:
    return MedidasPar(
        parametros.n,
        parametros.media_x,
        parametros.media_y,
        parametros.desvio_x,
        parametros.desvio_y,
        parametros.rho,
    )


def _contexto_pares(
    pedido: PedidoBivariado, base: BaseBivariada, parametros: ParametrosBivariado, semente: int
) -> textos.ContextoPares:
    return textos.ContextoPares(
        parametros.n,
        base.nomes[0],
        base.nomes[1],
        parametros.media_x,
        parametros.media_y,
        parametros.desvio_x,
        parametros.desvio_y,
        parametros.rho,
        semente,
        pedido.ajuste_exato,
    )


def _figura_pares(
    base: BaseBivariada, pares: tuple[np.ndarray, np.ndarray], r: float
) -> FiguraPronta:
    x_original, y_original = base.pontos_originais or (None, None)
    return figura_pares_gerados(
        DadosParesGerados(
            base.nomes[0],
            base.nomes[1],
            tuple(float(v) for v in pares[0]),
            tuple(float(v) for v in pares[1]),
            r,
            x_original,
            y_original,
        )
    )


class ServicoGerador:
    """Casos de uso do gerador; dados de origem vêm das fachadas de datasets e análise."""

    def __init__(
        self,
        datasets: ServicoDatasets,
        analise: ServicoAnalise,
        repositorio: RepositorioGerados[Gerado],
        config: Configuracao,
    ) -> None:
        self._datasets = datasets
        self._analise = analise
        self._repositorio = repositorio
        self._config = config

    def obter(self, gerado_id: str) -> Gerado:
        return self._repositorio.obter(gerado_id)

    def _guardar(self, gerado: Gerado) -> Gerado:
        self._repositorio.adicionar(gerado)
        return gerado

    def _nome_arquivo(self, dataset_id: str) -> str:
        return self._datasets.resumo(dataset_id).nome_arquivo

    # Univariado -------------------------------------------------------------------------

    def univariado(self, pedido: PedidoUnivariado) -> Gerado:
        """X valores preservando a coluna de origem ou com novos parâmetros (spec 11)."""
        semente = sortear_semente(pedido.semente)
        preparo = (
            self._com_origem(pedido, pedido.origem)
            if pedido.origem is not None
            else preparo_sem_origem(pedido)
        )
        resultado = gerar_univariado(preparo.tipo, preparo.entrada, semente)
        return self._guardar(self._montar_univariado(pedido, preparo, resultado, semente))

    def _amostra(self, origem: Origem) -> Amostra:
        """Valores válidos da coluna; identificador e data não servem de origem."""
        tipos = {c.coluna: c.tipo for c in self._datasets.colunas(origem.dataset_id)}
        if tipos.get(origem.coluna) in TIPOS_AUXILIARES:
            raise erros.coluna_nao_geravel(origem.coluna, tipos[origem.coluna])
        return self._analise.amostra(origem.dataset_id, origem.coluna)

    def origem(self, origem: Origem) -> ResumoOrigem:
        """Medidas da coluna de origem para o formulário da tela 6."""
        amostra = self._amostra(origem)
        rotulos = self._rotulos(amostra.tipo, amostra.valores)
        return resumo_origem(origem.coluna, amostra.tipo, amostra.valores, rotulos)

    def origem_par(self, origem: OrigemPar) -> ResumoOrigemPar:
        """Médias, desvios e r do par de origem (formulário bivariado)."""
        par = self._analise.par(origem.dataset_id, origem.x, origem.y)
        medidas = medidas_par(
            np.asarray(par.valores_x, dtype="float64"), np.asarray(par.valores_y, dtype="float64")
        )
        return resumo_origem_par(origem.x, origem.y, medidas)

    def _com_origem(self, pedido: PedidoUnivariado, origem: Origem) -> Preparo:
        amostra = self._amostra(origem)
        validar_parametros(amostra.tipo, pedido)
        entrada = EntradaEstrategia(
            x=pedido.x,
            modo=pedido.modo,
            originais=amostra.valores,
            media=pedido.media,
            desvio=pedido.desvio,
            p=pedido.p,
            rotulos=self._rotulos(amostra.tipo, amostra.valores),
            normal_compativel=self._normal_compativel(origem, amostra.tipo, pedido.modo),
            casas=casas_da_coluna(amostra.tipo, amostra.valores),
            limitar_faixa=pedido.limitar_faixa and amostra.tipo in TIPOS_NUMERICOS,
        )
        geracao = OrigemGeracao(
            origem.dataset_id, self._nome_arquivo(origem.dataset_id), (origem.coluna,)
        )
        return Preparo(amostra.tipo, origem.coluna, entrada, geracao)

    def _rotulos(self, tipo: TipoVariavel, valores: pd.Series) -> tuple[str, str] | None:
        """(fracasso, sucesso) com o sucesso da análise (spec 05)."""
        if tipo != TipoVariavel.BINARIA:
            return None
        textos_validos = valores.astype(str)
        sucesso = self._analise.sucesso_padrao(textos_validos)
        fracasso = next(c for c in sorted(textos_validos.unique()) if c != sucesso)
        return fracasso, sucesso

    def _normal_compativel(self, origem: Origem, tipo: TipoVariavel, modo: Modo) -> bool:
        if tipo != TipoVariavel.CONTINUA or modo != "preservar":
            return False
        forma = self._analise.analisar(origem.dataset_id, origem.coluna).forma
        teste = forma.normal.teste if forma is not None else None
        return bool(teste is not None and teste.compativel)

    def _comparacao(self, preparo: Preparo, gerados: pd.Series) -> tuple[LinhaComparacao, ...]:
        originais = preparo.entrada.originais
        if preparo.tipo not in TIPOS_NUMERICOS:
            return comparar_categoricos(originais, gerados)
        resumo = self._analise.resumo_numerico
        original = resumo(originais.to_numpy(dtype="float64")) if originais is not None else None
        return comparar_numericos(original, resumo(gerados.to_numpy(dtype="float64")))

    def _montar_univariado(
        self,
        pedido: PedidoUnivariado,
        preparo: Preparo,
        resultado: ResultadoEstrategia,
        semente: int,
    ) -> Gerado:
        contexto = contexto_univariado(pedido, preparo, resultado.metodo, semente)
        return Gerado(
            gerado_id=uuid.uuid4().hex,
            tipo="univariado",
            colunas=(preparo.coluna,),
            dados=pd.DataFrame({preparo.coluna: resultado.valores}),
            semente=semente,
            origem=preparo.origem,
            metodo=textos.NOMES_METODOS[resultado.metodo],
            explicacao=textos.explicacao_univariada(contexto),
            parametros=parametros_univariados(descricao_univariada(pedido, preparo, contexto)),
            comparacao=self._comparacao(preparo, resultado.valores),
            figuras=(_figura_univariada(preparo, resultado.valores),),
            tamanho_amostra=self._config.tamanho_amostra_gerada,
        )

    # Bivariado --------------------------------------------------------------------------

    def bivariado(self, pedido: PedidoBivariado) -> Gerado:
        """Pares com médias, desvios e correlação alvo (Cholesky, spec 11)."""
        semente = sortear_semente(pedido.semente)
        base = self._base(pedido)
        parametros = ParametrosBivariado(pedido.n, *base.valores())
        rng = np.random.default_rng(semente)
        if pedido.ajuste_exato:
            x, y = gerar_pares_exatos(parametros, rng)
        else:
            x, y = gerar_pares(parametros, rng)
            x, y = arredondar(x, base.casas[0]), arredondar(y, base.casas[1])
        return self._guardar(self._montar_bivariado(pedido, base, parametros, (x, y), semente))

    def _base(self, pedido: PedidoBivariado) -> BaseBivariada:
        if pedido.origem is None:
            return base_sem_origem(pedido)
        origem = pedido.origem
        par = self._analise.par(origem.dataset_id, origem.x, origem.y)
        geracao = OrigemGeracao(
            origem.dataset_id, self._nome_arquivo(origem.dataset_id), (origem.x, origem.y)
        )
        return base_com_origem(
            pedido,
            np.asarray(par.valores_x, dtype="float64"),
            np.asarray(par.valores_y, dtype="float64"),
            geracao,
        )

    def _montar_bivariado(
        self,
        pedido: PedidoBivariado,
        base: BaseBivariada,
        parametros: ParametrosBivariado,
        pares: tuple[np.ndarray, np.ndarray],
        semente: int,
    ) -> Gerado:
        nome_x, nome_y = base.nomes
        obtido = medidas_par(*pares)
        contexto = _contexto_pares(pedido, base, parametros, semente)
        origem = (
            origem_coluna(base.origem.colunas, base.origem.nome_arquivo)
            if base.origem is not None
            else textos.PARAMETROS_MANUAIS
        )
        return Gerado(
            gerado_id=uuid.uuid4().hex,
            tipo="bivariado",
            colunas=base.nomes,
            dados=pd.DataFrame({nome_x: pares[0], nome_y: pares[1]}),
            semente=semente,
            origem=base.origem,
            metodo=textos.NOMES_METODOS["cholesky"],
            explicacao=textos.explicacao_bivariada(contexto),
            parametros=parametros_bivariados(DescricaoBivariada(origem, contexto)),
            comparacao=comparar_pares(nome_x, nome_y, base.original or _alvo(parametros), obtido),
            figuras=(_figura_pares(base, pares, obtido.r),),
            tamanho_amostra=self._config.tamanho_amostra_gerada,
        )

    # Adotar ----------------------------------------------------------------------------

    def adotar(self, gerado_id: str, modo: ModoAdotar, dataset_id: str | None) -> Adotado:
        """ "novo" cria um dataset a partir do CSV; "anexar" põe as linhas no fim do atual."""
        gerado = self.obter(gerado_id)
        if modo == "novo":
            criado = self._datasets.importar(gerado.csv(), gerado.nome_csv, OpcoesLeitura())
            # As linhas do dataset criado (não as da geração): o aviso mostra o que foi lido.
            linhas = criado.metadados.n_linhas
            return Adotado(criado.dataset_id, criado.nome_arquivo, linhas, "novo")
        if dataset_id is None:
            raise erros.parametros_incompletos(["o dataset"])
        frase = (
            f"Anexamos {textos.quantidade(gerado.n, 'linha gerada', 'linhas geradas')} "
            f"em {juntar_lista(list(gerado.colunas))}."
        )
        resultado = self._datasets.anexar_linhas(dataset_id, gerado.dados, frase)
        return Adotado(dataset_id, self._nome_arquivo(dataset_id), resultado.n_linhas, "anexar")


@lru_cache
def obter_repositorio_gerados() -> RepositorioGerados[Gerado]:
    """Instância única (gerações em memória compartilhadas entre requisições, ADR 0009)."""
    return RepositorioGerados(obter_configuracao().max_gerados)
