# 14 — API (FastAPI)
Camada de apresentação: `router.py` + `schemas.py` de cada domínio; `app/main.py` registra tudo; erros em `app/core/` · Prefixo `/api` · Docs automáticas em `/docs`

## Endpoints
| Método | Rota | Corpo / query | Resposta | Spec |
|---|---|---|---|---|
| POST | `/datasets` | multipart `arquivo` + opções de leitura | `{dataset_id, metadados, previa[20], colunas[]}` | 01 |
| GET | `/datasets/{id}` | `?pagina=&tamanho=&versao=original|atual` | linhas paginadas | — |
| DELETE | `/datasets/{id}` | — | 204 | — |
| GET | `/datasets/{id}/colunas` | — | `TipoColuna[]` | 02 |
| PATCH | `/datasets/{id}/colunas/{col}` | `{tipo, categorias_ordem?}` | `TipoColuna` | 02 |
| GET | `/datasets/{id}/diagnostico` | `?limites={col:{min,max}}` | `Diagnostico` | 03 |
| POST | `/datasets/{id}/limpeza` | `{acoes[]}` | `{log[], n_linhas, colunas[]}` | 03 |
| POST | `/datasets/{id}/limpeza/desfazer` | — | `{n_linhas}` | 03 |
| GET | `/datasets/{id}/colunas/{col}/analise` | `?classes=` | `Analise` | 04–09 |
| GET | `/datasets/{id}/colunas/{col}/posicao` | `?valor=&tipo=quartil|decil|percentil` | `Posicao` | 06 |
| GET | `/datasets/{id}/bivariada` | `?x=&y=` | `Bivariada` | 10 |
| GET | `/datasets/{id}/bivariada/prever` | `?x=&y=&valor=` | `{y_previsto, extrapolacao, frase}` | 10 |
| GET | `/datasets/{id}/correlacoes` | — | matriz + figura heatmap | 10 |
| POST | `/gerador/univariado` | ver spec 11 | `GeradoUni` | 11 |
| POST | `/gerador/bivariado` | ver spec 11 | `GeradoBi` | 11 |
| GET | `/gerador/{gid}/csv` | — | `text/csv` download | 11 |
| POST | `/gerador/{gid}/adotar` | `{modo, dataset_id?}` | `{dataset_id}` | 11 |
| GET | `/datasets/{id}/detector` | `?regras=R1,R2…` | `ResultadoDetector` | 12 |
| GET | `/datasets/{id}/relatorio` | `?colunas=&secoes=&offline=` | `text/html` | 13 |

## Contrato `Analise` (único para todos os tipos)
```json
{
  "coluna": "idade", "tipo": "continua", "n": 230, "n_faltantes": 3,
  "aplicavel": { "media": true, "acumulada": true, "separatrizes": true, "...": "..." },
  "nao_aplicavel": [{ "item": "moda_czuber", "motivo": "..." }],
  "frequencias": { "...": "spec 04" },
  "tendencia": { "...": "spec 05" },
  "separatrizes": { "...": "spec 06" },
  "dispersao": { "...": "spec 07" },
  "forma": { "...": "spec 09 (M2)" },
  "interpretacoes": ["Média e mediana próximas...", "..."],
  "formulas": [{ "nome": "Média", "latex": "\\bar{x}=\\frac{\\sum x_i}{n}", "texto": "x̄ = Σxᵢ / n" }],
  "figuras": { "principal": { "...": "plotly json" }, "boxplot": {}, "ogiva": {} }
}
```
O frontend renderiza só o que veio; nunca decide aplicabilidade.

## Erros
Todas as falhas → HTTP 4xx/5xx com `{codigo, mensagem, sugestao}` (spec 17). Validação Pydantic é traduzida para mensagens em português.

## Dev
CORS liberado para `http://localhost:5173`; Vite faz proxy de `/api` → `http://localhost:8000`.
