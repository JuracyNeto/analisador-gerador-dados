# 0006 — Classificação automática de tipos
- **Status:** Aceito
- **Data:** 02/10/2026

## Contexto
O enunciado exige que o programa classifique cada coluna e, a partir disso, defina cálculos e gráficos. Distinguir ordinal × nominal e código numérico × quantidade é ambíguo por heurística.

## Decisão
Regras ordenadas (primeira que casar vence), cada uma gera um **motivo** legível:
1. Identificador (auxiliar, excluído).
2. Binária (2 valores distintos).
3. Texto ordinal (dicionário de escalas conhecidas).
4. Texto nominal.
5. Inteiro com ≤ 30 distintos → discreta.
6. Decimal, ou inteiro com > 30 distintos → contínua.

O usuário pode sobrescrever qualquer tipo e definir/reordenar categorias ordinais. Detalhes em `docs/specs/02-tipos.md`.

## Consequências
- (+) Automático e explicável; erros corrigíveis em 1 clique.
- (−) O limiar 30 é arbitrário; fica configurável.
- (−) O dicionário ordinal não cobre tudo; usuário corrige manualmente.
