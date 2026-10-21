# M4.4 — Relatório final do trabalho e prints — plano de implementação

> **Para o agente:** antes de começar, leia `CLAUDE.md`, `docs/padroes-codigo.md`, `docs/requisitos-professor.md` (objetivo 7 da versão final e o checklist), a spec 13 ("Relatório final do trabalho"), as specs 11 e 12, `docs/roadmap.md` e os contratos em `docs/plans/2026-10-18-m4-visao-geral.md`. **Sem seção sobre uso de IA e sem autoria de IA** no relatório, no código e nos commits.

**Objetivo:** entregar ao grupo, em `docs/relatorio-final/`, o relatório final do trabalho pedido pelo professor — "prints das telas e gráficos, fórmulas, explicação do gerador e do detector, documentação do trabalho" — já escrito (rascunho completo para o grupo revisar), com prints reproduzíveis da versão final, as fórmulas tiradas do catálogo do app, um exemplo do relatório HTML e o roteiro da apresentação.

**Arquitetura:** documentação em Markdown (D157); scripts: `frontend/scripts/prints.ts` (`playwright-core` com o Edge instalado, D156; fora do CI), `backend/scripts/exportar_formulas.py` e `backend/scripts/exportar_relatorio_exemplo.py` (ambos com `TestClient`, sem servidor). Fórmulas do detector num catálogo (`detector/formulas.py`) usado pelos textos dos detalhes e pela exportação.

**Branch:** `docs/relatorio-final` (sai de `develop` depois do merge do M4.3) → PR para `develop`. **Prazo sugerido:** 20/11/2026.

---

## Visão geral das tarefas

| # | Tarefa | Arquivos principais |
|---|---|---|
| 1 | Fórmulas do detector num catálogo | `detector/formulas.py`, `textos.py`, `textos_blocos.py` |
| 2 | Exportar as fórmulas | `backend/scripts/exportar_formulas.py`, `docs/relatorio-final/formulas.md` |
| 3 | Exemplo do relatório HTML | `backend/scripts/exportar_relatorio_exemplo.py`, `docs/relatorio-final/exemplo-relatorio.html` |
| 4 | Script de prints | `frontend/scripts/prints.ts`, `package.json`, `docs/relatorio-final/prints/*.png` |
| 5 | Texto do relatório final | `docs/relatorio-final/relatorio-final.md` |
| 6 | Roteiro de apresentação | `docs/relatorio-final/roteiro-apresentacao.md` |
| 7 | Guia da pasta e documentação | `docs/relatorio-final/README.md`, spec 13, `decisions.md`, `CHANGELOG.md` |
| 8 | Verificação, resumo e PR | — |

### Estrutura do relatório final (`relatorio-final.md`)
Capa (título, disciplina, professor, **campos a preencher**: integrantes e matrículas, data) · Sumário · 1. Introdução (objetivo, o que o programa faz, datasets usados) · 2. Arquitetura e tecnologias (camadas, domínios, frontend, decisões principais com link para as ADRs) · 3. Como usar (instalação, fluxo das 8 etapas) · 4. Leitura e classificação de tipos (regras da spec 02 e motivos) · 5. Limpeza · 6. Análise univariada: frequências, tendência central, separatrizes ("onde está meu valor"), dispersão, forma e distribuições (Normal, Binomial, assimetria, curtose) · 7. Correlação e regressão · 8. **Gerador**: univariado (métodos por tipo, reescala exata, limitar à faixa) e bivariado (Cholesky, ajuste exato), semente, tolerâncias testadas, prints 6a/6b · 9. **Detector**: tabela das 11 regras (o que mede, limiar, severidade, por que pode ser normal), controle de falsos positivos (200 amostras, < 5% por regra), dados plantados e o que cada arquivo dispara, demonstração com o Gerador, prints 7a–7c · 10. Relatório HTML (seções, apêndice, impressão) · 11. Qualidade e testes (CI, limites de complexidade, cobertura, nº de testes) · 12. Conclusão e limitações (R1 no meio só com k linhas, KaTeX offline, escala) · Referências (livros de estatística usados nas fórmulas, documentação do scipy) · Apêndice A: fórmulas (de `formulas.md`) · Apêndice B: exemplo do relatório HTML.

Cada seção traz o print da tela correspondente e cita os números reais do exemplo (`pesquisa_saude.txt`), conferidos no app.

---

### Tarefa 1: fórmulas do detector num catálogo
`detector/formulas.py`: `FORMULAS_REGRAS: dict[str, tuple[str, ...]]` (texto Unicode; R7 com as variantes Tukey, boxplot ajustado e z). `textos.py` e `textos_blocos.py` passam a usar as constantes (nenhum texto muda).

**Testes (falham):** cada regra do registro tem fórmula no catálogo; a fórmula dos detalhes de cada alerta de `alturas_plantadas.txt` e `vendas_correlacao_puxada.txt` está no catálogo da regra.

**Commit:** `refactor(detector): fórmulas das regras num catálogo`

### Tarefa 2: exportar as fórmulas
`exportar_formulas.py` (argparse `--saida`, padrão `docs/relatorio-final/formulas.md`): para cada grupo (Frequências, Tendência central, Separatrizes, Dispersão, Forma e distribuições, Correlação e regressão, Gerador, Detector), nome + `$$latex$$` + texto de reserva; detector com o texto e a regra. Usa só as fachadas (`analise.servico`, `gerador.servico`, `detector.servico`). LF, UTF-8.

**Testes (falham):** rodar numa pasta temporária gera um arquivo idêntico ao versionado (como os datasets plantados, D124); toda chave do catálogo da análise e do gerador aparece.

**Commit:** `docs: fórmulas do relatório final exportadas do catálogo`

### Tarefa 3: exemplo do relatório HTML
`exportar_relatorio_exemplo.py`: importa `pesquisa_saude.txt`, aplica a limpeza sugerida, gera um univariado de `peso_kg` (semente 42) e pede o relatório com as 9 seções (Plotly e KaTeX pelo CDN, para o arquivo ficar pequeno); data fixa no cabeçalho por parâmetro (`--data`), para o arquivo ser reproduzível.

**Testes:** rodar duas vezes com a mesma `--data` gera o mesmo arquivo.

**Commit:** `docs: exemplo do relatório HTML para o relatório final`

### Tarefa 4: script de prints
- `npm install -D playwright-core`; `frontend/scripts/prints.ts` + `npm run prints` (backend e frontend já rodando; URL por argumento, padrão `http://localhost:5173`).
- `chromium.launch({ channel: "msedge" })`, viewport 1440 × 900, `colorScheme` claro (e escuro para 4i, 7d), `reducedMotion: "reduce"`; carrega os exemplos pela tela Importar e percorre o fluxo; espera os gráficos (`.js-plotly-plot`) antes de cada print.
- Prints (mesmos nomes de `docs/design/telas/prints/`): 1a, 2a, 3a, 4a–4g, 4i, 5a, 6a, 6b, 7a, 7b, 7c, 7d, 8a → `docs/relatorio-final/prints/`.
- O script fica fora do lint de produção só se o ESLint já ignorar `scripts/`; senão, segue as mesmas regras.

**Verificação:** rodar com os servidores do preview (proxy local em `127.0.0.1`) e conferir cada PNG.

**Commit:** `chore: prints reproduzíveis das telas (playwright-core + Edge)` · `docs: prints da versão final`

### Tarefa 5: texto do relatório final
Escrever `relatorio-final.md` na estrutura acima, com os prints e as fórmulas (link para `formulas.md` e as principais no corpo). Conferir cada número citado no app; termos da spec 16; sem seção sobre uso de IA.

**Commit:** `docs: relatório final do trabalho`

### Tarefa 6: roteiro de apresentação
`roteiro-apresentacao.md`: ~10 minutos, quem fala o quê (campos), passos clicáveis: importar `pesquisa_saude.txt` → tipos → limpeza → univariada (`peso_kg`: separatrizes e "onde está meu valor") → bivariada (`altura_m` × `peso_kg`, prever) → gerador (univariado preservando; bivariado com ρ = 0,8) → detector (anexar 21 valores gerados a `alturas_reais.txt` e ver a R1; `alturas_plantadas.txt`) → relatório (baixar e imprimir); perguntas prováveis do professor e onde está a resposta.

**Commit:** `docs: roteiro de apresentação`

### Tarefa 7: guia da pasta e documentação
`docs/relatorio-final/README.md` (o que é cada arquivo, como refazer prints, fórmulas e o exemplo, como gerar o PDF — imprimir pelo navegador a partir do GitHub ou do VS Code); spec 13 (seção "Relatório final do trabalho" aponta para a pasta); `decisions.md` D156–D157; CHANGELOG › Adicionado: "Relatório final do trabalho em `docs/relatorio-final/`, com prints das telas, fórmulas, explicação do gerador e do detector e roteiro de apresentação."

**Commit:** `docs: guia do relatório final (spec 13, D156–D157)`

### Tarefa 8: verificação e PR
1. Verificação completa (os scripts novos passam no ruff/mypy; o `prints.ts` no lint e no `tsc`).
2. Conferir o relatório renderizado no GitHub (prévia do Markdown no preview, se possível) e os links internos.
3. Resumo ao usuário antes do push; com o ok, push e PR.

## Critérios de pronto do M4.4
- `docs/relatorio-final/` com relatório, fórmulas, exemplo HTML, prints e roteiro; tudo reproduzível pelos scripts.
- Itens do objetivo 7 da versão final cobertos: prints das telas e gráficos, fórmulas, explicação do gerador e do detector, documentação.
