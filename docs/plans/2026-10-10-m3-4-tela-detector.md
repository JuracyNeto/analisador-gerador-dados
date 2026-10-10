# M3.4 — Tela Detector — plano de implementação

> **Para o agente:** execute tarefa por tarefa, em TDD. Antes de escrever código, leia `CLAUDE.md`, `docs/padroes-codigo.md`, as specs 12, 15 e 16, a ADR 0005, `docs/design/telas.md` (tela 7), `docs/design/componentes.md` (BadgeSeveridade, Drawer, Accordion, CartaoAlerta), os prints `7a`–`7d` e os contratos em `docs/plans/2026-10-10-m3-visao-geral.md`.

**Objetivo:** liberar a etapa 7: resumo com contadores por severidade, filtros, agrupamento por coluna ou regra, lista de alertas no formato de 8 partes (spec 16), detalhes técnicos com a figura, "Ver na tabela" com as linhas destacadas num drawer, "Regras não verificadas" e o estado vazio. A tela Importar passa a oferecer os exemplos de demonstração.

**Arquitetura:** `features/detector` (`api.ts`, `hooks/`, `components/`, `agrupamento.ts`, `filtros.ts`, `textos.ts`). Componentes de design system novos em `shared/ui`: `BadgeSeveridade`, `ChipFiltro` (`role="checkbox"`), `Accordion` e `Drawer` (foco preso, Esc fecha, devolve o foco). `features/importar` ganha a lista de exemplos (`GET /datasets/exemplos`).

**Branch:** `feat/frontend-detector` (sai de `develop` depois do merge do M3.3) → PR para `develop`. **Prazo sugerido:** 13/11/2026.

---

## Visão geral das tarefas

| # | Tarefa | Arquivos principais |
|---|---|---|
| 1 | Etapa 7 liberada e navegação | `app/etapas.ts`, `rotas.ts`, `caminhos.ts`, Gerador e Relatório |
| 2 | `BadgeSeveridade` e `ChipFiltro` | `shared/ui/*` (+ tokens `--sev-*` já existentes) |
| 3 | `Accordion` e `Drawer` | `shared/ui/Accordion.tsx`, `Drawer.tsx` |
| 4 | API, filtros e agrupamento | `features/detector/api.ts`, `filtros.ts`, `agrupamento.ts`, `parametros.ts` |
| 5 | Resumo e barra de filtros | `components/ResumoDetector.tsx`, `BarraFiltros.tsx` |
| 6 | `CartaoAlerta` | `components/CartaoAlerta.tsx`, `DetalhesTecnicos.tsx` |
| 7 | Drawer "Ver na tabela" | `components/DrawerLinhas.tsx`, `hooks/useLinhasDoAviso.ts`, `exportarLinhas.ts` |
| 8 | Página, regras não verificadas e vazio | `PaginaDetector.tsx`, `components/RegrasNaoVerificadas.tsx` |
| 9 | Exemplos na tela Importar | `features/importar/*` |
| 10 | Documentação | spec 15, `telas.md`, `decisions.md`, `CHANGELOG.md` |
| 11 | Verificação, teste manual, resumo e PR | — |

### Regras
- **Topo:** título "Detector de dados artificiais", ajuda "Aplicamos 11 regras que procuram sinais comuns de dados inseridos ou gerados. Um alerta pede conferência, não é uma conclusão."; ação secundária "Analisar de novo" (`refresh`, refaz a consulta).
- **Resumo** (print 7a): "Encontramos 5 alertas em 3 colunas" + detalhe da API; contadores mono 28 na cor da severidade com ícone preenchido e palavra (Suspeita alta `report` · Atenção `warning` · Informativo `info`). Carregando: skeleton + "Aplicando as 11 regras em {arquivo}…".
- **Filtros:** "Mostrar" + `ChipFiltro` por severidade ("Suspeita alta (2)", marcado com `check`, borda/texto da severidade); Segmented "Agrupar por" Coluna/Regra. Estado na URL (`?sev=alta,atencao&agrupar=regra`, padrão: todas e coluna; D124). Sem nenhum chip marcado: "Marque ao menos uma severidade para ver os alertas.".
- **Lista:** grupos (coluna mono 15/600 ou "R4 · Valores redondos") com "2 alertas"; dentro, ordem da API; aviso de par (R2) entra no grupo "altura_m × peso_kg". O 1º alerta de cada grupo aberto, os demais recolhidos ("Ver explicação" / "Ocultar explicação").
- **CartaoAlerta** (8 partes, `componentes.md`): topo com badge · "R4 · Valores redondos" · coluna(s) mono; título h3; resumo; grid "POR QUE CHAMA ATENÇÃO" / "PODE SER NORMAL SE…"; exemplo com "Ver na tabela" (`table_view`) quando há linhas; "O que fazer:"; Accordion "Detalhes técnicos" com `<dl>` (Medida, Valor, Limiar, Teste, p-valor + tradução, Fórmula) e a figura (`Grafico`, sob demanda) quando houver.
- **Drawer** (print 7b, 600 px): badge, título do aviso, "Linhas 120 a 138 · peso_kg", frase "{k} linhas destacadas" (+ o complemento da regra quando a API mandar); tabela com ±3 linhas de contexto (`GET /linhas?de=&ate=`; contexto limitado ao início/fim), linhas do exemplo destacadas e a coluna afetada no cabeçalho na cor da severidade; rodapé com a contagem e "Exportar estas linhas" (CSV gerado no navegador com `;` e vírgula decimal, `baixarArquivo`; nome `linhas-R4-peso_kg.csv`).
- **Regras não verificadas:** seção recolhível (fechada) "Regras não verificadas — {n} regras, com motivo"; cada item com o nome em 600 e a frase da API.
- **Vazio** (7c): círculo sucesso-suave 64 com `verified`, "Nenhum alerta", texto `resumo.vazio`, ações "Ver as 11 regras" (abre um Drawer com nome e intuição de cada regra, a partir de `textos.ts`) e "Continuar para Relatório".
- **Navegação:** Gerador "Continuar para Detector"; Detector "Voltar para Gerador" / "Continuar para Relatório"; Relatório "Voltar para Detector".
- **Importar:** abaixo do link do exemplo atual, "Outros exemplos" com os arquivos de `GET /datasets/exemplos` (nome mono + descrição); escolher um importa e segue o fluxo normal da tela 1.

---

### Tarefa 1: etapa 7 e navegação
`CAMINHOS.detector`; etapa 7 sem `disponivelEm` (nenhuma etapa futura sobra: `EtapaFutura` e `PaginaIndisponivel` continuam para os próximos marcos ou saem se ficarem sem uso — sem código morto); destinos novos nos botões.

**Testes (falham):** etapas sem futuras; `/detector` renderiza; botões das telas 6 e 8 com os destinos novos.

**Commit:** `feat(detector): etapa 7 liberada na navegação`

### Tarefa 2: `BadgeSeveridade` e `ChipFiltro`
Mapa `severidade → {icone, palavra, token}` em `shared/ui/severidades.ts` (`as const satisfies`); `ChipFiltro` com `role="checkbox"`, `aria-checked`, espaço/Enter alternam.

**Testes (falham):** ícone e palavra de cada severidade (não depende só de cor); teclado no chip.

**Commit:** `feat(ui): BadgeSeveridade e ChipFiltro`

### Tarefa 3: `Accordion` e `Drawer`
`Accordion` (`aria-expanded`, `aria-controls`, `chevron_right`/`expand_more`); `Drawer` (portal, overlay, foco preso, Esc e clique no overlay fecham, foco volta ao botão que abriu, `aria-labelledby`).

**Testes (falham):** abrir/fechar, Esc, foco inicial e retorno.

**Commit:** `feat(ui): Accordion e Drawer`

### Tarefa 4: API, filtros e agrupamento
`useDetector(datasetId)` (chave `chavesDataset.detector(id)`, invalidada com as demais do dataset); `useLinhas(datasetId, de, ate)`; funções puras `filtrarPorSeveridade`, `agruparPorColuna`, `agruparPorRegra`, `lerParametros/escreverParametros`.

**Testes (falham):** agrupamento por coluna com aviso de par; ordem preservada; parâmetros inválidos na URL caem no padrão.

**Commit:** `feat(detector): consulta, filtros e agrupamento`

### Tarefa 5: resumo e barra de filtros
**Testes (falham):** frase e contadores; chips com as contagens; desmarcar todos mostra a orientação.

**Commit:** `feat(detector): resumo e filtros`

### Tarefa 6: `CartaoAlerta`
Componente ≤ 150 linhas (subcomponentes `TopoAlerta`, `ExemploAlerta`, `DetalhesTecnicos`).

**Testes (falham):** as 8 partes na ordem; modo recolhido com só 1–3; detalhes começam fechados; figura só quando existe; p-valor com a tradução.

**Commit:** `feat(detector): cartão de alerta em 8 partes (spec 16)`

### Tarefa 7: drawer "Ver na tabela"
`useLinhasDoAviso(aviso)` calcula `de`/`ate` com contexto; `exportarLinhas(linhas, colunas)` (pura).

**Testes (falham):** contexto nas bordas (linha 0); linhas destacadas com `aria-current`/texto oculto "destacada"; CSV exportado com cabeçalho e vírgula decimal.

**Commit:** `feat(detector): drawer com as linhas do alerta`

### Tarefa 8: página
`PaginaDetector` (≤ 150 linhas), `RegrasNaoVerificadas`, vazio, erro (`EstadoErro` com "Tentar de novo"), sem dataset (`SemDataset`).

**Testes (falham):** fluxo com a API simulada (avisos de 3 severidades): filtrar, agrupar por regra, abrir drawer; vazio com as duas ações; recarregar mantém filtros.

**Commit:** `feat(detector): tela Detector (7a–7d)`

### Tarefa 9: exemplos na tela Importar
**Testes (falham):** lista vinda da API; escolher "Alturas com dados plantados" importa e mostra a prévia.

**Commit:** `feat(importar): exemplos de demonstração`

### Tarefa 10: documentação
Spec 15 (tela 7: filtros na URL, drawer, exemplos na tela 1), `telas.md` (nota "Implementação do M3"), `decisions.md` (D124 e as que surgirem), CHANGELOG › Adicionado: "Etapa 7 Detector: resumo por severidade, filtros, agrupamento por coluna ou regra, alertas explicados em linguagem simples com detalhes técnicos, linhas na tabela e regras não verificadas; exemplos de demonstração na tela Importar." › Alterado: navegação Gerador → Detector → Relatório.

**Commit:** `docs: tela Detector (spec 15, telas, decisões)`

### Tarefa 11: verificação, teste manual e PR
1. Verificação completa.
2. Preview (1440 e 1024 px, claro e escuro — print 7d): `alturas_plantadas.txt` (alertas R1, R3, R4, R5, R10; drawer do R4; exportar linhas), `vendas_correlacao_puxada.txt` (R2 no grupo do par, R6), `alturas_reais.txt` (vazio ou só informativos), `pesquisa_saude.txt` antes e depois da limpeza; demonstração completa: gerar k valores de `altura_m` preservando as estatísticas (média e DP exatos; k = max(10, ⌊n/20⌋) da R1 contado já com o bloco, ex.: 11 no exemplo limpo, pois 222 + 11 = 233 e ⌊233/20⌋ = 11), anexar e rodar o detector (R1 dispara no bloco anexado).
3. Resumo ao usuário antes do push; com o ok, push e PR.

## Critérios de pronto do M3.4
- Telas 7a–7d iguais aos prints nos dois temas; acessível pelo teclado (chips, accordion, drawer).
- Demonstração gerador → anexar → detector funcionando de ponta a ponta.
