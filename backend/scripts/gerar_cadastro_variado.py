"""Gera backend/tests/fixtures/cadastro_variado.txt: um cadastro com tipos de dado variados.

Serve para testar leitura, classificação e detector juntos num arquivo parecido com os reais
(D131): códigos (id, telefone com e sem máscara, CPF, CEP, e-mail), datas, horários, datas com
horário, uma linha do tempo diária, valores com milhar e vírgula decimal, valores em reais,
percentuais, notas de 1 a 5, sim/não, contagens, saldo negativo, faltantes ("NA", "-", vazio),
uma série no tempo, categorias e uma escala em texto. Nada foi plantado: os dados são fictícios
(DDD 00, CPF começando com 000, e-mails em exemplo.com.br).

Cada coluna tem o seu sorteio (a semente e o CRC32 do nome): acrescentar ou tirar uma coluna
não muda as outras.

Uso (em backend/): python scripts/gerar_cadastro_variado.py [--arquivo tests/fixtures/...]
"""

import argparse
import zlib
from collections.abc import Callable
from datetime import date, timedelta
from pathlib import Path

import numpy as np

SEMENTE = 2026
ARQUIVO = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "cadastro_variado.txt"
LINHAS = 300
INICIO = date(2026, 1, 1)
CIDADES = ("Goiânia", "Anápolis", "Aparecida de Goiânia", "Rio Verde")
ESCOLARIDADES = ("fundamental", "médio", "superior")
SATISFACAO = (0.05, 0.1, 0.25, 0.35, 0.25)
DESCONTOS = (0.0, 5.0, 10.0, 12.5, 15.0)
FALTANTE_SALDO = 37
FALTANTE_REAIS = 41
COM_OBSERVACAO = 0.3

type Coluna = Callable[[np.random.Generator, int], list[str]]


def _pt(valor: float, casas: int = 2) -> str:
    """1234.5 → "1.234,50" (milhar com ponto, vírgula decimal)."""
    texto = f"{valor:,.{casas}f}"
    return texto.replace(",", "_").replace(".", ",").replace("_", ".")


def _id(_: np.random.Generator, n: int) -> list[str]:
    return [str(i) for i in range(1, n + 1)]


def _nome(_: np.random.Generator, n: int) -> list[str]:
    return [f"Cliente {i:03d}" for i in range(1, n + 1)]


def _numeros_celular(rng: np.random.Generator, n: int) -> list[str]:
    return [f"009{numero:08d}" for numero in rng.choice(10**8, n, replace=False)]


def _celular(rng: np.random.Generator, n: int) -> list[str]:
    """ "(00) 91234-5678": com máscara."""
    return [f"({c[:2]}) {c[2:7]}-{c[7:]}" for c in _numeros_celular(rng, n)]


def _contato(rng: np.random.Generator, n: int) -> list[str]:
    """ "00912345678": só dígitos (vira número na leitura)."""
    return _numeros_celular(rng, n)


def _cpf(rng: np.random.Generator, n: int) -> list[str]:
    numeros = [f"000{numero:08d}" for numero in rng.choice(10**8, n, replace=False)]
    return [f"{c[:3]}.{c[3:6]}.{c[6:9]}-{c[9:]}" for c in numeros]


def _cep(rng: np.random.Generator, n: int) -> list[str]:
    return [f"74{numero // 1000:03d}-{numero % 1000:03d}" for numero in rng.integers(0, 10**6, n)]


def _email(_: np.random.Generator, n: int) -> list[str]:
    return [f"cliente{i:03d}@exemplo.com.br" for i in range(1, n + 1)]


def _nascimento(rng: np.random.Generator, n: int) -> list[str]:
    dias = rng.integers(0, 20_000, n)
    return [(date(1950, 1, 1) + timedelta(days=int(d))).strftime("%d/%m/%Y") for d in dias]


def _dia(_: np.random.Generator, n: int) -> list[str]:
    """Um registro por dia: a linha do tempo do arquivo (a que a R6 usa)."""
    return [(INICIO + timedelta(days=i)).strftime("%d/%m/%Y") for i in range(n)]


def _horas(rng: np.random.Generator, n: int) -> list[tuple[int, int]]:
    return list(zip(rng.integers(8, 18, n).tolist(), rng.integers(0, 60, n).tolist(), strict=True))


def _hora_atendimento(rng: np.random.Generator, n: int) -> list[str]:
    return [f"{hora:02d}:{minuto:02d}" for hora, minuto in _horas(rng, n)]


def _data_hora(rng: np.random.Generator, n: int) -> list[str]:
    return [
        f"{dia} {hora:02d}:{minuto:02d}"
        for dia, (hora, minuto) in zip(_dia(rng, n), _horas(rng, n), strict=True)
    ]


def _valores(rng: np.random.Generator, n: int) -> np.ndarray:
    """Valores de compra com cauda longa (log-normal), como em vendas reais."""
    return np.asarray(np.exp(rng.normal(5, 1.1, n)), dtype="float64")


def _valor_compra(rng: np.random.Generator, n: int) -> list[str]:
    return [_pt(valor) for valor in _valores(rng, n)]


def _valor_reais(rng: np.random.Generator, n: int) -> list[str]:
    """ "R$ 1.234,56", com "-" no lugar de alguns valores."""
    valores = [f"R$ {_pt(valor)}" for valor in _valores(rng, n)]
    return ["-" if (i + 1) % FALTANTE_REAIS == 0 else valor for i, valor in enumerate(valores)]


def _desconto(rng: np.random.Generator, n: int) -> list[str]:
    return [f"{_pt(float(d), 1)}%" for d in rng.choice(DESCONTOS, n)]


def _satisfacao(rng: np.random.Generator, n: int) -> list[str]:
    return [str(nota) for nota in rng.choice(np.arange(1, 6), n, p=SATISFACAO)]


def _vip(rng: np.random.Generator, n: int) -> list[str]:
    return [str(resposta) for resposta in rng.choice(["sim", "não"], n, p=[0.2, 0.8])]


def _itens(rng: np.random.Generator, n: int) -> list[str]:
    return [str(itens) for itens in rng.poisson(3, n)]


def _saldo(rng: np.random.Generator, n: int) -> list[str]:
    """Saldo com negativos e "NA" como faltante."""
    saldos = [_pt(float(valor)) for valor in rng.normal(150, 400, n)]
    return ["NA" if (i + 1) % FALTANTE_SALDO == 0 else saldo for i, saldo in enumerate(saldos)]


def _temperatura(rng: np.random.Generator, n: int) -> list[str]:
    """Série diária: cada dia parecido com o anterior (autocorrelação real)."""
    temperatura, serie = 25.0, []
    for ruido in rng.normal(0, 0.8, n):
        temperatura = 0.9 * temperatura + 0.1 * 25 + ruido
        serie.append(_pt(temperatura, 1))
    return serie


def _cidade(rng: np.random.Generator, n: int) -> list[str]:
    return [str(cidade) for cidade in rng.choice(CIDADES, n)]


def _escolaridade(rng: np.random.Generator, n: int) -> list[str]:
    return [str(nivel) for nivel in rng.choice(ESCOLARIDADES, n, p=[0.3, 0.45, 0.25])]


def _observacao(rng: np.random.Generator, n: int) -> list[str]:
    """Texto livre, quase sempre vazio."""
    frases = ("cliente pediu nota fiscal", "entrega agendada", "troca de produto")
    return [str(rng.choice(frases)) if rng.random() < COM_OBSERVACAO else "" for _ in range(n)]


COLUNAS: dict[str, Coluna] = {
    "id": _id,
    "nome": _nome,
    "celular": _celular,
    "contato": _contato,
    "cpf": _cpf,
    "cep": _cep,
    "email": _email,
    "nascimento": _nascimento,
    "dia": _dia,
    "hora_atendimento": _hora_atendimento,
    "data_hora": _data_hora,
    "valor_compra": _valor_compra,
    "valor_reais": _valor_reais,
    "desconto": _desconto,
    "satisfacao": _satisfacao,
    "vip": _vip,
    "itens": _itens,
    "saldo": _saldo,
    "temperatura": _temperatura,
    "cidade": _cidade,
    "escolaridade": _escolaridade,
    "observacao": _observacao,
}


def texto_do_cadastro() -> str:
    """`;` como separador, vírgula decimal, UTF-8 e fim de linha LF."""
    valores = [
        gerar(np.random.default_rng([SEMENTE, zlib.crc32(nome.encode("utf-8"))]), LINHAS)
        for nome, gerar in COLUNAS.items()
    ]
    linhas = [";".join(COLUNAS), *(";".join(celulas) for celulas in zip(*valores, strict=True))]
    return "\n".join(linhas) + "\n"


def gravar(arquivo: Path) -> Path:
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    with arquivo.open("w", encoding="utf-8", newline="\n") as saida:
        saida.write(texto_do_cadastro())
    return arquivo


def main() -> None:
    parser = argparse.ArgumentParser(description="Gera o cadastro com tipos de dado variados.")
    parser.add_argument("--arquivo", type=Path, default=ARQUIVO)
    print(f"Gravado {gravar(parser.parse_args().arquivo)}")


if __name__ == "__main__":
    main()
