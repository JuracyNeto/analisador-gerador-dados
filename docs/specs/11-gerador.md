# 11 — Gerador de dados artificiais
Domínio: `app/dominios/gerador/` (`estrategias/` por tipo + `bivariado.py`) · Endpoints: `POST /api/gerador/univariado`, `POST /api/gerador/bivariado`, `POST /api/gerador/{gid}/adotar` · Marco M3

## Univariado
**Entrada:** `{origem: {dataset_id, coluna} | null, tipo (se sem origem), x: int (1..1.000.000), modo: "preservar"|"parametros", media?, desvio?, p? (binária), seed?, limitar_faixa: bool}`

| Tipo | Modo preservar | Modo parâmetros |
|---|---|---|
| Contínua | Se aderir à Normal (p ≥ 0,05) → Normal(x̄, s); senão **KDE** (`scipy.stats.gaussian_kde.resample`). Depois **reescala**: zᵢ = (gᵢ − ḡ)/s_g → gᵢ' = x̄ + s·zᵢ (média e DP exatos). Arredonda nas casas decimais do original. `limitar_faixa` → recorta em [mín, máx] observados | Normal(média, desvio) + reescala exata; arredonda em 2 casas (ou do original) |
| Discreta | Se \|x̄ − s²\| / x̄ < 0,2 → **Poisson**(x̄); senão **empírica** (sorteio com as frequências relativas) | Normal(média, desvio) arredondada para inteiro, limitada a ≥ 0 se o original não tinha negativos |
| Binária | **Bernoulli**(p̂) com os mesmos rótulos | Bernoulli(p informado) |
| Nominal/Ordinal | Sorteio com as frequências relativas observadas | — (só preservar) |

**Saída:** `{gerado_id, amostra (primeiras 50), comparacao[{estatistica, original, gerado, diferenca_pct}], metodo, explicacao, figuras{sobreposicao}}`.
Estatísticas comparadas: n, média, mediana, DP, mín, máx, assimetria, curtose (ou frequências relativas para qualitativas).
`explicacao` em linguagem simples: "Usamos uma distribuição Normal com média 34,2 e desvio 5,1, ajustada para bater exatamente essas medidas, e arredondamos com 1 casa decimal como no original."

## Bivariado
**Entrada:** `{origem: {dataset_id, x, y} | null, n, media_x, media_y, desvio_x, desvio_y, rho (−1..1), ajuste_exato: bool, seed?}`. Com origem, os parâmetros são copiados do par (podem ser editados).

**Método (Cholesky):**
1. Z₁, Z₂ ~ Normal(0, 1) independentes
2. Se `ajuste_exato`: centrar e ortonormalizar (Z₁, Z₂) (Gram-Schmidt) para que corr amostral = 0 e DP = 1 exatos
3. **X = μx + σx · Z₁**
4. **Y = μy + σy · (ρ·Z₁ + √(1 − ρ²) · Z₂)**

Matriz de covariância alvo Σ = [[σx², ρσxσy], [ρσxσy, σy²]] = L·Lᵀ (L = Cholesky). Com ajuste exato, r amostral = ρ exatamente; sem ajuste, r ≈ ρ (variação amostral).

**Saída:** `{gerado_id, amostra, comparacao (médias, DPs, r alvo × obtido), figuras{dispersao}, explicacao}`.

## Adotar
`POST /api/gerador/{gid}/adotar {modo: "novo"|"anexar", dataset_id?}` → "novo" cria dataset; "anexar" concatena linhas ao dataset existente (colunas de mesmo nome) — usado na demonstração do detector.

## Testes
Média/DP gerados dentro de 1% (reescala → exatos); bivariado com ajuste exato: |r − ρ| < 1e-9; sem ajuste, n = 10.000: |r − ρ| < 0,03; mesma seed → mesmo resultado.
