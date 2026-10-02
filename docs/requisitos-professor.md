# Enunciado original (professor)

> Transcrição do enunciado. Fonte da verdade para os requisitos. Observação: o texto cita "até 02/02/2026" para a versão final, mas a data oficial de entrega é **08/12/2026**.

**Grupo:** de 2 a 4 alunos.
**Datas:** prévia funcional 22/09/2026 · entrega final 08/12/2026.

## Objetivos da prévia
1. **Leitura de arquivos:** TXT obrigatório; se possível CSV, TSV, XLSX e JSON. Transformar o arquivo em tabela interna.
2. **Tipos de variáveis:** classificar cada coluna como qualitativa nominal, qualitativa ordinal, quantitativa discreta, quantitativa contínua ou binária. A partir dessa classificação, o próprio programa deve definir cálculos e gráficos.
3. **Limpeza básica:** tratar valores faltantes, duplicados e fora de faixa; garantir consistência.
4. **Frequências:** absoluta, relativa e acumulada quando aplicável, em tabela (lembrar do caso contínuo).
5. **Tendências centrais:** média, mediana e moda quando aplicável.
6. **Separatrizes:** quartis, decis e percentis quando aplicável, com opção de enviar um dado e saber em qual região da separatriz escolhida ele está.
7. **Dispersão:** amplitude, variância, desvio padrão, Q3 − Q1 e coeficiente de variação quando aplicável.
8. **Gráficos:** sempre escolhendo o melhor gráfico para o tipo de variável.

**Checklist da prévia:** lê TXT e analisa ao menos um conjunto · classifica tipo por coluna · calcula frequências, tendências, separatrizes e dispersão · mostra gráficos básicos · gera mini relatório simples.

## Objetivos da versão final
1. **Distribuições:** quando aplicável, ajustar Normal ou Binomial.
2. **Assimetria e curtose:** caudas e pico da distribuição.
3. **Correlação e regressão:** com duas variáveis numéricas, calcular correlação, ajustar regressão linear simples e prever Y por X.
4. **Gerador univariado:** ao informar X, criar X novos dados preservando estatísticas originais ou seguindo novos parâmetros (média, desvio); dados realistas.
5. **Gerador bivariado:** gerar duas variáveis com médias, desvios e correlação alvo, mantendo a relação.
6. **Detector de dados artificiais:** verificador simples que aponte suspeitas, mostre o que mediu e por que marcou.
7. **Relatório final simples:** prints das telas e gráficos, fórmulas, explicação do gerador e do detector, documentação do trabalho.

**Checklist da final:** tudo da prévia · distribuições, assimetria, curtose · correlação e regressão · gerador univariado · gerador bivariado com correlação · detector com resumo · relatório com imagens e fórmulas.

## Avaliação (60% da nota final)
- **40%:** análise estatística (tipos, frequências, tendências, separatrizes, dispersão, distribuições, assimetria, curtose, correlação, regressão)
- **10%:** gerador univariado e bivariado
- **10%:** detector de dados artificiais

## Ideias do professor para o detector
- Subconjunto pequeno com praticamente a mesma média e desvio do conjunto todo.
- Correlação geral muito maior que a média das correlações por blocos.
- Discrepância no formato dos números (inteiros em posições estratégicas entre decimais).
- Picos em números redondos (múltiplos de 5 ou 10).
- Duplicatas e quase duplicatas em bloco.
- Antes × depois no tempo, quando houver data.
- Saída: lista de avisos por regra, coluna(s) afetada(s), motivo e exemplo. Informar outliers. "Busquem mais ideias de regras."
