# M3.1 — Tela Gerador — plano de implementação

> **Para o agente:** execute tarefa por tarefa, em TDD. Antes de escrever código, leia `CLAUDE.md`, `docs/padroes-codigo.md`, as specs 11, 15 e 16, `docs/design/telas.md` (tela 6), `docs/design/componentes.md`, os prints `6a-gerador-univariado.png` e `6b-gerador-bivariado.png` e os contratos em `docs/plans/2026-10-10-m3-visao-geral.md`.

**Objetivo:** liberar a etapa 6. O usuário escolhe Univariado ou Bivariado, preenche o formulário (origem no dataset ou parâmetros manuais, quantidade, modo, semente, limite de faixa / correlação alvo e ajuste exato), gera, vê a tabela Original × Gerado, o gráfico e "Como geramos", e baixa o CSV, anexa ao dataset atual ou usa o resultado como novo dataset.

**Arquitetura:** `features/gerador` (`api.ts` com as mutations e chaves, `hooks/`, `components/`, `textos.ts`, `tipos.ts`). Componentes novos de design system em `shared/ui`: `CartaoOpcao` (rádio em cartão, modo "Preservar"/"Novos parâmetros") e `Slider` (ρ de −1 a 1). Gráfico pelo `shared/graficos/Grafico` (Plotly sob demanda). Sessão ganha `ultimoGerado` (M3.5 usa no relatório).

**Branch:** `feat/frontend-gerador` (sai de `develop` depois do merge do M3.0) → PR para `develop`. **Prazo sugerido:** 24/10/2026.

---

## Visão geral das tarefas

| # | Tarefa | Arquivos principais |
|---|---|---|
| 1 | Etapa 6 liberada e navegação | `app/etapas.ts`, `rotas.ts`, `shared/navegacao/caminhos.ts`, Bivariada e Relatório (`AcoesEtapa`) |
| 2 | `CartaoOpcao` e `Slider` | `shared/ui/CartaoOpcao.tsx`, `Slider.tsx` (+ CSS e testes) |
| 3 | API da feature e sessão | `features/gerador/api.ts`, `tipos.ts`, `shared/sessao/*` |
| 4 | Formulário univariado | `components/FormularioUnivariado.tsx`, `hooks/useFormularioUnivariado.ts`, `validacao.ts` |
| 5 | Formulário bivariado | `components/FormularioBivariado.tsx`, `hooks/useFormularioBivariado.ts` |
| 6 | Resultado | `components/ResultadoGeracao.tsx`, `TabelaComparacao.tsx`, `ComoGeramos.tsx` |
| 7 | Ações: Baixar CSV, Anexar, Usar como novo dataset | `hooks/useAcoesGeracao.ts` |
| 8 | Página, estados e textos | `PaginaGerador.tsx`, `textos.ts` |
| 9 | Documentação | spec 15, `telas.md` (nota de implementação), `decisions.md`, `CHANGELOG.md` |
| 10 | Verificação, teste manual, resumo e PR | — |

### Regras
- **Layout** (print 6a): título "Gerador de dados", ajuda "Crie dados artificiais parecidos com os seus, ou com parâmetros que você escolher."; `Abas` Univariado/Bivariado (aba na URL: `?aba=univariado|bivariado`, D78); grid `360px 1fr` (empilha abaixo de 1024 px).
- **Univariado:** Segmented "Origem" (Coluna do dataset / Parâmetros manuais; sem dataset na sessão, só manuais — D115) · Select "Coluna" (analisáveis, sem auxiliares) · "Quantidade de valores (X)" (`CampoNumero`, 1–1.000.000, padrão 500) · "Modo" com dois `CartaoOpcao`: "Preservar estatísticas — Mesma média (70,3) e desvio (11,2) da coluna." (qualitativas: "Mesmas frequências da coluna.") / "Novos parâmetros" com Média e Desvio desabilitados até ser escolhido (binária: "Chance de {sucesso}"; nominal/ordinal: cartão desabilitado com o motivo de `MODO_NAO_APLICAVEL`) · "Semente (repete o mesmo resultado)" opcional · Checkbox "Limitar à faixa original — Nenhum valor abaixo de 43,8 ou acima de 92,9." (só numéricas com origem). Sem origem: Select "Tipo" (Contínua, Discreta, Binária) + Média/Desvio ou Chance.
- **Bivariado** (print 6b): Origem (Par do dataset / Parâmetros manuais) · X e Y (numéricas, um desabilita o outro como na tela 5) · grid 2×3 Médias e Desvios, preenchidos a partir do par (análise de X e Y + r da bivariada) e editáveis · `Slider` "Correlação alvo (ρ)" −1…1, passo 0,01, marca no 0, valor mono · "Quantidade de pares" · Checkbox "Ajuste exato — A correlação dos dados gerados fica exatamente igual a ρ." · Semente.
- **Validação local** com mensagens da spec 16 ("Digite um número inteiro entre 1 e 1.000.000.", "O desvio precisa ser maior que zero.", "Use um valor entre −1 e 1."); erros da API (`PARAMETROS_INCOMPLETOS` etc.) no `MensagemCampo` do campo certo ou em toast.
- **Botão** primário largo "Gerar dados" (`auto_awesome`, `textoCarregando` "Gerando…"). Toast: "Geramos 500 valores." / "Geramos 500 pares.".
- **Resultado:** card "Original × Gerado" com subtítulo "Semente 42 · preservar estatísticas" (Tabela Medida · Original · Gerado ({n}) · Diferença em texto-2, números com `formatarNumero` e sinal "+"/"−"; sem origem a coluna Original mostra "—"); card com o gráfico (sobreposição ou dispersão) e "Como geramos" (`menu_book`) com `explicacao`. Ações abaixo: "Baixar CSV" (`download`), "Anexar ao dataset atual" (`playlist_add`, só com dataset na sessão), primário "Usar como novo dataset" (`table_view`).
- **Ações:** Baixar → `requisitarBlob(/gerador/{gid}/csv)` + `baixarArquivo`; Anexar → `adotar {modo: "anexar", dataset_id}`, invalida `chavesDataset.todas(id)`, toast "Anexamos 500 linhas a pesquisa_saude.txt."; Usar como novo → `adotar {modo: "novo"}`, `definirDataset` com o novo dataset, toast "Novo dataset criado: 500 linhas.". `COLUNAS_INCOMPATIVEIS` vira toast com a sugestão.
- **Sessão:** depois de gerar, `definirUltimoGerado({id, descricao: "peso_kg · 500 valores"})`; `encerrar` limpa. `GERADO_NAO_ENCONTRADO` numa ação limpa o resultado e mostra o erro com "Gerar de novo".
- **Navegação:** "Voltar para Bivariada" / "Continuar para Relatório" (até o M3.4); Bivariada passa a continuar para o Gerador e o Relatório volta para o Gerador.

---

### Tarefa 1: etapa 6 e navegação
- `CAMINHOS.gerador = '/gerador'`; `ETAPAS[5]` sem `disponivelEm`; `PAGINAS[6] = PaginaGerador` (lazy).
- Bivariada: `T.navegacao.continuar` → "Continuar para Gerador"; Relatório: "Voltar para Gerador".

**Testes (falham):** `etapas.test.ts` (etapa 6 liberada, 7 ainda futura); `rotas.test.tsx` (`/gerador` renderiza a página); testes das telas 5 e 8 com os novos destinos.

**Commit:** `feat(gerador): etapa 6 liberada na navegação`

### Tarefa 2: `CartaoOpcao` e `Slider`
- `CartaoOpcao`: `input type="radio"` real dentro de `label` (grupo com `fieldset`/`legend`), título 15/600, descrição 13,5 texto-2, `children` (campos) desabilitados quando não selecionado; selecionado com borda 2 primária e fundo primária-suave; `desabilitado` + `motivo` (tooltip/texto).
- `Slider`: `input type="range"` com rótulo, `min/max/step`, marca no 0 (CSS), valor mono ao lado, `aria-valuetext` pt-BR ("0,70").

**Testes (falham):** teclado (setas mudam o rádio e o range), `aria-checked`, campos internos desabilitados, valor formatado "−0,35".

**Commit:** `feat(ui): CartaoOpcao e Slider`

### Tarefa 3: API e sessão
- `api.ts`: `useGerarUnivariado`, `useGerarBivariado`, `useAdotarGeracao` (mutations), `caminhoCsv(gid)`; tipos derivados de `schema.d.ts` em `tipos.ts`.
- Sessão: `ultimoGerado` em `ValorSessao` + `definirUltimoGerado`; persistido junto (`persistencia.ts` lê sessões antigas sem o campo).

**Testes (falham):** corpo enviado (origem nula em manuais; semente omitida quando vazia); persistência com e sem `ultimoGerado`.

**Commit:** `feat(gerador): chamadas da API e última geração na sessão`

### Tarefa 4: formulário univariado
Estado em `useFormularioUnivariado` (origem, coluna, x, modo, média, desvio, chance, semente, limitar), derivados calculados (não guardados): descrição do "Preservar" a partir de `useAnalise` da coluna (consulta em `shared/api`; mover de `features/analise` se preciso, sem duplicar), habilitação dos campos, `pedido` pronto ou erros por campo (`validacao.ts`, funções puras).

**Testes (falham):** `validacao.test.ts` (limites, desvio > 0, chance 0–1, semente inteira); componente: trocar para "Novos parâmetros" habilita Média/Desvio; nominal desabilita o cartão com o motivo; sem dataset só "Parâmetros manuais".

**Commit:** `feat(gerador): formulário univariado`

### Tarefa 5: formulário bivariado
Mesmo padrão; prefill dos parâmetros a partir de `useAnalise(x)`, `useAnalise(y)` e da consulta da bivariada (r), em paralelo (`useQueries`), sem sobrescrever o que o usuário editou (estado "editado" por campo).

**Testes (falham):** prefill com o par; editar a média de X e trocar Y mantém a média editada; ρ fora de −1..1 bloqueia.

**Commit:** `feat(gerador): formulário bivariado`

### Tarefa 6: resultado
`TabelaComparacao` (usa `Tabela`), `ComoGeramos`, `ResultadoGeracao` (estados: vazio "Preencha o formulário e clique em Gerar dados." com `auto_awesome`; carregando com skeleton; erro com `EstadoErro`).

**Testes (falham):** linhas da comparação com sinal na diferença; "—" sem origem; figura renderizada pelo `Grafico` (mock do Plotly); explicação do servidor.

**Commit:** `feat(gerador): resultado com comparação, gráfico e explicação`

### Tarefa 7: ações
`useAcoesGeracao(gerado)`: baixar, anexar, usar como novo; estados de carregamento por botão.

**Testes (falham):** baixar chama `requisitarBlob` com o caminho e o nome `gerado-peso_kg.csv`; anexar invalida as chaves do dataset e mostra o toast; usar como novo troca o dataset da sessão; `COLUNAS_INCOMPATIVEIS` vira toast; "Anexar" some sem dataset.

**Commit:** `feat(gerador): baixar CSV, anexar e usar como novo dataset`

### Tarefa 8: página
`PaginaGerador` (≤ 150 linhas; abas, grid, ações do rodapé), `textos.ts` com todos os textos da tela (spec 16).

**Testes (falham):** fluxo completo com API simulada (`simularApi`): gerar univariado → tabela e toast; aba bivariada na URL; recarregar mantém a aba.

**Commit:** `feat(gerador): tela Gerador (6a, 6b)`

### Tarefa 9: documentação
- Spec 15 (tela 6: aba na URL, gerador sem dataset), `telas.md` (nota "Implementação do M3"), `decisions.md` (D115 e as que surgirem), CHANGELOG › Adicionado: "Etapa 6 Gerador: dados univariados e bivariados com comparação original × gerado, gráfico, explicação do método, CSV e uso como novo dataset ou anexado ao atual." › Alterado: navegação Bivariada → Gerador → Relatório.

**Commit:** `docs: tela Gerador (spec 15, telas, decisões)`

### Tarefa 10: verificação, teste manual e PR
1. Verificação completa.
2. Preview (1440 e 1024 px, claro e escuro), exemplo limpo: univariado `peso_kg` preservar com semente 42 (comparação perto do print 6a), "Limitar à faixa"; `escolaridade` (sorteio pelas frequências, "Novos parâmetros" desabilitado); manuais sem dataset (encerrar a sessão); bivariado `altura_m × peso_kg` com ρ = 0,7 e ajuste exato (r gerado = 0,7); baixar o CSV e importar de volta; anexar a `peso_kg` (n muda no cabeçalho); usar como novo (sessão troca).
3. Resumo ao usuário antes do push; com o ok, push e PR.

## Critérios de pronto do M3.1
- Telas 6a e 6b iguais aos prints nos dois temas; estados vazio, carregando e erro.
- As três ações funcionam e mantêm a sessão consistente.
