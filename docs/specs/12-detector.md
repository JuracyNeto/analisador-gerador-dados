# 12 — Detector de dados artificiais
Domínio: `app/dominios/detector/` (`regras/rNN_*.py` + `regras/base.py` + `registro.py` + `textos.py`) · Endpoint: `GET /api/datasets/{id}/detector` · ADR 0005 · Marco M3

## Contrato
```python
class Regra(Protocol):
    codigo: str          # "R4"
    nome: str            # "Valores redondos"
    def aplicavel(self, df, tipos) -> list[NaoAplicavel]   # colunas onde não se aplica + motivo
    def avaliar(self, df, tipos) -> list[Aviso]

Aviso = {regra, severidade: "info"|"atencao"|"alta", colunas[], titulo, resumo, por_que,
         exemplo{linhas[], valores[]}, pode_ser_normal, o_que_fazer,
         detalhes{medida, valor, limiar, teste, p_valor, formula}}
```
Textos montados a partir de `textos.py` (spec 16). Saída do endpoint: `{resumo{total, por_severidade, colunas_afetadas}, avisos[], nao_aplicadas[]}` ordenados por severidade.

## Regras
| # | Nome | Aplica-se a | Medida | Dispara | Severidade |
|---|---|---|---|---|---|
| R1 | Bloco alinhado | numéricas, n ≥ 60 | Janelas de k = max(10, ⌊n/20⌋) linhas consecutivas: dᵤ = \|x̄_bloco − x̄\|/s e dₛ = \|s_bloco − s\|/s. Referência: 1.000 blocos aleatórios de tamanho k (simulação) | dᵤ e dₛ < 0,01 **e** proporção de blocos aleatórios tão próximos < 1% | alta |
| R2 | Correlação por blocos | pares numéricos, n ≥ 60 | Dividir em 5 blocos consecutivos; r geral × média dos rᵦ; r sem cada bloco | r − média(rᵦ) > 0,3, **ou** remover um bloco muda \|r\| em > 0,3 | alta |
| R3 | Formato numérico | contínuas | % de linhas com casas decimais; posições dos inteiros | ≥ 80% decimais e inteiros agrupados (runs) ou em posições regulares | atenção |
| R4 | Valores redondos | numéricas com ≥ 1 casa variável, n ≥ 50 | % múltiplos de 5 e de 10 (no último dígito significativo) × esperado (20% / 10%) | teste binomial unilateral p < 0,01 e razão ≥ 1,5 | atenção |
| R5 | Duplicatas | todas | linhas idênticas; quase idênticas: numéricas padronizadas, distância euclidiana < 0,01·√p e qualitativas iguais | existir; **alta** se ≥ 3 em linhas consecutivas | atenção / alta |
| R6 | Temporal | se houver coluna `data`, n ≥ 40 | dividir em antes/depois da data mediana: média, DP, % de linhas novas idênticas a antigas | DP depois < 0,5 × DP antes, ou ≥ 10% das linhas novas repetem antigas (exceto a data) | alta |
| R7 | Outliers | numéricas | IQR: fora de [Q1 − 1,5·IQR, Q3 + 1,5·IQR] (moderado) e de 3·IQR (extremo); z = (x − x̄)/s > 3 | existir | info (moderado) / atenção (extremo) |
| R8 | Lei de Benford | numéricas positivas, n ≥ 100, máx/mín ≥ 100 | 1º dígito: P(d) = log₁₀(1 + 1/d); χ² (gl = 8) e MAD = média\|obs − esp\| | p < 0,01 **e** MAD > 0,015 (Nigrini: não conformidade) | atenção |
| R9 | Último dígito | numéricas com dígito final variável, n ≥ 50 | frequência do último dígito 0–9; χ² de uniformidade (gl = 9) | p < 0,01 | atenção |
| R10 | Normal perfeita demais | contínuas, n ≥ 200 | \|G₁\|, \|G₂\|, Shapiro p | \|G₁\| < 0,05 **e** \|G₂\| < 0,1 **e** p > 0,9 | info |
| R11 | Sequência / variância | numéricas, n ≥ 30 (ordem das linhas) | runs test acima/abaixo da mediana (Wald-Wolfowitz); progressão aritmética (diferenças constantes em ≥ 5 seguidas); autocorrelação lag-1 | runs p < 0,01, **ou** PA detectada, **ou** \|ρ₁\| > 0,8 | atenção |

## Fórmulas auxiliares
- Teste binomial (R4): P(X ≥ k | n, p₀), p₀ = 0,2 (múltiplos de 5) ou 0,1 (de 10)
- χ²: Σ (Oᵢ − Eᵢ)² / Eᵢ
- Runs test: Z = (R − μ_R)/σ_R, μ_R = 2n₁n₂/(n₁+n₂) + 1, σ²_R = 2n₁n₂(2n₁n₂ − n₁ − n₂) / [(n₁+n₂)²(n₁+n₂−1)]
- Autocorrelação lag-1: ρ₁ = Σ(xₜ − x̄)(xₜ₊₁ − x̄) / Σ(xₜ − x̄)²

## Controle de falsos positivos (teste obrigatório)
Em 100 amostras Normais aleatórias (n = 500) e 100 Exponenciais, cada regra dispara em < 5% das amostras (exceto R7, que é informativa).

## Dados de demonstração (`dados-exemplo/`)
- `alturas_reais.txt` — dados sem manipulação
- `alturas_plantadas.txt` — mesmo conjunto + bloco gerado com ajuste exato (dispara R1, R10), inteiros inseridos (R3), valores redondos (R4) e linhas duplicadas em sequência (R5)
- `vendas_correlacao_puxada.txt` — par com bloco final que infla r (R2)
