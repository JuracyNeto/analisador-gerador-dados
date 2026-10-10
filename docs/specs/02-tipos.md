# 02 — Classificação de tipos de variável
Domínio: `app/dominios/datasets/` (`classificacao.py`) · Endpoints: `GET /api/datasets/{id}/colunas`, `PATCH /api/datasets/{id}/colunas/{col}` · ADR 0006

## Saída por coluna
`TipoColuna {coluna, tipo, motivo, origem: "auto"|"manual", n_validos, n_faltantes, n_distintos, exemplos[5], categorias_ordem[] (ordinal)}`

## Regras (ordem importa; a primeira que casar vence)
Considerar só valores não faltantes. Antes, tentar converter texto para número com o decimal detectado (spec 01).

Coluna de texto conta como numérica se ≥ 90% dos valores válidos viram número (`LIMIAR_NUMERICO = 0,9`, D48); os demais aparecem como "tipo misto" na limpeza.

| # | Condição | Tipo | Motivo (modelo) |
|---|---|---|---|
| 0 | ≥ 90% dos valores válidos (`LIMIAR_DATA = 0,9`) num mesmo formato de data ou hora (abaixo), ou células de data/hora do XLSX; só para colunas que não são numéricas (D90) | `data` (auxiliar) | "Datas no formato DD/MM/AAAA (ex.: 07/10/2026)." / "Datas no formato AAAA-MM-DD (ex.: …)." / "Datas com horário (ex.: 07/10/2026 08:30)." / "Horários (ex.: 08:30)." / "Datas da planilha (ex.: …)." — no XLSX, só horários usam "Horários", só datas com horário usam "Datas com horário" e o resto "Datas da planilha" (D107) |
| 1 | Nome casa `^(id|cod|codigo|código|cpf|cnpj|cep|telefone|fone|matricula|matrícula)\b` (sem acento/caixa) **ou** (não numérico contínuo e ≥ 95% únicos com n ≥ 20) | `identificador` | "Parece um código: {pct}% dos valores são únicos." / "O nome da coluna indica um código ({nome})." |
| 2 | Exatamente 2 valores distintos | `binaria` | "Tem só dois valores: {a} e {b}." |
| 3 | Texto e o conjunto de valores (normalizado) está contido em uma escala do dicionário ordinal | `ordinal` | "Os valores seguem uma escala conhecida: {escala}." |
| 4 | Texto (demais) | `nominal` | "São categorias sem ordem natural ({k} categorias)." |
| 5 | Numérico, todos inteiros, distintos ≤ `LIMIAR_DISCRETA` (30) | `discreta` | "Números inteiros com {k} valores diferentes (contagem)." |
| 6 | Numérico com decimais, ou inteiros com distintos > 30 | `continua` | "Números com casas decimais." / "Inteiros com muitos valores diferentes ({k}); tratada como contínua." |
| — | 0 valores válidos | `identificador` (vazia) | "A coluna está vazia; foi ignorada." |

A regra 0 roda logo depois da coluna vazia: datas únicas por linha não viram "código".

## Datas e horários (tipo auxiliar `data`, D90–D92)
- Formatos explícitos (sem `pd.to_datetime` livre, que tomaria códigos e números por datas), em `app/compartilhado/datas.py`: `DD/MM/AAAA` (separador `/`, `-` ou `.`; dia e mês com 1 ou 2 dígitos), `AAAA-MM-DD`, qualquer um dos dois seguido de ` HH:MM[:SS]` (ou `T` no ISO) e só `HH:MM[:SS]`. Datas impossíveis (31/02, 25:00) não contam.
- Dia primeiro (padrão brasileiro); mês primeiro (`MM/DD/AAAA`) só quando nenhum 1º campo passa de 12 e algum 2º campo passa (D91).
- Colunas `data` ficam fora das análises (univariada, bivariada e relatório por coluna), como o identificador; aparecem na tela Variáveis com o chip "Data". O detector (R6, M3) usa as datas.
- Fora do escopo: separar mês, ano ou dia da semana em colunas novas; datas por extenso.

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
`PATCH` com `{tipo, categorias_ordem?}`. Validações: `continua`/`discreta` exigem coluna numérica (erro `TIPO_INCOMPATIVEL`: "Esta coluna tem textos; não pode ser numérica."); `data` exige ≥ 90% de datas reconhecíveis (`TIPO_INCOMPATIVEL`: "Esta coluna não tem datas ou horários que dê para reconhecer.") (D92). Ordinal sem `categorias_ordem` usa ordem alfabética e avisa.

## Configuração
`LIMIAR_DISCRETA = 30`, `LIMIAR_UNICOS_ID = 0.95`, `LIMIAR_NUMERICO = 0.9`, `LIMIAR_DATA = 0.9` em `app/core/config.py`.
