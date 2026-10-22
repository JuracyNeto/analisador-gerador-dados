# 13 — Relatório HTML
Domínio: `app/dominios/relatorio/` (templates Jinja2 em `templates/`) · Endpoint: `GET /api/datasets/{id}/relatorio?secoes=`

## Mini relatório (M1)
1. Cabeçalho: nome do arquivo, data/hora, n linhas × colunas
2. Leitura: formato, separador, decimal, codificação
3. Tipos: tabela coluna → tipo → motivo
4. Limpeza: log em frases
5. Por coluna analisada: tabela de frequência, tendência central, separatrizes, dispersão, gráfico principal, interpretações automáticas
6. Distribuições (M2, D106), dentro da seção de cada coluna, com o subtítulo "Forma e distribuição": assimetria G₁ e curtose G₂ com a classificação, As₁, As₂ e K, os ajustes Normal e Binomial/Bernoulli em frases ("Shapiro-Wilk: W = 0,9933 · p = 0,399 ≥ 0,05. Os dados são compatíveis com a distribuição Normal."), a frase conjunta e a 1ª figura da forma (histograma ou bastões com curva Normal, ou observado × Binomial). Nominal e ordinal mostram a frase de não se aplica. As fórmulas da forma vão para o apêndice (item 10) só com esta seção marcada.
7. Bivariada (M2, D106), seção própria depois das colunas: heatmap da matriz de correlação com o resumo e, para cada um dos até 3 pares de maior |r| (≥ 0,3; empate pela ordem das colunas), o subtítulo "{y} em função de {x}", as medidas (r com força e sentido, p-valor do teste t, Spearman, R², Sₑ, n), a equação, as interpretações e a dispersão com a reta. Sem par com |r| ≥ 0,3: "Nenhum par de colunas numéricas tem correlação moderada ou forte (|r| ≥ 0,3)."; com menos de 2 colunas numéricas, só o resumo da matriz. Pares com `POUCOS_PARES` ou `SEM_VARIACAO` ficam de fora. As fórmulas dos pares vão para o apêndice (item 10).

8. Gerador (M3, D141), seção própria depois da Bivariada: a geração de `?gerado=` (a última da sessão) com o subtítulo "Univariado · 500 valores · semente 42" ("300 pares" no bivariado), os parâmetros e o método, "Como geramos" (a explicação da spec 11), a tabela Original × Gerado com as colunas da tela 6 (Medida · Original · Gerado (n) · Diferença com sinal, na precisão dos valores; frequências em p.p.) e a figura (sobreposição ou dispersão). Sem `gerado`, ou com a geração já descartada (`GERADO_NAO_ENCONTRADO`), a seção não entra e o relatório segue.
9. Detector (M3, D141), a última seção: todas as regras na versão atual; a frase e o detalhe do resumo, os contadores em texto ("2 suspeitas altas · 3 de atenção · 2 informativos") e cada alerta, na ordem da API, com as 8 partes da spec 16: selo com ícone e palavra ("⚠️ Atenção"), título "R4 · Muitos valores redondos em altura_m", resumo, por que chama atenção, pode ser normal se…, exemplo, o que fazer e os detalhes técnicos sempre abertos (medida, valor, limiar, teste, p-valor com a tradução, fórmula em texto) com a figura numerada (R1, R8, R9). Depois, "Regras não verificadas" com as frases da API; sem alertas, o texto vazio da spec 16.

Parâmetros: `secoes` (leitura, tipos, limpeza, analises, distribuicoes, bivariada, gerador, detector, formulas; sem o parâmetro, as 9 — D57, D106, D141, D151), `colunas` (valem para analises e distribuicoes), `gerado` (id da geração da seção Gerador) e `offline`. Colunas identificador, data e vazias ficam fora. A seção de uma coluna aparece se analises **ou** distribuicoes estiver marcada; cada bloco só com a sua caixa. Figuras numeradas na ordem do documento ("Figura N · …").

10. Fórmulas usadas (M4, D151), o apêndice, a última seção: só as fórmulas das seções incluídas, cada uma com o nome, o KaTeX e o texto de reserva, em grupos na ordem do documento — "Análise por coluna" e "Forma e distribuição" (na ordem do catálogo da análise, com as colunas em que a fórmula aparece: "em idade, altura_m e peso_kg", ou "em todas as colunas" quando vale para todas as que têm o bloco), "Bivariada" (as dos pares mostrados), "Gerador" (as do método da geração: o sorteio e, quando a spec 11 reescala, a reescala; Cholesky e, com ajuste exato, Gram-Schmidt) e "Detector" (uma por regra com alerta, "R1 · Bloco alinhado", com a fórmula em texto dos detalhes e as colunas dos alertas dela). A mesma fórmula não se repete no grupo; grupo sem fórmula sai; sem nenhuma, a seção não entra. As listas de fórmulas no fim de cada coluna e da Bivariada (M1–M3) saíram: o apêndice as substitui (escolha do usuário em 18/10/2026). Na impressão, o apêndice começa numa página nova e cada fórmula não se divide.

## Requisitos
- Arquivo único autocontido: CSS inline, Plotly via CDN **ou** embutido (opção "funciona offline" → `include_plotlyjs=True`)
- Fórmulas renderizadas com KaTeX (CDN) e fallback em texto
- CSS `@media print`: quebra de página por seção, gráficos com largura total, sem elementos interativos; o texto de cada alerta do detector não se divide entre páginas (`break-inside: avoid`), e a figura dele (que também não se divide) pode ir para a página seguinte
- O usuário escolhe colunas e seções na tela Relatório
- Os mesmos rótulos e selos da tela (Coeficiente de variação, Amplitude interquartil (IQR), Correlação de Pearson (r), Correlação positiva forte, Sem moda), frases na 1ª pessoa do plural ("Lemos 230 linhas e 8 colunas.") e contagens com concordância e milhar ("1.500 valores válidos · 1 faltante"), D159
- A prévia da tela usa sempre `offline=true`; o arquivo baixado segue a opção "Funciona sem internet" (D84)
- Sem seção sobre uso de IA

## Relatório final do trabalho (documento do grupo)
Gerado à parte (fora do app) a partir deste HTML + prints das telas + explicação do gerador e do detector. Template em `docs/relatorio-final/` (criado no M4).
