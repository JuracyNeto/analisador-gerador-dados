# Telas

Referências: `telas/Telas.dc.html` (todas, com ids 1a…8a) e prints PNG 1440 px em `telas/prints/<id>-<nome>.png` (1a, 1b, 1c, 2a, 3a, 4a–4j, 5a, 6a, 6b, 7a–7d, 8a). Todas as telas usam o layout de `README.md` (barra lateral + cabeçalho + main). Textos abaixo são finais; ficam nos módulos de textos (spec 16), não no JSX. Dados dos mockups: `pesquisa_saude.txt`.

## 1 Importar → `features/importar` (1a enviado, 1b vazio, 1c erro)
- **Antes do envio (1b):** barra com etapas 2–8 bloqueadas; cabeçalho "Nenhum arquivo importado". AreaUpload ("Tamanho máximo: 50 MB", D71) + linha "Sem dados à mão? Abrir pesquisa_saude.txt de exemplo" (link).
- **Erro (1c):** banner de erro acima da área: "Não conseguimos ler este arquivo: relatorio_final.pdf" / "PDF não é um formato de tabela. Abra o arquivo na planilha de origem e salve como CSV ou XLSX, depois envie de novo." + link "Usar o arquivo de exemplo" (o link "Como exportar para CSV" fica fora do M1: não há página de ajuda). Mensagem vem da API (`mensagem`, `sugestao`).
- **Enviado (1a):** card "O que detectamos" (cabeçalho com `check_circle` sucesso + "Lemos 230 linhas e 8 colunas. Se algo estiver diferente do seu arquivo, corrija abaixo.") e grid de 5 colunas, cada uma com rótulo, Select com o valor detectado e motivo 12,5 texto-2: Formato "Texto (TXT)" · Separador "Ponto e vírgula ( ; )" · Decimal "Vírgula ( , )" · Codificação "UTF-8" · Cabeçalho "Linha 1" (opções: as linhas não vazias do início do arquivo e "Sem cabeçalho (só dados)", D86). Mudar um Select relê o arquivo (mutation) e atualiza a prévia. Abaixo, card "Início do arquivo": as 12 primeiras linhas como estão escritas, numeradas, com a coluna "Uso" ("Fica de fora" acima do cabeçalho, "Cabeçalho" destacado).
- Card "Prévia — 20 primeiras linhas de 230": Tabela com cabeçalho fixo, zebra, altura máx. 520 com rolagem.
- Ações: secundário "Ler de novo", primário lg "Continuar para Variáveis" (`arrow_forward`). Toast: "Arquivo lido: 230 linhas e 8 colunas." / "As etapas 2 a 8 foram liberadas."

## 2 Variáveis → `features/variaveis` (2a)
- Topo direito: resumo por tipo ("2 contínuas · 1 discreta · 2 ordinais · 1 nominal · 1 binária"), número em mono na cor do tipo.
- Tabela (grid `140px 200px 1fr 120px 170px 200px`): Coluna (mono 600) · Tipo detectado (ChipTipo) · Por quê (motivo da spec 02, ex.: "Números com casas decimais", "Tem só dois valores: F e M", "Os valores seguem uma escala conhecida: ruim < regular < bom < ótimo") · Válidos / faltantes (mono) · Exemplos (mono texto-2, reticências) · Corrigir tipo (Select 36 com os 6 tipos completos).
- Para cada ordinal, card "Ordem das categorias · {coluna}" com ChipTipo, instrução "Arraste para mudar a ordem, do menor para o maior. Pelo teclado: foque um item e use ↑ e ↓." e lista: item 44 alto, `drag_indicator`, posição mono, nome, "{n} linhas", botões Subir/Descer 28. Item arrastado: borda primaria, sombra-2, anel de foco, "Movendo…". Abaixo, a escala em mono. Implementação: arrastar nativo (HTML5) + botões Subir/Descer + ↑/↓ na alça focada, com anúncio da nova posição (D62).
- Ação: "Continuar para Limpeza".

## 3 Limpeza → `features/limpeza` (3a)
> Implementação do M1: ações começam em "Manter" (D75); "Corrigir para 1,72" fica fora do M1 (D76); limites refazem o diagnóstico 600 ms depois da digitação (D74); o Select de ação tem nome "Ação para {coluna} ({seção})", porque a mesma coluna aparece em mais de uma seção.
- 4 cards de resumo (ícone + rótulo 13 texto-2, número mono 32 + unidade, frase): Faltantes 7 células · Duplicados 3 linhas · Fora de faixa 5 valores · Grafias diferentes 2 grupos.
- Coluna esquerda (1fr): uma seção por problema (cabeçalho título + subtítulo; linhas em grid `120px 1fr 250px`: coluna/grupo mono, linhas/valores afetados, Select de ação). Ações por tipo: Faltantes "Preencher com a mediana (69,8)", "Manter como 'não informado'", "Remover a linha"; Duplicados "Remover"/"Manter"; Fora de faixa "Corrigir para 1,72", "Remover o valor", "Manter"; Grafias "Unificar 'Goiania' → 'Goiânia'".
- Seção "Limites por coluna" (opcional): por coluna numérica, campos Mínimo/Máximo; validação "O mínimo precisa ser menor que o máximo (110). Ajuste um dos dois."
- Ações: perigo "Desfazer tudo" (`undo`), primário "Aplicar limpeza" (`cleaning_services`). Toast: "Limpeza aplicada: 3 linhas removidas."
- Coluna direita (320): "O que fizemos" (`history`) — log em frases na 1ª pessoa do plural com detalhe mono ("Removemos 3 linhas duplicadas." / "linhas 45, 46, 47") e resultado "227 linhas (eram 230)."

## 4 Análise univariada → `features/analise` (4a–4j)
- Topo: título + Select "Coluna" (320, 44 alto) com nome mono + ChipTipo.
- Abas: Frequências · Tendência central · Separatrizes · Dispersão · Forma e distribuição · Gráficos. Aba não aplicável ao tipo: desabilitada com `block` e motivo em tooltip.
- **Frequências (4b):** grid `1.15fr 1fr`. Tabela de classes com controle "Número de classes" (− 9 +) e "Sturges: 9"; colunas Classe (kg) "60,0 ⊢ 65,5" mono · Ponto médio · fi (600) · fr% · Fi · Fr%; classe modal com bg primaria-suave; linha Total; nota "⊢ inclui o limite da esquerda e exclui o da direita. Amplitude de cada classe: h = 5,5 kg." Ao lado, histograma + resumo.
- **Tendência (4c):** 3 CardMetrica (Média 70,3 kg com fórmula aberta · Mediana 69,8 · Moda 72,0) + banner info "Média e mediana estão próximas (diferença de 0,5 kg): os dados são quase simétricos."
- **Separatrizes (4a, principal):** grid `1fr 1.35fr`. Esquerda: tabela de 3 colunas Quartis / Decis / Percentis (k mono texto-2, valor mono; destaque da separatriz relevante). Direita: "Onde está meu valor?" — CampoNumero "Valor de peso_kg" + Segmented Quartil/Decil/Percentil, ReguaSeparatrizes e frase de resultado.
- **Dispersão (4d):** CardMetrica Desvio padrão (fórmula aberta) · Coeficiente de variação 15,9% com selo "Variação moderada" · IQR 15,8 · Amplitude 49,1 · Variância 125,4 kg² ("Fica em kg ao quadrado; para ler, use o desvio padrão."); banner info com faixas do CV.
- **Forma (4e):** cards Assimetria 0,32 "Aprox. simétrica" · Curtose −0,18 "Mesocúrtica" · Ajuste à Normal "p = 0,21" com selo "Compatível com a Normal" e detalhe Shapiro-Wilk · Ajuste Binomial **não aplicável** ("Binomial não se aplica a contínuas: precisa de contagens de sucessos em n tentativas."). Abaixo, 2 gráficos: histograma com curva Normal e QQ-plot, cada um com resumo.
- **Gráficos (4f):** Segmented Histograma (selo "recomendado") / Boxplot / Ogiva, gráfico principal grande e os dois secundários abaixo; à direita "Por que este gráfico?" (`lightbulb`) e "Resumo do gráfico".
- **Coluna nominal (4g, cidade):** abas Separatrizes/Dispersão/Forma desabilitadas. Tabela Cidade · fi · fr% · Fr% acum. (coluna esmaecida com "—" e nota do motivo) + barras horizontais ordenadas com "Por que barras?". Linha de 4 cards: Moda "Goiânia" + Média, Mediana, Desvio padrão **não aplicáveis** com motivo.
- **Carregando (4h):** skeleton de 3 cards + bloco de gráfico com barras + texto de status.
- **Escuro (4i, 4j):** mesmas telas com `data-tema="escuro"`.

## 5 Bivariada → `features/bivariada` (5a)
- Topo: Selects "X (explica)" e "Y (é explicada)" + botão 44 "Trocar X e Y" (`swap_horiz`). Só colunas numéricas.
- 3 cards: r de Pearson 0,78 + selo "Correlação positiva forte" + "Quem é mais alto tende a pesar mais." · R² 61% "61% da variação do peso é explicada pela altura." · Reta "Ŷ = −98,4 + 98,1·X" (mono 26) "A cada 1 cm a mais de altura, o peso previsto sobe cerca de 0,98 kg." com fórmula aberta.
- Grid `1.5fr 1fr`: dispersão com reta (esquerda); à direita "Prever Y para X =" (campo + "Prever", resultado mono 26 em bloco superficie-2, **banner de extrapolação** quando X fora de [mín, máx]: "Fora da faixa observada. As alturas vão de 1,48 a 1,96 m. Prever fora disso (extrapolar) pode dar resultados pouco confiáveis.") e heatmap da matriz de correlação com resumo.
- Card largo: gráfico de resíduos + "Como ler os resíduos".
- Vazio: "Escolha duas colunas numéricas" / "Selecione X e Y acima para ver a correlação e a reta de regressão."

## 6 Gerador → `features/gerador` (6a univariado, 6b bivariado)
- Abas Univariado / Bivariado. Grid `360px 1fr`.
- Formulário univariado: Segmented Origem (Coluna do dataset / Parâmetros manuais) · Select Coluna · Quantidade (X) · Modo como 2 cartões de rádio ("Preservar estatísticas — Mesma média (70,3) e desvio (11,2) da coluna." / "Novos parâmetros" com Média e Desvio, desabilitados até ser escolhido; selecionado com borda 2 primaria e bg primaria-suave) · Semente "(repete o mesmo resultado)" · Checkbox "Limitar à faixa original — Nenhum valor abaixo de 43,8 ou acima de 92,9."
- Formulário bivariado: X, Y, médias e desvios em grid 2×3 · Slider "Correlação alvo (ρ)" −1…1 com marca no 0 e valor mono · Quantidade de pares · Checkbox "Ajuste exato" com explicação.
- Botão primário largo "Gerar dados" (`auto_awesome`).
- Resultado: tabela "Original × Gerado" (Medida · Original · Gerado (600) · Diferença texto-2), gráfico sobreposto (uni) ou dispersão (bi) + "Como geramos" em linguagem simples. Ações: "Baixar CSV", "Anexar ao dataset atual", primário "Usar como novo dataset". Toasts: "Geramos 500 valores." / "Novo dataset criado: 500 linhas."

## 7 Detector → `features/detector` (7a, 7b drawer, 7c vazio, 7d escuro)
- Ação no topo: secundário "Analisar de novo" (`refresh`).
- Card de resumo: "Encontramos 5 alertas em 3 colunas" (20/600) + "altura_m, peso_kg e idade · 9 regras verificadas, 2 não se aplicam a este arquivo"; contadores mono 28 na cor da severidade com ícone + palavra (2 Suspeita alta · 2 Atenção · 1 Informativo).
- Filtros: chips 34 alto raio 999 por severidade (marcado: borda e texto da severidade, bg suave, `check`; `role="checkbox"`) + Segmented "Agrupar por" Coluna/Regra.
- Lista agrupada (cabeçalho do grupo: coluna mono 15/600 + "2 alertas"), ordenada por severidade. O 1º alerta de cada grupo aberto e os demais recolhidos.
- "Ver na tabela" abre Drawer (7b): badge, "Linhas 120 a 138 · peso_kg", "19 linhas destacadas; 17 delas terminam em 0 ou 5.", tabela com contexto de ±3 linhas, destacadas e coluna afetada no cabeçalho na cor da severidade; rodapé "Exportar estas linhas".
- Seção recolhível "Regras não verificadas — 2 regras, com motivo": "Lei de Benford não verificada em idade: precisa de valores que variem em várias ordens de grandeza." · "Comparação temporal não verificada: o arquivo não tem uma coluna de data."
- Vazio (7c): `verified` em círculo sucesso-suave 64, "Nenhum alerta", texto da spec 16 e ações "Ver as 11 regras" / "Continuar para Relatório".

## 8 Relatório → `features/relatorio` (8a)
- Topo: "Baixar HTML" (`code`) e primário "Imprimir / salvar PDF" (`print`).
- Grid `300px 1fr`. Esquerda: fieldsets "Seções" (Leitura, Tipos, Limpeza, Análises por coluna, Distribuições, Bivariada, Gerador, Detector, Fórmulas, cada uma com página) e "Colunas" (nome mono + tipo com ícone e cor), checkboxes 20 raio 5, contador "8 de 9".
- Direita: área superficie-2 com "Prévia · A4 retrato" e "Página 1 de 11"; página A4 620×877 (proporção 1:1,414) **sempre clara** (#fff, texto #161a20), sombra-2, padding 48 52. A prévia real é o `iframe` do HTML gerado (spec 13). O relatório impresso segue esse estilo: cabeçalho com régua 1,5 px, título 22/700, seções numeradas 13/700, corpo 11/1,55, tabelas 10,5 com régua, figuras numeradas ("Figura 1 · …"), rodapé com paginação.
