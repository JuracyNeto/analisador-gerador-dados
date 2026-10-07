# 15 — Frontend (telas e fluxo)
Pasta: `frontend/` · React + Vite + TypeScript · `react-plotly.js` · roteamento `react-router` · estado do servidor com `@tanstack/react-query` · design em `docs/design/`

## Layout geral
- **Barra lateral fixa** com as 8 etapas (ícone + nome + estado: concluída ✓ / atual / bloqueada). Etapas 2–8 liberadas após importar. Etapas que entram em versões futuras (5–7 no M1) ficam bloqueadas com "Disponível na versão {v}." (D60).
- **Cabeçalho:** nome do arquivo ativo, n linhas × colunas, botão "Trocar arquivo", seletor de tema claro/escuro.
- **Área principal** com título da etapa, uma frase de ajuda e o conteúdo.
- **Sessão:** o arquivo ativo e as etapas visitadas ficam salvos no navegador; se a API avisar que a sessão expirou, o app volta para Importar com um aviso (D61).
- Responsivo: ≥ 1280 px principal; 768–1279 px barra lateral recolhida (72 px), abre por cima do conteúdo; < 768 px leitura básica (não é foco).

## Telas
| # | Tela | Conteúdo principal | Ações |
|---|---|---|---|
| 1 | Importar | Área de arrastar/soltar; formatos aceitos; após envio: detecções (formato, separador, decimal, codificação) com opção de corrigir; prévia de 20 linhas | Enviar, corrigir leitura, continuar |
| 2 | Variáveis | Tabela: coluna · tipo (chip colorido + ícone) · motivo · n válidos/faltantes · exemplos · seletor para corrigir; editor de ordem para ordinais: arrastar nativo, Subir/Descer e ↑/↓ (D62) | Corrigir tipo, reordenar categorias |
| 3 | Limpeza | Cards de resumo (faltantes, duplicados, fora de faixa, inconsistências); por problema, lista com ação escolhida; limites min/máx opcionais; log das ações | Aplicar, desfazer tudo |
| 4 | Análise univariada | Seletor de coluna (com chip de tipo); abas: Frequências · Tendência · Separatrizes · Dispersão · Gráficos (Forma e distribuição entra no M2, D60); coluna escolhida na URL (D78); cada métrica em card com valor, interpretação e "ver fórmula"; itens não aplicáveis aparecem esmaecidos com motivo; painel "Onde está meu valor?" | Trocar coluna, nº de classes, consultar valor |
| 5 | Bivariada | Seletores X e Y; cards r, R², equação; gráfico dispersão + reta; resíduos; campo "Prever Y para X ="; heatmap de correlação | Prever |
| 6 | Gerador | Abas Univariado / Bivariado; formulário (origem ou parâmetros, X, modo, seed, ajuste exato); resultado: comparação original × gerado, gráfico sobreposto, explicação | Gerar, baixar CSV, usar como dataset / anexar |
| 7 | Detector | Resumo (contadores por severidade, colunas afetadas); filtro por severidade; agrupar por coluna/regra; lista de avisos (spec 16); "Regras não aplicadas" recolhível | Analisar, ver na tabela (abre drawer com linhas destacadas) |
| 8 | Relatório | Checklist de seções (no M1: leitura, tipos, limpeza, análises — D57) e colunas; prévia em iframe sempre clara (D47) e sempre com `offline=true` (D84); "Funciona sem internet" vale para o arquivo baixado | Baixar HTML (D85), imprimir |

## Estados obrigatórios em toda tela
Carregando (skeleton), vazio (com orientação do próximo passo), erro (mensagem da API + ação), sucesso (toast). Sessão expirada (`DATASET_NAO_ENCONTRADO`) em qualquer consulta encerra a sessão e volta para Importar, com um aviso só (D61/D69).

## Acessibilidade
Navegação por teclado completa; foco visível; `aria-live` para toasts e resultados; contraste AA; severidade e tipo nunca só por cor; gráficos com título e resumo textual (`aria-label`).
