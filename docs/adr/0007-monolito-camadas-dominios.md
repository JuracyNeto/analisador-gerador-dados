# 0007 — Monólito em camadas com separação por domínio
- **Status:** Aceito (substitui a estrutura de pastas do ADR 0002; o princípio "domínio sem framework" continua)
- **Data:** 02/10/2026

## Contexto
O ADR 0002 propunha um pacote único `analisador/` + `api/`. Com 6 áreas funcionais (datasets, análise, gráficos, gerador, detector, relatório) e 2–4 pessoas trabalhando em paralelo, um pacote plano cresce sem fronteiras claras. Exigência do projeto: arquitetura monolítica em camadas com separação de domínios e limites rígidos de tamanho/complexidade (`docs/padroes-codigo.md`).

## Opções consideradas
1. Pacote plano por tipo de arquivo (`routers/`, `services/`, `schemas/`) — camadas claras, domínios misturados.
2. **Monólito modular: `dominios/<nome>/` com camadas internas** (`router`, `schemas`, `servico`, módulos de domínio, `repositorio`).
3. Microsserviços — fora de proporção (YAGNI).

## Decisão
Opção 2. Um processo FastAPI (`app/main.py`), com:
- `core/` (config, erros, handlers), `compartilhado/` (utils sem regra de negócio), `dominios/` (datasets, analise, graficos, gerador, detector, relatorio).
- Dependência: `router → servico → domínio/repositório`; domínios só se comunicam via `servico.py` (fachada).
- Módulos de domínio são puros (pandas/numpy/scipy), sem FastAPI/Pydantic.
- Contratos verificados por `import-linter` no CI.

## Consequências
- (+) Cada membro do grupo é dono de um domínio; fronteiras explícitas reduzem conflitos.
- (+) Arquivos pequenos por construção (limite de 500 linhas).
- (−) Mais arquivos e alguma cerimônia (`servico.py` mesmo quando fino). Aceitável pelo ganho de clareza.
