# 04 — Tabelas de frequência
Domínio: `app/dominios/analise/` (`frequencias.py`)

## Por tipo
| Tipo | Linhas da tabela | Colunas |
|---|---|---|
| Nominal | cada categoria, ordenada por fᵢ desc | fᵢ, frᵢ, fr% |
| Binária | as 2 categorias | fᵢ, frᵢ, fr% |
| Ordinal | categorias na ordem da escala | fᵢ, frᵢ, fr%, Fᵢ, Frᵢ |
| Discreta | cada valor, ordem crescente | fᵢ, frᵢ, fr%, Fᵢ, Frᵢ |
| Contínua | classes (intervalos) | limite inferior, limite superior, ponto médio xᵢ, fᵢ, frᵢ, fr%, Fᵢ, Frᵢ |

Linha final "Total" (n, 1, 100%). Acumulada **não** se aplica a nominal/binária (motivo: "categorias sem ordem; acumular não tem significado").

## Fórmulas
- Frequência absoluta: fᵢ = nº de ocorrências
- Relativa: frᵢ = fᵢ / n
- Acumulada: Fᵢ = Σⱼ≤ᵢ fⱼ ; relativa acumulada Frᵢ = Fᵢ / n

## Caso contínuo (classes)
- Número de classes (Sturges): **k = ⌈1 + 3,322 · log₁₀ n⌉** (opção do usuário: 3 a 30)
- Amplitude total: AT = máx − mín
- Amplitude da classe: **h = AT / k**, arredondada para cima na casa decimal dos dados
- Classes `[Lᵢ, Lᵢ + h)`; a última é fechada `[Lₖ, Lₖ + h]`
- Ponto médio: xᵢ = (Lᵢ + Lᵢ₊₁) / 2
- Notação de exibição: `10 ⊢ 20`

## Saída
`TabelaFrequencia {tipo, linhas[], total, k?, h?, metodo_classes?, formulas[]}`
