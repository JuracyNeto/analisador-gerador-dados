"""Gera os arquivos de demonstração do detector em dados-exemplo/ (semente fixa, D124).

O que cada arquivo dispara (spec 12):
- alturas_reais.txt — id;altura_m;peso_kg, 400 pessoas sem manipulação: nenhum alerta de
  atenção ou de suspeita alta (a R7 pode dar um informativo).
- alturas_plantadas.txt — o mesmo conjunto com dados plantados e a coluna cintura_cm:
  linhas 181–200 com alturas de um bloco gerado com a média e o DP do restante (R1);
  linhas 61–70 com pesos inteiros no meio de pesos com decimais (R3);
  linhas 301–380 com alturas de 5 em 5 cm (R4; o último dígito também sai do padrão, R9);
  a mesma linha 4 vezes seguidas entre as linhas 250 e 299 (R5, suspeita alta);
  cintura_cm tirada direto da curva Normal, perfeita demais (R10).
- vendas_correlacao_puxada.txt — data;anuncios;vendas, 120 semanas: as 24 últimas,
  alinhadas numa faixa mais larga, puxam a correlação (R2); 9 das semanas 61–96 copiam
  semanas anteriores (R6; a data muda, então a R5 não as conta como duplicatas).

Uso (em backend/): python scripts/gerar_exemplos_detector.py [--pasta ../dados-exemplo]
"""

import argparse
from collections.abc import Sequence
from datetime import date, timedelta
from pathlib import Path

import numpy as np
from scipy import stats

from app.compartilhado.tipos import TipoVariavel
from app.core.config import Configuracao
from app.dominios.analise.servico import ServicoAnalise
from app.dominios.datasets.repositorio import RepositorioDatasets
from app.dominios.datasets.servico import ServicoDatasets
from app.dominios.gerador.pedidos import PedidoUnivariado
from app.dominios.gerador.servico import RepositorioGerados, ServicoGerador

SEMENTE = 2060
PASTA = Path(__file__).resolve().parents[2] / "dados-exemplo"
PESSOAS = 400
CENTIMETROS = 100

BLOCO_ALINHADO = slice(180, 200)
INTEIROS = slice(60, 70)
REDONDAS = slice(300, 380)
PASSO_REDONDO = 5
"""Alturas de 5 em 5 cm (R4)."""
ORIGENS_COPIAS = range(249, 296)
COPIAS = 3
CINTURA = (80.0, 10.0)

SEMANAS = 120
INICIO_VENDAS = date(2025, 1, 6)
SEMANAS_ANTIGAS = 60
SEMANAS_PUXADAS = 24
SEMANAS_COPIADAS = 9


# Pessoas ------------------------------------------------------------------------------------


def pessoas(rng: np.random.Generator, n: int) -> tuple[np.ndarray, np.ndarray]:
    """Alturas Normal(1,70; 0,09) em centímetros e pesos pelo IMC (ligados à altura)."""
    alturas = np.round(rng.normal(1.70, 0.09, n) * CENTIMETROS).astype("int64")
    return alturas, _pesos(rng, alturas)


def _pesos(rng: np.random.Generator, alturas: np.ndarray) -> np.ndarray:
    imc = rng.normal(24.5, 3.0, len(alturas))
    return np.round(imc * (alturas / CENTIMETROS) ** 2, 1)


def _gerar_exato(n: int, media: float, desvio: float, semente: int) -> np.ndarray:
    """n valores com média e DP exatos pelo gerador do app (Normal com reescala)."""
    config = Configuracao()
    datasets = ServicoDatasets(RepositorioDatasets(config.max_datasets), config)
    gerador = ServicoGerador(
        datasets, ServicoAnalise(datasets), RepositorioGerados(config.max_gerados), config
    )
    pedido = PedidoUnivariado(
        x=n,
        modo="parametros",
        tipo=TipoVariavel.CONTINUA,
        media=media,
        desvio=desvio,
        semente=semente,
    )
    return gerador.univariado(pedido).dados.iloc[:, 0].to_numpy(dtype="float64")


def _melhor_troca(bloco: np.ndarray, falta: float) -> tuple[int, int, float]:
    """+1 em i e −1 em j (a soma fica igual) que deixa Σx² mais perto do alvo."""
    variacao = (2 * (bloco[:, np.newaxis] - bloco[np.newaxis, :]) + 2).astype("float64")
    np.fill_diagonal(variacao, np.inf)
    i, j = np.unravel_index(int(np.argmin(np.abs(falta - variacao))), variacao.shape)
    return int(i), int(j), float(variacao[i, j])


def bloco_alinhado(resto: np.ndarray, k: int, semente: int) -> np.ndarray:
    """k valores inteiros (cm) com a média e o DP do restante das linhas (R1 compara com ele, D142).

    Média igual ⇔ soma do bloco = k · soma do resto / (n − k) (em cm, só quando a conta é exata);
    DP igual ⇔ Σx² do bloco = (k − 1) · s²_resto + soma² / k. Começa pelo gerador do app e acerta
    Σx² trocando 1 cm entre dois valores.
    """
    soma = k * int(resto.sum()) // len(resto)
    desvio = float(resto.std(ddof=1))
    bloco = np.round(_gerar_exato(k, soma / k, desvio, semente)).astype("int64")
    diferenca = soma - int(bloco.sum())
    bloco[np.arange(abs(diferenca)) % k] += np.sign(diferenca)
    falta = (k - 1) * desvio**2 + soma**2 / k - float(np.sum(bloco**2))
    while True:
        i, j, variacao = _melhor_troca(bloco, falta)
        if abs(falta - variacao) >= abs(falta):
            return bloco
        bloco[i] += 1
        bloco[j] -= 1
        falta -= variacao


def _copias(origem: int) -> slice:
    return slice(origem + 1, origem + 1 + COPIAS)


def _media_exata_possivel(alturas: np.ndarray, posicoes_bloco: np.ndarray) -> bool:
    """Em cm inteiros, o bloco só tem a média exata se k · soma do resto divide por n − k."""
    resto = np.delete(alturas, posicoes_bloco)
    return len(posicoes_bloco) * int(resto.sum()) % len(resto) == 0


def _origem_das_copias(alturas: np.ndarray, posicoes_bloco: np.ndarray) -> int:
    """1ª linha (de 250 a 296) cujas cópias deixam a média exata possível."""
    for origem in ORIGENS_COPIAS:
        copiadas = alturas.copy()
        copiadas[_copias(origem)] = alturas[origem]
        if _media_exata_possivel(copiadas, posicoes_bloco):
            return origem
    raise ValueError("nenhuma linha serve de origem das cópias")


def cintura_perfeita(rng: np.random.Generator, n: int, iguais: slice) -> np.ndarray:
    """Quantis da Normal(80; 10) embaralhados: a forma exata da curva (R10).

    As linhas iguais (R5) ficam com um valor do meio da curva no lugar dos quantis do meio:
    copiar um valor da ponta deformaria a forma. O valor tem casa decimal, para as cópias não
    virarem inteiros seguidos (R3).
    """
    media, desvio = CINTURA
    quantis = np.round(media + desvio * stats.norm.ppf((np.arange(1, n + 1) - 0.5) / n), 1)
    tamanho = iguais.stop - iguais.start
    do_meio = np.arange(tamanho) + n // 2 - tamanho // 2
    outras = np.ones(n, dtype=bool)
    outras[iguais] = False
    cintura = np.empty(n)
    cintura[outras] = rng.permutation(np.delete(quantis, do_meio))
    cintura[iguais] = next(valor for valor in quantis[n // 2 :] if valor != round(valor))
    return cintura


def plantar(
    rng: np.random.Generator, alturas: np.ndarray, pesos: np.ndarray
) -> tuple[np.ndarray, ...]:
    """Inteiros (R3), alturas redondas (R4), cópias (R5), bloco (R1) e cintura (R10)."""
    alturas, pesos = alturas.copy(), pesos.copy()
    pesos[INTEIROS] = np.round(pesos[INTEIROS])
    alturas[REDONDAS] = np.round(alturas[REDONDAS] / PASSO_REDONDO) * PASSO_REDONDO
    posicoes_bloco = np.arange(len(alturas))[BLOCO_ALINHADO]
    origem = _origem_das_copias(alturas, posicoes_bloco)
    cintura = cintura_perfeita(rng, len(alturas), slice(origem, _copias(origem).stop))
    for coluna in (alturas, pesos):
        coluna[_copias(origem)] = coluna[origem]
    resto = np.delete(alturas, posicoes_bloco)
    alturas[BLOCO_ALINHADO] = bloco_alinhado(resto, len(posicoes_bloco), SEMENTE)
    pesos[BLOCO_ALINHADO] = _pesos(rng, alturas[BLOCO_ALINHADO])
    return alturas, pesos, cintura


# Escrita ------------------------------------------------------------------------------------


def _decimal(valor: float, casas: int) -> str:
    return f"{valor:.{casas}f}".replace(".", ",")


def _texto(cabecalho: Sequence[str], linhas: Sequence[Sequence[str]]) -> str:
    """`;` como separador, vírgula decimal e fim de linha LF."""
    return "\n".join(";".join(celulas) for celulas in [list(cabecalho), *linhas]) + "\n"


def _linhas_pessoas(alturas: np.ndarray, pesos: np.ndarray) -> list[list[str]]:
    return [
        [str(i), _decimal(altura / CENTIMETROS, 2), _decimal(peso, 1)]
        for i, (altura, peso) in enumerate(zip(alturas, pesos, strict=True), start=1)
    ]


def gerar_alturas_reais(rng: np.random.Generator) -> tuple[str, np.ndarray, np.ndarray]:
    alturas, pesos = pessoas(rng, PESSOAS)
    return _texto(("id", "altura_m", "peso_kg"), _linhas_pessoas(alturas, pesos)), alturas, pesos


def gerar_alturas_plantadas(
    rng: np.random.Generator, alturas: np.ndarray, pesos: np.ndarray
) -> str:
    plantadas, pesos_plantados, cintura = plantar(rng, alturas, pesos)
    linhas = [
        [*linha, _decimal(medida, 1)]
        for linha, medida in zip(_linhas_pessoas(plantadas, pesos_plantados), cintura, strict=True)
    ]
    return _texto(("id", "altura_m", "peso_kg", "cintura_cm"), linhas)


# Vendas -------------------------------------------------------------------------------------


def _vendas_comuns(rng: np.random.Generator, n: int) -> tuple[np.ndarray, np.ndarray]:
    """Anúncios ~ 20 ± 4 e vendas ligadas a eles com r ≈ 0,3 (R$ mil)."""
    anuncios = np.round(rng.normal(20, 4, n))
    return anuncios, np.round(150 + 2 * anuncios + rng.normal(0, 25.4, n), 1)


def _vendas_puxadas(rng: np.random.Generator, n: int) -> tuple[np.ndarray, np.ndarray]:
    """Faixa mais larga de anúncios, com as vendas quase numa reta (r ≈ 0,99)."""
    anuncios = rng.permutation(np.round(np.linspace(8, 32, n)))
    return anuncios, np.round(190 + 10 * (anuncios - 20) + rng.normal(0, 8, n), 1)


def gerar_vendas(rng: np.random.Generator) -> str:
    comuns = SEMANAS - SEMANAS_PUXADAS
    anuncios, vendas = (
        np.concatenate(partes)
        for partes in zip(
            _vendas_comuns(rng, comuns), _vendas_puxadas(rng, SEMANAS_PUXADAS), strict=True
        )
    )
    novas = np.sort(rng.choice(np.arange(SEMANAS_ANTIGAS, comuns), SEMANAS_COPIADAS, replace=False))
    antigas = rng.choice(SEMANAS_ANTIGAS, SEMANAS_COPIADAS, replace=False)
    anuncios[novas], vendas[novas] = anuncios[antigas], vendas[antigas]
    linhas = [
        [
            (INICIO_VENDAS + timedelta(weeks=i)).strftime("%d/%m/%Y"),
            str(int(anuncio)),
            _decimal(venda, 1),
        ]
        for i, (anuncio, venda) in enumerate(zip(anuncios, vendas, strict=True))
    ]
    return _texto(("data", "anuncios", "vendas"), linhas)


# Arquivos -----------------------------------------------------------------------------------


def textos_dos_exemplos() -> dict[str, str]:
    """Conteúdo de cada arquivo (cada um com o seu gerador, a partir da mesma semente)."""
    rng_pessoas, rng_plantio, rng_vendas = (np.random.default_rng([SEMENTE, i]) for i in range(3))
    reais, alturas, pesos = gerar_alturas_reais(rng_pessoas)
    return {
        "alturas_reais.txt": reais,
        "alturas_plantadas.txt": gerar_alturas_plantadas(rng_plantio, alturas, pesos),
        "vendas_correlacao_puxada.txt": gerar_vendas(rng_vendas),
    }


def gravar(pasta: Path) -> list[Path]:
    pasta.mkdir(parents=True, exist_ok=True)
    caminhos = []
    for nome, conteudo in textos_dos_exemplos().items():
        caminho = pasta / nome
        with caminho.open("w", encoding="utf-8", newline="\n") as arquivo:
            arquivo.write(conteudo)
        caminhos.append(caminho)
    return caminhos


def main() -> None:
    parser = argparse.ArgumentParser(description="Gera os arquivos de demonstração do detector.")
    parser.add_argument("--pasta", type=Path, default=PASTA)
    for caminho in gravar(parser.parse_args().pasta):
        print(f"Gravado {caminho}")


if __name__ == "__main__":
    main()
