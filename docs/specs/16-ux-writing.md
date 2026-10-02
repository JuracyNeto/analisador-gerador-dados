# 16 — Redação de textos (UX writing)
Aplica-se a: avisos do detector, motivos de classificação, "não se aplica", interpretações, mensagens de erro, toasts. ADR 0005.

## Princípios
1. **Linguagem simples** (nível ensino médio). Jargão só nos detalhes técnicos.
2. **Tom neutro, sem acusação.** Nunca: "fraude", "falso", "manipulado", "errado". Usar: "fora do esperado", "suspeita", "chama atenção".
3. **Número com contexto:** "46% (o esperado seria cerca de 20%, 2,3× mais)" em vez de "46%".
4. **p-valor traduzido:** "chance de acontecer por acaso: menos de 1 em 1.000" (p < 0,001) · "cerca de 1 em 50" (p ≈ 0,02).
5. **Voz ativa, frases curtas** (≤ 25 palavras), primeira pessoa do plural para o sistema ("Encontramos…", "Removemos…").
6. **Toda mensagem negativa traz o próximo passo.**
7. **Divulgação progressiva:** o simples primeiro; o técnico recolhido.
8. **Formato pt-BR:** vírgula decimal, ponto de milhar, datas DD/MM/AAAA.

## Estrutura do aviso (8 partes)
| Parte | Regra | Exemplo (R4) |
|---|---|---|
| 1. Título | O que foi visto, ≤ 8 palavras, sem jargão | "Muitos valores redondos em *peso*" |
| 2. Severidade | Ícone + palavra + cor | ⚠️ Atenção |
| 3. Resumo | O quê + onde + quanto vs esperado (1 frase) | "46% dos valores terminam em 0 ou 5; em medições reais o esperado seria cerca de 20% (2,3× mais)." |
| 4. Por que chama atenção | Intuição da regra (1–2 frases) | "Quando números são inventados ou digitados de cabeça, as pessoas tendem a arredondar." |
| 5. Exemplo | Linhas e valores concretos + "Ver na tabela" | "Linhas 120 a 138: 70, 75, 80, 75, 70…" |
| 6. Pode ser normal se… | Explicação inocente | "…a balança só mede de 5 em 5 kg." |
| 7. O que fazer | Ação sugerida | "Confira a origem dessas linhas." |
| 8. Detalhes técnicos | Recolhido: medida, valor, limiar, teste, p, fórmula | "Teste binomial · p = 0,0003 · limiar p < 0,01" |

## Severidades
| Nível | Ícone | Palavra | Cor (token) | Quando |
|---|---|---|---|---|
| info | ℹ️ (círculo i) | Informativo | `--sev-info` (azul) | curiosidade, não indica problema |
| atencao | ⚠️ (triângulo) | Atenção | `--sev-atencao` (âmbar) | padrão incomum, vale conferir |
| alta | ⛔ (octógono) | Suspeita alta | `--sev-alta` (vermelho) | forte indício de inserção dirigida |

## Modelos por regra (resumo → por que → pode ser normal)
- **R1** "Um bloco de {k} linhas ({ini}–{fim}) tem média e desvio quase idênticos ao conjunto todo (diferença de {d}%)." → "Em dados reais, pedaços pequenos variam bastante; um bloco que 'bate' tudo pode ter sido colocado para alinhar as estatísticas." → "…o conjunto foi ordenado ou amostrado de forma sistemática."
- **R2** "A correlação geral entre *{x}* e *{y}* é {r}, mas a média dos blocos é só {rb}." → "Se poucos dados novos fazem a correlação subir muito, eles podem ter sido adicionados para 'puxar' a relação." → "…os blocos têm faixas de valores muito diferentes."
- **R3** "Em *{col}*, {pct}% dos valores têm casas decimais, mas {k} inteiros aparecem juntos (linhas {ini}–{fim})." → "Uma mudança de formato no meio dos dados pode indicar outra origem." → "…parte dos dados veio de outro instrumento."
- **R4** (acima)
- **R5** "Encontramos {k} linhas iguais (ou quase), {em_sequencia}." → "Cópias seguidas costumam surgir de 'copiar e colar'." → "…registros legítimos repetidos (ex.: mesma compra)."
- **R6** "Os dados depois de {data} {comportamento} em relação aos anteriores." → "Dados novos que copiam os antigos ou variam pouco demais podem ter sido inseridos." → "…houve mudança real no processo."
- **R7** "{k} valores de *{col}* estão muito longe dos demais (ex.: {v})." → "Valores extremos podem ser erros de digitação ou casos especiais." → "…são casos raros, mas reais."
- **R8** "Os primeiros dígitos de *{col}* não seguem o padrão natural (Lei de Benford)." → "Em muitos dados reais, o dígito 1 aparece no início ~30% das vezes; números inventados tendem a ser mais 'uniformes'." → "…os dados têm faixa limitada (ex.: idades, notas)."
- **R9** "O último dígito de *{col}* não está bem distribuído: o {d} aparece {pct}% das vezes (esperado 10%)." → "Medições reais têm o último dígito quase aleatório; pessoas evitam ou repetem certos dígitos." → "…o instrumento arredonda."
- **R10** "*{col}* parece uma curva Normal perfeita demais (assimetria {g1}, curtose {g2})." → "Dados reais quase nunca são tão perfeitos; isso é típico de números gerados por computador." → "…a amostra é grande e o fenômeno é realmente Normal."
- **R11** "A ordem dos valores de *{col}* segue um padrão ({padrao})." → "Em dados reais, a sequência costuma parecer aleatória." → "…os dados estão ordenados por tempo ou por outra coluna."

## Estado vazio e regras não aplicadas
- Sem avisos: "Nenhuma das 11 regras encontrou suspeitas. Isso não garante que os dados sejam reais, mas não vimos sinais comuns de dados artificiais."
- Não aplicada: "{regra} não verificada em *{col}*: {motivo}." Ex.: "precisa de 100 valores ou mais; a coluna tem 48."

## Outros textos
- "Não se aplica": "{medida} não se aplica a {tipo_legivel}: {motivo}."
- Erros: "{o que aconteceu}. {como resolver}." Ex.: "Não encontramos a coluna *peso*. Ela pode ter sido renomeada — recarregue a página."
- Toasts: verbo no passado + quantidade. "Limpeza aplicada: 12 linhas removidas."
