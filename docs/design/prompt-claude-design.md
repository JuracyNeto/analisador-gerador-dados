# Prompt para o Claude Design

> Copie o bloco abaixo inteiro e cole no Claude Design. Depois de aprovado, salve as telas exportadas em `docs/design/telas/` e os tokens em `docs/design/tokens.md`.

```text
Crie o design system e as telas de uma aplicação web chamada "Analisador e Gerador de Dados", seguindo boas práticas de UX/UI e acessibilidade WCAG 2.1 AA. Todo o texto da interface deve estar em português do Brasil, com números no formato pt-BR (vírgula decimal, ponto de milhar).

## Contexto do produto
- Ferramenta acadêmica de Estatística, usada por estudantes universitários em uma apresentação ao professor. Ela lê um arquivo de dados (TXT, CSV, TSV, XLSX, JSON), classifica as variáveis, limpa os dados, calcula estatísticas, mostra gráficos, gera dados artificiais e detecta suspeitas de dados artificiais.
- Público: estudantes e professor. Conhecimento de estatística de intermediário a básico. Precisa ser claro para leigos e completo para quem quer os detalhes.
- Uso em notebook/desktop (1280–1920 px). Tablet (768 px) com barra lateral recolhível. Celular não é prioridade.
- As telas serão capturadas em prints para um relatório acadêmico. Precisam ser limpas, legíveis e bonitas impressas.
- A implementação será em React + TypeScript. Os gráficos serão renderizados com Plotly.js, então desenhe os gráficos como áreas com o estilo que o Plotly deve seguir (cores, tipografia, grade, rótulos), sem efeitos que o Plotly não reproduza (sem 3D, sombras ou gradientes em gráficos).

## Princípios de UX
1. Fluxo guiado em 8 etapas, com divulgação progressiva: o simples primeiro e os detalhes técnicos recolhidos ("Ver fórmula", "Detalhes técnicos").
2. O sistema explica o que fez: cada tipo de variável, cálculo e alerta vem com um motivo em linguagem simples.
3. Itens que não se aplicam a um tipo de variável aparecem esmaecidos, com o motivo (ex.: "Média não se aplica a categorias sem número"), em vez de sumirem.
4. Nunca transmitir significado só com cor. Tipo de variável e severidade sempre têm ícone + palavra + cor.
5. Toda tela tem estados de carregando (skeleton), vazio (com orientação do próximo passo), erro (mensagem + ação) e sucesso (toast).
6. Tom neutro e amigável, sem palavras acusatórias como "fraude", "falso" ou "manipulado".
7. Hierarquia visual forte: um número-chave por card, rótulo curto, interpretação em uma frase.

## Design system (entregar como página própria)
- Tokens de cor para tema CLARO e ESCURO: fundo, superfície, superfície elevada, borda, texto primário/secundário/desabilitado, primária (ação), foco, sucesso, erro.
- Cores semânticas para os 6 tipos de variável, cada uma com ícone e rótulo:
  Qualitativa nominal · Qualitativa ordinal · Quantitativa discreta · Quantitativa contínua · Binária · Identificador (ignorada).
- Cores semânticas para 3 severidades do detector, com ícone e palavra:
  Informativo (círculo "i", azul) · Atenção (triângulo, âmbar) · Suspeita alta (octógono, vermelho).
- Paleta categórica de gráficos com até 8 cores, segura para daltonismo, com contraste adequado nos dois temas.
- Tipografia: uma família sans-serif legível (sugestão: Inter) e uma monoespaçada para números e fórmulas (sugestão: JetBrains Mono). Escala de tamanhos, pesos e altura de linha. Números tabulares em tabelas.
- Espaçamento em grade de 4/8 px, raios de borda, elevações e foco visível (anel de 2 px).
- Componentes, com todos os estados (padrão, hover, foco, ativo, desabilitado, carregando, erro):
  Botão (primário, secundário, fantasma, perigo) · Campo de texto/número · Select · Segmented control · Abas · Chip de tipo de variável · Badge de severidade · Card de métrica (rótulo, valor, interpretação, link "Ver fórmula") · Tabela de dados (cabeçalho fixo, zebra, linhas destacadas, paginação) · Área de upload (arrastar e soltar) · Stepper/Barra lateral de etapas (concluída ✓ / atual / bloqueada) · Toast · Drawer lateral · Accordion "Detalhes técnicos" · Tooltip · Estado vazio · Skeleton · Banner de aviso · Bloco de fórmula · Régua de separatrizes.

## Layout geral
- Barra lateral fixa à esquerda com as 8 etapas numeradas: 1 Importar · 2 Variáveis · 3 Limpeza · 4 Análise univariada · 5 Bivariada · 6 Gerador · 7 Detector · 8 Relatório. As etapas 2 a 8 ficam bloqueadas até um arquivo ser importado.
- Cabeçalho com nome do arquivo ativo, "230 linhas × 8 colunas", botão "Trocar arquivo" e alternância de tema claro/escuro.
- Área principal com título da etapa, uma frase de ajuda e o conteúdo.

## Dados fictícios para usar nos mockups
Arquivo "pesquisa_saude.txt", 230 linhas, colunas:
- id (identificador) · sexo (binária: F/M) · idade (discreta) · altura_m (contínua, ex.: 1,72) · peso_kg (contínua, ex.: 68,4) · escolaridade (ordinal: fundamental < médio < superior < pós) · cidade (nominal: Goiânia, Anápolis, Aparecida…) · satisfacao (ordinal: ruim < regular < bom < ótimo)
Estatísticas de exemplo para peso_kg: n = 227, média 70,3; mediana 69,8; moda 72,0; DP 11,2; CV 15,9% (variação moderada); Q1 62,1; Q3 77,9; IQR 15,8; assimetria 0,32 (aproximadamente simétrica); curtose −0,18 (mesocúrtica); compatível com a Normal (p = 0,21).

## Telas (desenhar cada uma no tema claro; telas 4 e 7 também no escuro)
1. IMPORTAR: área grande de arrastar e soltar com os formatos aceitos. Depois do envio: cartão "O que detectamos" (formato, separador ";", decimal ",", codificação UTF-8, cabeçalho sim), com opção de corrigir cada item, e prévia das 20 primeiras linhas. Botão "Continuar para Variáveis". Desenhar também o estado de erro ("Não conseguimos ler este arquivo…" + sugestão).
2. VARIÁVEIS: tabela com coluna · chip do tipo detectado · motivo em linguagem simples (ex.: "Números com casas decimais", "Tem só dois valores: F e M", "Os valores seguem uma escala conhecida: ruim < regular < bom < ótimo") · válidos/faltantes · exemplos · seletor para corrigir o tipo. Para ordinais, um editor de ordem das categorias com arrastar e soltar.
3. LIMPEZA: cards de resumo (Faltantes 7 · Duplicados 3 · Fora de faixa 5 · Grafias diferentes 2 grupos). Abaixo, uma seção por problema com as linhas/colunas afetadas e a ação escolhida (ex.: "Preencher com a mediana", "Remover", "Manter", "Unificar 'Goiania' → 'Goiânia'"), campos opcionais de mínimo e máximo por coluna, botão "Aplicar limpeza" e "Desfazer tudo". Log das ações em frases ("Removemos 3 linhas duplicadas.").
4. ANÁLISE UNIVARIADA (tela mais importante): seletor de coluna com chip de tipo; abas Frequências · Tendência central · Separatrizes · Dispersão · Forma e distribuição · Gráficos.
   - Frequências: tabela de classes para contínua (classe "60,0 ⊢ 65,5", ponto médio, fi, fr%, Fi, Fr%) e controle "número de classes (Sturges: 9)".
   - Tendência / Dispersão: cards de métrica com valor grande, interpretação de uma frase e "Ver fórmula" (bloco com a fórmula renderizada).
   - Separatrizes: tabela de quartis/decis/percentis e o painel "Onde está meu valor?" (campo numérico + segmented control Quartil/Decil/Percentil), com resultado em régua horizontal mín→máx, marcas das separatrizes e marcador do valor. Frase: "O valor 75 está no 3º quartil (entre Q2 = 69,8 e Q3 = 77,9). Cerca de 66% dos dados são menores que ele."
   - Forma e distribuição: assimetria, curtose, ajuste Normal (p-valor traduzido: "compatível com a Normal"), histograma com curva Normal sobreposta e QQ-plot.
   - Gráficos: o gráfico principal escolhido para o tipo (histograma, boxplot, ogiva) com uma nota "Por que este gráfico?".
   - Mostrar também a versão para uma coluna NOMINAL (cidade), com cards não aplicáveis esmaecidos e motivo, e barras horizontais ordenadas.
5. BIVARIADA: seletores X e Y; cards r de Pearson (0,78, "correlação positiva forte"), R² (61%, "61% da variação do peso é explicada pela altura"), equação "Ŷ = −98,4 + 98,1·X"; gráfico de dispersão com reta; gráfico de resíduos; campo "Prever Y para X =" com resultado e aviso de extrapolação quando fora da faixa; heatmap da matriz de correlação.
6. GERADOR: abas Univariado / Bivariado.
   - Univariado: origem (coluna do dataset ou parâmetros manuais), quantidade X, modo "Preservar estatísticas" ou "Novos parâmetros" (média, desvio), semente, "limitar à faixa original".
   - Bivariado: médias, desvios, correlação alvo ρ (slider −1 a 1) e "ajuste exato".
   - Resultado: tabela de comparação Original × Gerado × Diferença, gráfico sobreposto, explicação em linguagem simples do método, botões "Baixar CSV", "Usar como novo dataset" e "Anexar ao dataset atual".
7. DETECTOR: cabeçalho com resumo ("Encontramos 5 alertas em 3 colunas": 2 Suspeita alta, 2 Atenção, 1 Informativo), filtros por severidade e agrupamento por coluna ou por regra. Lista de cartões de alerta. Cada cartão tem exatamente esta estrutura:
   (1) Título simples · (2) Badge de severidade · (3) Resumo de uma frase com número e comparação ao esperado · (4) "Por que chama atenção" · (5) Exemplo com linhas/valores + botão "Ver na tabela" (abre um drawer com a tabela e as linhas destacadas) · (6) "Pode ser normal se…" · (7) "O que fazer" · (8) Accordion recolhido "Detalhes técnicos" (medida, valor, limiar, teste, p-valor, fórmula).
   Exemplo de cartão:
   ⚠️ Atenção — "Muitos valores redondos em peso_kg"
   Resumo: "46% dos valores terminam em 0 ou 5; em medições reais o esperado seria cerca de 20% (2,3× mais)."
   Por que chama atenção: "Quando números são inventados ou digitados de cabeça, as pessoas tendem a arredondar."
   Exemplo: "Linhas 120 a 138: 70, 75, 80, 75, 70…" [Ver na tabela]
   Pode ser normal se: "a balança só mede de 5 em 5 kg."
   O que fazer: "Confira a origem dessas linhas."
   Detalhes técnicos: "Teste binomial · p = 0,0003 · limiar p < 0,01"
   Outro cartão, de Suspeita alta: "Bloco alinhado demais em altura_m: as linhas 181–200 têm média e desvio quase idênticos ao conjunto todo (diferença de 0,3%)."
   Ao final, seção recolhida "Regras não verificadas" com motivo (ex.: "Lei de Benford não verificada em idade: precisa de valores que variem em várias ordens de grandeza."). Desenhar também o estado vazio: "Nenhuma das 11 regras encontrou suspeitas. Isso não garante que os dados sejam reais, mas não vimos sinais comuns de dados artificiais."
8. RELATÓRIO: checklist de seções (Leitura, Tipos, Limpeza, Análises por coluna, Distribuições, Bivariada, Gerador, Detector, Fórmulas) e de colunas, pré-visualização do relatório à direita (página A4 em fundo claro, com estilo de impressão) e botões "Baixar HTML" e "Imprimir / salvar PDF".

## Acessibilidade obrigatória
- Contraste mínimo 4,5:1 para texto e 3:1 para elementos de interface e gráficos, nos dois temas.
- Foco visível em todos os elementos interativos; ordem de foco lógica; alvos clicáveis de pelo menos 24×24 px (ideal 44×44 px).
- Tabelas com cabeçalhos claros; gráficos com título descritivo ("Distribuição de peso_kg (n = 227)") e resumo textual ao lado.
- Ícones sempre acompanhados de texto ou rótulo acessível.

## Entregáveis
1. Página do design system (tokens claro/escuro, tipografia, cores semânticas, componentes com estados).
2. As 8 telas no tema claro, mais as telas 4 e 7 no escuro.
3. Estados: tela 1 com erro; tela 4 com coluna nominal; tela 7 vazia; skeleton de carregamento da tela 4; toast de sucesso.
4. Componente "Cartão de alerta" nas 3 severidades, recolhido e expandido.
5. Notas de handoff para desenvolvedores: tokens nomeados (ex.: --cor-superficie, --tipo-continua, --sev-alta), espaçamentos e comportamento responsivo.
```
