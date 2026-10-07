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
2. **Separador:** entre `; , \t |` e espaço múltiplo, o que aparece o mesmo número de vezes em ≥ 90% das 50 primeiras linhas e gera mais colunas (D53). Linhas de título acima da tabela não seguem a contagem: sem separador constante, tenta de novo a partir da 2ª, 3ª… linha (até a 10ª).
3. **Linha do cabeçalho** (TXT/CSV/TSV/XLSX, D86): entre as 10 primeiras linhas não vazias, a 1ª com só textos únicos, na largura da tabela, que não aparecem como valor na própria coluna. As linhas acima dela (título, linhas vazias ou incompletas) ficam de fora. Se uma linha completa que não é cabeçalho vier antes, o arquivo não tem cabeçalho → `col_1..col_n`. A numeração é a do arquivo (linhas vazias contam; no XLSX, a linha da planilha). No XLSX, colunas vazias em toda a aba saem antes da leitura.
4. **Decimal:** entre os números com `,` ou `.`, vírgula se ≥ 80% casam o padrão `1.234,5`; sem números decimais, `;` → vírgula. Padrão: `^\-?\d{1,3}(\.\d{3})*(,\d+)?$|^\-?\d+,\d+$` → decimal `,` e milhar `.`.
5. **Nomes de colunas:** `strip()`, espaços múltiplos → um; duplicados recebem sufixo `_2`.
6. **Valores faltantes reconhecidos:** vazio, `NA`, `N/A`, `NaN`, `null`, `None`, `-`, `?`, `—`.

## Entrada / saída
- Entrada: bytes do arquivo + nome + opções opcionais (`separador`, `decimal`, `codificacao`, `aba`, `linha_cabecalho` — nº da linha; `0` = sem cabeçalho) que sobrescrevem a detecção.
- Saída: `DataFrame` + `MetadadosLeitura {formato, codificacao, separador, decimal, linha_cabecalho, n_linhas, n_colunas, abas[], avisos[], motivos{}, linhas_iniciais[]}` — `motivos` explica cada detecção (formato, codificação, separador, decimal, cabeçalho; D53). `linhas_iniciais` traz as 12 primeiras linhas do arquivo como estão escritas (`{numero, celulas[]}`; vazia = sem células), para conferir e escolher a linha do cabeçalho. No JSON, `linha_cabecalho` é nulo (os nomes vêm das chaves).
- A API devolve `dataset_id`, metadados e prévia das 20 primeiras linhas.

## Erros (mensagens conforme spec 16)
| Código | Quando | Mensagem |
|---|---|---|
| `ARQUIVO_VAZIO` | 0 linhas | "O arquivo está vazio." |
| `FORMATO_NAO_SUPORTADO` | extensão desconhecida | "Este tipo de arquivo não é aceito. Use TXT, CSV, TSV, XLSX ou JSON." |
| `UMA_COLUNA` | só 1 coluna detectada e linhas contêm `;`/`,`/tab | aviso (não erro): "Encontramos só uma coluna. O separador pode estar errado — tente escolher outro." |
| `ARQUIVO_GRANDE` | > 50 MB | "O arquivo passa de 50 MB." |
| `LINHA_CABECALHO_INVALIDA` | linha escolhida vazia ou além do fim do arquivo | "A linha N não existe no arquivo ou está vazia." |
| `JSON_INVALIDO` | parse falhou | "Não conseguimos ler este JSON. Verifique se é uma lista de registros." |

## Testes
Um arquivo de exemplo por formato em `backend/tests/fixtures/`; casos: `;` + vírgula decimal, tab, sem cabeçalho, título acima do cabeçalho (`com_titulo.csv` e XLSX), latin-1 com acentos, JSON aninhado.
