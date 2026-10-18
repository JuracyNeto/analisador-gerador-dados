# M4.1 — Apêndice de fórmulas — plano de implementação

> **Para o agente:** execute tarefa por tarefa, em TDD. Antes de escrever código, leia `CLAUDE.md`, `docs/padroes-codigo.md`, as specs 11, 13, 14 e 16, `docs/design/telas.md` (tela 8, print 8a) e os contratos em `docs/plans/2026-10-18-m4-visao-geral.md`.

**Objetivo:** o relatório HTML ganha a 9ª seção, "Fórmulas usadas" (item 10 da spec 13): só as fórmulas das seções incluídas, agrupadas (Análise por coluna, Forma e distribuição, Bivariada, Gerador, Detector), sem repetir e com onde cada uma aparece; a tela 8 ganha a caixa "Fórmulas" ("9 de 9").

**Arquitetura:** `Formula` vai para `compartilhado/tipos.py` (D152); domínio `gerador` ganha `formulas.py` (catálogo por método) e `Gerado.formulas`; domínio `relatorio` ganha `apendice.py` (função pura sobre o conteúdo das seções; o `servico.py` está com 428 linhas e só chama o módulo). Frontend: `features/relatorio`.

**Branch:** `feat/relatorio-apendice-formulas` (sai de `develop` depois do merge do M4.0) → PR para `develop`. **Prazo sugerido:** 30/10/2026.

---

## Visão geral das tarefas

| # | Tarefa | Arquivos principais |
|---|---|---|
| 1 | `Formula` no compartilhado | `compartilhado/tipos.py`, `analise/resultados.py`, `analise/formulas.py` |
| 2 | Fórmulas do gerador | `gerador/formulas.py`, `servico.py`, `schemas.py`, `resultados.py` |
| 3 | Seção `formulas` no contrato | `relatorio/conteudo.py`, `router.py` |
| 4 | Montagem do apêndice | `relatorio/apendice.py`, `servico.py` |
| 5 | Template e impressão | `templates/relatorio.html.j2`, `estilos.css` |
| 6 | Tipos do frontend e tela 8 | `schema.d.ts`, `features/relatorio/*` |
| 7 | Documentação | specs 11, 13, 14, `telas.md`, `decisions.md`, `CHANGELOG.md` |
| 8 | Verificação, teste manual, resumo e PR | — |

### Regras
- `Secao` com 9 valores (… `detector`, `formulas`); `SECOES_PADRAO` com as 9. `?secoes=formulas` sozinho → apêndice vazio → a seção não entra (sem erro).
- **Grupos**, na ordem do documento, só das seções incluídas:
  - "Análise por coluna": fórmulas da seção `analises` de cada coluna (chaves fora de `CHAVES_FORMA`), na ordem do catálogo da análise; `onde` = as colunas em que a fórmula aparece, na ordem do relatório ("peso_kg, altura_m"; todas as colunas → "todas as colunas analisadas").
  - "Forma e distribuição": as de `CHAVES_FORMA`, com o mesmo `onde`.
  - "Bivariada": as dos pares do relatório, sem `onde`.
  - "Gerador": `Gerado.formulas` da geração da seção, sem `onde`.
  - "Detector": uma por regra com alerta, `nome` = "R4 · Valores redondos", `texto` = a fórmula dos detalhes, sem LaTeX; regra sem fórmula fica de fora.
- Mesma `chave` não se repete no grupo; grupo vazio sai; sem nenhum grupo, `formulas = None`.
- Com o apêndice, as listas "Fórmulas usadas" das colunas e da Bivariada saem do template (D151). Os dados continuam em `SecaoColuna.formulas` e `SecaoBivariada.formulas` (o apêndice os lê).
- Catálogo do gerador (LaTeX + texto, docstring com a fórmula): `reescala`, `normal`, `kde` (h de Scott, o padrão do `gaussian_kde`), `poisson`, `empirica`, `normal_inteira`, `bernoulli`, `frequencias`, `cholesky`, `ajuste_exato`. Univariado: a fórmula do método + `reescala` quando a spec 11 reescala (Normal, KDE e a discreta em parâmetros). Bivariado: `cholesky` + `ajuste_exato` quando ligado.

---

### Tarefa 1: `Formula` no compartilhado
Mover a dataclass para `compartilhado/tipos.py`; `analise/resultados.py` passa a importá-la de lá (e reexporta para `analise.servico`). Nenhum comportamento muda.

**Testes:** a suíte da análise e do relatório passa sem mudança; `tests/arquitetura` passa (gerador não importa a análise).

**Commit:** `refactor: Formula como value object compartilhado (D152)`

### Tarefa 2: fórmulas do gerador
`gerador/formulas.py`: `FORMULAS` (dict por chave) e `formulas_da_geracao(metodo, reescalado) -> tuple[Formula, ...]`; `Gerado.formulas` no resultado e no schema (`schemas.Formula` da análise reaproveitado, ou um `FormulaGeracao` se o nome conflitar no OpenAPI — conferir).

**Testes (falham):**
- `test_formulas.py`: cada método do `NOMES_METODOS` tem fórmula; Normal com reescala → [`normal`, `reescala`]; Poisson → [`poisson`]; bivariado com ajuste exato → [`cholesky`, `ajuste_exato`], sem → [`cholesky`];
- `test_router.py` do gerador: `formulas` no `POST /gerador/univariado` e no `GET /gerador/{gid}`.

**Commit:** `feat(gerador): fórmulas do método em cada geração`

### Tarefa 3: seção `formulas` no contrato
**Testes (falham)** — `test_router.py` do relatório: `?secoes=formulas` aceito (200); sem `secoes` → título "Fórmulas usadas" presente; `test_servico.py`: `PedidoRelatorio()` usa as 9.

**Commit:** `feat(relatorio): seção formulas no pedido`

### Tarefa 4: montagem do apêndice
`relatorio/apendice.py`: `FormulaApendice`, `GrupoFormulas`, `ApendiceFormulas` (em `conteudo.py`, junto dos outros) e `montar_apendice(...)`; `FormulaTexto` ganha `chave`; `servico.gerar` chama `montar_apendice` só com `formulas` marcada.

**Testes (falham)** — `test_apendice.py` (puro, com conteúdo montado à mão) e `test_servico.py`:
- `pesquisa_saude.txt` com as 9 seções → grupos na ordem; "Média" uma vez, com `onde` de todas as colunas numéricas; "Moda de Czuber" só com as contínuas;
- só `analises` + `formulas` → um grupo; `distribuicoes` + `formulas` → só "Forma e distribuição";
- Gerador com geração Normal (semente 42) → "Distribuição Normal" e "Reescala"; sem `gerado` → sem grupo Gerador;
- Detector em `alturas_plantadas.txt` → uma fórmula por regra com alerta, na ordem dos alertas, sem LaTeX;
- só `leitura` + `formulas` → sem a seção.

**Commit:** `feat(relatorio): apêndice com as fórmulas das seções incluídas`

### Tarefa 5: template e impressão
Seção `section.apendice` numerada (a última), `h3` por grupo, `<dl>` ou lista com nome, `span.formula[data-latex]` (só com LaTeX) com o texto de reserva e o "onde" em `.nota`; listas por coluna e da Bivariada removidas; `@media print`: `break-before: page` no apêndice e `break-inside: avoid` em cada fórmula.

**Testes (falham)** — `test_montagem.py`: apêndice depois do Detector; nenhuma "Fórmulas usadas" dentro das colunas; fórmula do detector sem `data-latex`; textos escapados.

**Commit:** `feat(relatorio): template com o apêndice de fórmulas`

### Tarefa 6: tipos e tela 8
- `exportar_openapi.py` → `gerar:tipos` (`Gerado.formulas`).
- `SECOES_RELATORIO` com `formulas` (rótulo "Fórmulas", a última); "9 de 9" (com geração) e "8 de 9" (sem); fixtures do gerador com `formulas: []`.
- **Testes:** `selecao.test.ts`, `api.test.ts` (`secoes=formulas` na URL), `PaginaRelatorio.test.tsx` (9 caixas).

**Commit:** `feat(relatorio): caixa Fórmulas na tela 8`

### Tarefa 7: documentação
Spec 13 (item 10 implementado no M4.1; parâmetro `secoes` com as 9; listas por seção substituídas pelo apêndice), spec 14 (`secoes`, `Gerado.formulas`), spec 11 (fórmulas por método), `telas.md` (tela 8: nota da implementação do M4), `decisions.md` D151–D152; CHANGELOG › Adicionado: "Relatório com o apêndice de fórmulas: só as das seções incluídas, agrupadas e sem repetir, com as colunas em que cada uma aparece; na tela Relatório, a caixa "Fórmulas"." · Alterado: "As fórmulas saem do fim de cada coluna e da Bivariada e passam para o apêndice."

**Commit:** `docs: apêndice de fórmulas (specs 11, 13 e 14, D151–D152)`

### Tarefa 8: verificação, teste manual e PR
1. Verificação completa; tipos da API sem diferença depois de regenerar.
2. Preview: tela 8 com `pesquisa_saude.txt` e uma geração na sessão — prévia com as 9 seções, KaTeX renderizado (com internet) e texto de reserva no arquivo offline; desmarcar seções e ver os grupos sumirem; imprimir (apêndice na própria página).
3. Resumo ao usuário antes do push; com o ok, push e PR.

## Critérios de pronto do M4.1
- Apêndice com as fórmulas só das seções incluídas, sem repetição, com "onde"; prévia e download iguais.
- Tela 8 com 9 caixas; API do gerador com `formulas`; `servico.py` do relatório abaixo de 450 linhas.
