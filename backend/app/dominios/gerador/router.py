"""Rotas do gerador (spec 11, spec 14). Sem lógica: valida → serviço → schema."""

from typing import Annotated

from fastapi import APIRouter, Depends, Response, status

from app.compartilhado.tipos import TipoVariavel
from app.core.config import obter_configuracao
from app.dominios.analise.servico import ServicoAnalise
from app.dominios.datasets.servico import ServicoDatasets, obter_servico_datasets
from app.dominios.gerador import schemas
from app.dominios.gerador.servico import (
    Gerado,
    Origem,
    OrigemPar,
    PedidoBivariado,
    PedidoUnivariado,
    RepositorioGerados,
    ServicoGerador,
    obter_repositorio_gerados,
)

router = APIRouter(prefix="/gerador", tags=["gerador"])


def _servico(
    datasets: Annotated[ServicoDatasets, Depends(obter_servico_datasets)],
    repositorio: Annotated[RepositorioGerados[Gerado], Depends(obter_repositorio_gerados)],
) -> ServicoGerador:
    return ServicoGerador(datasets, ServicoAnalise(datasets), repositorio, obter_configuracao())


Servico = Annotated[ServicoGerador, Depends(_servico)]


def _univariado(pedido: schemas.PedidoUnivariado) -> PedidoUnivariado:
    origem = pedido.origem
    return PedidoUnivariado(
        x=pedido.x,
        modo=pedido.modo,
        origem=Origem(origem.dataset_id, origem.coluna) if origem else None,
        tipo=TipoVariavel(pedido.tipo) if pedido.tipo else None,
        media=pedido.media,
        desvio=pedido.desvio,
        p=pedido.p,
        rotulos=pedido.rotulos,
        semente=pedido.semente,
        limitar_faixa=pedido.limitar_faixa,
    )


def _bivariado(pedido: schemas.PedidoBivariado) -> PedidoBivariado:
    origem = pedido.origem
    return PedidoBivariado(
        origem=OrigemPar(origem.dataset_id, origem.x, origem.y) if origem else None,
        **pedido.model_dump(exclude={"origem"}),
    )


@router.post(
    "/univariado",
    status_code=status.HTTP_201_CREATED,
    summary="Gera valores de uma coluna (preservando ou com novos parâmetros)",
)
def gerar_univariado(servico: Servico, pedido: schemas.PedidoUnivariado) -> schemas.Gerado:
    return schemas.Gerado.model_validate(servico.univariado(_univariado(pedido)))


@router.post(
    "/bivariado",
    status_code=status.HTTP_201_CREATED,
    summary="Gera pares com médias, desvios e correlação alvo",
)
def gerar_bivariado(servico: Servico, pedido: schemas.PedidoBivariado) -> schemas.Gerado:
    return schemas.Gerado.model_validate(servico.bivariado(_bivariado(pedido)))


@router.get("/origem", summary="Medidas da coluna de origem (formulário univariado)")
def resumir_origem(servico: Servico, dataset_id: str, coluna: str) -> schemas.ResumoOrigem:
    return schemas.ResumoOrigem.model_validate(servico.origem(Origem(dataset_id, coluna)))


@router.get("/origem-par", summary="Médias, desvios e r do par de origem (formulário bivariado)")
def resumir_origem_par(
    servico: Servico, dataset_id: str, x: str, y: str
) -> schemas.ResumoOrigemPar:
    return schemas.ResumoOrigemPar.model_validate(servico.origem_par(OrigemPar(dataset_id, x, y)))


@router.get("/{gerado_id}", summary="Uma geração guardada")
def obter(servico: Servico, gerado_id: str) -> schemas.Gerado:
    return schemas.Gerado.model_validate(servico.obter(gerado_id))


@router.get("/{gerado_id}/csv", summary="Dados gerados em CSV", response_class=Response)
def baixar_csv(servico: Servico, gerado_id: str) -> Response:
    gerado = servico.obter(gerado_id)
    return Response(
        content=gerado.csv(),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{gerado.nome_csv}"'},
    )


@router.post(
    "/{gerado_id}/adotar",
    status_code=status.HTTP_201_CREATED,
    summary="Usa a geração como novo dataset ou anexa ao dataset atual",
)
def adotar(servico: Servico, gerado_id: str, pedido: schemas.PedidoAdotar) -> schemas.Adotado:
    return schemas.Adotado.model_validate(servico.adotar(gerado_id, pedido.modo, pedido.dataset_id))
