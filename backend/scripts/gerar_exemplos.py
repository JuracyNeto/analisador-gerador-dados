"""Gera os datasets de demonstração em dados-exemplo/ (semente fixa, resultado reprodutível).

pesquisa_saude.txt reproduz os mockups (docs/design/telas/prints/1a e 3a): as 20 primeiras
linhas são as da prévia e os problemas da tela Limpeza ficam nas linhas indicadas abaixo.
"""

from dataclasses import dataclass
from pathlib import Path

import numpy as np

SEMENTE = 2026
PASTA = Path(__file__).resolve().parents[2] / "dados-exemplo"
TOTAL_LINHAS = 230

COLUNAS_SAUDE = (
    "id",
    "sexo",
    "idade",
    "altura_m",
    "peso_kg",
    "escolaridade",
    "cidade",
    "satisfacao",
)

# Prévia do print 1a (linha 12 sem peso).
PREVIA = (
    ("F", 34, 1.62, 58.2, "médio", "Goiânia", "bom"),
    ("M", 27, 1.78, 79.6, "fundamental", "Goiania", "regular"),
    ("F", 45, 1.58, 63.0, "pós", "Goiânia", "ruim"),
    ("F", 52, 1.66, 71.4, "superior", "Anápolis", "ótimo"),
    ("M", 23, 1.81, 84.1, "médio", "Luziânia", "bom"),
    ("M", 31, 1.74, 68.4, "fundamental", "Rio Verde", "bom"),
    ("F", 61, 1.60, 66.7, "pós", "Aparecida de Goiânia", "regular"),
    ("M", 29, 1.69, 72.0, "superior", "Goiânia", "ruim"),
    ("F", 38, 1.57, 55.9, "médio", "Goiania", "ótimo"),
    ("M", 44, 1.83, 90.3, "fundamental", "Goiânia", "bom"),
    ("F", 26, 1.64, 61.8, "pós", "Anápolis", "bom"),
    ("F", 57, 1.71, None, "superior", "Luziânia", "regular"),
    ("M", 33, 1.59, 57.4, "médio", "Rio Verde", "ruim"),
    ("F", 41, 1.76, 77.2, "fundamental", "Aparecida de Goiânia", "ótimo"),
    ("M", 22, 1.65, 62.5, "pós", "Goiânia", "bom"),
    ("M", 48, 1.79, 81.0, "superior", "Goiania", "bom"),
    ("F", 36, 1.61, 64.3, "médio", "Goiânia", "regular"),
    ("F", 30, 1.68, 69.8, "fundamental", "Anápolis", "ruim"),
    ("M", 55, 1.72, 74.6, "pós", "Luziânia", "ótimo"),
    ("F", 39, 1.63, 60.1, "superior", "Rio Verde", "bom"),
)

CIDADES = (
    "Goiânia",
    "Anápolis",
    "Aparecida de Goiânia",
    "Rio Verde",
    "Luziânia",
    "Catalão",
    "Trindade",
)
PESOS_CIDADES = (0.40, 0.18, 0.17, 0.10, 0.07, 0.05, 0.03)
ESCOLARIDADES = ("fundamental", "médio", "superior", "pós")
PESOS_ESCOLARIDADE = (0.17, 0.42, 0.30, 0.11)
SATISFACOES = ("ruim", "regular", "bom", "ótimo")
PESOS_SATISFACAO = (0.10, 0.24, 0.43, 0.23)

# Problemas plantados (número da linha de dados, a partir de 1) — print 3a.
LINHA_DUPLICADA = 44
COPIAS = (45, 46, 47)
FALTANTES = {"peso_kg": (12, 141, 207), "cidade": (64, 190), "idade": (88,), "altura_m": (153,)}
FORA_DE_FAIXA = {
    "altura_m": {77: 17.2},
    "idade": {19: 0, 201: 230},
    "peso_kg": {99: 6.8, 160: 712.0},
}
# Na prévia já há 3 "Goiania"; aqui ficam as outras grafias.
GRAFIAS = {"Goiania": (58, 112, 175), "goiânia": (83, 219), "Anapolis": (31, 126, 198)}

type Registro = dict[str, object]


@dataclass(frozen=True, slots=True)
class Pessoa:
    sexo: str
    idade: int
    altura: float
    peso: float


def _sortear_pessoa(rng: np.random.Generator) -> Pessoa:
    sexo = str(rng.choice(["F", "M"]))
    media_altura, desvio_altura = (1.62, 0.06) if sexo == "F" else (1.75, 0.07)
    altura = round(float(rng.normal(media_altura, desvio_altura)), 2)
    imc = float(rng.normal(24.5, 3.2))
    return Pessoa(
        sexo=sexo,
        idade=int(rng.integers(18, 71)),
        altura=altura,
        peso=round(imc * altura**2, 1),
    )


def _registro_sorteado(rng: np.random.Generator) -> Registro:
    pessoa = _sortear_pessoa(rng)
    return {
        "sexo": pessoa.sexo,
        "idade": pessoa.idade,
        "altura_m": pessoa.altura,
        "peso_kg": pessoa.peso,
        "escolaridade": str(rng.choice(ESCOLARIDADES, p=PESOS_ESCOLARIDADE)),
        "cidade": str(rng.choice(CIDADES, p=PESOS_CIDADES)),
        "satisfacao": str(rng.choice(SATISFACOES, p=PESOS_SATISFACAO)),
    }


def _registro_da_previa(valores: tuple[object, ...]) -> Registro:
    return dict(zip(COLUNAS_SAUDE[1:], valores, strict=True))


def _registros_saude(rng: np.random.Generator) -> dict[int, Registro]:
    registros = {i: _registro_da_previa(v) for i, v in enumerate(PREVIA, start=1)}
    for linha in range(len(PREVIA) + 1, TOTAL_LINHAS + 1):
        registros[linha] = _registro_sorteado(rng)
    for linha in COPIAS:
        registros[linha] = dict(registros[LINHA_DUPLICADA])
    return registros


def _plantar_problemas(registros: dict[int, Registro]) -> None:
    for coluna, linhas in FALTANTES.items():
        for linha in linhas:
            registros[linha][coluna] = None
    for coluna, valores in FORA_DE_FAIXA.items():
        for linha, valor in valores.items():
            registros[linha][coluna] = valor
    for grafia, linhas in GRAFIAS.items():
        for linha in linhas:
            registros[linha]["cidade"] = grafia


def _celula_ptbr(valor: object) -> str:
    if valor is None:
        return ""
    if isinstance(valor, float):
        return f"{valor:.2f}".rstrip("0").rstrip(".").replace(".", ",")
    return str(valor)


def _celula_saude(coluna: str, valor: object) -> str:
    if coluna == "peso_kg" and isinstance(valor, float):
        return f"{valor:.1f}".replace(".", ",")
    if coluna == "altura_m" and isinstance(valor, float):
        return f"{valor:.2f}".replace(".", ",")
    return _celula_ptbr(valor)


def gerar_pesquisa_saude(rng: np.random.Generator) -> str:
    """Texto do pesquisa_saude.txt: `;` como separador e vírgula decimal."""
    registros = _registros_saude(rng)
    _plantar_problemas(registros)
    linhas = [";".join(COLUNAS_SAUDE)]
    for numero, registro in sorted(registros.items()):
        celulas = [str(numero)] + [_celula_saude(c, registro[c]) for c in COLUNAS_SAUDE[1:]]
        linhas.append(";".join(celulas))
    return "\n".join(linhas) + "\n"


def _conceito(media: float) -> str:
    limites = ((5.0, "ruim"), (7.0, "regular"), (8.5, "bom"))
    return next((nome for limite, nome in limites if media < limite), "ótimo")


def gerar_notas_turma(rng: np.random.Generator, n: int = 40) -> str:
    """Texto do notas_turma.csv: vírgula como separador, ponto decimal, sem problemas."""
    linhas = ["matricula,turma,faltas,nota_p1,nota_p2,conceito"]
    for i in range(1, n + 1):
        p1 = float(np.clip(round(rng.normal(6.8, 1.6), 1), 0, 10))
        p2 = float(np.clip(round(p1 + rng.normal(0.3, 1.0), 1), 0, 10))
        celulas = (
            f"2026{i:03d}",
            str(rng.choice(["A", "B"])),
            str(int(rng.poisson(3))),
            f"{p1:.1f}",
            f"{p2:.1f}",
            _conceito((p1 + p2) / 2),
        )
        linhas.append(",".join(celulas))
    return "\n".join(linhas) + "\n"


def main() -> None:
    rng = np.random.default_rng(SEMENTE)
    PASTA.mkdir(exist_ok=True)
    arquivos = {
        "pesquisa_saude.txt": gerar_pesquisa_saude(rng),
        "notas_turma.csv": gerar_notas_turma(rng),
    }
    for nome, conteudo in arquivos.items():
        (PASTA / nome).write_text(conteudo, encoding="utf-8", newline="\n")
        print(f"Gravado {PASTA / nome}")


if __name__ == "__main__":
    main()
