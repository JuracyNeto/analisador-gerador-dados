# 15 — Frontend (telas e fluxo)
Pasta: `frontend/` · React + Vite + TypeScript · `react-plotly.js` · roteamento `react-router` · estado do servidor com `@tanstack/react-query` · design em `docs/design/`

## Layout geral
- **Barra lateral fixa** com as 8 etapas (ícone + nome + estado: concluída ✓ / atual / bloqueada). Etapas 2–8 liberadas após importar. Nas versões anteriores, as etapas ainda não liberadas ficavam bloqueadas com "Disponível na versão {v}." (D60); desde o M3 as 8 etapas estão disponíveis (D140).
- **Cabeçalho:** nome do arquivo ativo, n linhas × colunas, botão "Trocar arquivo", seletor de tema claro/escuro.
- **Área principal** com título da etapa, uma frase de ajuda e o conteúdo.
- **Barra de ações** no fim das etapas 2 a 8: secundário "Voltar para <etapa anterior>" à esquerda e primário "Continuar para <próxima etapa>" à direita (D89, D105, D140): Análise → Bivariada → Gerador → Detector → Relatório. Na Limpeza sem problemas e no Detector sem alertas, o "Continuar" fica só no estado vazio.
- **Sessão:** o arquivo ativo e as etapas visitadas ficam salvos no navegador; se a API avisar que a sessão expirou, o app volta para Importar com um aviso (D61).
- Responsivo: ≥ 1280 px principal; 768–1279 px barra lateral recolhida (72 px), abre por cima do conteúdo; < 768 px leitura básica (não é foco).

## Telas
| # | Tela | Conteúdo principal | Ações |
|---|---|---|---|
| 1 | Importar | Área de arrastar/soltar; formatos aceitos; após envio: detecções (formato, separador, decimal, codificação, aba, linha do cabeçalho) com opção de corrigir — também depois de avançar ou recarregar, pelo arquivo guardado no servidor (D88); início do arquivo; prévia de 20 linhas; antes do envio, o exemplo principal e "Outros exemplos" (`GET /datasets/exemplos`, D140) | Enviar, corrigir leitura (com aviso se houver tipos corrigidos ou limpeza), ler de novo, continuar |
| 2 | Variáveis | Tabela: coluna · tipo (chip colorido + ícone; auxiliares identificador e data com borda tracejada e fora do resumo do topo, D92) · motivo · n válidos/faltantes · exemplos · seletor para corrigir; editor de ordem para ordinais: arrastar nativo, Subir/Descer e ↑/↓ (D62) | Corrigir tipo, reordenar categorias |
| 3 | Limpeza | Cards de resumo (faltantes, duplicados, fora de faixa, inconsistências); por problema, lista com ação escolhida; limites min/máx opcionais; log das ações | Aplicar, desfazer tudo |
| 4 | Análise univariada | Seletor de coluna (com chip de tipo); abas: Frequências · Tendência · Separatrizes · Dispersão · Forma e distribuição · Gráficos; coluna, nº de classes e nº de tentativas da Binomial na URL (D78, D99); cada métrica em card com valor, interpretação e "ver fórmula"; itens não aplicáveis aparecem esmaecidos com motivo; painel "Onde está meu valor?" | Trocar coluna, nº de classes, nº de tentativas (discreta), consultar valor |
| 5 | Bivariada | Seletores X e Y só com numéricas, X e Y na URL (`?x=&y=`; padrão = as duas primeiras numéricas) e "Trocar X e Y"; cards r (com teste t e Spearman no "Ver fórmula"), R², reta; gráfico dispersão + reta; resíduos × X; campo "Prever Y para X =" (consulta só ao clicar) com aviso de extrapolação; heatmap de correlação, que carrega e falha à parte (D105) | Trocar X e Y, prever |
| 6 | Gerador | Abas Univariado / Bivariado (aba na URL, `?aba=`); formulário (origem no dataset ou parâmetros manuais, X, modo em cartões de rádio, semente, limitar à faixa / X e Y, médias e desvios, ρ, ajuste exato); campos sem edição usam o valor exato da origem (`GET /gerador/origem`, `/origem-par`); resultado: Original × Gerado (diferença na precisão dos valores), gráfico sobreposto ou dispersão, "Como geramos"; sem dataset, só parâmetros manuais (D115) | Gerar dados, Baixar CSV, Anexar ao dataset atual, Usar como novo dataset (a última geração fica na sessão para o relatório) |
| 7 | Detector | Resumo (frase e detalhe da API, contadores por severidade); chips por severidade e "Agrupar por" Coluna/Regra, na URL (`?sev=&agrupar=`); grupos na ordem dos avisos, com o par (R2) num grupo próprio e as linhas inteiras (R5, R6) em "Linhas inteiras"; cartões em 8 partes (spec 16), o 1º de cada grupo aberto, detalhes técnicos recolhidos com a figura (R1, R8, R9); drawer "Ver na tabela" com as linhas do exemplo e ±3 de contexto por trecho; "Regras não verificadas" recolhível (aberta sem alertas); vazio com "Ver as 11 regras" (D140) | Analisar de novo, filtrar, agrupar, ver na tabela, exportar estas linhas |
| 8 | Relatório | Checklist de seções (Leitura, Tipos, Limpeza, Análises por coluna, Distribuições, Bivariada, Gerador e Detector — D57, D106, D141; a caixa Gerador fica desabilitada sem geração na sessão e leva `gerado=` da última) e colunas, habilitadas com "Análises por coluna" ou "Distribuições"; prévia em iframe sempre clara (D47) e sempre com `offline=true` (D84); "Funciona sem internet" vale para o arquivo baixado | Baixar HTML (D85), imprimir |

## Estados obrigatórios em toda tela
Carregando (skeleton), vazio (com orientação do próximo passo), erro (mensagem da API + ação), sucesso (toast). Sessão expirada (`DATASET_NAO_ENCONTRADO`) em qualquer consulta encerra a sessão e volta para Importar, com um aviso só (D61/D69).

## Acessibilidade
Navegação por teclado completa; foco visível; `aria-live` para toasts e resultados; contraste AA; severidade e tipo nunca só por cor; gráficos com título e resumo textual (`aria-label`).
