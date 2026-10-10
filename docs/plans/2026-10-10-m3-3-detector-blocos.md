# M3.3 — Detector: regras de bloco e ordem + demonstração — plano de implementação

> **Para o agente:** execute tarefa por tarefa, em TDD. Antes de escrever código, leia `CLAUDE.md`, `docs/padroes-codigo.md`, as specs 08, 12, 16 e 17, o plano do M3.2 e os contratos em `docs/plans/2026-10-10-m3-visao-geral.md`.

**Objetivo:** completar as 11 regras com R1 (bloco alinhado), R2 (correlação por blocos), R6 (temporal), R10 (Normal perfeita demais) e R11 (sequência/variância); dar figuras às regras R1, R8 e R9 (spec 08); criar os datasets de demonstração com dados plantados e deixá-los escolhíveis; provar o controle de falsos positivos.

**Arquitetura:** novas regras em `detector/regras/` sobre a base do M3.2; `detector/blocos.py` (janelas e simulação vetorizada com somas acumuladas, D119); figuras no domínio `graficos` (`figuras_detector.py`), pedidas pelo `ServicoDetector` (o domínio do detector devolve só os dados da figura, como a análise faz). Script `backend/scripts/gerar_exemplos_detector.py` (usa o `ServicoGerador` para o bloco com ajuste exato). Exemplos escolhíveis no domínio `datasets`.

**Branch:** `feat/detector-blocos` (sai de `develop` depois do merge do M3.2) → PR para `develop`. **Prazo sugerido:** 06/11/2026.

---

## Visão geral das tarefas

| # | Tarefa | Arquivos principais |
|---|---|---|
| 1 | Blocos e simulação | `detector/blocos.py` |
| 2 | R1 Bloco alinhado | `regras/r01_bloco_alinhado.py` |
| 3 | R2 Correlação por blocos | `regras/r02_correlacao_blocos.py` |
| 4 | R6 Temporal | `regras/r06_temporal.py` |
| 5 | R10 Normal perfeita demais | `regras/r10_normal_perfeita.py` |
| 6 | R11 Sequência / variância | `regras/r11_sequencia.py` |
| 7 | Figuras do detector | `graficos/figuras_detector.py`, `entradas.py`, `fabrica.py`, `servico.py`, `detector/servico.py` |
| 8 | Datasets plantados | `backend/scripts/gerar_exemplos_detector.py`, `dados-exemplo/*.txt` |
| 9 | Exemplos escolhíveis | `datasets/servico.py`, `router.py`, `schemas.py`, `config.py` |
| 10 | Falsos positivos e datasets plantados nos testes | `tests/dominios/detector/test_falsos_positivos.py`, `test_exemplos_plantados.py` |
| 11 | Tipos do frontend, specs, decisões e CHANGELOG | `schema.d.ts`, `docs/**` |
| 12 | Verificação, Swagger, resumo e PR | — |

### Regras que o código implementa (spec 12)
- **R1** (numéricas, n ≥ 60, alta): k = max(10, ⌊n/20⌋); para cada janela de k linhas consecutivas (valores válidos na ordem), dᵤ = |x̄_bloco − x̄|/s e dₛ = |s_bloco − s|/s; candidata = menor max(dᵤ, dₛ); referência: 1.000 blocos aleatórios de tamanho k (`default_rng(SEMENTE_R1)`), proporção com max(dᵤ, dₛ) ≤ o da candidata. Dispara com dᵤ e dₛ < 0,01 **e** proporção < 1%. Resumo: "Um bloco de 20 linhas (181–200) tem média e desvio quase idênticos ao conjunto todo (diferença de 0,3%)."; exemplo "Linhas 181-200: média 1,702 (geral 1,701) · DP 0,0881 (geral 0,0884)".
- **R2** (pares numéricos, n ≥ 60, alta): 5 blocos consecutivos (linhas com X e Y válidos); r geral, média dos rᵦ e r sem cada bloco. Dispara com r − média(rᵦ) > 0,3 **ou** |r| − |r sem bloco| > 0,3 (em módulo, para qualquer bloco). Colunas = [x, y]; resumo da spec 16 ("A correlação geral entre altura_m e peso_kg é 0,78, mas a média dos blocos é só 0,41."); exemplo com as linhas do bloco que mais muda r.
- **R6** (precisa de coluna `data`, n ≥ 40, alta): ordena pela 1ª coluna `data`; divide na data mediana; para cada numérica: DP depois < 0,5 × DP antes; para a linha inteira (sem a data): ≥ 10% das linhas novas idênticas a alguma antiga. Sem coluna `data` → não aplicada sem coluna ("Comparação temporal não verificada: o arquivo não tem uma coluna de data.").
- **R10** (contínuas, n ≥ 200, info): |G₁| < 0,05 **e** |G₂| < 0,1 **e** Shapiro p > 0,9 (n ≤ 5.000; acima, D'Agostino) — G₁/G₂ via `ServicoAnalise.resumo_numerico` (D108), passado pelo serviço na `TabelaDetector` para manter a regra pura.
- **R11** (numéricas, n ≥ 30, atenção): runs acima/abaixo da mediana (valores iguais à mediana saem) com p < 0,01, **ou** progressão aritmética (≥ 5 diferenças iguais seguidas, diferença ≠ 0), **ou** |ρ₁| > 0,8. O resumo cita o padrão: "valores alternam acima e abaixo do meio com regularidade" · "progressão aritmética nas linhas 50–56" · "cada valor é muito parecido com o anterior".
- **Figuras** (D120; `meta` com papéis do tema): R1 linha da média por bloco (pontos `principal`) com a faixa x̄ ± s tracejada (`referencia`) e o bloco destacado; R8 barras observado × esperado (Benford) por 1º dígito; R9 barras de frequência do último dígito com a linha de 10%.
- **Datasets plantados** (D121, semente fixa, LF, UTF-8, `;` e vírgula decimal):
  - `alturas_reais.txt` — `id;altura_m;peso_kg`, 300 linhas, alturas Normal(1,70; 0,09) com 2 casas e pesos ligados à altura com ruído (sem manipulação);
  - `alturas_plantadas.txt` — o mesmo + bloco de 20 linhas gerado com ajuste exato (R1, R10), 10 inteiros seguidos em `peso_kg` (R3), trecho com pesos redondos (R4) e 3 linhas duplicadas em sequência (R5);
  - `vendas_correlacao_puxada.txt` — `data;anuncios;vendas`, 120 semanas: os primeiros 96 com r ≈ 0,3 e os 24 últimos com r ≈ 0,95 (R2), e ~15% dessas últimas copiando semanas antigas (R6).
- **Falsos positivos** (spec 12, teste obrigatório): 100 amostras Normal(50, 10) e 100 Exponenciais(média 10), n = 500, arredondadas a 2 casas, sementes fixas; para cada regra exceto R7, disparos < 5% em cada família. O teste roda no CI (alvo: < 60 s; R1 vetorizada).

---

### Tarefa 1: `blocos.py`
`janelas(valores, k) -> tuple[np.ndarray medias, np.ndarray desvios]` (somas acumuladas de x e x², O(n)); `blocos_aleatorios(valores, k, quantidade, rng)`; `dividir_em_blocos(n, partes=5) -> list[slice]`.

**Testes (falham):** médias/desvios das janelas iguais aos de um laço simples; 1.000 blocos com n = 10.000 em < 0,2 s.

**Commit:** `feat(detector): janelas e blocos aleatórios vetorizados`

### Tarefas 2 a 6: uma regra por tarefa
Para cada regra: dispara / não dispara / não aplicável (com motivo), conferindo severidade, colunas, exemplo e detalhes.
- **R1:** Normal(70, 10), n = 400, com as linhas 181–200 substituídas por um bloco reescalado para a média e o DP do conjunto → alta; Normal pura → nada; n = 50 → não se aplica.
- **R2:** 100 pares com r ≈ 0,3 + 25 pares finais muito alinhados → alta; pares com r ≈ 0,7 homogêneo → nada.
- **R6:** 100 linhas com datas crescentes, segunda metade com DP 0,3× → alta; com 12% de linhas novas copiando antigas → alta; sem coluna `data` → não aplicada.
- **R10:** 1.000 valores com quantis exatos da Normal (`stats.norm.ppf`) → info; Normal aleatória (semente 3) → nada; n = 150 → não se aplica.
- **R11:** sequência 1, 2, 3, … → atenção (PA); alternância alta/baixa → atenção (runs); Normal aleatória → nada.

**Commits:** `feat(detector): R1 bloco alinhado` · `feat(detector): R2 correlação por blocos` · `feat(detector): R6 comparação temporal` · `feat(detector): R10 Normal perfeita demais` · `feat(detector): R11 sequência e variância`

### Tarefa 7: figuras
`graficos/entradas.py`: `DadosBlocos`, `DadosBenford`, `DadosUltimoDigito`; `figuras_detector.py` + funções na fábrica/fachada. As regras R1, R8 e R9 devolvem os dados da figura em `Medicao`; o `ServicoDetector` pede a figura ao `graficos` e coloca em `Aviso.figura`.

**Testes (falham):** papéis e títulos ("Média por bloco de 20 linhas", "1º dígito: observado × Benford", "Último dígito de idade"); payload pequeno.

**Commit:** `feat(graficos): figuras do detector (blocos, Benford, último dígito)`

### Tarefa 8: datasets plantados
Script com `argparse` (`--pasta`, padrão `dados-exemplo/`), semente fixa e funções pequenas por "plantio"; README curto no topo do script com o que cada arquivo dispara.

**Testes (falham):** rodar o script numa pasta temporária gera arquivos idênticos aos versionados (reprodutível).

**Commit:** `feat(dados): datasets de demonstração do detector (script com semente)`

### Tarefa 9: exemplos escolhíveis
`config.py`: `exemplos: tuple[Exemplo, ...]` (arquivo + descrição: "Pesquisa de saúde (valores fora de faixa e duplicados)", "Alturas reais (sem manipulação)", "Alturas com dados plantados", "Vendas com correlação puxada"); `GET /datasets/exemplos`; `POST /datasets/exemplo?arquivo=` (padrão `pesquisa_saude.txt`; fora da lista → 404 `EXEMPLO_NAO_ENCONTRADO`). `importar_exemplo` continua funcionando sem parâmetro (D52).

**Testes (falham):** lista com 4 exemplos; importar cada um; arquivo inexistente → 404.

**Commit:** `feat(datasets): exemplos escolhíveis`

### Tarefa 10: falsos positivos e datasets plantados nos testes
- `test_falsos_positivos.py`: as 200 amostras (gerador `default_rng(1000 + i)`), taxa por regra e família < 5% (mensagem do assert com a taxa).
- `test_exemplos_plantados.py`: `alturas_plantadas.txt` dispara R1, R3, R4, R5 e R10; `vendas_correlacao_puxada.txt` dispara R2 e R6; `alturas_reais.txt` sem alertas de atenção ou alta (R7 informativo permitido).

**Commit:** `test(detector): falsos positivos e datasets plantados (spec 12, spec 17)`

### Tarefa 11: tipos e documentação
- `exportar_openapi.py` → `gerar:tipos`.
- Spec 12 (detalhes de R1/R2/R6/R11, figuras, datasets plantados e coluna `data` em vendas), spec 08 (figuras do detector), spec 14 (exemplos), spec 17 (tempo do teste); `decisions.md` D119–D121; CHANGELOG › Adicionado: "Detector completo com as 11 regras (bloco alinhado, correlação por blocos, comparação temporal, Normal perfeita demais e sequência), gráficos nos detalhes técnicos e três arquivos de demonstração com dados plantados, escolhíveis entre os exemplos."

**Commit:** `docs: detector — regras de bloco e ordem, demonstração (spec 12, decisões)`

### Tarefa 12: verificação e PR
1. Verificação completa (o pytest inteiro deve continuar em poucos minutos; medir e citar o tempo no PR).
2. Swagger: detector dos três arquivos novos; conferir resumo e textos.
3. Resumo ao usuário antes do push; com o ok, push e PR.

## Critérios de pronto do M3.3
- 11 regras no registro; falsos positivos < 5% (exceto R7); cada dataset plantado dispara o esperado.
- Datasets reproduzíveis pelo script; exemplos escolhíveis pela API.
