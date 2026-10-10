# M3.6 — Documentação e release v0.3.0 — plano

> **Para o agente:** este bloco não tem código de produção (salvo ajustes achados no teste manual, que vão num PR `fix/` antes do release). Siga `padroes-codigo.md` §8 (release) e as regras do pedido do M3: PR, merge e release só com o ok do usuário; merge só com os 3 checks verdes; nunca commit direto em `main` ou `develop`.

**Objetivo:** revisar a documentação do M3, conferir os critérios de pronto com um teste manual completo, publicar a `v0.3.0` (PR para `develop`, PR `develop → main`, tag anotada e release no GitHub) e deixar a `develop` em dia com a `main` depois do release.

**Prazo sugerido:** 20/11/2026 (marco: 27/11/2026).

---

### Tarefa 1: revisão da documentação (branch `docs/revisao-m3`, PR para `develop`)
- `README.md`: funcionalidades do gerador e do detector como entregues; exemplos de demonstração.
- `docs/roadmap.md`: conferir o checklist do professor do M3 (gerador univariado, bivariado com correlação, detector com resumo).
- Specs 08, 11, 12, 13, 14, 15, 16 e 17: atualizações dos blocos entraram e não sobrou "fica para o M3".
- `docs/design/telas.md`: notas de implementação das telas 6 e 7.
- `docs/decisions.md`: D108 em diante em ordem, sem buracos; `CHANGELOG.md` › Não lançado com Adicionado/Alterado/Corrigido conferidos à mão.
- Commit: `docs: revisão da documentação do M3`.

### Tarefa 2: critérios de pronto + teste manual completo
Com `develop` atualizada (worktree limpo, `pip install -e ".[dev]"` e `npm ci`):
1. Verificação completa (backend, frontend, jscpd, tipos da API sem diferença); anotar o tempo do pytest (teste de falsos positivos).
2. Preview, temas claro e escuro, 1440 px e 1024 px:
   - `pesquisa_saude.txt`: fluxo do M2 rápido (limpeza, análise, bivariada) → Gerador (univariado preservar e parâmetros, bivariado com ajuste exato; baixar CSV; anexar; usar como novo) → Detector (antes e depois da limpeza) → Relatório (8 seções, baixar offline).
   - `alturas_plantadas.txt`, `vendas_correlacao_puxada.txt`, `alturas_reais.txt` pelos exemplos da tela Importar: alertas esperados, drawer, exportar linhas, vazio.
   - Demonstração para a apresentação: gerar um bloco preservando as estatísticas, anexar e ver a R1 disparar.
   - Recarregar em cada etapa (URL, filtros e sessão mantidos); sessão expirada volta para Importar com o aviso; geração expirada (reiniciar o backend) mostra o erro com "Gerar de novo".
3. Conferir o checklist do professor do M3 (`roadmap.md`).
4. Resumo ao usuário com o resultado e os prints principais (6a, 6b, 7a, 7b, relatório) — **antes** de abrir o release. Detalhes achados vão num PR `fix/detalhes-m3` (com o ok do usuário).

### Tarefa 3: release `v0.3.0` (só com o ok do usuário)
1. Branch `chore/release-v0.3.0` a partir da `develop`:
   - versão `0.3.0` em `backend/app/core/config.py` e no teste de `/api/saude` (`tests/core/test_saude.py`), `backend/pyproject.toml` e `frontend/package.json` (+ `npm install --package-lock-only`);
   - `CHANGELOG.md`: *Não lançado* vira `## [0.3.0] - AAAA-MM-DD` (data do dia), *Não lançado* vazio no topo;
   - `docs/roadmap.md`: M3 marcado como entregue (`v0.3.0` ✓ DD/MM);
   - verificação completa; commit `chore: release v0.3.0`; PR para `develop`; merge com os checks verdes.
2. PR `develop → main` ("Release v0.3.0", corpo com as notas da seção 0.3.0 do CHANGELOG); merge com os checks verdes e o ok do usuário.
3. Tag anotada na `main`: `git tag -a v0.3.0 -m "v0.3.0 — Gerador e Detector"` · `git push origin v0.3.0`.
4. `gh release create v0.3.0 --title "v0.3.0 — Gerador e Detector" --notes-file <notas da seção 0.3.0> --verify-tag`.

### Tarefa 4: sincronizar `main → develop` (início do M4)
Depois do release, a `develop` fica 1 merge atrás da `main` (a `main` exige PR em dia, `strict`):
1. `git fetch origin` · `git switch -c chore/sincroniza-main-pos-v0.3.0 origin/develop` · `git merge --no-ff origin/main -m "chore: sincroniza main (v0.3.0) na develop"` (diff vazio).
2. Push, PR para `develop`, merge com os checks verdes e o ok do usuário. Anotar na memória do projeto.

## Critérios de pronto do M3
- Checklist do professor do M3 coberto; telas 6 e 7 iguais aos prints nos dois temas; relatório com Gerador e Detector.
- Tolerâncias do gerador e falsos positivos do detector cobertos por testes; CI verde em todos os PRs; cobertura ≥ 80% em `dominios/` e `compartilhado/`; jscpd 0.
- `v0.3.0` com tag e release no GitHub; `develop` sincronizada com a `main`.
