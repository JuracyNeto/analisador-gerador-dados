# 17 — Tratamento de erros e testes

## Erros
- Exceções do núcleo: `ErroAplicacao(codigo, mensagem, sugestao)` em `app/core/erros.py`.
- `app/core/handlers.py` converte para HTTP: 400 (entrada), 404 (`DATASET_NAO_ENCONTRADO`, `COLUNA_NAO_ENCONTRADA`), 413 (`ARQUIVO_GRANDE`), 422 (validação), 500 (`ERRO_INTERNO` com mensagem genérica; detalhes só no log).
- `DATASET_NAO_ENCONTRADO`: "Sua sessão expirou. Envie o arquivo novamente." (ADR 0004)
- Casos de borda estatísticos não são erros: retornam `aplicavel: false` + motivo (specs 05–09).

## Testes (pytest)
| Alvo | Estratégia |
|---|---|
| leitura | fixture por formato e variação (spec 01) |
| tipos | 1 caso por regra + casos ambíguos (CEP numérico, Likert, 0/1) |
| limpeza | cada ação; ordem; desfazer; log |
| frequencias / descritiva | exemplos de livro com resposta calculada à mão; Sturges; Czuber |
| separatrizes | quantis conhecidos; "onde está meu valor" nos limites e fora da faixa |
| distribuicoes | amostra Normal → aderente; Exponencial → não aderente; Binomial conhecida |
| correlacao | r = 1, r = −1, r ≈ 0; extrapolação |
| gerador | tolerâncias da spec 11 (média/DP exatos com reescala, \|r − ρ\| < 1e-9 com ajuste exato, < 0,03 sem ajuste com n = 10.000); mesma semente → mesmo resultado; figura leve com 1.000.000 de valores; adotar novo/anexar e desfazer |
| detector | falsos positivos < 5% por regra e família (spec 12, D129: regras de coluna na amostra sozinha; R2, R5 e R6 numa tabela com data e 2ª amostra; ~20 s no CI); cada arquivo plantado dispara a regra esperada e `alturas_reais.txt` não tem alertas de atenção ou alta; o script dos arquivos de demonstração refaz os versionados |
| cadastro variado | `tests/fixtures/cadastro_variado.txt` (D131): tipo de cada coluna (códigos, datas, horários, datas com horário, números, sim/não, escalas, faltantes "NA", "-" e vazio) e um retrato do detector (sem suspeita alta, alertas só nas numéricas, linha do tempo da R6) |
| api | `TestClient`: fluxo feliz por endpoint + 404 + arquivo inválido |

Frontend: Vitest para formatadores (número pt-BR, p-valor traduzido). Checklist manual por tela antes de cada tag.

## Qualidade / CI
- `ruff check` + `ruff format --check`, `pytest -q`, `npm run build` (+ `tsc --noEmit`) em `.github/workflows/ci.yml` em push e PR.
- Cobertura alvo do núcleo: ≥ 80%.
