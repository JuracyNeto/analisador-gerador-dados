# M2.6 — Documentação e release v0.2.0 — plano

> **Para o agente:** este bloco não tem código de produção. Siga `padroes-codigo.md` §8 (release) e as regras do pedido do M2: PR, merge e release só com o ok do usuário; merge só com os 3 checks verdes; nunca commit direto em `main` ou `develop`.

**Objetivo:** deixar a `develop` em dia com a `main`, revisar a documentação do M2, conferir os critérios de pronto com um teste manual completo e publicar a `v0.2.0` (PR para `develop`, PR `develop → main`, tag anotada e release no GitHub).

**Prazo sugerido:** 06/11/2026 (marco: 13/11/2026).

---

### Tarefa 1: sincronizar `main → develop`
A `develop` está 1 commit atrás da `main` (o merge do PR de release #21; a árvore é igual — `git diff origin/develop origin/main` vazio), e a `main` exige PR em dia (`strict`).
1. `git fetch origin` · `git switch -c chore/sincroniza-main-pos-v0.1.1 origin/develop` · `git merge --no-ff origin/main -m "chore: sincroniza main (v0.1.1) na develop"`.
2. Push, PR para `develop` ("Sincroniza a main na develop antes do release v0.2.0"), pedir ao usuário para avisar quando os checks passarem, `gh pr merge N --merge` com o ok dele.

(Se o usuário preferir, esta tarefa pode ser feita logo no começo do M2: não depende de nada.)

### Tarefa 2: revisão da documentação
- `README.md`: conferir a lista de funcionalidades (já cita distribuições, assimetria/curtose, correlação/regressão) e acrescentar "Etapa Bivariada" se a seção de telas listar as etapas.
- `docs/roadmap.md`: marcar o M2 como entregue (`v0.2.0`, data).
- `docs/specs/00-visao-geral.md`, 08, 09, 10, 13, 14, 15: conferir que as atualizações dos blocos entraram e que não sobrou "fica para o M2".
- `docs/design/telas.md` e `graficos-plotly.md`: notas de implementação do M2 (resíduos × X, unidades omitidas).
- `docs/decisions.md`: D90–D105 em ordem, sem buracos; `CHANGELOG.md` › Não lançado com as seções Adicionado/Alterado/Corrigido conferidas à mão.
- Commit (branch `docs/revisao-m2`, PR para `develop`): `docs: revisão da documentação do M2`.

### Tarefa 3: critérios de pronto + teste manual completo
Com `develop` atualizada (worktree limpo, `pip install -e ".[dev]"` e `npm ci`):
1. Verificação completa (backend, frontend, jscpd, tipos da API sem diferença).
2. Preview, temas claro e escuro, 1440 px e 1024 px:
   - `pesquisa_saude.txt`: Importar → Variáveis → Limpeza (aplicar algo) → Análise (aba Forma em `peso_kg`, `idade`, `sexo`, `cidade`) → Bivariada (`altura_m × peso_kg`, prever dentro e fora da faixa, trocar X e Y) → Relatório (6 seções, baixar).
   - `notas_turma.csv`: `faltas` (Binomial, tentativas), `nota_p1 × nota_p2`.
   - CSV e XLSX com colunas de data, hora e data com hora: chip "Data", motivo, correção manual e ausência nas telas 4 e 5 e no relatório por coluna.
   - Recarregar em cada etapa (URL e sessão mantidas); sessão expirada (reiniciar o backend) volta para Importar com um aviso.
3. Conferir o checklist do professor do M2 (`roadmap.md`): distribuições, assimetria, curtose; correlação e regressão.
4. Resumo ao usuário com o resultado e os prints principais (4e, 5a, relatório) — **antes** de abrir o release.

### Tarefa 4: release `v0.2.0` (só com o ok do usuário)
1. Branch `chore/release-v0.2.0` a partir da `develop`:
   - versão `0.2.0` em `backend/app/core/config.py` e no teste de `/api/saude` (`tests/core/test_saude.py`), `backend/pyproject.toml` e `frontend/package.json` (+ `npm install --package-lock-only`);
   - `CHANGELOG.md`: *Não lançado* vira `## [0.2.0] - AAAA-MM-DD` (data do dia), *Não lançado* vazio no topo;
   - verificação completa; commit `chore: release v0.2.0`; PR para `develop`; merge com os checks verdes.
2. PR `develop → main` ("Release v0.2.0", corpo com as notas da seção 0.2.0 do CHANGELOG); merge com os checks verdes e o ok do usuário.
3. Tag anotada na `main`: `git tag -a v0.2.0 -m "v0.2.0 — Análise avançada"` · `git push origin v0.2.0`.
4. `gh release create v0.2.0 --title "v0.2.0 — Análise avançada" --notes-file <notas da seção 0.2.0>`.
5. Depois do release, a `develop` fica 1 merge atrás da `main` de novo: anotar na memória do projeto que o próximo marco começa com um PR `chore/sincroniza-main-pos-v0.2.0`.

## Critérios de pronto do M2
- Checklist do professor do M2 coberto; colunas de data reconhecidas e fora das análises; telas 4 (Forma) e 5 iguais aos prints nos dois temas; relatório com Distribuições e Bivariada.
- CI verde em todos os PRs; cobertura ≥ 80% em `dominios/` e `compartilhado/`; jscpd 0.
- `v0.2.0` com tag e release no GitHub.
