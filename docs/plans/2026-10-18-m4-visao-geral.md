# M4 — Entrega: visão geral dos blocos

> Índice do M4. Cada bloco tem plano, branch e PR próprios. Os contratos abaixo são a **fonte única** entre os blocos: quem implementa um bloco não muda um contrato sem atualizar este arquivo e avisar no PR.

**Objetivo do marco:** fechar o trabalho para a entrega final. O relatório HTML ganha o apêndice de fórmulas (item 10 da spec 13, caixa "Fórmulas" do print 8a); as telas passam por uma auditoria de acessibilidade (WCAG 2.1 AA, spec 15) e por ajustes de UX achados num teste completo; o grupo recebe o relatório final do trabalho em `docs/relatorio-final/` (prints das telas e gráficos, fórmulas, explicação do gerador e do detector, documentação), um roteiro de apresentação e o README final. Fecham também as pendências do M3: a R1 no começo do arquivo e a fixture antiga do detector. Prazo **08/12/2026**, versão **v1.0.0** (`roadmap.md`).

**Critérios de pronto** (pedido do M4, `roadmap.md` e checklist da versão final do professor):
- Checklist da final completo: tudo da prévia · distribuições, assimetria, curtose · correlação e regressão · gerador univariado · gerador bivariado com correlação · detector com resumo · **relatório com imagens e fórmulas**.
- Relatório HTML com o apêndice de fórmulas (só as das seções incluídas), na prévia da tela 8 e no arquivo baixado; impressão com o apêndice na sua página.
- Telas 1–8 sem violações do axe (regras que o jsdom consegue medir) e com o contraste dos tokens ≥ 4,5:1 (texto) e ≥ 3:1 (bordas, ícones e foco) nos dois temas; teclado completo e foco visível conferidos no preview.
- `docs/relatorio-final/` com o relatório do grupo (sem seção sobre uso de IA), os prints atuais das telas, as fórmulas tiradas do mesmo catálogo do app e o roteiro de apresentação.
- Requisitos não funcionais da spec 00 medidos: análise de uma coluna < 2 s e detector completo < 10 s com 10 mil linhas.
- Cobertura ≥ 80% em `dominios/` e `compartilhado/`; CI verde (`backend`, `frontend`, `duplicacao`) em todos os PRs; `v1.0.0` com tag e release no GitHub.

## Blocos

| Bloco | Plano | Branch | Conteúdo |
|---|---|---|---|
| **M4.0** R1 no começo do arquivo + fixture | `2026-10-18-m4-0-r1-comeco.md` | `fix/detector-r1-comeco` | R1 procura também no começo do arquivo (de 10 a n/2 linhas), na mesma família do fim, sem aumentar os falsos positivos; fixture do detector no frontend com os textos atuais da R1 |
| **M4.1** Apêndice de fórmulas | `2026-10-18-m4-1-apendice-formulas.md` | `feat/relatorio-apendice-formulas` | 9ª seção `formulas` no relatório (módulo `relatorio/apendice.py`); catálogo de fórmulas do gerador (`Gerado.formulas`); fórmulas do detector a partir dos alertas; caixa "Fórmulas" na tela 8 ("9 de 9") |
| **M4.2** Acessibilidade | `2026-10-18-m4-2-acessibilidade.md` | `fix/acessibilidade` | axe nos testes das 8 telas e dos componentes de `shared/ui`; contraste dos tokens testado; teclado, foco, `aria-live`, foco ao trocar de etapa, `prefers-reduced-motion`, 200% de zoom |
| **M4.3** Ajustes de UX | `2026-10-18-m4-3-ajustes-ux.md` | `fix/ajustes-ux` | Teste completo com os 5 exemplos e arquivos grandes; lista de achados aprovada pelo usuário; correções; textos conferidos com a spec 16; medição dos tempos da spec 00 |
| **M4.4** Relatório final e prints | `2026-10-18-m4-4-relatorio-final.md` | `docs/relatorio-final` | `docs/relatorio-final/` (relatório do grupo, fórmulas geradas, roteiro de apresentação); script de prints reproduzíveis; exemplo do relatório HTML |
| **M4.5** Documentação e release | `2026-10-18-m4-5-documentacao-release.md` | `docs/revisao-m4`, `chore/release-v1.0.0` | README final, revisão das specs, teste manual completo, `v1.0.0`, sincronização `main → develop` |

**Por que 6 blocos:** a R1 (M4.0) e o apêndice (M4.1) mexem no backend e são independentes; acessibilidade (M4.2) e UX (M4.3) mexem nos mesmos componentes do frontend e vêm em sequência, com a auditoria antes dos ajustes; o relatório final (M4.4) depende da interface pronta, porque os prints são da versão entregue; o release (M4.5) fecha. PRs de 300 a 1.200 linhas.

## Dependências e ordem

| Bloco | Depende de (mergeado em `develop`) | Pode andar em paralelo com |
|---|---|---|
| M4.0 | — | M4.1 (conflitos só em `decisions.md` e `CHANGELOG.md`) |
| M4.1 | — | M4.0 |
| M4.2 | M4.1 (tela 8 com a caixa nova) | — |
| M4.3 | M4.2 (mesmos componentes) | — |
| M4.4 | M4.0–M4.3 (prints da interface final; fórmulas do catálogo do M4.1) | — |
| M4.5 | todos | — |

```
backend : M4.0 ── M4.1 ─┐
frontend:               └── M4.2 ── M4.3 ── M4.4 ── M4.5 (release v1.0.0)
```
Execução prevista (um bloco por vez): M4.0 → M4.1 → M4.2 → M4.3 → M4.4 → M4.5. Datas sugeridas: M4.0 23/10 · M4.1 30/10 · M4.2 06/11 · M4.3 13/11 · M4.4 20/11 · release 27/11 (folga até 08/12).

## Convenções que valem para todos os blocos

- Regras de `CLAUDE.md` e `padroes-codigo.md`. Rodar **antes de cada push**:
  - backend (em `backend/`, venv `.venv`): `ruff check . && ruff format --check . && mypy app && complexipy app --max-complexity-allowed 15 && pytest`
  - frontend (em `frontend/`): `npm run lint && npm run format && npm run test && npm run build`
  - raiz: `npx --yes jscpd@4 backend/app backend/tests frontend/src`
- Worktree novo: `python -m venv .venv` + `.venv/Scripts/python -m pip install -e ".[dev]"` em `backend/`; `npm ci` em `frontend/`.
- Depois de mudar a API: `python scripts/exportar_openapi.py` (em `backend/`) → `npm run gerar:tipos` (em `frontend/`) → commit do `schema.d.ts` **no mesmo bloco do backend** (só o M4.1 muda a API).
- TDD em toda tarefa: teste falhando → código → teste passando → commit (Conventional Commits em português, **sem atribuição de IA**: nada de `Co-Authored-By` nem "Generated with").
- Nunca silenciar lint, tipos ou complexidade (`noqa`, `eslint-disable`, `type: ignore`, `pragma: no cover`, overrides). Sem parâmetro booleano que escolhe comportamento; o ruff recusa `assert a and b`.
- Nomes que começam com "test" são coletados pelo pytest: nos testes, importe o módulo.
- **pandas 3**: nunca comparar `dtype == object`. Arquivos escritos por script: LF, UTF-8 (no Windows, `write_bytes` com `\n`; `write_text` grava CRLF).
- Números exibidos com o sinal de menos (−) (`formatar_com_sinal`, D107). Aleatoriedade sempre com `np.random.default_rng(semente)`.
- Toda decisão nova vai para `docs/decisions.md` com o **próximo número livre** (a partir da **D150**; os números abaixo são os previstos na ordem dos blocos). Toda entrega vai para `CHANGELOG.md` › *Não lançado*.
- Detector: critério do usuário "enviesar o mínimo" — mudança em regra não pode aumentar os falsos positivos; o teste de falsos positivos (spec 12, D129) continua < 5% por regra e família.
- Teste manual no preview (`.claude/launch.json`: `backend` 8000, `frontend` 5173) antes do push de cada bloco com tela; viewport fixa com `resize_window` e conferência pelo DOM. Depois de editar o backend, o `--reload` apaga os datasets: recarregue o exemplo antes de testar.
- **Ambiente Windows:** o Docker/WSL ocupa a porta 8000 em outro endereço e o proxy do Vite (`http://localhost:8000`) cai nele (502). Para o teste no preview, troque o proxy de `frontend/vite.config.ts` para `http://127.0.0.1:8000` **só localmente**, sem commitar, e desfaça no fim.
- Resumo ao usuário antes de cada push; PR, merge e release só com o ok do usuário; merge só com os 3 checks verdes (`gh pr merge N --merge`; o repositório não aceita auto-merge).

## Contratos do backend

### R1 (M4.0) — domínio `detector`
- `blocos.afastamentos_do_comeco(matriz, menor, maior) -> np.ndarray`: max(dᵤ, dₛ) dos primeiros `menor` a `maior` valores de cada linha contra o resto (espelho de `afastamentos_do_fim`).
- `r01_bloco_alinhado`: dois tipos de trecho, cada um contra o seu acaso, como na D148: (1) janelas de k linhas; (2) **bordas** = começo e fim, de 10 a ⌊n/2⌋ linhas. O candidato das bordas é o mais parecido entre começo e fim; a referência é a melhor borda (começo ou fim) de cada embaralhamento. Juntar começo e fim numa família só mantém duas famílias e não aumenta os falsos positivos (D150).
- Textos: os detalhes técnicos dizem "Janelas de 20 linhas seguidas, o começo e o fim do arquivo (de 10 a 150 linhas)"; resumo e exemplo não mudam. API sem mudança.

### Fórmulas (M4.1)
```
Formula {chave: str, nome: str, latex: str, texto: str}     # sai de analise/resultados.py para compartilhado/tipos.py (a análise reexporta; D152)
Gerado.formulas: [Formula]                                  # API: Gerado ganha `formulas` (como Analise.formulas)
```
- `gerador/formulas.py`: catálogo por método — `reescala` (zᵢ = (gᵢ − ḡ)/s_g → gᵢ' = x̄ + s·zᵢ), `normal`, `kde` (f̂(x) = (1/nh) Σ K((x − xᵢ)/h), h de Scott, como o `gaussian_kde`), `poisson`, `empirica`, `normal_inteira`, `bernoulli`, `frequencias`, `cholesky` (X = μx + σx·Z₁ · Y = μy + σy·(ρZ₁ + √(1 − ρ²)·Z₂)) e `ajuste_exato` (Gram-Schmidt); `formulas_do_metodo(metodo, reescala: aplicada?)` escolhe as que valem para a geração (reescala só onde a spec 11 a aplica).
- Detector: o apêndice usa a fórmula em texto dos detalhes de cada alerta (uma por regra, sem LaTeX). No M4.4, as fórmulas das regras viram um catálogo em texto (`detector/formulas.py`, R7 com as variantes), usado pelos textos dos detalhes e pela exportação para o relatório final.

### Relatório (M4.1) — domínio `relatorio`
```
Secao += "formulas"                                          # ordem: leitura, tipos, limpeza, analises, distribuicoes, bivariada, gerador, detector, formulas
SECOES_PADRAO = as 9
FormulaTexto {chave, nome, latex, texto}                     # ganha `chave` (para juntar sem repetir)
FormulaApendice {nome, latex: str | None, texto, onde: str | None}   # onde = "peso_kg, altura_m" (análise e forma) ou "R4" (detector)
GrupoFormulas {titulo, formulas: tuple[FormulaApendice, ...]}
ApendiceFormulas {grupos: tuple[GrupoFormulas, ...]}         # vazio → a seção não entra
ConteudoRelatorio.formulas: ApendiceFormulas | None
```
- `relatorio/apendice.py` (módulo novo; `servico.py` está com 428 linhas): `montar_apendice(colunas, bivariada, gerador, detector) -> ApendiceFormulas | None`, função pura sobre o conteúdo já montado das seções incluídas. Grupos, na ordem do documento: "Análise por coluna", "Forma e distribuição", "Bivariada", "Gerador", "Detector"; dentro de cada grupo, a ordem do catálogo, sem repetir a mesma `chave`; grupo sem fórmula não entra.
- Com o apêndice, as listas "Fórmulas usadas" de cada coluna e da Bivariada saem do template (D151; ver "Pontos de atenção" 1).
- Template: seção numerada como as outras, título "Fórmulas usadas", `h3` por grupo, cada fórmula com nome, KaTeX (`data-latex`) e o texto de reserva, e o "onde" em nota; `@media print` com quebra antes do apêndice.

### Códigos de erro novos
Nenhum.

## Contratos do frontend

| Bloco | O que muda |
|---|---|
| M4.0 | `testes/fixtures/detector.ts`: textos atuais da R1 ("Bloco alinhado ao restante dos dados em …", "(resto …)") |
| M4.1 | `SECOES_RELATORIO` com `formulas` (rótulo "Fórmulas"), contador "9 de 9"; tipos regenerados (`Gerado.formulas`) |
| M4.2 | `testes/acessibilidade.ts` (`esperarSemViolacoes(container)` com o axe); teste de contraste lendo `shared/ui/tokens.css`; correções nos componentes de `shared/ui` e nas telas |
| M4.3 | Correções da lista de achados aprovada (componentes e textos) |
| M4.4 | `frontend/scripts/prints.ts` + `npm run prints` (fora do CI) |

## Decisões previstas (entram em `docs/decisions.md` no bloco indicado; use o próximo número livre)
| # | Decisão | Bloco |
|---|---|---|
| D150 | R1: começo do arquivo (10 a ⌊n/2⌋ linhas) na mesma família do fim ("bordas", contra a melhor borda de cada embaralhamento); no meio, só janelas de k linhas (procurar todos os tamanhos custaria O(n²) por embaralhamento) | M4.0 |
| D151 | Apêndice de fórmulas como 9ª seção (`formulas`, caixa "Fórmulas" do print 8a), só com as fórmulas das seções incluídas, agrupadas e sem repetir; as listas por coluna e da Bivariada saem (o apêndice as substitui) | M4.1 |
| D152 | `Formula` em `compartilhado/tipos.py` (value object usado por análise, gerador e relatório); catálogo do gerador por método em `gerador/formulas.py` e `Gerado.formulas` na API; detector usa a fórmula em texto dos alertas | M4.1 |
| D153 | Acessibilidade testada com o axe (`axe-core` em dev) em cada tela e componente; contraste dos tokens testado à parte (o jsdom não mede cor) | M4.2 |
| D154 | Foco no título da etapa ao trocar de rota e `prefers-reduced-motion` sem animações (achados previstos da auditoria; a numeração final segue o que a auditoria achar) | M4.2 |
| D155 | Prints reproduzíveis com `playwright-core` usando o Edge instalado (sem baixar navegador), por `npm run prints`, fora do CI | M4.4 |
| D156 | Relatório final do grupo em Markdown (`docs/relatorio-final/relatorio-final.md`, fórmulas com `$$…$$`, que o GitHub renderiza); fórmulas exportadas do catálogo por `backend/scripts/exportar_formulas.py` (fonte única) | M4.4 |
| D157+ | Achados do teste de UX (M4.3) e do teste manual do release (M4.5) | M4.3, M4.5 |

## Dependências novas
- `axe-core` (dev, frontend) — M4.2, D153.
- `playwright-core` (dev, frontend; usa o Edge do Windows pelo `channel: "msedge"`, nada a baixar além do pacote) — M4.4, D155.
- Backend: nenhuma.

## Tamanho dos PRs
| Bloco | Linhas estimadas (código + testes + docs) |
|---|---|
| M4.0 | ~300 |
| M4.1 | ~1.000 |
| M4.2 | ~800 (depende dos achados) |
| M4.3 | ~600 (depende dos achados) |
| M4.4 | ~1.200 (texto + script; + PNGs) |
| M4.5 | ~200 (docs e versões) |

## Pontos de atenção encontrados nas specs, no design e no código
1. **Fórmulas repetidas:** hoje cada coluna do relatório traz a sua lista "Fórmulas usadas" (média, mediana, variância… repetidas em toda coluna) e a Bivariada traz a dela. O print 8a mostra "Fórmulas" como seção própria (p. 11) e as colunas sem lista. O apêndice junta tudo uma vez, com o "onde" (D151).
2. **KaTeX sem internet:** o KaTeX vem do CDN; no arquivo "Funciona sem internet" as fórmulas aparecem no texto de reserva (a spec 13 já prevê). Embutir o KaTeX (~300 KB + fontes) fica fora do M4.
3. **R1 no meio do arquivo:** um bloco no meio só é achado com exatamente k linhas; achar qualquer tamanho exige todos os tamanhos em cada um dos 1.000 embaralhamentos (O(n²); com 10 mil linhas, minutos). O M4.0 resolve o começo (o caso simétrico ao fim, D148) e documenta o limite na spec 12.
4. **Fórmulas do detector:** estão só em texto Unicode nos detalhes (sem LaTeX); o apêndice mostra o texto, sem KaTeX.
5. **axe no jsdom:** o jsdom não calcula cores nem layout; contraste, foco visível e ordem visual ficam com o teste dos tokens e com a conferência no preview.
6. **Prints:** dependem da data do dia (cabeçalho do relatório) e do tema; o script fixa viewport (1440 × 900), tema e exemplos, e os PNGs não entram em teste automatizado.
7. **Relatório final:** documento do grupo, gerado fora do app (spec 13); sem seção sobre uso de IA e sem autoria de IA; nomes e matrículas do grupo ficam como campos a preencher.
8. **Versão 1.0.0:** a API passa a ser estável (SemVer); mudanças depois do release vão para `hotfix/*` (padrões §8).
