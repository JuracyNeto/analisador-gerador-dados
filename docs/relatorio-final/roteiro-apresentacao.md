# Roteiro de apresentação

Cerca de **10 minutos** de demonstração ao vivo, mais as perguntas. Cada bloco diz quem fala, o que clicar e o que dizer; os números são os que aparecem na tela com os arquivos de `dados-exemplo/` (conferidos na versão 1.0.0). Os nomes ficam com o grupo.

| Quem | Blocos |
|---|---|
| **[integrante 1]** | 1, 2 e 3 |
| **[integrante 2]** | 4 e 5 |
| **[integrante 3]** | 6 e 7 |
| **[integrante 4]** | 8, 9 e encerramento |

## Antes de começar (5 minutos antes)

- Abrir o backend (`uvicorn app.main:app` em `backend/`) e o frontend (`npm run dev` em `frontend/`); abrir http://localhost:5173 no navegador, em tela cheia, tema claro.
- Se já houver um arquivo aberto, clicar em "Trocar arquivo" para começar do zero.
- Deixar aberto numa outra janela o plano B: os prints em `docs/relatorio-final/prints/` e o `exemplo-relatorio.html`, caso algo falhe na hora.

## 1. Abertura (≈ 30 s) — [integrante 1]

> "O Analisador e Gerador de Dados lê um arquivo, descobre o tipo de cada coluna e escolhe sozinho os cálculos e os gráficos. Além da análise, ele gera dados artificiais e tenta descobrir dados artificiais. São 8 etapas, na barra lateral."

## 2. Importar e tipos (≈ 1 min 30 s) — [integrante 1]

1. Na tela **Importar**, clicar em **"Abrir pesquisa_saude.txt de exemplo"**.
2. Mostrar o card "O que detectamos": "Lemos 230 linhas e 8 colunas." — separador ponto e vírgula, decimal vírgula, UTF-8, cabeçalho na linha 1, cada um com o motivo.
3. **Continuar para Variáveis.** Mostrar os tipos e os motivos: `id` identificador, `sexo` binária, `idade`, `altura_m` e `peso_kg` contínuas, `escolaridade` e `satisfacao` ordinais, `cidade` nominal.

> "O tipo decide o resto: média só para números, mediana também para ordinais, histograma para contínuas, barras para categorias. Se o programa errar, o tipo pode ser trocado aqui."

## 3. Limpeza (≈ 1 min) — [integrante 1]

1. **Continuar para Limpeza.** Mostrar os problemas: 7 faltantes, 3 duplicados (linha 44 repetida), valores fora de faixa (idade 230, altura 17,2, peso 712) e as grafias "Goiania"/"goiânia".
2. Escolher a primeira opção de cada linha (mediana, remover, remover o valor, unificar) e clicar em **Aplicar limpeza**.
3. Mostrar o log ("Removemos 3 linhas duplicadas.", …) e "Resultado: 227 linhas (eram 230)."

> "Nada muda até aplicar, e 'Desfazer tudo' volta ao arquivo original."

## 4. Análise univariada (≈ 1 min 30 s) — [integrante 2]

1. **Continuar para Análise univariada**; escolher a coluna **peso_kg**.
2. Aba **Frequências**: 9 classes pela regra de Sturges, tabela com fᵢ, fr% e Fr%, histograma.
3. Aba **Tendência central**: média 70,11, mediana 68,7; abrir "Ver fórmula" da média (fórmula e cálculo com os números).
4. Aba **Separatrizes**: quartis, decis e percentis. Em **"Onde está meu valor?"**, digitar **80**: "O valor 80 está no 4º quartil (acima de Q3 = 77,35). Cerca de 79% dos dados são menores que ele."
5. Aba **Dispersão**: desvio padrão 11,22, IQR 15,05, CV 16,01%.
6. Aba **Forma e distribuição**: assimetria 0,21 (aprox. simétrica), curtose −0,31 (mesocúrtica), Shapiro-Wilk p = 0,111 → compatível com a Normal; histograma com a curva e QQ-plot.
7. (Se sobrar tempo) Coluna **cidade**: as abas que não se aplicam ficam desabilitadas, com o motivo.

## 5. Bivariada (≈ 1 min) — [integrante 2]

1. **Continuar para Bivariada.** A tela abre no par mais forte: **altura_m × peso_kg**.
2. Mostrar r = 0,687 (correlação positiva moderada, significativa), R² = 47% e a reta Ŷ = −70,19 + 83,15·X.
3. Em **"Prever Y para X ="**, digitar **1,75** e clicar em **Prever**: 75,32 kg.
4. Mostrar a matriz de correlação: idade quase não se relaciona com as outras.

## 6. Gerador (≈ 1 min 30 s) — [integrante 3]

1. **Continuar para Gerador**, aba **Univariado**: coluna **peso_kg**, quantidade **500**, "Preservar estatísticas", semente **42** → **Gerar dados**.
2. Mostrar a tabela Original × Gerado: média 70,11 e desvio 11,22 iguais; mediana, mínimo e máximo diferentes. Ler "Como geramos".

> "Os valores são sorteados de uma Normal e depois reescalados para bater exatamente a média e o desvio; a mesma semente repete o resultado."

3. Aba **Bivariado**: X **altura_m**, Y **peso_kg**, **Correlação alvo (ρ) = 0,8**, semente 42 → **Gerar dados**. Mostrar "Correlação (r): 0,6869 → 0,8000" e a dispersão dos pares.

> "Método de Cholesky; com o ajuste exato, a correlação sai exatamente igual a ρ."

## 7. Detector no arquivo da pesquisa (≈ 30 s) — [integrante 3]

1. **Continuar para Detector.** "Encontramos 1 alerta em 1 coluna": R11 em altura_m.
2. Abrir o alerta e mostrar as partes: por que chama atenção, **pode ser normal se** "…os dados estão ordenados por tempo ou por outra coluna", e os detalhes técnicos (teste de runs, p = 0,0077).

> "Um alerta pede conferência, não é conclusão. Aqui as primeiras linhas alternam homens e mulheres; o padrão é do próprio arquivo."

## 8. Relatório (≈ 45 s) — [integrante 4]

1. **Continuar para Relatório.** Mostrar as 9 seções ("9 de 9", com o Gerador e as Fórmulas) e a prévia em A4.
2. Clicar em **Baixar HTML** e em **Imprimir / salvar PDF** (mostrar a janela de impressão e cancelar).

> "O relatório tem as mesmas tabelas, gráficos e frases da tela, e no fim todas as fórmulas usadas. Com 'Funciona sem internet', abre em qualquer computador."

O relatório vem antes da demonstração final porque trocar de arquivo encerra a sessão da pesquisa.

## 9. Demonstração final: o Gerador contra o Detector (≈ 1 min 30 s) — [integrante 4]

1. **Trocar arquivo** → **Trocar mesmo assim** → em "Outros exemplos", abrir **alturas_reais.txt** (400 pessoas, sem manipulação).
2. Ir ao **Detector**: "Nenhum alerta".
3. Ir ao **Gerador**, aba Univariado: coluna **peso_kg**, quantidade **21**, semente **7** → **Gerar dados** → **Anexar ao arquivo atual**.
4. Voltar ao **Detector**: R1 com **suspeita alta** — "Um bloco de 21 linhas (401–421) tem média e desvio quase idênticos aos do restante dos dados". Abrir os detalhes técnicos e mostrar o gráfico das médias dos blocos.

> "O caso mais difícil de pegar é justamente gerar valores com a média e o desvio da própria coluna. O detector compara cada trecho com o restante e com 1.000 embaralhamentos da coluna: um bloco tão alinhado quase nunca acontece por acaso."

5. (Se sobrar tempo) **Trocar arquivo** → **alturas_plantadas.txt** → Detector: 7 alertas em 3 colunas; no R4, clicar em **Ver na tabela** e mostrar as linhas 301 a 320 destacadas.

## Encerramento (≈ 15 s) — [integrante 4]

> "O programa cobre todos os itens do enunciado; o relatório final explica as fórmulas, o gerador e o detector, e o código tem testes automáticos para cada cálculo."

## Perguntas prováveis e onde está a resposta

| Pergunta | Resposta curta | No relatório final |
|---|---|---|
| Por que `idade` é contínua e não discreta? | Inteiros com mais de 30 valores diferentes são tratados como contínuos (regra 6); o tipo pode ser trocado na tela Variáveis | Seção 4 |
| Como vocês escolhem o número de classes? | Regra de Sturges, k = ⌈1 + 3,322·log₁₀ n⌉; o usuário pode mudar | Seção 6.1 |
| Por que a variância divide por n − 1? | É a variância amostral (estimador sem viés); a populacional aparece ao lado | Seção 6.4 |
| Qual método das separatrizes? | Interpolação linear entre os valores ordenados, h = (n − 1)·p | Seção 6.3 |
| Como sabem se os dados são Normais? | Shapiro-Wilk (até 5.000 valores; acima, D'Agostino-Pearson), conferido com o qui-quadrado; QQ-plot | Seção 6.5 |
| Qual a diferença entre Pearson e Spearman? | Pearson mede relação linear; Spearman usa os postos e resiste a valores extremos | Seção 7 |
| Como o gerador garante a média e o desvio? | Reescala exata depois do sorteio: zᵢ = (gᵢ − ḡ)/s_g, xᵢ' = x̄ + s·zᵢ | Seção 8.1 |
| Como garantem a correlação pedida? | Cholesky; com o ajuste exato, Gram-Schmidt deixa Z₁ e Z₂ sem correlação, e r sai igual a ρ | Seção 8.2 |
| Os dados gerados não são cópias? | Não: média e desvio iguais, mas mediana, extremos e forma variam como numa amostra real | Seção 8.1 (tabela) |
| O detector acusa dados reais? | Pode, por isso cada alerta diz quando é normal; em 200 amostras sorteadas, cada regra dispara em menos de 5%; `alturas_reais.txt` não tem alertas | Seções 9.3 e 9.4 |
| Por que p < 0,01 no detector e 0,05 na análise? | Para errar menos ao acusar alguém de inventar dados | Seção 9.1 |
| Quais regras são ideias do professor? | R1 a R6; a R7 informa os outliers; R8 a R11 são ideias a mais | Seção 9.2 |
| Por que a R1 compara com o restante, e não com o conjunto? | O bloco gerado tem as medidas do restante; contra o conjunto, a regra virava cara ou coroa (8 de 20) | Seção 9.2 |
| Por que apareceu um alerta na pesquisa limpa? | R11: as primeiras linhas alternam F e M; está na fronteira (p = 0,0077) e o próprio alerta diz quando é normal | Seção 9.4 |
| Onde estão as fórmulas? | Na seção "Fórmulas usadas" do relatório HTML e em `formulas.md` | Apêndice A |
| E com um arquivo grande? | Até ~100 mil linhas; com 10 mil, análise em ~0,1 s e detector em menos de 1 s | Seções 11 e 12 |
| O que acontece se fechar o servidor? | Os dados ficam só na memória (uso local, sem banco); a sessão se perde | Seção 12 |
