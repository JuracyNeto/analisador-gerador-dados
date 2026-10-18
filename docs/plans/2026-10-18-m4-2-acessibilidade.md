# M4.2 — Acessibilidade — plano de implementação

> **Para o agente:** execute tarefa por tarefa, em TDD. Antes de escrever código, leia `CLAUDE.md`, `docs/padroes-codigo.md` (§5, §6 Acessibilidade), as specs 00 (WCAG 2.1 AA), 15 (Acessibilidade) e 16, `docs/design/tokens.md`, `docs/design/componentes.md` e os contratos em `docs/plans/2026-10-18-m4-visao-geral.md`.

**Objetivo:** as 8 telas cumprem a spec 15 — teclado completo, foco visível, `aria-live` para toasts e resultados, contraste AA, severidade e tipo nunca só por cor, gráficos com título e resumo — com testes automáticos (axe e contraste dos tokens) que impedem regressões.

**Já existe (não refazer):** link "Pular para o conteúdo" (`LayoutApp`), `document.title` por etapa (`PaginaEtapa`), `aria-live` nos toasts, gráficos com `aria-label` e `aria-describedby` (`Grafico.tsx`), `jsx-a11y` no lint, chips de filtro com `role="checkbox"`, setas no `useNavegacaoPorSetas`.

**Arquitetura:** `axe-core` em dev (D153); helper `frontend/src/testes/acessibilidade.ts`; teste de contraste que lê `shared/ui/tokens.css`. Correções em `shared/ui` e nas telas.

**Branch:** `fix/acessibilidade` (sai de `develop` depois do merge do M4.1) → PR para `develop`. **Prazo sugerido:** 06/11/2026.

---

## Visão geral das tarefas

| # | Tarefa | Arquivos principais |
|---|---|---|
| 1 | Auditoria (lista de achados) | notas na pasta compartilhada da sessão |
| 2 | Helper do axe | `package.json`, `testes/acessibilidade.ts` |
| 3 | axe nos componentes de `shared/ui` | `shared/ui/*.test.tsx` |
| 4 | axe nas 8 telas | `features/*/Pagina*.test.tsx` |
| 5 | Contraste dos tokens | `shared/ui/tokens.test.ts`, `tokens.css` |
| 6 | Foco ao trocar de etapa e movimento reduzido | `PaginaEtapa.tsx`, `base.css` |
| 7 | Correções da auditoria | componentes indicados na tarefa 1 |
| 8 | Documentação | spec 15, `componentes.md`, `decisions.md`, `CHANGELOG.md` |
| 9 | Verificação, teste manual, resumo e PR | — |

### Regras
- `esperarSemViolacoes(container, opcoes?)`: roda `axe.run` no container com as regras WCAG 2.0/2.1 A e AA; falha listando `id`, `impact` e o seletor de cada violação. `color-contrast` desligada no jsdom (sem cálculo de cor; coberta pela tarefa 5).
- Contraste (WCAG 1.4.3 e 1.4.11), nos temas claro e escuro: texto (`--texto`, `--texto-2`, `--texto-3` quando usado em texto) sobre `--superficie`, `--superficie-2` e `--fundo` ≥ 4,5:1; cores de severidade e de tipo usadas em texto ≥ 4,5:1 sobre o fundo do chip/badge; bordas de campos, ícones sem texto e anel de foco ≥ 3:1. Texto grande (≥ 18,66 px negrito ou ≥ 24 px) ≥ 3:1.
- Teclado: toda ação alcançável por Tab na ordem visual; Esc fecha drawer, tooltip e menus; o drawer prende o foco e devolve ao botão que o abriu; nada de `tabindex` > 0.
- Troca de etapa: o foco vai para o `h1` da etapa (`tabIndex={-1}`), para o leitor de tela anunciar a página nova (D154).
- `prefers-reduced-motion: reduce`: transições e animações (skeleton, drawer, toast) desligadas ou ≤ 0,01 s (D154).
- Severidade e tipo sempre com ícone + palavra (já no design); conferir chips, badges, contadores e o heatmap.
- Zoom de 200% (1280 → 640 px de largura útil): sem perder conteúdo nem ação (WCAG 1.4.4, 1.4.10 na medida do possível; < 768 px é "leitura básica" na spec 15).

---

### Tarefa 1: auditoria
No preview, com `pesquisa_saude.txt` e `alturas_plantadas.txt`, temas claro e escuro, 1440 e 1024 px:
1. Só teclado, etapa por etapa (Tab, Shift+Tab, Enter, Espaço, setas, Esc): ordem, foco visível, armadilhas.
2. `read_page` (árvore de acessibilidade): nomes de botões, campos, abas, tabelas (`th scope`), gráficos, regiões (`main`, `nav`, `header`), títulos em ordem (h1 → h2 → h3).
3. `aria-live`: resultado do "Onde está meu valor?", previsão da Bivariada, "Gerar dados", "Analisar de novo", erros de formulário.
4. Contraste dos pares de tokens (cálculo da tarefa 5 rodado à mão antes de virar teste).
5. Zoom 200% e `prefers-reduced-motion` (emulação no preview).

Saída: lista de achados (tela · problema · critério WCAG · correção proposta) — no resumo ao usuário antes da tarefa 7, para ele escolher o que entra.

### Tarefa 2: helper do axe
`npm install -D axe-core`; `testes/acessibilidade.ts` com `esperarSemViolacoes`.

**Testes (falham):** um botão sem nome falha com a violação `button-name`; um botão com nome passa.

**Commit:** `test(frontend): verificação de acessibilidade com o axe`

### Tarefa 3: axe em `shared/ui`
Um caso por componente interativo (Abas, Accordion, Botao, CaixaSelecao, CampoNumero, CartaoOpcao, ChipFiltro, Drawer aberto, Segmented, Select, Slider, Tabela, Tooltip aberto, Toast, Banner, EstadoErro/Vazio/Carregando) nos estados principais.

**Testes (falham onde houver violação):** `await esperarSemViolacoes(container)` em cada `*.test.tsx`.

**Commit:** `test(frontend): componentes sem violações de acessibilidade` (+ `fix(ui): …` para cada correção)

### Tarefa 4: axe nas 8 telas
Em cada `Pagina*.test.tsx`, com as fixtures existentes: estado com dados, vazio e erro (o drawer da tela 7 aberto num caso).

**Commit:** `test(frontend): telas sem violações de acessibilidade` (+ correções)

### Tarefa 5: contraste dos tokens
`tokens.test.ts`: lê `tokens.css` (`fs` no Vitest), resolve as variáveis dos temas claro e escuro, calcula a luminância relativa (WCAG 2.1) e confere a tabela de pares da regra acima (`as const satisfies`). Par que falha → ajustar o token em `tokens.css` (e `docs/design/tokens.md`), sem mudar a identidade visual (mesma matiz, só a luminosidade).

**Commit:** `test(ui): contraste dos tokens nos dois temas` (+ `fix(ui): contraste de …`)

### Tarefa 6: foco e movimento
- `PaginaEtapa`: `h1` com `tabIndex={-1}` e foco ao montar a etapa (não no primeiro carregamento da app, para não roubar o foco do link "Pular para o conteúdo").
- `base.css`: bloco `@media (prefers-reduced-motion: reduce)`.

**Testes (falham):** trocar de rota (`renderizar` com o roteador de memória) → `document.activeElement` é o `h1`; CSS com o bloco de movimento reduzido (teste de texto do arquivo).

**Commit:** `feat(ui): foco no título ao trocar de etapa e movimento reduzido`

### Tarefa 7: correções da auditoria
Uma correção por commit (`fix(<feature>): …`), cada uma com o teste que a prova (axe, teclado com `user-event` ou papel/nome com Testing Library).

### Tarefa 8: documentação
Spec 15 (Acessibilidade: o que é testado automaticamente e o que é conferido à mão; foco ao trocar de etapa; movimento reduzido), `componentes.md` (Drawer: foco preso e devolvido), `tokens.md` (tokens ajustados), `decisions.md` D153–D154 (+ as da auditoria), CHANGELOG › Alterado/Corrigido com as mudanças visíveis ("O foco vai para o título ao trocar de etapa…", "Contraste maior em …").

**Commit:** `docs: acessibilidade (spec 15, D153–D154)`

### Tarefa 9: verificação, teste manual e PR
1. Verificação completa.
2. Preview: refazer o roteiro da tarefa 1 e conferir cada achado corrigido; prints antes × depois dos tokens ajustados.
3. Resumo ao usuário antes do push; com o ok, push e PR.

## Critérios de pronto do M4.2
- axe sem violações nas 8 telas e nos componentes de `shared/ui`; contraste dos tokens testado nos dois temas.
- Teclado completo, foco visível, foco no título ao trocar de etapa, movimento reduzido; achados aprovados corrigidos.
