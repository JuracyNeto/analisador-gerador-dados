# 00 — Visão geral

## Resumo
- **O quê:** aplicação web local (FastAPI + React) que lê um conjunto de dados, classifica variáveis, limpa, analisa estatisticamente, gera gráficos e relatório, sintetiza dados artificiais e detecta suspeitas de dados artificiais.
- **Por quê:** trabalho em grupo de Estatística (60% da nota): 40% análise, 10% gerador, 10% detector.
- **Para quem:** o grupo (2–4 alunos) opera e apresenta; o professor avalia por demonstração, prints e relatório.
- **Prazo:** final em 08/12/2026 (ver `roadmap.md`).

## Fluxo do usuário (8 etapas)
1. Importar → 2. Variáveis → 3. Limpeza → 4. Análise univariada → 5. Bivariada → 6. Gerador → 7. Detector → 8. Relatório

## Requisitos não funcionais / premissas
| Tema | Premissa |
|---|---|
| Execução | Local (`uvicorn` + `vite`), 1 usuário por vez |
| Escala | Até ~100 mil linhas × 50 colunas; arquivo ≤ 50 MB |
| Desempenho | Análise de uma coluna < 2 s; detector completo < 10 s para 10 mil linhas |
| Segurança | Sem login; dados ficam na máquina; sem dados sensíveis |
| Disponibilidade | Não aplicável (local); reinício perde estado (ADR 0004) |
| Acessibilidade | WCAG 2.1 AA: contraste, foco visível, não depender só de cor, teclado |
| Idioma | Interface, código e docs em português; números no formato pt-BR (vírgula decimal) |
| Manutenção | Núcleo modular, 1 spec por módulo, testes por módulo, CI |

## Fora do escopo
Login, banco de dados, multiusuário, hospedagem pública, machine learning, regressão múltipla, séries temporais avançadas, seção "uso de IA" no relatório.

## Tipos de variável
`nominal`, `ordinal`, `discreta`, `continua`, `binaria` + auxiliar `identificador` (excluído da análise).

## Convenções estatísticas
- Variância e DP amostrais (n−1) por padrão; populacional exibida ao lado.
- Separatrizes por interpolação linear (`numpy.quantile`, método `linear`).
- Nível de significância padrão α = 0,05 (detector usa 0,01 para reduzir falsos positivos).
- Arredondamento de exibição: 4 casas significativas; valores internos sem arredondar.
