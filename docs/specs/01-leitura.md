# 01 — Leitura de arquivos
Domínio: `app/dominios/datasets/` (`leitura.py`) · Endpoint: `POST /api/datasets`

## Formatos
| Formato | Como |
|---|---|
| TXT (obrigatório) | Texto delimitado; separador detectado |
| CSV | `,` ou `;` |
| TSV | tab |
| XLSX | `openpyxl`; primeira aba por padrão, opção de escolher a aba |
| JSON | lista de objetos (`[{...}]`) ou `{coluna: [valores]}`; objetos aninhados → `pandas.json_normalize` |

## Detecção automática
1. **Codificação:** tentar `utf-8-sig` → `utf-8` → `cp1252` → `latin-1`.
2. **Separador:** entre `; , \t |` e espaço múltiplo, o que aparece o mesmo número de vezes em ≥ 90% das 50 primeiras linhas e gera mais colunas (D53).
3. **Cabeçalho:** a 1ª linha tem só textos únicos que não aparecem como valor na própria coluna; senão `col_1..col_n`.
4. **Decimal:** entre os números com `,` ou `.`, vírgula se ≥ 80% casam o padrão `1.234,5`; sem números decimais, `;` → vírgula. Padrão: `^\-?\d{1,3}(\.\d{3})*(,\d+)?$|^\-?\d+,\d+$` → decimal `,` e milhar `.`.
5. **Nomes de colunas:** `strip()`, espaços múltiplos → um; duplicados recebem sufixo `_2`.
6. **Valores faltantes reconhecidos:** vazio, `NA`, `N/A`, `NaN`, `null`, `None`, `-`, `?`, `—`.

## Entrada / saída
- Entrada: bytes do arquivo + nome + opções opcionais (`separador`, `decimal`, `codificacao`, `aba`, `tem_cabecalho`) que sobrescrevem a detecção.
- Saída: `DataFrame` + `MetadadosLeitura {formato, codificacao, separador, decimal, tem_cabecalho, n_linhas, n_colunas, abas[], avisos[], motivos{}}` — `motivos` explica cada detecção (formato, codificação, separador, decimal, cabeçalho; D53).
- A API devolve `dataset_id`, metadados e prévia das 20 primeiras linhas.

## Erros (mensagens conforme spec 16)
| Código | Quando | Mensagem |
|---|---|---|
| `ARQUIVO_VAZIO` | 0 linhas | "O arquivo está vazio." |
| `FORMATO_NAO_SUPORTADO` | extensão desconhecida | "Este tipo de arquivo não é aceito. Use TXT, CSV, TSV, XLSX ou JSON." |
| `UMA_COLUNA` | só 1 coluna detectada e linhas contêm `;`/`,`/tab | aviso (não erro): "Encontramos só uma coluna. O separador pode estar errado — tente escolher outro." |
| `ARQUIVO_GRANDE` | > 50 MB | "O arquivo passa de 50 MB." |
| `JSON_INVALIDO` | parse falhou | "Não conseguimos ler este JSON. Verifique se é uma lista de registros." |

## Testes
Um arquivo de exemplo por formato em `backend/tests/fixtures/`; casos: `;` + vírgula decimal, tab, sem cabeçalho, latin-1 com acentos, JSON aninhado.
