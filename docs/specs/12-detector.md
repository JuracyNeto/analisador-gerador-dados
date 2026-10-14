# 12 — Detector de dados artificiais
Domínio: `app/dominios/detector/` (`regras/rNN_*.py` + `regras/base.py` + `registro.py` + `textos.py`/`textos_blocos.py` + `blocos.py` + `tempo.py`) · Endpoint: `GET /api/datasets/{id}/detector` · ADR 0005 · Marco M3

## Contrato
```python
class RegraBase[A, M]:                 # Template Method (D118)
    codigo: str                        # "R4"
    nome: str                          # "Valores redondos"
    seletor: SeletorAlvos[A]           # alvos: colunas de certos tipos, pares de numéricas ou o arquivo
    requisito: Requisito[A]            # motivo de não se aplicar ao alvo, ou None
    def medir(self, alvo: A) -> M
    def dispara(self, medicao: M) -> bool
    def conteudo_aviso(self, alvo: A, medicao: M) -> ConteudoAviso
    def executar(self, tabela: TabelaDetector) -> ResultadoRegra   # avisos, não aplicadas, verificada

Aviso = {regra, nome_regra, severidade: "info"|"atencao"|"alta", colunas[], titulo, resumo, por_que,
         exemplo{linhas[], valores[], texto} | None, pode_ser_normal, o_que_fazer,
         detalhes{medida, valor, limiar, teste?, p_valor?, p_em_palavras?, formula?},
         figura: Figura | None}        # R1, R8 e R9 (D123)
```
- A entrada das regras é a `TabelaDetector` (versão atual do dataset: números das linhas como na prévia, e cada coluna com números — NaN nos faltantes —, textos, datas nas colunas `data` e, nas contínuas, a forma da aba Forma: G₁, G₂ e o p do teste de normalidade), montada pelo `ServicoDetector`. As regras são puras.
- Seletor e requisito são objetos compostos e reaproveitados entre regras (`COLUNAS_NUMERICAS`, `COLUNAS_CONTINUAS`, `PARES_NUMERICOS`, `SemZeros`, `NaLinhaDoTempo`, `MinimoDeValores`, `DigitoFinalTestavel`, `valores_variam`, `Todos`). Sem nenhum alvo, a regra não se aplica ao arquivo com o motivo do seletor ("o arquivo não tem colunas contínuas"). Colunas de outro tipo não viram "não verificada".
- Uma regra com alvos de tipos diferentes junta partes com o mesmo código (`executar_em_partes`, R6); o motivo repetido pelas partes aparece uma vez só.
- Textos montados só em `textos.py` e `textos_blocos.py` (spec 16). No OpenAPI o aviso se chama `AvisoDetector` (D121).
- Avisos da R5 e das cópias da R6 têm `colunas` vazio: falam de linhas inteiras. O da R2 tem as duas colunas do par.
- **Figuras (D123):** R1, R8 e R9 deixam os dados do gráfico no aviso; o `ServicoDetector` pede a figura ao domínio `graficos` (spec 08). Nas demais regras, `figura` é nula.

## Saída do endpoint
`{resumo, avisos[], nao_aplicadas[]}`:
- **Ordem dos avisos:** severidade (alta → atenção → info), número da regra, coluna.
- **Resumo:** `total`, `por_severidade{alta, atencao, info}`, `colunas_afetadas` (na ordem dos avisos), `regras_verificadas` (aplicaram-se a pelo menos um alvo), `regras_nao_aplicadas` (não se aplicaram a nada), `frase` ("Encontramos 5 alertas em 3 colunas"; sem colunas: "Encontramos 1 alerta"; sem alertas: "Nenhum alerta"), `detalhe` ("altura_m, peso_kg e idade · 9 regras verificadas, 2 não se aplicam a este arquivo") e `vazio` (texto da spec 16 quando não há alertas; com uma regra só: "A regra pedida não encontrou suspeitas…"; sem nenhuma regra aplicável: "Nenhuma das regras se aplica a este arquivo; os motivos estão em Regras não verificadas.").
- **Não aplicadas:** uma por (regra, coluna ou par) não verificada, ou sem coluna quando a regra não se aplica ao arquivo; `frase` = "{nome} não verificada em {col}: {motivo}." (no par: "…em altura_m e peso_kg: precisa de 60 pares ou mais; o par tem 48."). A R5 acrescenta "Quase duplicatas não verificadas: o arquivo tem 6.000 linhas e o limite é 5.000." quando o arquivo passa de 5.000 linhas (as idênticas continuam verificadas). Sem coluna de data: "Comparação temporal não verificada: o arquivo não tem uma coluna de data."
- **Exemplo:** linhas e valores (até 20) do trecho onde o padrão se concentra (marcas separadas por no máximo 2 linhas sem o padrão); o texto mostra até 8 valores com "…" e usa "; " quando há decimais ("Linhas 99, 106, 160 e 178: 6,8; 106,4; 712; 109,4"). R3 mostra os inteiros do padrão; R5, as linhas do grupo com uma linha escrita ("Linhas 44 a 47: M · 39 · 1,9 · 98,2 · pós · Goiânia · regular"); R1, o bloco com as médias e os DPs ("Linhas 181 a 200: média 1,702 (geral 1,702) · DP 0,09034 (geral 0,09036)"); R2, as linhas do bloco que mais muda r como "x · y"; R6, as linhas novas copiadas e as antigas iguais ("Linhas 63, 66 e 67: iguais às linhas 53, 55 e 31, fora a data"); R10 não tem exemplo (fala da coluna toda).

## Regras
| # | Nome | Aplica-se a | Medida | Dispara | Severidade |
|---|---|---|---|---|---|
| R1 | Bloco alinhado | numéricas, n ≥ 60, valores não todos iguais | Janelas de k = max(10, ⌊n/20⌋) linhas consecutivas: dᵤ = \|x̄_bloco − x̄\|/s e dₛ = \|s_bloco − s\|/s; candidata = menor max(dᵤ, dₛ). Referência: a melhor janela de cada um de 1.000 embaralhamentos da coluna (D122) | dᵤ e dₛ < 0,01 **e** menos de 1% dos embaralhamentos com uma janela tão parecida | alta |
| R2 | Correlação por blocos | pares de numéricas (todos), n ≥ 60 pares, valores variando em cada bloco | 5 blocos consecutivos; r geral, r de cada bloco e r sem cada bloco | \|r\| − \|média(rᵦ)\| > 0,3, **ou** tirar um bloco baixa \|r\| em mais de 0,3 (D122) | alta (atenção numa série no tempo, D137) |
| R3 | Formato numérico | contínuas, n ≥ 30 | % de valores com casas decimais; posições dos inteiros (o mesmo inteiro em linhas seguidas conta uma vez, D135) | ≥ 80% decimais e inteiros agrupados (≥ 5 seguidos) ou em posições regulares (passo constante repetido ≥ 4 vezes), improváveis com os inteiros espalhados ao acaso: esperados = nº de inteiros · P(intervalo = passo)^repetições, Poisson p < 0,01 | atenção |
| R4 | Valores redondos | numéricas sem os zeros, com dígito final testável (D119, D134), n ≥ 50 | % terminados em 0 ou 5 e em 0, no dígito da precisão da coluna × esperado (20% / 10%) | teste binomial unilateral p < 0,01 e razão ≥ 1,5 (avisa o mais forte) | atenção |
| R5 | Duplicatas | arquivo com ≥ 2 colunas fora os identificadores | linhas com algum número (D138): idênticas; quase idênticas (até 5.000 linhas): numéricas padronizadas, distância euclidiana < 0,01·√p e demais colunas iguais; cada contagem × o acaso (D120) | iguais ou quase iguais além do acaso (Poisson, p < 0,01); **alta** com ≥ 3 iguais em linhas consecutivas, improváveis em ordem aleatória | atenção / alta |
| R6 | Comparação temporal | arquivo com coluna `data`, n ≥ 40, ≥ 10 linhas antes e depois da data do meio | antes × depois da data do meio (mediana inferior da coluna `data` que acompanha a ordem das linhas, D130): DP de cada numérica; linhas novas iguais a alguma antiga, fora datas e identificadores e as linhas sem nenhum número (D125, D138) | DP depois < 0,5 × DP antes com F unilateral p < 0,01, **ou** ≥ 10% das linhas novas iguais a antigas e acima do que as antigas se repetem entre si (binomial, p < 0,01) | alta |
| R7 | Valores distantes | numéricas, n ≥ 10, metade central não constante | IQR: fora de [Q1 − 1,5·IQR, Q3 + 1,5·IQR] ou z = (x − x̄)/s com \|z\| > 3 (moderado); fora de 3·IQR (extremo) (D128); as cercas se alargam do lado da cauda longa (boxplot ajustado, D136) | existir | info (só moderados) / atenção (algum extremo) |
| R8 | Lei de Benford | numéricas sem negativos (zeros fora), n ≥ 100 positivos, P99/P1 ≥ 100 | 1º dígito: P(d) = log₁₀(1 + 1/d); χ² (gl = 8) e MAD = média\|obs − esp\| | p < 0,01 **e** MAD > 0,015 (Nigrini: não conformidade) | atenção |
| R9 | Último dígito | numéricas sem os zeros, com dígito final testável (D119, D134), n ≥ 50 | frequência do último dígito 0–9; χ² de uniformidade (gl = 9) | p < 0,01 **e** o dígito mais comum em ≥ 15% (1,5× o esperado, D134) | atenção |
| R10 | Normal perfeita demais | contínuas, n ≥ 200, valores não todos iguais | \|G₁\|, \|G₂\| e o p do teste de normalidade da aba Forma (Shapiro-Wilk até 5.000 valores; acima, D'Agostino) | \|G₁\| < 0,05 **e** \|G₂\| < 0,1 **e** p > 0,99 (D126) | info |
| R11 | Sequência | numéricas, n ≥ 30, valores não todos iguais (ordem das linhas) | runs acima/abaixo da mediana (Wald-Wolfowitz; os iguais à mediana saem); progressões aritméticas (5 diferenças iguais e não nulas seguidas, na precisão da coluna); autocorrelação lag-1 | runs p < 0,01, **ou** progressões além do acaso (Poisson, p < 0,01), **ou** \|ρ₁\| > 0,8 (D127) | atenção (informativo numa série no tempo, D137) |

### Dígito final testável (R4, R9; D119)
O dígito final é o da precisão da coluna (maior nº de casas observado, até 6): `round(|x| · 10^casas) mod 10` — em `peso_kg` com uma casa, 70 conta como 70,0 (termina em 0). A regra não se aplica se esse dígito é sempre o mesmo ("o último dígito é sempre o mesmo") ou se a metade central (Q1 a Q3) cobre menos de 10 passos da precisão ("os valores variam pouco para o último dígito ser aleatório", ex.: notas de 0 a 10).

Com dados reais (D134): os zeros saem antes — zero é "nada medido" (vento calmo, dia sem chuva), e o motivo de não se aplicar termina em ", fora os zeros". A regra também não se aplica com menos de 10 valores diferentes ("a coluna tem só 4 valores diferentes": descontos de uma tabela) nem com o 1º quartil de |x| abaixo de 10 passos do instrumento ("os valores são pequenos demais para o último dígito ser aleatório"); o passo é o maior divisor comum dos valores na precisão (chuva de 0,2 em 0,2 mm). A R9 exige, além do p, o dígito mais comum em pelo menos 15% (1,5× o esperado, como a R4): com milhares de valores, 13% contra 10% já passa no χ². Um dígito evitado sem nenhum acima de 15% não dispara.

### Duplicatas e o acaso (R5; D120)
Com poucas colunas ou valores de pouca precisão, linhas iguais e quase iguais aparecem sozinhas (altura em cm tem ~30 valores comuns). Por isso cada contagem é comparada ao que o acaso produziria, com teste de Poisson (P(X ≥ observados) < 0,01):
- **Densidade local** (colunas numéricas): na grade da precisão de cada coluna, dados reais têm tantos pares numa posição vizinha quanto na mesma posição. Contam-se os pares numa caixa de até 3 raios (ou 1 passo) em cada numérica, com as demais colunas iguais, fora os iguais e quase iguais; dividindo pelas posições da caixa sai o número de pares por posição. Iguais esperados = 1 posição; quase iguais esperados = posições da grade a distância < 0,01·√p.
- **Colunas independentes** (vale para as não numéricas e como piso das iguais): C(n,2) · Π P(duas linhas coincidirem na coluna j).
- **Linhas seguidas:** com as linhas em ordem aleatória, trincas seguidas de um mesmo grupo de m linhas iguais: Σ m(m−1)(m−2)/(n(n−1)).
Acima de 20.000 linhas, os pares vizinhos são contados numa amostra fixa de 20.000 linhas e escalados por n(n−1)/(m(m−1)) (os pares crescem com n²). Os detalhes técnicos mostram a comparação que justificou o aviso ("3 cópias em 1 grupo · 6 pares iguais (o acaso daria 0,0006361)").

### Bloco alinhado e o acaso (R1; D122)
A candidata é a melhor de n − k + 1 janelas; comparada com um bloco aleatório só, quase toda coluna tem uma janela "alinhada" (44–64% de alertas em amostras Normais e Exponenciais de 500 valores). A referência é, então, a melhor janela de cada embaralhamento da mesma coluna: 1.000 embaralhamentos com semente fixa, em lotes de até 1 milhão de valores, com as janelas por somas acumuladas de x e x² (O(n) por embaralhamento); a simulação para quando 1% dos embaralhamentos já chegou tão perto (a regra não dispara) e só roda quando a candidata passa de dᵤ e dₛ < 0,01. A proporção é o p dos detalhes ("Simulação: 1.000 embaralhamentos da coluna (semente fixa)"). Em colunas de pouca precisão (altura em cm), um bloco arredondado fica a ~0,3% do conjunto e o acaso chega tão perto: só um bloco acertado na precisão da coluna vira alerta.

### Correlação por blocos (R2; D122)
r de qualquer união de blocos sai das somas Σx, Σy, Σx², Σy², Σxy (centradas nas médias gerais). As comparações são em módulo: valem para correlações negativas, e um r geral mais fraco que o dos blocos (valores digitados errado derrubam r) não vira alerta. O resumo usa a média dos blocos ("A correlação geral entre altura_m e peso_kg é 0,78, mas a média dos blocos é só 0,41.") ou, quando só a remoção dispara, o r sem o bloco ("…mas sem as linhas 97–120 ela fica em 0,29.").

### Comparação temporal (R6; D125)
Duas partes com o mesmo código: a variação de cada numérica (só as linhas com data e valor) e as linhas inteiras (colunas fora datas e identificadores). A linha do tempo é a coluna de data que mais acompanha a ordem das linhas (ρ de Spearman com o número da linha ≥ 0,5; sem nenhuma assim, a 1ª coluna de data; D130): num cadastro com nascimento e dia do registro, é o dia. A data do meio é a mediana inferior dessas datas (uma data do arquivo); "antes" vai até ela, inclusive; os detalhes dizem a coluna ("14/12/2026 (data do meio de dia)"). A queda do DP precisa ser improvável ao acaso (F = s²_depois / s²_antes, unilateral, p < 0,01); as cópias, passar do que as linhas antigas se repetem entre si (binomial, p < 0,01) — com poucos valores possíveis (notas 1 a 3), linhas novas repetem antigas sozinhas.

### Sequência (R11; D127)
O aviso cita o padrão mais específico: progressão aritmética ("progressão aritmética nas linhas 50–55"), depois autocorrelação (ρ₁ > 0,8: "cada valor é muito parecido com o anterior"; ρ₁ < −0,8: "valores alternam acima e abaixo do meio com regularidade"), depois runs (muitas trocas: alternância; poucas: "valores acima e abaixo do meio aparecem em sequências longas"). Com valores sorteados, 6 seguidos em progressão têm chance de no máximo p_max⁴ (p_max = frequência do valor mais comum): esperadas = (n − 5) · p_max⁴, e as progressões contam com Poisson p < 0,01.

### Séries no tempo (R2, R11; D137)
Quando uma coluna de data acompanha a ordem das linhas (ρ de Spearman ≥ 0,5, a mesma escolha da R6, em `tempo.py`), o arquivo é uma série no tempo: valores vizinhos são parecidos e a relação entre colunas muda com a época. A R11 fica informativa (qualquer padrão, inclusive progressões: umidade subindo 1% por hora) e a R2 cai de alta para atenção; o "pode ser normal" diz a coluna ("…é uma série no tempo (as linhas seguem a coluna dia): valores vizinhos costumam ser parecidos." / "…a relação muda com o tempo (as linhas seguem a coluna dia; ex.: estações do ano)."). Linhas sem nenhum número (estação desligada) não contam como iguais (R5) nem como cópias (R6) (D138).

### Valores distantes e cauda longa (R7; D136)
As cercas de Tukey se alargam do lado da cauda longa pelo medcouple (MC, assimetria robusta; em `compartilhado/estatistica.py`, numa amostra fixa de 2.000 valores acima disso): com MC ≥ 0, Q3 + k·e^(3·MC)·IQR e Q1 − k·e^(−4·MC)·IQR (boxplot ajustado de Hubert e Vandervieren; espelhado com MC < 0), com k = 1,5 (moderado) e 3 (extremo). Só alargam: cada lado fica no mínimo na cerca de Tukey (o ajuste puro estreitava o outro lado e dava 609 extremos nos preços da ANP, que têm dois grupos). Amostras com algum extremo (n = 300): Exponencial 92,5% → 4%, Gama 67% → 2,5%, Normal 0%; erros ×10 continuam extremos. A log-normal de cauda muito pesada (σ = 1,1) ainda tem extremo em 66% das amostras.

## Fórmulas auxiliares
- Teste binomial (R4, R6): P(X ≥ k | n, p₀); na R4, p₀ = 0,2 (múltiplos de 5) ou 0,1 (de 10)
- χ²: Σ (Oᵢ − Eᵢ)² / Eᵢ
- Runs test: Z = (R − μ_R)/σ_R, μ_R = 2n₁n₂/(n₁+n₂) + 1, σ²_R = 2n₁n₂(2n₁n₂ − n₁ − n₂) / [(n₁+n₂)²(n₁+n₂−1)]
- Autocorrelação lag-1: ρ₁ = Σ(xₜ − x̄)(xₜ₊₁ − x̄) / Σ(xₜ − x̄)²
- Poisson (R3, R5, R11): P(X ≥ k | λ) com λ = casos esperados ao acaso
- F (R6): P(F ≤ s²_depois / s²_antes), gl = (n_depois − 1, n_antes − 1)

Testes binomial, qui-quadrado, runs, Poisson e a autocorrelação ficam em `compartilhado/estatistica.py`; G₁, G₂ e o teste de normalidade vêm da fachada da análise (`ServicoAnalise.resumo_numerico` e `teste_normalidade`, D108).

## Controle de falsos positivos (teste obrigatório; D129)
Em 100 amostras Normais(50, 10) e 100 Exponenciais (média 10), n = 500, arredondadas a 2 casas (`default_rng(1000 + i)`), cada regra dispara em < 5% das amostras (exceto R7, que é informativa). As regras de coluna rodam na amostra sozinha; R2, R5 e R6 numa tabela com datas diárias, a amostra e uma 2ª amostra da mesma família. Taxas obtidas: R11 1% nas duas famílias, R8 2% nas Exponenciais, as demais 0% (a R8 chega a 7–9% nas Exponenciais com outras sementes: a Exponencial não segue Benford à risca). O teste roda no CI (~20 s).

## Dados de demonstração (`dados-exemplo/`; D124)
Gerados por `backend/scripts/gerar_exemplos_detector.py` (semente fixa; `;`, vírgula decimal, UTF-8, LF; um teste confere que o script refaz os arquivos versionados) e escolhíveis em `GET /datasets/exemplos` / `POST /datasets/exemplo?arquivo=`:
- `alturas_reais.txt` — `id;altura_m;peso_kg`, 400 pessoas sem manipulação (altura Normal(1,70; 0,09) em cm, peso pelo IMC): nenhum alerta.
- `alturas_plantadas.txt` — o mesmo conjunto com dados plantados e a coluna `cintura_cm`: linhas 181–200 com alturas de um bloco gerado com a média e o DP do conjunto, acertado na precisão de 1 cm (R1, suspeita alta); linhas 61–70 com pesos inteiros (R3); linhas 301–380 com alturas de 5 em 5 cm (R4; o último dígito também sai do padrão, R9); a mesma linha 4 vezes seguidas (R5, suspeita alta); `cintura_cm` tirada dos quantis da Normal (R10, informativo).
- `vendas_correlacao_puxada.txt` — `data;anuncios;vendas`, 120 semanas: as 96 primeiras com r ≈ 0,3 e as 24 últimas quase numa reta numa faixa mais larga, que puxam a correlação (R2, em atenção: as semanas seguem a ordem das linhas, D137); 9 das semanas 61–96 copiam semanas anteriores (R6; com a data diferente, a R5 não as conta).
