# 12 — Detector de dados artificiais
Domínio: `app/dominios/detector/` (`regras/rNN_*.py` + `regras/base.py` + `registro.py` + `textos.py`) · Endpoint: `GET /api/datasets/{id}/detector` · ADR 0005 · Marco M3

## Contrato
```python
class RegraBase[A, M]:                 # Template Method (D118)
    codigo: str                        # "R4"
    nome: str                          # "Valores redondos"
    seletor: SeletorAlvos[A]           # alvos: colunas de certos tipos, pares (M3.3) ou o arquivo
    requisito: Requisito[A]            # motivo de não se aplicar ao alvo, ou None
    def medir(self, alvo: A) -> M
    def dispara(self, medicao: M) -> bool
    def conteudo_aviso(self, alvo: A, medicao: M) -> ConteudoAviso
    def executar(self, tabela: TabelaDetector) -> ResultadoRegra   # avisos, não aplicadas, verificada

Aviso = {regra, nome_regra, severidade: "info"|"atencao"|"alta", colunas[], titulo, resumo, por_que,
         exemplo{linhas[], valores[], texto} | None, pode_ser_normal, o_que_fazer,
         detalhes{medida, valor, limiar, teste?, p_valor?, p_em_palavras?, formula?}}
```
- A entrada das regras é a `TabelaDetector` (versão atual do dataset: números das linhas como na prévia, e cada coluna com números — NaN nos faltantes —, textos e datas), montada pelo `ServicoDetector`. As regras são puras.
- Seletor e requisito são objetos compostos e reaproveitados entre regras (`COLUNAS_NUMERICAS`, `COLUNAS_CONTINUAS`, `MinimoDeValores`, `DigitoFinalTestavel`, `Todos`). Sem nenhum alvo, a regra não se aplica ao arquivo com o motivo do seletor ("o arquivo não tem colunas contínuas"). Colunas de outro tipo não viram "não verificada".
- Textos montados só em `textos.py` (spec 16). No OpenAPI o aviso se chama `AvisoDetector` (D121).
- Aviso da R5 tem `colunas` vazio: fala de linhas inteiras.

## Saída do endpoint
`{resumo, avisos[], nao_aplicadas[]}`:
- **Ordem dos avisos:** severidade (alta → atenção → info), número da regra, coluna.
- **Resumo:** `total`, `por_severidade{alta, atencao, info}`, `colunas_afetadas` (na ordem dos avisos), `regras_verificadas` (aplicaram-se a pelo menos um alvo), `regras_nao_aplicadas` (não se aplicaram a nada), `frase` ("Encontramos 5 alertas em 3 colunas"; sem colunas: "Encontramos 1 alerta"; sem alertas: "Nenhum alerta"), `detalhe` ("altura_m, peso_kg e idade · 9 regras verificadas, 2 não se aplicam a este arquivo") e `vazio` (texto da spec 16 quando não há alertas; com uma regra só: "A regra pedida não encontrou suspeitas…"; sem nenhuma regra aplicável: "Nenhuma das regras se aplica a este arquivo; os motivos estão em Regras não verificadas.").
- **Não aplicadas:** uma por (regra, coluna) não verificada, ou sem coluna quando a regra não se aplica ao arquivo; `frase` = "{nome} não verificada em {col}: {motivo}.". A R5 acrescenta "Quase duplicatas não verificadas: o arquivo tem 6.000 linhas e o limite é 5.000." quando o arquivo passa de 5.000 linhas (as idênticas continuam verificadas).
- **Exemplo:** linhas e valores (até 20) do trecho onde o padrão se concentra (marcas separadas por no máximo 2 linhas sem o padrão); o texto mostra até 8 valores com "…" e usa "; " quando há decimais ("Linhas 99, 106, 160 e 178: 6,8; 106,4; 712; 109,4"). R3 mostra os inteiros do padrão; R5, as linhas do grupo com uma linha escrita ("Linhas 44 a 47: M · 39 · 1,9 · 98,2 · pós · Goiânia · regular").

## Regras
| # | Nome | Aplica-se a | Medida | Dispara | Severidade |
|---|---|---|---|---|---|
| R1 | Bloco alinhado | numéricas, n ≥ 60 | Janelas de k = max(10, ⌊n/20⌋) linhas consecutivas: dᵤ = \|x̄_bloco − x̄\|/s e dₛ = \|s_bloco − s\|/s. Referência: 1.000 blocos aleatórios de tamanho k (simulação) | dᵤ e dₛ < 0,01 **e** proporção de blocos aleatórios tão próximos < 1% | alta |
| R2 | Correlação por blocos | pares numéricos, n ≥ 60 | Dividir em 5 blocos consecutivos; r geral × média dos rᵦ; r sem cada bloco | r − média(rᵦ) > 0,3, **ou** remover um bloco muda \|r\| em > 0,3 | alta |
| R3 | Formato numérico | contínuas, n ≥ 30 | % de valores com casas decimais; posições dos inteiros | ≥ 80% decimais e inteiros agrupados (≥ 5 seguidos) ou em posições regulares (passo constante repetido ≥ 4 vezes), improváveis com os inteiros espalhados ao acaso: esperados = nº de inteiros · P(intervalo = passo)^repetições, Poisson p < 0,01 | atenção |
| R4 | Valores redondos | numéricas com dígito final testável (D119), n ≥ 50 | % terminados em 0 ou 5 e em 0, no dígito da precisão da coluna × esperado (20% / 10%) | teste binomial unilateral p < 0,01 e razão ≥ 1,5 (avisa o mais forte) | atenção |
| R5 | Duplicatas | arquivo com ≥ 2 colunas fora os identificadores | linhas idênticas; quase idênticas (até 5.000 linhas): numéricas padronizadas, distância euclidiana < 0,01·√p e demais colunas iguais; cada contagem × o acaso (D120) | iguais ou quase iguais além do acaso (Poisson, p < 0,01); **alta** com ≥ 3 iguais em linhas consecutivas, improváveis em ordem aleatória | atenção / alta |
| R6 | Temporal | se houver coluna `data`, n ≥ 40 | dividir em antes/depois da data mediana: média, DP, % de linhas novas idênticas a antigas | DP depois < 0,5 × DP antes, ou ≥ 10% das linhas novas repetem antigas (exceto a data) | alta |
| R7 | Valores distantes | numéricas, n ≥ 10, metade central não constante | IQR: fora de [Q1 − 1,5·IQR, Q3 + 1,5·IQR] (moderado) e de 3·IQR (extremo); z = (x − x̄)/s > 3 também é extremo | existir | info (só moderados) / atenção (algum extremo) |
| R8 | Lei de Benford | numéricas sem negativos (zeros fora), n ≥ 100 positivos, P99/P1 ≥ 100 | 1º dígito: P(d) = log₁₀(1 + 1/d); χ² (gl = 8) e MAD = média\|obs − esp\| | p < 0,01 **e** MAD > 0,015 (Nigrini: não conformidade) | atenção |
| R9 | Último dígito | numéricas com dígito final testável (D119), n ≥ 50 | frequência do último dígito 0–9; χ² de uniformidade (gl = 9) | p < 0,01 | atenção |
| R10 | Normal perfeita demais | contínuas, n ≥ 200 | \|G₁\|, \|G₂\|, Shapiro p | \|G₁\| < 0,05 **e** \|G₂\| < 0,1 **e** p > 0,9 | info |
| R11 | Sequência / variância | numéricas, n ≥ 30 (ordem das linhas) | runs test acima/abaixo da mediana (Wald-Wolfowitz); progressão aritmética (diferenças constantes em ≥ 5 seguidas); autocorrelação lag-1 | runs p < 0,01, **ou** PA detectada, **ou** \|ρ₁\| > 0,8 | atenção |

### Dígito final testável (R4, R9; D119)
O dígito final é o da precisão da coluna (maior nº de casas observado, até 6): `round(|x| · 10^casas) mod 10` — em `peso_kg` com uma casa, 70 conta como 70,0 (termina em 0). A regra não se aplica se esse dígito é sempre o mesmo ("o último dígito é sempre o mesmo") ou se a metade central (Q1 a Q3) cobre menos de 10 passos da precisão ("os valores variam pouco para o último dígito ser aleatório", ex.: notas de 0 a 10).

### Duplicatas e o acaso (R5; D120)
Com poucas colunas ou valores de pouca precisão, linhas iguais e quase iguais aparecem sozinhas (altura em cm tem ~30 valores comuns). Por isso cada contagem é comparada ao que o acaso produziria, com teste de Poisson (P(X ≥ observados) < 0,01):
- **Densidade local** (colunas numéricas): na grade da precisão de cada coluna, dados reais têm tantos pares numa posição vizinha quanto na mesma posição. Contam-se os pares numa caixa de até 3 raios (ou 1 passo) em cada numérica, com as demais colunas iguais, fora os iguais e quase iguais; dividindo pelas posições da caixa sai o número de pares por posição. Iguais esperados = 1 posição; quase iguais esperados = posições da grade a distância < 0,01·√p.
- **Colunas independentes** (vale para as não numéricas e como piso das iguais): C(n,2) · Π P(duas linhas coincidirem na coluna j).
- **Linhas seguidas:** com as linhas em ordem aleatória, trincas seguidas de um mesmo grupo de m linhas iguais: Σ m(m−1)(m−2)/(n(n−1)).
Acima de 20.000 linhas, os pares vizinhos são contados numa amostra fixa de 20.000 linhas e escalados por n(n−1)/(m(m−1)) (os pares crescem com n²). Os detalhes técnicos mostram a comparação que justificou o aviso ("3 cópias em 1 grupo · 6 pares iguais (o acaso daria 0,0006361)").

## Fórmulas auxiliares
- Teste binomial (R4): P(X ≥ k | n, p₀), p₀ = 0,2 (múltiplos de 5) ou 0,1 (de 10)
- χ²: Σ (Oᵢ − Eᵢ)² / Eᵢ
- Runs test: Z = (R − μ_R)/σ_R, μ_R = 2n₁n₂/(n₁+n₂) + 1, σ²_R = 2n₁n₂(2n₁n₂ − n₁ − n₂) / [(n₁+n₂)²(n₁+n₂−1)]
- Autocorrelação lag-1: ρ₁ = Σ(xₜ − x̄)(xₜ₊₁ − x̄) / Σ(xₜ − x̄)²
- Poisson (R5): P(X ≥ k | λ) com λ = pares esperados ao acaso

Testes binomial, qui-quadrado, runs e a autocorrelação ficam em `compartilhado/estatistica.py`.

## Controle de falsos positivos (teste obrigatório)
Em 100 amostras Normais aleatórias (n = 500) e 100 Exponenciais, cada regra dispara em < 5% das amostras (exceto R7, que é informativa).

## Dados de demonstração (`dados-exemplo/`)
- `alturas_reais.txt` — dados sem manipulação
- `alturas_plantadas.txt` — mesmo conjunto + bloco gerado com ajuste exato (dispara R1, R10), inteiros inseridos (R3), valores redondos (R4) e linhas duplicadas em sequência (R5)
- `vendas_correlacao_puxada.txt` — par com bloco final que infla r (R2)
