# M3.2 — Detector: base e regras de uma coluna — plano de implementação

> **Para o agente:** execute tarefa por tarefa, em TDD. Antes de escrever código, leia `CLAUDE.md`, `docs/padroes-codigo.md`, as specs 12, 14 e 16, a ADR 0005, `docs/design/componentes.md` (CartaoAlerta) e os contratos em `docs/plans/2026-10-10-m3-visao-geral.md`.

**Objetivo:** montar o esqueleto completo do detector (contrato `Aviso`, Template Method, registro, textos, resumo, endpoint e linhas para o drawer) e entregar as seis regras que olham uma coluna de cada vez: R3 (formato numérico), R4 (valores redondos), R5 (duplicatas), R7 (outliers), R8 (Benford) e R9 (último dígito).

**Arquitetura:** domínio `detector` (spec 12, ADR 0005, D116):
```
detector/
├── tabela.py          TabelaDetector, ColunaDetector (entrada pura das regras)
├── resultados.py      Aviso, ExemploAviso, DetalhesAviso, RegraNaoAplicada, ResumoDetector, ResultadoDetector
├── regras/
│   ├── base.py        RegraBase (Template Method) + Alvo (coluna ou par) + Medicao
│   ├── r03_formato.py · r04_redondos.py · r05_duplicatas.py · r07_outliers.py · r08_benford.py · r09_ultimo_digito.py
├── registro.py        REGRAS em ordem (R1…R11; o M3.3 completa) e busca por código
├── digitos.py         resolução da coluna, dígito final, 1º dígito (R4, R8, R9)
├── resumo.py          contagens, frases do resumo, ordenação
├── textos.py          títulos, resumos, "por que", "pode ser normal", "o que fazer", detalhes (spec 16)
├── erros.py · servico.py · schemas.py · router.py
```
`ServicoDetector(datasets, analise)` (a análise só é usada a partir do M3.3, na R10) monta a `TabelaDetector` com `ServicoDatasets.colunas` e `coluna_para_analise` (+ `reconhecer_datas` nas colunas `data`) e roda as regras pedidas. Testes estatísticos em `compartilhado/estatistica.py`.

**Branch:** `feat/detector-base` (sai de `develop`) → PR para `develop`. **Prazo sugerido:** 30/10/2026.

---

## Visão geral das tarefas

| # | Tarefa | Arquivos principais |
|---|---|---|
| 1 | Testes estatísticos compartilhados e `Severidade` | `compartilhado/estatistica.py`, `compartilhado/tipos.py` |
| 2 | Entrada e resultados | `detector/tabela.py`, `resultados.py` |
| 3 | Template Method, registro e textos base | `regras/base.py`, `registro.py`, `textos.py` |
| 4 | Dígitos | `detector/digitos.py` |
| 5 | R7 Outliers | `regras/r07_outliers.py` |
| 6 | R4 Valores redondos e R9 Último dígito | `regras/r04_redondos.py`, `r09_ultimo_digito.py` |
| 7 | R8 Benford | `regras/r08_benford.py` |
| 8 | R3 Formato numérico | `regras/r03_formato.py` |
| 9 | R5 Duplicatas | `regras/r05_duplicatas.py` |
| 10 | Resumo, fachada, schemas, router e `GET /linhas` | `resumo.py`, `servico.py`, `schemas.py`, `router.py`, `datasets/router.py` |
| 11 | Tipos do frontend, specs, decisões e CHANGELOG | `schema.d.ts`, `docs/**` |
| 12 | Verificação, Swagger, resumo e PR | — |

### Regras que o código implementa
- **Template Method** (`RegraBase.executar(tabela) -> ResultadoRegra`): para cada alvo de `alvos(tabela)` (colunas do tipo certo, ou pares no M3.3) → `motivo_nao_aplicavel(alvo)` → `medir(alvo)` → `dispara(medicao)` → `montar_aviso(alvo, medicao)`. As subclasses implementam só os passos; nenhuma monta texto fora de `textos.py`. Cada regra tem `codigo`, `nome` e constantes nomeadas para os limiares (sem números mágicos).
- **Severidades e limiares** (spec 12): R3 atenção (≥ 80% com decimais e inteiros agrupados — run de ≥ 5 inteiros seguidos — ou em posições regulares — passo constante entre os inteiros, ≥ 4 vezes); R4 atenção (n ≥ 50, binomial unilateral p < 0,01 e razão ≥ 1,5, para múltiplos de 5 — p₀ 0,2 — e de 10 — p₀ 0,1; avisa o mais forte); R5 atenção, **alta** com ≥ 3 cópias em linhas consecutivas; R7 info (moderado: fora de Q1 − 1,5·IQR / Q3 + 1,5·IQR) / atenção (extremo: fora de 3·IQR, ou |z| > 3); R8 atenção (positivas, n ≥ 100, máx/mín ≥ 100; χ² gl 8 com p < 0,01 **e** MAD > 0,015); R9 atenção (n ≥ 50, dígito final variável; χ² gl 9, p < 0,01).
- **Dígito final** (D117): resolução da coluna = maior nº de casas observado (até 6); dígito = `round(|x| · 10^casas) mod 10`; constante (ex.: todos inteiros terminados em 0) → R4/R9 não se aplicam ("o último dígito é sempre o mesmo").
- **R5** (D118): exatas em todas as colunas (linhas idênticas); quase idênticas só até 5.000 linhas: numéricas padronizadas, distância euclidiana < 0,01·√p e qualitativas iguais. Exemplo = o maior grupo de cópias.
- **Textos** (spec 16, tom neutro): título ≤ 8 palavras ("Muitos valores redondos em peso_kg"); resumo com o número e o esperado ("46% dos valores terminam em 0 ou 5; em medições reais o esperado seria cerca de 20% (2,3× mais)."); `por_que`, `pode_ser_normal` (começa com "…"), `o_que_fazer`; p-valor traduzido com `p_valor_em_palavras`; exemplo "Linhas 120 a 138: 70, 75, 80, 75, 70…" (até 8 valores, com "…"); não aplicada: "{nome} não verificada em {col}: {motivo}." (ex.: "precisa de 100 valores ou mais; a coluna tem 48.").
- **Resumo:** "Encontramos {n} alerta(s) em {k} coluna(s)" · detalhe "altura_m, peso_kg e idade · {v} regras verificadas, {k} não se aplicam a este arquivo" · vazio: "Nenhuma das 11 regras encontrou suspeitas. Isso não garante que os dados sejam reais, mas não vimos sinais comuns de dados artificiais." (no M3.2 o número vem de `len(registro)`, que chega a 11 no M3.3).

---

### Tarefa 1: estatística compartilhada e `Severidade`
`teste_binomial_unilateral(k, n, p0) -> float` (`stats.binom.sf(k − 1, n, p0)`), `teste_qui_quadrado(observados, esperados) -> ResultadoQuiQuadrado {estatistica, gl, p_valor}`, `teste_runs(acima: np.ndarray) -> ResultadoRuns {runs, z, p_valor}` (fórmulas da spec 12), `autocorrelacao_lag1(valores) -> float`; `Severidade` e `ORDEM_SEVERIDADE` em `compartilhado/tipos.py`.

**Testes (falham)** — importe o módulo (`estatistica.teste_binomial_unilateral`): binomial (k = 46, n = 100, p₀ = 0,2) < 1e-8; qui-quadrado igual a `stats.chisquare`; runs de uma sequência alternada → p pequeno; lag-1 de uma rampa ≈ 1.

**Commit:** `feat(compartilhado): testes binomial, qui-quadrado, runs e autocorrelação`

### Tarefa 2: entrada e resultados
`TabelaDetector`, `ColunaDetector` (ver visão geral), com `numericas()`, `valores_validos(col) -> tuple[np.ndarray linhas, np.ndarray valores]`; value objects de `resultados.py` (`frozen=True, slots=True`).

**Testes (falham):** montar a tabela a partir de um DataFrame pequeno pelos helpers de teste (`tests/dominios/detector/conftest.py`: `tabela_de(df, tipos)`), linhas e faltantes preservados.

**Commit:** `feat(detector): entrada das regras e contrato do aviso (spec 12)`

### Tarefa 3: Template Method, registro e textos base
`RegraBase` (classe abstrata de 1 nível), `Alvo`, `ResultadoRegra {avisos, nao_aplicadas}`; `registro.py` (`REGRAS: tuple[RegraBase, ...]`, `regras_pedidas(codigos)`); `textos.py` com as funções comuns (`frase_nao_aplicada`, `texto_exemplo(linhas, valores)`, `faixa_de_linhas`, `p_em_palavras`).

**Testes (falham):** uma regra falsa de teste mostra a ordem dos passos (não aplicável → sem medir; não dispara → sem aviso); `texto_exemplo([120, 121, …, 138], [...])` = "Linhas 120 a 138: 70, 75, 80, 75, 70, 75, 80, 70…"; linhas não seguidas → "Linhas 3, 9 e 14: …".

**Commit:** `feat(detector): regra base (Template Method), registro e textos comuns`

### Tarefa 4: `digitos.py`
`resolucao(valores) -> int`, `digitos_finais(valores, casas) -> np.ndarray`, `primeiros_digitos(valores) -> np.ndarray` (positivos; ignora zeros).

**Testes (falham):** `[1.25, 3.5, 7]` → resolução 2, dígitos finais `[5, 0, 0]`; primeiro dígito de `[0.0123, 456, 7.8]` = `[1, 4, 7]`.

**Commit:** `feat(detector): dígitos final e inicial`

### Tarefas 5 a 9: uma regra por tarefa
Para cada regra: testes com dados construídos que **disparam** (e conferem severidade, colunas, exemplo e detalhes) e que **não disparam**, mais os casos de não aplicável com o motivo. Exemplos mínimos:
- **R7:** Normal(70, 10), n = 200 + valores 150 e 155 → atenção (extremos), exemplo com os dois; só moderados → info; coluna constante → não se aplica ("todos os valores são iguais").
- **R4:** 100 valores com 46 múltiplos de 5 → atenção, resumo com 46% e 2,3×; uniforme → nada; n = 30 → "precisa de 50 valores ou mais; a coluna tem 30.".
- **R9:** 200 inteiros com 24% terminando em 0 → atenção ("o 0 aparece 24% das vezes (esperado 10%)"); uniformes → nada.
- **R8:** valores log-uniformes (segue Benford) → nada; uniformes entre 100 e 999 com máx/mín ≥ 100 forçado → atenção; idades (máx/mín < 100) → não se aplica ("precisa de valores que variem em várias ordens de grandeza").
- **R3:** 100 decimais com 10 inteiros seguidos nas linhas 40–49 → atenção ("… mas 10 inteiros aparecem juntos (linhas 40–49)"); inteiros espalhados ao acaso → nada; discreta → não se aplica.
- **R5:** 3 linhas iguais seguidas → alta; 2 iguais distantes → atenção; quase iguais (diferença 0,001 numa numérica) → atenção; 6.000 linhas → quase duplicatas não verificadas (motivo), exatas sim.

**Commits:** `feat(detector): R7 outliers` · `feat(detector): R4 valores redondos e R9 último dígito` · `feat(detector): R8 Lei de Benford` · `feat(detector): R3 formato numérico` · `feat(detector): R5 duplicatas`

### Tarefa 10: resumo, fachada, schemas, router e linhas
- `resumo.py`: ordenação (severidade → regra → coluna), contagens, frases.
- `ServicoDetector.analisar(dataset_id, regras: tuple[str, ...] | None) -> ResultadoDetector`.
- `schemas.py` (`CodigoRegra = Literal["R1", …, "R11"]`), `router.py` (`GET /datasets/{dataset_id}/detector`, `tags=["detector"]`).
- `GET /datasets/{id}/linhas?de=&ate=` no domínio `datasets` (`ServicoDatasets.linhas(dataset_id, de, ate)`, reusa `linhas_dados`; > 200 linhas ou `de > ate` → 400 `INTERVALO_INVALIDO`).

**Testes (falham):** API com o exemplo `pesquisa_saude.txt` sem limpeza: R5 (3 duplicados) e R7 (altura 17,2 m) aparecem; `?regras=R4` só roda a R4; `?regras=R99` → 422; resumo com as contagens; `/linhas?de=10&ate=15` devolve 6 linhas; `de=0&ate=500` → 400.

**Commit:** `feat(detector): resumo e API do detector; linhas por intervalo`

### Tarefa 11: tipos e documentação
- `exportar_openapi.py` → `gerar:tipos`.
- Spec 12 (dígito final, quase duplicatas até 5.000, contagens do resumo), spec 14 (rotas e erro), `decisions.md` D116–D118 (próximos números livres), CHANGELOG › Adicionado: "API do detector com resumo e as regras de formato numérico, valores redondos, duplicatas, outliers, Lei de Benford e último dígito, cada alerta com explicação em linguagem simples."

**Commit:** `docs: detector — base e regras de uma coluna (spec 12, API, decisões)`

### Tarefa 12: verificação e PR
1. Verificação completa.
2. Swagger: detector do exemplo sem limpeza e limpo (o R5 some depois de remover duplicados); textos conferidos com a spec 16.
3. Resumo ao usuário antes do push; com o ok, push e PR.

## Critérios de pronto do M3.2
- Seis regras com testes de disparo, não disparo e não aplicável; textos todos em `textos.py`.
- Endpoint, resumo e linhas prontos para a tela 7.
