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
- **R1** título "Bloco alinhado ao restante dos dados em *{col}*"; "Um bloco de {k} linhas ({ini}–{fim}) tem média e desvio quase idênticos aos do restante dos dados (diferença de {d}%)." (abaixo de 0,01%: "diferença de menos de 0,01%"; o restante são as linhas fora do bloco, D142; {k} é o tamanho do trecho: o das janelas ou o do fim do arquivo, D148) → "Em dados reais, pedaços pequenos variam bastante; um bloco que 'bate' tudo pode ter sido colocado para alinhar as estatísticas." → "…o conjunto foi ordenado ou amostrado de forma sistemática."
- **R2** "A correlação geral entre *{x}* e *{y}* é {r}, mas a média dos blocos é só {rb}." (r com 2 casas; quando só tirar um bloco dispara: "…mas sem as linhas {ini}–{fim} ela fica em {r_sem}.") → "Se poucos dados novos fazem a correlação subir muito, eles podem ter sido adicionados para 'puxar' a relação." → "…os blocos têm faixas de valores muito diferentes." (numa série no tempo, D137: "…a relação muda com o tempo (as linhas seguem a coluna {data}; ex.: estações do ano).")
- **R3** "Em *{col}*, {pct}% dos valores têm casas decimais, mas {k} inteiros aparecem juntos (linhas {ini}–{fim})." (em posições regulares: "…aparecem a cada {passo} linhas (linhas {ini}–{fim})") → "Uma mudança de formato no meio dos dados pode indicar outra origem." → "…parte dos dados veio de outro instrumento."
- **R4** (acima; só 0: "{pct}% dos valores terminam em 0; … cerca de 10% ({r}× mais).") → pode ser normal: "…o instrumento só mede de {passo} em {passo}." (5 em 5; 0,5 em 0,5 com uma casa)
- **R5** "Encontramos {k} linhas iguais (ou quase iguais) a outras do arquivo; as linhas {ini} a {fim} são iguais e seguidas." (sem sequência, a frase termina em "do arquivo.") → seguidas: "Cópias seguidas costumam surgir de 'copiar e colar'."; demais: "Linhas repetidas podem ter sido copiadas de outras partes do arquivo." → "…são registros legítimos repetidos (ex.: a mesma compra)."
- **R6** "Os dados depois de {data} {comportamento} em relação aos anteriores." — variação: "Os dados de *{col}* depois de {data} variam bem menos em relação aos anteriores (desvio padrão {s2}; antes, {s1})." (com muitos zeros, D144: "(desvio padrão fora os zeros {s2}; antes, {s1})"); cópias: "Os dados depois de {data} copiam os anteriores: {k} das {m} linhas novas ({pct}) são iguais a linhas de antes, fora a data." → "Dados novos que copiam os antigos ou variam pouco demais podem ter sido inseridos." → "…houve mudança real no processo." (na variação, D137: "…houve mudança real no processo ou a época do ano muda os dados (ex.: chuva, vendas de fim de ano).")
- **R7** título "{k} valores distantes dos demais em *{col}*"; "{k} valores de *{col}* estão muito longe dos demais (ex.: {v}); o limite usual seria {limite}." — o critério que marcou o exemplo (D170): cerca alargada pela cauda longa, "…(ex.: {v}); o limite, ajustado à assimetria da coluna, seria {limite}."; só o escore z, "…(ex.: {v}, a mais de 3 desvios padrão da média)." → "Valores extremos podem ser erros de digitação ou casos especiais." → "…são casos raros, mas reais." → o que fazer: "Confira esses valores na fonte; se forem erros de digitação, corrija no arquivo e envie de novo, ou remova-os na etapa Limpeza." (a Limpeza não corrige valores, D76)
- **R8** "Os primeiros dígitos de *{col}* não seguem o padrão natural (Lei de Benford): o {d} abre {pct}% dos valores; o esperado seria cerca de {esp}%." → "Em muitos dados reais, o dígito 1 aparece no início cerca de 30% das vezes; números inventados tendem a ser mais 'uniformes'." → "…os dados têm faixa limitada (ex.: idades, notas)."
- **R9** "O último dígito de *{col}* não está bem distribuído: o {d} aparece {pct}% das vezes (esperado 10%)." → "Medições reais têm o último dígito quase aleatório; pessoas evitam ou repetem certos dígitos." → "…são preços (ex.: 5,99) ou o instrumento arredonda." (D137)
- **R10** "*{col}* parece uma curva Normal perfeita demais (assimetria {g1}, curtose {g2})." (G₁ e G₂ com 3 casas) → "Dados reais quase nunca são tão perfeitos; isso é típico de números gerados por computador." → "…a amostra é grande e o fenômeno é realmente Normal."
- **R11** "A ordem dos valores de *{col}* segue um padrão ({padrao})." — padrões: "progressão aritmética nas linhas {ini}–{fim}", "cada valor é muito parecido com o anterior", "valores alternam acima e abaixo do meio com regularidade", "valores acima e abaixo do meio aparecem em sequências longas" → "Em dados reais, a sequência costuma parecer aleatória." → "…os dados estão ordenados por tempo ou por outra coluna." (numa série no tempo, informativo, D137: "…é uma série no tempo (as linhas seguem a coluna {data}): valores vizinhos costumam ser parecidos.")

## Estado vazio e regras não aplicadas
- Sem avisos: "Nenhuma das 11 regras encontrou suspeitas. Isso não garante que os dados sejam reais, mas não vimos sinais comuns de dados artificiais." (o número é o de regras pedidas; com uma só: "A regra pedida não encontrou suspeitas. …"; se nenhuma se aplica: "Nenhuma das regras se aplica a este arquivo; os motivos estão em Regras não verificadas.")
- Exemplo: até 8 valores, com "…" se houver mais; separados por "; " ("Linhas 99 e 160: 6,8; 712"). A Limpeza segue o mesmo formato, com até 3 ocorrências ("Linhas 99, 106, 160 e mais 1: 6,8; 106,4; 712…"). Números de linha com ponto de milhar, como na Limpeza ("Linhas 1.200 a 1.238"); a linha inteira (R5) com o nome das colunas e as vazias no fim ("sexo M · idade 39 · peso_kg 98,2"; "peso_kg 70,1 (sexo e idade vazias)"); sem siglas ("média 71,12 (restante 71,12) · desvio padrão 11,94 (restante 11,94)") (D170–D172).
- "Ver na tabela": subtítulo "{n} linhas destacadas." ou, quando o exemplo mostra só parte das linhas do alerta, "Destacamos as {n} primeiras das {total} linhas do alerta."; rodapé só com os trechos ("Linhas 228–253"), sem o total do arquivo (D172).
- Não aplicada: "{regra} não verificada em *{col}*: {motivo}." Ex.: "precisa de 100 valores ou mais; a coluna tem 48." Quando a regra tirou valores da coluna, o motivo diz quais: ", fora os zeros" (R4, R9; R6 e R7 com muitos zeros, D143, D144) e ", fora os valores abaixo de 2 (10 vezes o passo de 0,2 do instrumento)" (R8, D145).

## Outros textos
- "Não se aplica": "{medida} não se aplica a {tipo_legivel}: {motivo}."
- Erros: "{o que aconteceu}. {como resolver}." Ex.: "Não encontramos a coluna *peso*. Ela pode ter sido renomeada — recarregue a página."
- Toasts: verbo no passado + quantidade, no singular quando é 1 ("Geramos 1 valor."). "Limpeza aplicada: 12 linhas removidas."
- Números: sinal de menos (−) e ponto de milhar em todo texto exibido, inclusive cálculos e títulos de figura (D156); nas tabelas, as mesmas casas em cada coluna (D157); códigos e números de linha das células de dados como no arquivo, sem ponto de milhar.
- Termos únicos (D159): "arquivo" (não "dataset") na interface, "desvio padrão", "Amplitude interquartil (IQR)", "Coeficiente de variação", tipos auxiliares "Identificador (ignorado)" e "Data ou hora (ignorada)".
