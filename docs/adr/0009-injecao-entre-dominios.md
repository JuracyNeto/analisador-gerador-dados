# 0009 — Injeção de serviços entre domínios
- **Status:** Aceito
- **Data:** 05/10/2026

## Contexto
Domínios conversam só pela fachada `servico.py` (ADR 0007), e o `servico` não pode importar FastAPI. Mesmo assim, o repositório em memória precisa ser único por processo e trocável nos testes (`dependency_overrides`), e o domínio `analise` precisa do `datasets`.

## Opções consideradas
1. Funções soltas no `servico` lendo um repositório global.
2. `Depends` dentro do `servico`.
3. Classe de fachada por domínio + provedor sem FastAPI; o `router` monta as dependências.

## Decisão
Opção 3. Cada domínio expõe `Servico<Dominio>` (fachada com os casos de uso) e `obter_servico_<dominio>()` com `@lru_cache` em `servico.py`. Quem depende de outro domínio recebe a fachada no construtor. Só o `router.py` usa `Depends`, por exemplo `def _servico(datasets: Annotated[ServicoDatasets, Depends(obter_servico_datasets)]) -> ServicoAnalise`.

## Consequências
- (+) `servico` continua sem FastAPI e testável com objetos comuns.
- (+) Um único override (`obter_servico_datasets`) isola o estado em todos os testes de API.
- (−) Um pouco de código de montagem em cada router. Aceitável.
