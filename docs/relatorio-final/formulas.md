# Fórmulas

> Gerado por `backend/scripts/exportar_formulas.py` a partir dos catálogos do app (`analise/formulas.py`, `gerador/formulas.py` e `detector/formulas.py`): são as mesmas fórmulas da tela, do apêndice do relatório HTML e dos detalhes do detector. Não edite à mão; para refazer, rode `python scripts/exportar_formulas.py` em `backend/`.

Cada fórmula aparece com o nome, a forma matemática e o texto que o app mostra quando a fórmula não pode ser desenhada (por exemplo, no relatório aberto sem internet).

## Frequências

### Frequência relativa

```math
fr_i = \frac{f_i}{n}
```

Em texto: `frᵢ = fᵢ / n`

### Frequência acumulada

```math
F_i = \sum_{j \le i} f_j
```

Em texto: `Fᵢ = Σⱼ≤ᵢ fⱼ`

### Número de classes (Sturges)

```math
k = \lceil 1 + 3{,}322 \log_{10} n \rceil
```

Em texto: `k = ⌈1 + 3,322 · log₁₀ n⌉`

### Amplitude da classe

```math
h = \frac{x_{max} - x_{min}}{k}
```

Em texto: `h = (xₘₐₓ − xₘᵢₙ) / k`

### Ponto médio

```math
x_i = \frac{L_i + L_{i+1}}{2}
```

Em texto: `xᵢ = (Lᵢ + Lᵢ₊₁) / 2`

## Tendência central

### Média

```math
\bar{x} = \frac{\sum x_i}{n}
```

Em texto: `x̄ = Σxᵢ / n`

### Mediana

```math
Md = x_{\left(\frac{n+1}{2}\right)}
```

Em texto: `Md = valor central dos dados ordenados`

### Moda

```math
Mo = \text{valor de maior } f_i
```

Em texto: `Mo = valor mais frequente`

### Moda de Czuber

```math
Mo = L_i + \frac{\Delta_1}{\Delta_1 + \Delta_2} \cdot h
```

Em texto: `Mo = Lᵢ + [Δ₁ / (Δ₁ + Δ₂)] · h`

### Proporção

```math
p = \frac{\text{sucessos}}{n}
```

Em texto: `p = nº de sucessos / n`

## Separatrizes

### Separatriz (interpolação linear)

```math
Q_p = x_{(\lfloor h \rfloor)} + (h - \lfloor h \rfloor)(x_{(\lfloor h \rfloor + 1)} - x_{(\lfloor h \rfloor)}),\ h = (n-1)p
```

Em texto: `Qp = x₍⌊h⌋₎ + (h − ⌊h⌋)·(x₍⌊h⌋+1₎ − x₍⌊h⌋₎), h = (n − 1)·p`

### Posição percentil

```math
PR = 100 \cdot \frac{\#(x_i < v) + 0{,}5 \cdot \#(x_i = v)}{n}
```

Em texto: `PR = 100 · (nº de xᵢ < v + 0,5 · nº de xᵢ = v) / n`

## Dispersão

### Amplitude

```math
A = x_{max} - x_{min}
```

Em texto: `A = xₘₐₓ − xₘᵢₙ`

### Variância amostral

```math
s^2 = \frac{\sum (x_i - \bar{x})^2}{n - 1}
```

Em texto: `s² = Σ(xᵢ − x̄)² / (n − 1)`

### Variância populacional

```math
\sigma^2 = \frac{\sum (x_i - \mu)^2}{n}
```

Em texto: `σ² = Σ(xᵢ − μ)² / n`

### Desvio padrão

```math
s = \sqrt{s^2}
```

Em texto: `s = √s²`

### Amplitude interquartil

```math
IQR = Q_3 - Q_1
```

Em texto: `IQR = Q3 − Q1`

### Coeficiente de variação

```math
CV = \frac{s}{\bar{x}} \cdot 100\%
```

Em texto: `CV = (s / x̄) · 100%`

### Variância (binária)

```math
Var = p(1 - p)
```

Em texto: `Var = p(1 − p)`

## Forma e distribuições

### Assimetria (Fisher)

```math
G_1 = \frac{\sqrt{n(n-1)}}{n-2} \cdot \frac{m_3}{m_2^{3/2}},\ m_k = \frac{\sum (x_i - \bar{x})^k}{n}
```

Em texto: `G₁ = [√(n(n−1)) / (n−2)] · m₃ / m₂^(3/2), mₖ = Σ(xᵢ − x̄)ᵏ / n`

### 1º coeficiente de Pearson

```math
As_1 = \frac{\bar{x} - Mo}{s}
```

Em texto: `As₁ = (x̄ − Mo) / s`

### 2º coeficiente de Pearson

```math
As_2 = \frac{3(\bar{x} - Md)}{s}
```

Em texto: `As₂ = 3(x̄ − Md) / s`

### Curtose (excesso)

```math
G_2 = \frac{(n+1)n(n-1)}{(n-2)(n-3)} \cdot \frac{\sum (x_i-\bar{x})^4}{(\sum (x_i-\bar{x})^2)^2} - \frac{3(n-1)^2}{(n-2)(n-3)}
```

Em texto: `G₂ = curtose amostral − 3 (Normal = 0)`

### Curtose percentílica

```math
K = \frac{Q_3 - Q_1}{2(P_{90} - P_{10})}
```

Em texto: `K = (Q3 − Q1) / [2(P90 − P10)] (Normal ≈ 0,263)`

### Distribuição Normal

```math
f(x) = \frac{1}{\sigma\sqrt{2\pi}} e^{-\frac{(x-\mu)^2}{2\sigma^2}}
```

Em texto: `f(x) = (1 / (σ√(2π))) · e^(−(x−μ)² / (2σ²))`

### Distribuição Binomial

```math
P(X = k) = \binom{n}{k} p^k (1-p)^{n-k}
```

Em texto: `P(X = k) = C(n,k) · pᵏ · (1−p)ⁿ⁻ᵏ`

### Distribuição de Bernoulli

```math
P(X = 1) = p,\ E[X] = p,\ Var = p(1-p)
```

Em texto: `P(X = 1) = p · E[X] = p · Var = p(1 − p)`

### Qui-quadrado de aderência

```math
\chi^2 = \sum \frac{(O_i - E_i)^2}{E_i}
```

Em texto: `χ² = Σ (Oᵢ − Eᵢ)² / Eᵢ`

## Correlação e regressão

### Correlação de Pearson

```math
r = \frac{\sum (x_i - \bar{x})(y_i - \bar{y})}{\sqrt{\sum (x_i - \bar{x})^2 \cdot \sum (y_i - \bar{y})^2}}
```

Em texto: `r = Σ(xᵢ − x̄)(yᵢ − ȳ) / √[Σ(xᵢ − x̄)² · Σ(yᵢ − ȳ)²]`

### Teste de significância de r

```math
t = \frac{r\sqrt{n-2}}{\sqrt{1-r^2}},\ gl = n - 2
```

Em texto: `t = r√(n − 2) / √(1 − r²), gl = n − 2`

### Correlação de Spearman

```math
\rho = r(\text{postos de } X, \text{postos de } Y)
```

Em texto: `ρ = Pearson dos postos de X e de Y`

### Reta de regressão

```math
\hat{Y} = a + bX,\ b = \frac{\sum (x_i - \bar{x})(y_i - \bar{y})}{\sum (x_i - \bar{x})^2},\ a = \bar{y} - b\bar{x}
```

Em texto: `Ŷ = a + bX · b = Σ(xᵢ − x̄)(yᵢ − ȳ) / Σ(xᵢ − x̄)² · a = ȳ − b·x̄`

### Coeficiente de determinação

```math
R^2 = r^2
```

Em texto: `R² = r²`

### Erro padrão da estimativa

```math
S_e = \sqrt{\frac{\sum (y_i - \hat{y}_i)^2}{n - 2}}
```

Em texto: `Sₑ = √[Σ(yᵢ − ŷᵢ)² / (n − 2)]`

### Resíduo

```math
e_i = y_i - \hat{y}_i
```

Em texto: `eᵢ = yᵢ − ŷᵢ`

## Gerador

### Sorteio da Normal

```math
g_i \sim \mathcal{N}(\mu, \sigma^2)
```

Em texto: `gᵢ ~ Normal(μ, σ²)`

### Densidade por núcleo (KDE, banda de Scott)

```math
\hat{f}(x) = \frac{1}{nh} \sum_{i=1}^{n} K\left(\frac{x - x_i}{h}\right),\ h = s \cdot n^{-1/5}
```

Em texto: `f̂(x) = (1 / nh) · Σ K((x − xᵢ) / h), K = Normal(0, 1), h = s · n^(−1/5)`

### Normal arredondada

```math
x_i' = \operatorname{arred}(\mu + \sigma \cdot z_i)
```

Em texto: `xᵢ' = arredondar(μ + σ·zᵢ), sem negativos se o original não tinha`

### Distribuição de Poisson

```math
P(X = k) = \frac{\lambda^k e^{-\lambda}}{k!},\ \lambda = \bar{x}
```

Em texto: `P(X = k) = λᵏ · e^(−λ) / k!, λ = x̄`

### Sorteio pelos valores observados

```math
P(X = v) = \frac{f_v}{n}
```

Em texto: `P(X = v) = f_v / n (sorteio com reposição)`

### Distribuição de Bernoulli

```math
P(\text{sucesso}) = p,\ P(\text{fracasso}) = 1 - p
```

Em texto: `P(sucesso) = p · P(fracasso) = 1 − p`

### Sorteio pelas frequências

```math
P(X = c) = fr_c = \frac{f_c}{n}
```

Em texto: `P(categoria c) = fr_c = f_c / n`

### Reescala exata

```math
z_i = \frac{g_i - \bar{g}}{s_g},\ x_i' = \bar{x} + s \cdot z_i
```

Em texto: `zᵢ = (gᵢ − ḡ) / s_g → xᵢ' = x̄ + s·zᵢ`

### Pares com correlação (Cholesky)

```math
X = \mu_x + \sigma_x Z_1,\ Y = \mu_y + \sigma_y \left(\rho Z_1 + \sqrt{1 - \rho^2}\, Z_2\right)
```

Em texto: `X = μx + σx·Z₁ · Y = μy + σy·(ρ·Z₁ + √(1 − ρ²)·Z₂)`

### Ajuste exato (Gram-Schmidt)

```math
Z_2' = Z_2 - \frac{Z_2 \cdot Z_1}{Z_1 \cdot Z_1} Z_1
```

Em texto: `Z₂' = Z₂ − (Z₂·Z₁ / Z₁·Z₁)·Z₁, com Z₁ e Z₂' centradas e com DP 1 (r amostral = ρ)`

## Detector

As regras do detector mostram estas fórmulas em texto nos detalhes técnicos de cada alerta, com os valores do alerta no lugar de k, n, p₀ e do medcouple. Os limiares de cada regra estão na seção 9 do relatório final e na spec 12.

### R1 · Bloco alinhado

- `dᵤ = |x̄_bloco − x̄_resto| / s_resto`
- `dₛ = |s_bloco − s_resto| / s_resto`

### R2 · Correlação por blocos

- `r = Σ(x − x̄)(y − ȳ) / √[Σ(x − x̄)² · Σ(y − ȳ)²]`

### R3 · Formato numérico

- `Esperados = nº de inteiros · P(intervalo = passo)^repetições`

### R4 · Valores redondos

- `P(X ≥ k), X ~ Binomial(n; p₀)`

### R5 · Duplicatas

- `Quase iguais: distância entre as linhas padronizadas < 0,01·√p (p = nº de colunas numéricas, fora as vazias nas duas linhas) e as demais colunas iguais; contam quando passam do acaso, estimado pelos pares vizinhos na precisão de cada coluna`
- `Só linhas idênticas`

### R6 · Comparação temporal

- `F = s²_depois / s²_antes`
- `P(X ≥ k), X ~ Binomial(linhas novas; fração das antigas que se repetem)`

### R7 · Valores distantes

- `IQR = Q3 − Q1`
- `z = (x − x̄) / s`
- `MC = medcouple da coluna; com MC > 0 a cerca de cima vai a Q3 + k·e^(3·MC)·IQR, nunca abaixo de Q3 + k·IQR; a etapa Limpeza usa as cercas sem o ajuste`

### R8 · Lei de Benford

- `P(d) = log₁₀(1 + 1/d)`
- `MAD = média de |observado − esperado|`

### R9 · Último dígito

- `χ² = Σ (Oᵢ − Eᵢ)² / Eᵢ, com Eᵢ = n / 10`

### R10 · Normal perfeita demais

- `G₁ e G₂ amostrais, como na aba Forma; p do teste de aderência à Normal`

### R11 · Sequência

- `Z = (R − μ_R) / σ_R`
- `ρ₁ = Σ(xₜ − x̄)(xₜ₊₁ − x̄) / Σ(xₜ − x̄)²`
