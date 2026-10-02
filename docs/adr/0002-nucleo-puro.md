# 0002 — Núcleo estatístico sem framework
- **Status:** Substituído parcialmente por [0007](0007-monolito-camadas-dominios.md) (estrutura de pastas); princípio do núcleo puro mantido
- **Data:** 02/10/2026

## Contexto
A nota depende principalmente da corretude estatística (40%). Os cálculos precisam ser testáveis isoladamente e reaproveitados pela API e pelo relatório.

## Decisão
`backend/analisador/` contém apenas funções puras sobre `pandas.DataFrame`/`Series` e retorna dicionários/dataclasses serializáveis. Não importa FastAPI, Pydantic nem nada de HTTP. `backend/api/` só valida entrada, busca o DataFrame no store, chama o núcleo e serializa.

Módulos: `leitura`, `tipos`, `limpeza`, `frequencias`, `descritiva` (tendência, separatrizes, dispersão), `distribuicoes` (ajustes, assimetria, curtose), `correlacao`, `graficos`, `gerador`, `detector/` (uma regra por arquivo + `textos.py` + registro), `relatorio`.

## Consequências
- (+) Testes unitários sem servidor; cada membro do grupo trabalha em um módulo.
- (+) Fácil explicar no relatório "onde está cada fórmula".
- (−) Uma camada de conversão a mais (núcleo → schema). Aceitável.
