# 02 — Classificação de tipos de variável
Domínio: `app/dominios/datasets/` (`classificacao.py`) · Endpoints: `GET /api/datasets/{id}/colunas`, `PATCH /api/datasets/{id}/colunas/{col}` · ADR 0006

## Saída por coluna
`TipoColuna {coluna, tipo, motivo, origem: "auto"|"manual", n_validos, n_faltantes, n_distintos, exemplos[5], categorias_ordem[] (ordinal)}`

## Regras (ordem importa; a primeira que casar vence)
Considerar só valores não faltantes. Antes, tentar converter texto para número com o decimal detectado (spec 01).

Coluna de texto conta como numérica se ≥ 90% dos valores válidos viram número (`LIMIAR_NUMERICO = 0,9`, D48); os demais aparecem como "tipo misto" na limpeza.

| # | Condição | Tipo | Motivo (modelo) |
|---|---|---|---|
| 1 | Nome casa `^(id|cod|codigo|código|cpf|cnpj|cep|telefone|fone|matricula|matrícula)\b` (sem acento/caixa) **ou** (não numérico contínuo e ≥ 95% únicos com n ≥ 20) | `identificador` | "Parece um código: {pct}% dos valores são únicos." / "O nome da coluna indica um código ({nome})." |
| 2 | Exatamente 2 valores distintos | `binaria` | "Tem só dois valores: {a} e {b}." |
| 3 | Texto e o conjunto de valores (normalizado) está contido em uma escala do dicionário ordinal | `ordinal` | "Os valores seguem uma escala conhecida: {escala}." |
| 4 | Texto (demais) | `nominal` | "São categorias sem ordem natural ({k} categorias)." |
| 5 | Numérico, todos inteiros, distintos ≤ `LIMIAR_DISCRETA` (30) | `discreta` | "Números inteiros com {k} valores diferentes (contagem)." |
| 6 | Numérico com decimais, ou inteiros com distintos > 30 | `continua` | "Números com casas decimais." / "Inteiros com muitos valores diferentes ({k}); tratada como contínua." |
| — | 0 valores válidos | `identificador` (vazia) | "A coluna está vazia; foi ignorada." |

Datas (`datetime` detectado via `pd.to_datetime` em ≥ 90% dos valores) → marcadas `data` (auxiliar), usadas apenas pelo detector R6.

## Dicionário ordinal (normalizar: minúsculas, sem acento, trim)
- muito baixo < baixo < medio < alto < muito alto
- pessimo < ruim < regular < bom < otimo / excelente
- discordo totalmente < discordo < neutro < concordo < concordo totalmente
- nunca < raramente < as vezes < frequentemente < sempre
- pp < p < m < g < gg < xg
- fundamental incompleto < fundamental < medio incompleto < medio < superior incompleto < superior < pos-graduacao / pos (D51)
- 1º/2º/3º… e 1°… (ordinal numérico por extenso)
- pequeno < medio < grande
- leve < moderado < grave

## Ajuste manual
`PATCH` com `{tipo, categorias_ordem?}`. Validações: `continua`/`discreta` exigem coluna numérica (erro `TIPO_INCOMPATIVEL`: "Esta coluna tem textos; não pode ser numérica."). Ordinal sem `categorias_ordem` usa ordem alfabética e avisa.

## Configuração
`LIMIAR_DISCRETA = 30`, `LIMIAR_UNICOS_ID = 0.95`, `LIMIAR_NUMERICO = 0.9` em `app/core/config.py`.
