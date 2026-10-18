# M4.5 — Documentação final e release v1.0.0 — plano

> **Para o agente:** este bloco não tem código de produção (salvo ajustes achados no teste manual, que vão num PR `fix/` antes do release). Siga `padroes-codigo.md` §8 (release) e as regras do pedido do M4: PR, merge e release só com o ok do usuário; merge só com os 3 checks verdes; nunca commit direto em `main` ou `develop`.

**Objetivo:** revisar toda a documentação para a entrega, conferir os critérios de pronto do M4 e o checklist da versão final do professor num teste manual completo, publicar a `v1.0.0` (PR para `develop`, PR `develop → main`, tag anotada e release no GitHub) e deixar a `develop` em dia com a `main`.

**Prazo sugerido:** 27/11/2026 (entrega: 08/12/2026).

---

### Tarefa 1: revisão da documentação (branch `docs/revisao-m4`, PR para `develop`)
- `README.md` final: o que o app faz (com 3 ou 4 prints de `docs/relatorio-final/prints/`), como rodar, dados de exemplo, demonstração rápida, link para `docs/relatorio-final/`, qualidade (comandos), documentação.
- `docs/roadmap.md`: checklist do professor completo (relatório final com imagens e fórmulas no M4).
- Specs 00–17: atualizações dos blocos do M4 entraram; nada de "fica para o M4"; spec 13 com o item 10 implementado; spec 15 com a acessibilidade testada; spec 00 com os tempos medidos.
- `docs/design/telas.md`: notas de implementação do M4 (tela 8 com "Fórmulas"; ajustes do M4.2 e M4.3).
- `CLAUDE.md`: tabela "Qual arquivo ler" com `docs/relatorio-final/`.
- `docs/decisions.md`: D150 em diante em ordem, sem buracos; `CHANGELOG.md` › Não lançado com Adicionado/Alterado/Corrigido conferidos à mão.
- Commit: `docs: revisão da documentação do M4`.

### Tarefa 2: critérios de pronto + teste manual completo
Com `develop` atualizada (worktree limpo, `pip install -e ".[dev]"` e `npm ci`):
1. Verificação completa (backend, frontend, jscpd, tipos da API sem diferença); tempo do pytest; cobertura de `dominios/` e `compartilhado/`.
2. Preview, temas claro e escuro, 1440 px e 1024 px: o roteiro de apresentação (`docs/relatorio-final/roteiro-apresentacao.md`) do começo ao fim, cronometrado; os 5 exemplos; recarregar em cada etapa; sessão expirada; relatório com as 9 seções, baixado offline e impresso.
3. Checklist da versão final do professor (`requisitos-professor.md`) item a item, com onde cada item aparece (tela e seção do relatório final).
4. Resumo ao usuário com o resultado e os prints principais — **antes** de abrir o release. Detalhes achados vão num PR `fix/detalhes-m4` (com o ok do usuário).

### Tarefa 3: release `v1.0.0` (só com o ok do usuário)
1. Branch `chore/release-v1.0.0` a partir da `develop`:
   - versão `1.0.0` em `backend/app/core/config.py` e no teste de `/api/saude` (`tests/core/test_saude.py`), `backend/pyproject.toml` e `frontend/package.json` (+ `npm install --package-lock-only`);
   - `CHANGELOG.md`: *Não lançado* vira `## [1.0.0] - AAAA-MM-DD` (data do dia), *Não lançado* vazio no topo;
   - `docs/roadmap.md`: M4 marcado como entregue (`v1.0.0` ✓ DD/MM);
   - verificação completa; commit `chore: release v1.0.0`; PR para `develop`; merge com os checks verdes.
2. PR `develop → main` ("Release v1.0.0", corpo com as notas da seção 1.0.0 do CHANGELOG); merge com os checks verdes e o ok do usuário.
3. Tag anotada na `main`: `git tag -a v1.0.0 -m "v1.0.0 — Entrega final"` · `git push origin v1.0.0`.
4. `gh release create v1.0.0 --title "v1.0.0 — Entrega final" --notes-file <notas da seção 1.0.0> --verify-tag`.

### Tarefa 4: sincronizar `main → develop`
1. `git fetch origin` · `git switch -c chore/sincroniza-main-pos-v1.0.0 origin/develop` · `git merge --no-ff origin/main -m "chore: sincroniza main (v1.0.0) na develop"` (diff vazio).
2. Push, PR para `develop`, merge com os checks verdes e o ok do usuário. Anotar na memória do projeto.

## Critérios de pronto do M4
- Checklist da versão final do professor coberto, com relatório final em `docs/relatorio-final/`.
- Relatório HTML com o apêndice de fórmulas; telas sem violações do axe e com contraste testado; achados de UX aprovados corrigidos.
- CI verde em todos os PRs; cobertura ≥ 80% em `dominios/` e `compartilhado/`; jscpd 0.
- `v1.0.0` com tag e release no GitHub; `develop` sincronizada com a `main`.
