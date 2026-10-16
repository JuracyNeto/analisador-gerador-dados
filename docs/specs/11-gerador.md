# 11 — Gerador de dados artificiais
Domínio: `app/dominios/gerador/` (`estrategias/` por tipo + `bivariado.py`) · Endpoints: `POST /api/gerador/univariado`, `POST /api/gerador/bivariado`, `GET /api/gerador/{gid}`, `GET /api/gerador/{gid}/csv`, `POST /api/gerador/{gid}/adotar` · Marco M3

## Univariado
**Entrada:** `{origem: {dataset_id, coluna} | null, tipo (sem origem: continua | discreta | binaria), x: int (1..1.000.000), modo: "preservar"|"parametros", media?, desvio? (> 0), p? (binária, 0..1), rotulos? ([fracasso, sucesso] da binária sem origem; padrão ["0", "1"]), semente? (0..2³²−1), limitar_faixa: bool}`. Sem origem, só `parametros`. Sem semente, o servidor sorteia uma e a devolve (D109).

| Tipo | Modo preservar | Modo parâmetros |
|---|---|---|
| Contínua | Se aderir à Normal (p ≥ 0,05) → Normal(x̄, s); senão **KDE** (`scipy.stats.gaussian_kde.resample`). Depois **reescala**: zᵢ = (gᵢ − ḡ)/s_g → gᵢ' = x̄ + s·zᵢ (média e DP exatos). Arredonda nas casas decimais do original (maior nº de casas, até 6). `limitar_faixa` → valores fora de [mín, máx] são sorteados de novo e a reescala é refeita, até 20 rodadas; o que sobrar é recortado (D112) | Normal(média, desvio) + reescala exata; arredonda em 2 casas (ou nas do original, com origem) |
| Discreta | Se x̄ > 0 e \|x̄ − s²\| / x̄ < 0,2 → **Poisson**(x̄); senão **empírica** (sorteio com as frequências relativas). `limitar_faixa` na Poisson: resorteio sem reescala | Normal(média, desvio) + reescala, arredondada para inteiro, limitada a ≥ 0 se o original não tinha negativos |
| Binária | **Bernoulli**(p̂) com os mesmos rótulos; sucesso = o mesmo da análise (spec 05) | Bernoulli(p informado) |
| Nominal/Ordinal | Sorteio com as frequências relativas observadas | — (só preservar; `MODO_NAO_APLICAVEL`) |

**Saída (`Gerado`):** `{gerado_id, tipo: "univariado", colunas, n, semente, origem {dataset_id, nome_arquivo, colunas} | null, metodo, explicacao, parametros [{nome, valor}], amostra (primeiras 50 linhas), comparacao [{estatistica, original, gerado, diferenca}], figuras [sobreposicao]}`.
Estatísticas comparadas: n, média, mediana, DP, mín, máx, assimetria, curtose (qualitativas: n e "fr% · {categoria}"). `diferenca = gerado − original` (absoluta, como no print 6a; qualitativas em pontos percentuais; D110). Sem origem, `original` e `diferenca` são nulos.
`explicacao` em linguagem simples: "Sorteamos 500 valores de uma curva Normal com a mesma média (70,3) e desvio (11,2) de peso_kg, usando a semente 42, e ajustamos para bater exatamente essas medidas. Arredondamos com 1 casa decimal, como no original."
Figura `sobreposicao`: histogramas de frequência relativa nas mesmas classes (faixa da união, k de Sturges da menor série), barras sobrepostas com opacidade 0,55; qualitativas em barras agrupadas (D113). Só as alturas das barras vão para o JSON.

## Bivariado
**Entrada:** `{origem: {dataset_id, x, y} | null, n (3..1.000.000), media_x, media_y, desvio_x, desvio_y, rho (−1..1), nome_x?, nome_y?, ajuste_exato: bool (padrão true), semente?}`. Com origem, o que for omitido é copiado do par (médias e DPs amostrais, r de Pearson); sem origem, os cinco parâmetros são obrigatórios e os nomes padrão são "x" e "y".

**Método (Cholesky):**
1. Z₁, Z₂ ~ Normal(0, 1) independentes
2. Se `ajuste_exato`: centrar e ortonormalizar (Z₁, Z₂) (Gram-Schmidt) para que corr amostral = 0 e DP = 1 exatos
3. **X = μx + σx · Z₁**
4. **Y = μy + σy · (ρ·Z₁ + √(1 − ρ²) · Z₂)**

Matriz de covariância alvo Σ = [[σx², ρσxσy], [ρσxσy, σy²]] = L·Lᵀ (L = Cholesky). Com ajuste exato, r amostral = ρ exatamente e os valores **não são arredondados** (arredondar desfaria a exatidão); sem ajuste, r ≈ ρ (variação amostral) e os valores seguem as casas das colunas de origem (2 sem origem) (D114).

**Saída (`Gerado`, `tipo: "bivariado"`):** `comparacao` com n, médias, desvios e "Correlação (r)" (com origem, `original` = o par; sem origem, `original` = o alvo pedido), `figuras [dispersao]` (pares gerados e, com origem, os originais; até 5.000 pontos por série, D101) e `explicacao`.

## Medidas da origem (tela 6)
- `GET /api/gerador/origem?dataset_id=&coluna=` → `{coluna, tipo, n, media, desvio, minimo, maximo, sucesso, fracasso, chance, so_preservar}`: numéricas trazem média, desvio, mín e máx ("Mesma média (70,3) e desvio (11,2) da coluna.", "Nenhum valor abaixo de 43,8 ou acima de 92,9."); binária, o sucesso e a chance; nominal e ordinal, `so_preservar` (D116).
- `GET /api/gerador/origem-par?dataset_id=&x=&y=` → `{x, y, n, media_x, media_y, desvio_x, desvio_y, r}` para preencher o formulário bivariado.
- Campo que o usuário não editou não vai no pedido (bivariado) ou vai com o valor exato da origem (univariado), nunca com o texto arredondado da tela.

## CSV e adotar
- `GET /api/gerador/{gid}/csv`: `;` como separador e vírgula decimal (como o app lê), nome `gerado-{colunas}.csv`.
- `POST /api/gerador/{gid}/adotar {modo: "novo"|"anexar", dataset_id?}` → `{dataset_id, nome_arquivo, n_linhas, modo}`. "novo" importa o CSV da geração como um dataset novo; "anexar" põe as linhas no fim da versão atual do dataset (colunas de mesmo nome; as demais ficam faltantes), registra "Anexamos 500 linhas geradas em peso_kg." no log da limpeza e sai com "Desfazer limpeza" (D111) — usado na demonstração do detector. Coluna que não existe no dataset → 400 `COLUNAS_INCOMPATIVEIS`.
- Gerações ficam em memória (até `max_gerados = 20`; a mais antiga sai); sumiu → 404 `GERADO_NAO_ENCONTRADO`; na tela 6, o aviso traz "Gerar de novo", que refaz o pedido com a mesma semente (D149). "Usar como novo dataset" devolve as linhas do dataset criado; o CSV univariado (uma coluna, vírgula decimal) é lido com uma coluna só (D147).

## Testes
Média/DP gerados dentro de 1% (reescala → exatos; sem `limitar_faixa`); bivariado com ajuste exato: |r − ρ| < 1e-9; sem ajuste, n = 10.000: |r − ρ| < 0,03; mesma seed → mesmo resultado; figura de sobreposição leve com 1.000.000 de valores.
