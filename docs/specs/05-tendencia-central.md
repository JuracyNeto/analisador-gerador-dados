# 05 — Medidas de tendência central
Domínio: `app/dominios/analise/` (`tendencia.py`)

## Aplicabilidade
| Tipo | Média | Mediana | Moda |
|---|---|---|---|
| Nominal | — | — | ✔ |
| Binária | proporção p (se 0/1 ou mapeada) | — | ✔ |
| Ordinal | — | ✔ (categoria) | ✔ |
| Discreta | ✔ | ✔ | ✔ |
| Contínua | ✔ | ✔ | ✔ bruta + Czuber |

Itens "—" retornam `{aplicavel: false, motivo}`. Ex.: "Média não se aplica a categorias sem número (nominal)."

## Fórmulas
- Média: **x̄ = Σxᵢ / n**
- Mediana: valor central dos dados ordenados; n par → média dos dois centrais
- Mediana ordinal: categoria que contém a posição (n+1)/2 na ordem da escala
- Moda: valor(es) de maior frequência. Classificação: amodal (todas iguais), unimodal, bimodal, multimodal
- Proporção (binária): **p = nº de "sucessos" / n** (sucesso = categoria escolhida pelo usuário; padrão: `1`, `sim`, `s`, `true`, ou a menos frequente; a API aceita `?sucesso=` para escolher outra)
- Moda de Czuber (dados em classes): **Mo = Lᵢ + [Δ₁ / (Δ₁ + Δ₂)] · h**, onde Δ₁ = fᵢ − fᵢ₋₁ e Δ₂ = fᵢ − fᵢ₊₁ da classe modal

## Interpretação (texto automático)
- Se |x̄ − Md| / s < 0,1 → "Média e mediana próximas: a distribuição parece simétrica."
- Se x̄ > Md → "Média maior que a mediana: há valores altos puxando a média (assimetria à direita)."
- Se x̄ < Md → análogo à esquerda.
