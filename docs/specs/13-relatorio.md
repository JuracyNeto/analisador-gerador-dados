# 13 — Relatório HTML
Domínio: `app/dominios/relatorio/` (templates Jinja2 em `templates/`) · Endpoint: `GET /api/datasets/{id}/relatorio?secoes=`

## Mini relatório (M1)
1. Cabeçalho: nome do arquivo, data/hora, n linhas × colunas
2. Leitura: formato, separador, decimal, codificação
3. Tipos: tabela coluna → tipo → motivo
4. Limpeza: log em frases
5. Por coluna analisada: tabela de frequência, tendência central, separatrizes, dispersão, gráfico principal, interpretações automáticas
6. Distribuições (M2, D106), dentro da seção de cada coluna, com o subtítulo "Forma e distribuição": assimetria G₁ e curtose G₂ com a classificação, As₁, As₂ e K, os ajustes Normal e Binomial/Bernoulli em frases ("Shapiro-Wilk: W = 0,9933 · p = 0,399 ≥ 0,05. Os dados são compatíveis com a distribuição Normal."), a frase conjunta e a 1ª figura da forma (histograma ou bastões com curva Normal, ou observado × Binomial). Nominal e ordinal mostram a frase de não se aplica. As fórmulas da forma entram na lista da coluna só com esta seção marcada.
7. Bivariada (M2, D106), seção própria depois das colunas: heatmap da matriz de correlação com o resumo e, para cada um dos até 3 pares de maior |r| (≥ 0,3; empate pela ordem das colunas), o subtítulo "{y} em função de {x}", as medidas (r com força e sentido, p-valor do teste t, Spearman, R², Sₑ, n), a equação, as interpretações e a dispersão com a reta. Sem par com |r| ≥ 0,3: "Nenhum par de colunas numéricas tem correlação moderada ou forte (|r| ≥ 0,3)."; com menos de 2 colunas numéricas, só o resumo da matriz. Pares com `POUCOS_PARES` ou `SEM_VARIACAO` ficam de fora. Fórmulas no fim da seção.

Parâmetros: `secoes` (leitura, tipos, limpeza, analises, distribuicoes, bivariada; sem o parâmetro, as 6 — D57, D106), `colunas` (valem para analises e distribuicoes) e `offline`. Colunas identificador, data e vazias ficam fora. A seção de uma coluna aparece se analises **ou** distribuicoes estiver marcada; cada bloco só com a sua caixa. Figuras numeradas na ordem do documento ("Figura N · …").

## Relatório completo (M4) — adiciona
8. Gerador (se usado): parâmetros, método, explicação, tabela de comparação
9. Detector: resumo + avisos completos (com detalhes técnicos expandidos) + regras não aplicadas
10. Apêndice de fórmulas usadas (só as das seções incluídas)

## Requisitos
- Arquivo único autocontido: CSS inline, Plotly via CDN **ou** embutido (opção "funciona offline" → `include_plotlyjs=True`)
- Fórmulas renderizadas com KaTeX (CDN) e fallback em texto
- CSS `@media print`: quebra de página por seção, gráficos com largura total, sem elementos interativos
- O usuário escolhe colunas e seções na tela Relatório
- A prévia da tela usa sempre `offline=true`; o arquivo baixado segue a opção "Funciona sem internet" (D84)
- Sem seção sobre uso de IA

## Relatório final do trabalho (documento do grupo)
Gerado à parte (fora do app) a partir deste HTML + prints das telas + explicação do gerador e do detector. Template em `docs/relatorio-final/` (criado no M4).
