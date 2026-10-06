# 13 — Relatório HTML
Domínio: `app/dominios/relatorio/` (templates Jinja2 em `templates/`) · Endpoint: `GET /api/datasets/{id}/relatorio?secoes=`

## Mini relatório (M1)
1. Cabeçalho: nome do arquivo, data/hora, n linhas × colunas
2. Leitura: formato, separador, decimal, codificação
3. Tipos: tabela coluna → tipo → motivo
4. Limpeza: log em frases
5. Por coluna analisada: tabela de frequência, tendência central, separatrizes, dispersão, gráfico principal, interpretações automáticas

Parâmetros: `secoes` (leitura, tipos, limpeza, analises; D57), `colunas` e `offline`. Colunas identificador e vazias ficam fora.

## Relatório completo (M4) — adiciona
6. Distribuição ajustada, assimetria e curtose
7. Bivariada: r, equação, R², gráfico
8. Gerador (se usado): parâmetros, método, explicação, tabela de comparação
9. Detector: resumo + avisos completos (com detalhes técnicos expandidos) + regras não aplicadas
10. Apêndice de fórmulas usadas (só as das seções incluídas)

## Requisitos
- Arquivo único autocontido: CSS inline, Plotly via CDN **ou** embutido (opção "funciona offline" → `include_plotlyjs=True`)
- Fórmulas renderizadas com KaTeX (CDN) e fallback em texto
- CSS `@media print`: quebra de página por seção, gráficos com largura total, sem elementos interativos
- O usuário escolhe colunas e seções na tela Relatório
- Sem seção sobre uso de IA

## Relatório final do trabalho (documento do grupo)
Gerado à parte (fora do app) a partir deste HTML + prints das telas + explicação do gerador e do detector. Template em `docs/relatorio-final/` (criado no M4).
