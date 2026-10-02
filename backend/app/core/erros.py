"""Exceções da aplicação com mensagem amigável (docs/specs/17-erros-testes.md)."""

from http import HTTPStatus


class ErroAplicacao(Exception):
    """Base: todo erro previsto tem código, mensagem e sugestão de próximo passo."""

    status: HTTPStatus = HTTPStatus.BAD_REQUEST

    def __init__(self, codigo: str, mensagem: str, sugestao: str = "") -> None:
        super().__init__(mensagem)
        self.codigo = codigo
        self.mensagem = mensagem
        self.sugestao = sugestao

    def como_dict(self) -> dict[str, str]:
        return {"codigo": self.codigo, "mensagem": self.mensagem, "sugestao": self.sugestao}


class EntradaInvalida(ErroAplicacao):
    status = HTTPStatus.BAD_REQUEST


class NaoEncontrado(ErroAplicacao):
    status = HTTPStatus.NOT_FOUND
