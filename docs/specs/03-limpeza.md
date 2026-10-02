# 03 — Limpeza de dados
Domínio: `app/dominios/datasets/` (`limpeza.py`) · Endpoints: `GET /api/datasets/{id}/diagnostico`, `POST /api/datasets/{id}/limpeza`

## Diagnóstico (não altera nada)
| Problema | Como detecta | Por coluna/linha |
|---|---|---|
| Faltantes | valores nulos após leitura | contagem e % por coluna; linhas afetadas |
| Duplicados | `df.duplicated(keep="first")` linhas inteiras | índices das cópias |
| Fora de faixa | numéricas: fora de [Q1 − 1,5·IQR, Q3 + 1,5·IQR] **ou** fora de limites informados pelo usuário (`min`, `max`) | índices e valores |
| Inconsistência de texto | mesma categoria com grafias diferentes após normalizar (caixa, acento, espaços): "SP", "sp ", "Sp" | grupos sugeridos para unificar |
| Tipo misto | coluna numérica com alguns textos (ex.: "12", "doze") | valores não convertidos |

## Ações disponíveis
| Problema | Ações |
|---|---|
| Faltantes | `remover_linhas` · `preencher_media` (contínua/discreta) · `preencher_mediana` · `preencher_moda` (qualquer) · `preencher_valor` · `manter` |
| Duplicados | `remover` · `manter` |
| Fora de faixa | `remover_linhas` · `limitar` (winsorizar no limite) · `marcar_faltante` · `manter` |
| Inconsistência de texto | `unificar` (para a grafia mais frequente) · `manter` |
| Tipo misto | `marcar_faltante` · `manter` |

Ações são aplicadas sobre `atual` (ADR 0004) em ordem: inconsistência → tipo misto → duplicados → fora de faixa → faltantes. `original` nunca é alterado; existe "Desfazer tudo" (restaura `atual = original`).

## Log
Cada ação gera `{acao, coluna, linhas_afetadas, antes_exemplo, depois_exemplo, quando}` e uma frase: "Removemos 12 linhas duplicadas." / "Preenchemos 5 valores faltantes de *idade* com a mediana (34)." O log vai para o relatório.

## Regras
- Preencher com média só para numéricas; ordinal/nominal só moda.
- Após limpeza, reclassificar tipos apenas das colunas cujo conteúdo mudou e que estão com `origem="auto"`.
