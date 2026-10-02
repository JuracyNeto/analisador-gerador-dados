# 0004 — Estado em memória por dataset_id
- **Status:** Aceito
- **Data:** 02/10/2026

## Contexto
Uso local, um usuário, arquivos de até ~100 mil linhas. Várias telas operam sobre o mesmo conjunto.

## Decisão
`app/dominios/datasets/repositorio.py` (padrão Repositório, injetado via `Depends`) mantém um dicionário `dataset_id (uuid4) → Dataset`, onde `Dataset` guarda: nome do arquivo, `original: DataFrame`, `atual: DataFrame` (após limpeza), `tipos: dict[col, TipoColuna]`, `log_limpeza: list`, `criado_em`. Resultados do gerador ficam em `gerado_id → DataFrame` até serem adotados ou descartados. Limite: 20 datasets; o mais antigo é descartado.

## Consequências
- (+) Zero infraestrutura; rápido.
- (−) Reiniciar o servidor perde os dados. Mitigação: erro amigável "Sua sessão expirou. Envie o arquivo novamente." e o frontend guarda o nome do último arquivo para facilitar o reenvio.
- (−) Não serve para multiusuário/hospedagem — fora do escopo.
