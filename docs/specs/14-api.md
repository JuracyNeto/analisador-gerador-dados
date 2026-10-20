# 14 — API (FastAPI)
Camada de apresentação: `router.py` + `schemas.py` de cada domínio; `app/main.py` registra tudo; erros em `app/core/` · Prefixo `/api` · Docs automáticas em `/docs`

## Endpoints
| Método | Rota | Corpo / query | Resposta | Spec |
|---|---|---|---|---|
| POST | `/datasets` | multipart `arquivo` + opções de leitura (`separador`, `decimal`, `codificacao`, `aba`, `linha_cabecalho`) | `{dataset_id, metadados, previa[20], colunas[]}` | 01 |
| GET | `/datasets/exemplos` | — | `ArquivoExemplo[] {arquivo, descricao}` (arquivos de demonstração, D124) | 12 |
| POST | `/datasets/exemplo` | `?arquivo=` (um dos de `GET /datasets/exemplos`; sem o campo, `pesquisa_saude.txt`, D52) | igual ao `POST /datasets`; fora da lista → 404 `EXEMPLO_NAO_ENCONTRADO` | 01 |
| POST | `/datasets/{id}/leitura` | `{separador?, decimal?, codificacao?, aba?, linha_cabecalho?}` (vazio = detectar tudo de novo) | igual ao `POST /datasets`, com o mesmo `dataset_id`; tipos e limpeza recomeçam (D88) | 01 |
| GET | `/datasets/{id}` | `?pagina=&tamanho=&versao=original|atual` | `{resumo, versao, pagina, tamanho, total_paginas, linhas}` (D55); `resumo` traz `opcoes_leitura` e `tem_ajustes` (tipos corrigidos ou limpeza aplicada) | — |
| DELETE | `/datasets/{id}` | — | 204 | — |
| GET | `/datasets/{id}/colunas` | — | `TipoColuna[]` | 02 |
| PATCH | `/datasets/{id}/colunas/{col}` | `{tipo, categorias_ordem?}` | `TipoColuna` | 02 |
| GET | `/datasets/{id}/diagnostico` | `?limites={col:{min,max}}` | `Diagnostico` | 03 |
| POST | `/datasets/{id}/limpeza` | `{acoes[]}` | `{log[], n_linhas, colunas[]}` | 03 |
| POST | `/datasets/{id}/limpeza/desfazer` | — | `{n_linhas}` | 03 |
| GET | `/datasets/{id}/colunas/{col}/analise` | `?classes=&sucesso=&tentativas=` (`tentativas` ≥ 1: nº de tentativas da Binomial; menor que o máximo observado → 400 `TENTATIVAS_INVALIDAS`) | `Analise` | 04–09 |
| GET | `/datasets/{id}/colunas/{col}/posicao` | `?valor=&tipo=quartil|decil|percentil` | `Posicao` | 06 |
| GET | `/datasets/{id}/bivariada` | `?x=&y=` | `Bivariada` (r, teste t, Spearman, reta, R², Sₑ, faixa de X, figuras) | 10 |
| GET | `/datasets/{id}/bivariada/prever` | `?x=&y=&valor=` | `Previsao {x, y_previsto, extrapolacao, faixa_x, frase, aviso}` | 10 |
| GET | `/datasets/{id}/correlacoes` | — | `MatrizCorrelacao {colunas, valores, resumo, figura}` | 10 |
| POST | `/gerador/univariado` | `PedidoUnivariado` (spec 11) | `Gerado` (201; com `formulas` do método, como a análise, D152) | 11 |
| POST | `/gerador/bivariado` | `PedidoBivariado` (spec 11) | `Gerado` (201) | 11 |
| GET | `/gerador/{gid}` | — | `Gerado` | 11 |
| GET | `/gerador/origem` | `?dataset_id=&coluna=` | `ResumoOrigem {coluna, tipo, n, media, desvio, minimo, maximo, sucesso, fracasso, chance, so_preservar}` | 11 |
| GET | `/gerador/origem-par` | `?dataset_id=&x=&y=` | `ResumoOrigemPar {x, y, n, media_x, media_y, desvio_x, desvio_y, r}` | 11 |
| GET | `/gerador/{gid}/csv` | — | `text/csv` download (`;` e vírgula decimal) | 11 |
| POST | `/gerador/{gid}/adotar` | `{modo: novo \| anexar, dataset_id?}` | `Adotado {dataset_id, nome_arquivo, n_linhas, modo}` (201) | 11 |
| GET | `/datasets/{id}/detector` | `?regras=R1,R2…` (códigos separados por vírgula; sem o campo = todas; código desconhecido → 422) | `ResultadoDetector {resumo, avisos: AvisoDetector[], nao_aplicadas[]}`; `AvisoDetector.figura` traz o gráfico dos detalhes em R1, R8 e R9 (nulo nas demais, D123) | 12 |
| GET | `/datasets/{id}/linhas` | `?de=&ate=` (números das linhas, como na prévia; inclusive; no máximo 200, senão 400 `INTERVALO_INVALIDO`) | `LinhaDados[]` da versão atual (linhas removidas na limpeza não voltam) | 12 |
| GET | `/datasets/{id}/relatorio` | `?colunas=&secoes=&gerado=&offline=` (`secoes`: leitura, tipos, limpeza, analises, distribuicoes, bivariada, gerador, detector, formulas; padrão = as 9; outra → 422; `gerado`: id da geração mostrada na seção Gerador; sem ele, ou com a geração descartada, a seção sai sem erro, D141) | `text/html` | 13 |

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
  "forma": { "...": "spec 09: assimetria, curtose, ajustes normal/binomial, figuras (null em nominal/ordinal)" },
  "interpretacoes": ["Média e mediana próximas...", "..."],
  "formulas": [{ "chave": "media", "nome": "Média", "latex": "\\bar{x}=\\frac{\\sum x_i}{n}", "texto": "x̄ = Σxᵢ / n" }],
  "figuras": [{ "id": "principal", "rotulo": "Histograma", "titulo": "...", "resumo": "...", "porque": "...", "recomendado": true, "dados": { "...": "plotly json" } }]
}
```
Cada medida (`Medida {valor, aplicavel, motivo, calculo, interpretacao, formula}`) traz em `formula` a `chave` da sua fórmula em `formulas[]` (D66). O frontend renderiza só o que veio; nunca decide aplicabilidade.

## Erros
Bivariada (spec 10): `COLUNA_NAO_NUMERICA`, `COLUNAS_IGUAIS`, `POUCOS_PARES`, `SEM_VARIACAO` (400). Linhas por intervalo (drawer do detector): `INTERVALO_INVALIDO` (400): Peça no máximo 200 linhas, com "de" menor ou igual a "até". Exemplos: `EXEMPLO_NAO_ENCONTRADO` (404): Não encontramos o exemplo {arquivo}. Gerador (spec 11): `GERADO_NAO_ENCONTRADO` (404), `MODO_NAO_APLICAVEL`, `PARAMETROS_INCOMPLETOS`, `COLUNA_NAO_GERAVEL` e `COLUNAS_INCOMPATIVEIS` (400). `COLUNA_IGNORADA` (400) vale para os tipos auxiliares: "A coluna {col} é um identificador e fica fora das análises." / "A coluna {col} tem datas e fica fora das análises." (D90). `TipoVariavel` = `nominal`, `ordinal`, `discreta`, `continua`, `binaria`, `identificador`, `data`.

Todas as falhas → HTTP 4xx/5xx com `{codigo, mensagem, sugestao}` (spec 17). Validação Pydantic é traduzida para mensagens em português.

## Dev
CORS liberado para `http://localhost:5173`; Vite faz proxy de `/api` → `http://localhost:8000`.
