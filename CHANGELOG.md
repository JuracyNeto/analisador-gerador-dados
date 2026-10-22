# Changelog

Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/) e [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [Não lançado]

### Adicionado
- Relatório com o apêndice "Fórmulas usadas": só as fórmulas das seções incluídas, em grupos (análise por coluna, forma e distribuição, bivariada, gerador e detector), sem repetir e com as colunas em que cada uma aparece; na tela Relatório, a caixa "Fórmulas".
- API do gerador: cada geração traz as fórmulas do método (o sorteio, a reescala, Cholesky e o ajuste exato).
- Testes automáticos de acessibilidade (axe) nas 8 telas, no layout e nos componentes, e de contraste das cores nos dois temas.
- Script de medição de desempenho (`backend/scripts/medir_desempenho.py`): leitura, análise de cada coluna, bivariada, detector e relatório com 10 mil e 100 mil linhas.
- API do detector: o exemplo de cada alerta diz quantas linhas o alerta tem (`total_linhas`).

### Alterado
- As fórmulas saem do fim de cada coluna e da seção Bivariada do relatório e passam para o apêndice.
- Ao trocar de etapa, o foco vai para o título, e o leitor de tela anuncia a etapa nova; ao enviar um formulário com erro, o foco vai para o primeiro campo a corrigir; "Analisar de novo" no Detector avisa o resultado.
- Bivariada: sem colunas escolhidas, a tela abre no par mais correlacionado (o que o mapa de calor aponta).
- "Trocar arquivo" pede confirmação quando já há tipos corrigidos, limpeza ou dados gerados.
- Gerador: ao voltar para a etapa, a última geração aparece de novo; com menos de duas colunas numéricas, o bivariado usa só parâmetros manuais.
- Análise univariada: a aba escolhida fica no endereço da página e continua depois de recarregar.
- Relatório: a prévia anterior continua visível enquanto a nova é montada; arquivos grandes montam o relatório mais rápido.
- Textos revisados pela redação do projeto: "arquivo" no lugar de "dataset", "desvio padrão" e "Amplitude interquartil (IQR)" em todas as telas, o relatório com os mesmos nomes da tela, a chance de acontecer por acaso no lugar do valor p na frase da forma, "Como geramos" em frases curtas e mensagens de erro sem termos técnicos.

### Corrigido
- Números negativos com o sinal de menos (−) e contagens com ponto de milhar em todos os textos (cálculos, classes, títulos dos gráficos, registro da limpeza e relatório).
- Tabelas com as mesmas casas decimais em cada coluna (ponto médio, separatrizes, Original × Gerado); na prévia, códigos como a matrícula 2026001 não ganham mais ponto de milhar.
- Concordância no singular: "Marcamos 1 valor … como faltante por estar fora da faixa.", "Geramos 1 valor.", "A única linha do arquivo"; o registro da limpeza mostra todos os valores mudados.
- "Onde está meu valor?" fora da faixa não repete o aviso e diz "Todos os dados são menores que ele."; "Prever" com o campo inválido não deixa o resultado anterior na tela.
- Planilhas com mais de uma aba avisam que há outras abas para escolher.
- Detector, valores distantes: o resumo diz o que marcou o exemplo (o limite, ajustado à assimetria da coluna quando for o caso, ou a distância de mais de 3 desvios padrão da média), e "O que fazer" manda corrigir no arquivo ou remover na Limpeza, que não corrige valores. O exemplo do bloco alinhado fala em "restante" e "desvio padrão", sem siglas.
- Detector, duplicatas: as linhas anexadas pelo Gerador (só com a coluna gerada) e as linhas com células vazias não viram mais "quase iguais" por acaso; a comparação usa só as colunas preenchidas, e o exemplo mostra o nome das colunas.
- Detector, "Ver na tabela": o bloco alinhado e o bloco da correlação aparecem inteiros (até 194 linhas), como no texto do alerta; quando o painel mostra só parte das linhas, ele diz quantas são; o rodapé não junta mais o número da linha com o total do arquivo; números de linha com ponto de milhar nos textos.
- Acessibilidade (WCAG 2.1 AA): títulos sem pular nível na Análise, na Bivariada e na Limpeza; áreas laterais com nome; o painel "Ver na tabela" sem um segundo cabeçalho de página; o balão de ajuda das abas desabilitadas não entra mais na lista de abas; "não se aplica" na tabela de frequências com contraste suficiente; borda dos campos um pouco mais escura no tema claro; com zoom de 200%, a tabela de Variáveis rola dentro dela e não alarga mais a página.

## [0.3.0] - 2026-10-16

### Adicionado
- Etapa 6 Gerador: dados univariados e bivariados (pela coluna ou par do dataset, ou com parâmetros manuais) com a tabela Original × Gerado, gráfico, explicação do método, Baixar CSV, Anexar ao dataset atual e Usar como novo dataset; se a geração sair da memória do servidor, o aviso traz "Gerar de novo", com a mesma semente.
- API do gerador: dados univariados (preservando as estatísticas de uma coluna ou com novos parâmetros) e pares com médias, desvios e correlação alvo, com comparação com o original, explicação do método, gráfico sobreposto, CSV e uso como novo dataset ou anexado ao atual.
- Etapa 7 Detector: resumo por severidade, filtros (guardados no endereço da página), agrupamento por coluna ou regra, alertas explicados em linguagem simples com detalhes técnicos e gráfico, as linhas de cada alerta numa tabela lateral (com exportação em CSV), regras não verificadas com o motivo e a lista das 11 regras quando não há alertas.
- API do detector com as 11 regras (bloco alinhado, correlação por blocos, formato numérico, valores redondos, duplicatas, comparação temporal, valores distantes, Lei de Benford, último dígito, Normal perfeita demais e sequência) e resumo; cada alerta tem explicação em linguagem simples, exemplo com as linhas e detalhes técnicos, com gráfico no bloco alinhado (média por bloco), na Lei de Benford e no último dígito; as regras que não se aplicam vêm com o motivo. Repetições de linhas só viram alerta quando passam do que o acaso produziria.
- Detector testado com dados reais (preços da ANP e uma estação do INMET), para dar menos alertas falsos:
  - os zeros ficam fora dos valores redondos e do último dígito, que também pedem valores variados e não muito pequenos; o último dígito só avisa quando o excesso passa de 1,5× o esperado; o mesmo inteiro repetido não conta como mudança de formato; valores distantes levam em conta a cauda longa; em séries no tempo, a sequência fica informativa e a correlação por blocos em atenção; linhas sem nenhum número não contam como cópias; "pode ser normal" fala de preços e da época do ano;
  - em colunas com muitos zeros (chuva por dia), valores distantes e a variação no tempo olham só os valores acima de zero, e a estação seca não dá suspeita alta; a Lei de Benford não conta os valores perto do passo do instrumento (chuva de 0,2 em 0,2 mm); os motivos e os detalhes técnicos dizem o que ficou de fora;
  - valores distantes: só os que passam de 3·IQR dão "atenção"; |z| > 3 sozinho fica informativo;
  - bloco alinhado: cada bloco de linhas seguidas é comparado com o restante dos dados, e valores gerados com a média e o desvio de uma coluna e anexados a ela são encontrados sempre; o exemplo mostra a média e o desvio do bloco ao lado dos do restante; janelas do acaso que empatam com o bloco contam (com poucos valores distintos, o arredondamento das contas gerava alertas sem nada plantado);
  - bloco alinhado também no fim do arquivo, de 10 linhas até metade dele: dados anexados pelo Gerador são encontrados com qualquer quantidade (antes, só com um número exato de linhas).
- Três arquivos de demonstração com dados plantados (alturas reais, alturas com dados plantados e vendas com correlação puxada), escolhíveis em "Outros exemplos" na tela Importar (`GET /datasets/exemplos` e `POST /datasets/exemplo?arquivo=`).
- Linhas da versão atual por intervalo (`GET /datasets/{id}/linhas?de=&ate=`, até 200), para mostrar o exemplo de um alerta na tabela.
- Relatório com as seções Gerador (última geração: parâmetros, método, explicação e comparação) e Detector (resumo, alertas com detalhes técnicos e regras não verificadas); na tela Relatório, as caixas "Gerador" (desabilitada enquanto não há dados gerados na sessão) e "Detector".

### Alterado
- A Bivariada continua para o Gerador, o Gerador para o Detector, e o Relatório volta para o Detector.
- O relatório pedido sem escolher seções traz as 8 seções (a seção Gerador só com a geração informada em `gerado`).

### Corrigido
- Preencher faltantes com a média ou a mediana usa as casas decimais da coluna (68,8, e não 68,75, em pesos com 1 casa); antes, o valor preenchido mudava a precisão da coluna e o detector via valores redondos onde não havia.
- Arquivos de uma coluna só com vírgula decimal (como o CSV univariado do gerador) eram lidos com a vírgula como separador, em duas colunas; "Usar como novo dataset" com dados univariados sai com uma coluna, e o motivo do separador diz "1 vez" no singular.
- Datas no formato AAAA/MM/DD e horários como `0000 UTC` (arquivos do INMET) são reconhecidos; horários impossíveis (25:00) não contam mais.
- Valores em reais (`R$ 1.234,56`, `−R$ 10,00`) e percentuais (`12,5%`) viram número (antes, código ou categorias); o percentual fica na escala do arquivo (12,5), o motivo diz a unidade ("Valores em reais (ex.: R$ 1.234,56).") e a prévia mostra as células como no arquivo.
- Arquivos com `;` e duas ou mais colunas com vírgula decimal (ex.: `1,5;2,25`) eram lidos com a vírgula como separador.

## [0.2.0] - 2026-10-10

### Adicionado
- Relatório com as seções Distribuições (forma de cada coluna: assimetria, curtose, ajustes e o gráfico com a curva) e Bivariada (matriz de correlação e os até 3 pares mais fortes, com medidas, equação e dispersão); na tela Relatório, as caixas "Distribuições" e "Bivariada", e as colunas habilitadas com "Análises por coluna" ou "Distribuições".
- Etapa 5 Bivariada: escolha de X e Y (com troca), correlação de Pearson (com teste de significância e Spearman), R², reta de regressão, gráfico de dispersão com a reta, resíduos, previsão de Y por X com aviso de extrapolação e matriz de correlação.
- API da análise bivariada: correlação de Pearson (com teste t) e Spearman, força e sentido, regressão linear simples (equação, R², erro padrão), resíduos, previsão de Y por X com aviso de extrapolação e matriz de correlação das colunas numéricas, com gráficos (dispersão com reta, resíduos e heatmap).
- Aba "Forma e distribuição" na Análise univariada: assimetria, curtose, ajuste à Normal e à Binomial (ou Bernoulli), coeficientes de Pearson e curtose percentílica, frase de interpretação, histograma com curva Normal e QQ-plot; na discreta, campo "Número de tentativas (n)".
- Forma e distribuição de cada coluna numérica na API (`Analise.forma`): assimetria (Fisher e Pearson), curtose (excesso e percentílica), ajuste à Normal (Shapiro-Wilk ou D'Agostino-Pearson, com qui-quadrado complementar), à Binomial (com `?tentativas=`) e Bernoulli para binárias, com frase de interpretação e gráficos (histograma ou bastões com curva Normal, QQ-plot, observado × Binomial).
- Colunas de data, hora ou data e hora são reconhecidas (tipo Data), com o formato no motivo ("Datas no formato DD/MM/AAAA (ex.: 07/10/2026)."), chip próprio e correção manual na tela Variáveis, e ficam fora das análises.

### Alterado
- A Análise univariada continua para a Bivariada, e o Relatório volta para ela.
- O relatório pedido sem escolher seções traz as 6 seções.

### Corrigido
- Números negativos aparecem com o sinal de menos (−) também na tela (cards, heatmap e demais valores), como no relatório.
- Na planilha, colunas só de horários têm o motivo "Horários (ex.: 08:00)." (antes, "Datas da planilha"), e horários de uma coluna mudada para outro tipo aparecem como 08:00 (antes, 08:00:00).
- Colunas de datas não aparecem mais como categorias (nominal) nem como código (identificador).
- Datas de planilhas aparecem na prévia no formato 07/10/2026 (antes, 2026-10-07T00:00:00).

## [0.1.1] - 2026-10-07

### Adicionado
- Linha do cabeçalho em qualquer posição: a leitura acha sozinha o cabeçalho abaixo de títulos e linhas vazias (TXT, CSV, TSV e XLSX), e a tela Importar deixa escolher a linha ("Linha 3") ou "Sem cabeçalho", com o card "Início do arquivo" mostrando as primeiras linhas e o que fica de fora.
- Corrigir a leitura (separador, decimal, codificação, aba, linha do cabeçalho) também depois de avançar para outras etapas ou de recarregar a página: o servidor guarda o arquivo enviado e lê de novo (`POST /api/datasets/{id}/leitura`). Se já houver tipos corrigidos ou limpeza aplicada, a tela avisa antes que eles serão desfeitos.
- Botões "Voltar para …" e "Continuar para …" no fim das etapas Variáveis, Limpeza, Análise univariada e Relatório.

### Alterado
- API: a opção de leitura `tem_cabecalho` virou `linha_cabecalho` (nº da linha; `0` = sem cabeçalho), e os metadados trazem `linhas_iniciais`.
- XLSX: colunas vazias em toda a aba são ignoradas.
- O primeiro envio do arquivo sempre detecta a leitura sozinho; as correções vão pela releitura.

### Corrigido
- "Sem cabeçalho" lê arquivos com título acima da tabela (antes a leitura falhava).

## [0.1.0] - 2026-10-07

### Adicionado
- Documentação inicial: visão geral, especificações por módulo (00–17), registro de decisões, ADRs 0001–0007, roadmap e prompt de design das telas (Claude Design).
- Padrões de código (`docs/padroes-codigo.md`): limites de tamanho e complexidade, monólito em camadas por domínio, padrões de projeto, regras de Python/FastAPI/TypeScript/React.
- Estrutura do repositório, licença MIT e `.gitignore`.
- Fluxo de branches `main` + `develop` documentado em `padroes-codigo.md` §8.
- Esqueleto do backend (FastAPI em camadas por domínio) com configuração, erros padronizados e `/api/saude`.
- Verificador de arquitetura (camadas, fronteiras entre domínios, limite de 500 linhas).
- Esqueleto do frontend (React + Vite + TS strict, react-query, react-router) com cliente HTTP e tipos gerados do OpenAPI.
- Lint com limites de complexidade/aninhamento/tamanho (ruff, complexipy, ESLint + sonarjs), Prettier, jscpd.
- CI no GitHub Actions.
- Design system e telas (Claude Design) em `docs/design/`: tokens claro/escuro, componentes com estados, 8 telas e estados de erro, vazio, carregando e toast.
- `frontend/src/shared/ui/tokens.css` com os tokens de design.
- ADR 0008 (design system com variáveis CSS) e decisões D42–D47.
- Planos de implementação do M1 em `docs/plans/` (visão geral com blocos, dependências e contratos, e um plano por bloco: M1.1 a M1.7).
- Datasets de demonstração em `dados-exemplo/` (`pesquisa_saude.txt`, com os problemas dos mockups de limpeza, e `notas_turma.csv`) e o script que os gera com semente fixa (`backend/scripts/gerar_exemplos.py`).
- Importação de TXT, CSV, TSV, XLSX e JSON com detecção de codificação, separador, decimal e cabeçalho, e o motivo de cada detecção.
- Classificação automática do tipo de cada coluna (nominal, ordinal, discreta, contínua, binária, identificador) com motivo, e ajuste manual do tipo e da ordem das categorias.
- Datasets em memória (até 20) e endpoints `POST /api/datasets`, `POST /api/datasets/exemplo`, `GET/DELETE /api/datasets/{id}`, `GET /api/datasets/{id}/colunas`, `PATCH /api/datasets/{id}/colunas/{coluna}`.
- Diagnóstico de limpeza (faltantes, duplicados, fora de faixa com limites opcionais, grafias diferentes e tipo misto) e aplicação de ações com log em frases, "Desfazer tudo" e reclassificação dos tipos (`GET /api/datasets/{id}/diagnostico`, `POST /api/datasets/{id}/limpeza`, `POST /api/datasets/{id}/limpeza/desfazer`).
- Análise univariada por coluna (`GET /api/datasets/{id}/colunas/{coluna}/analise`): tabela de frequências (com classes de Sturges), média, mediana, moda, moda de Czuber, proporção, quartis, decis, percentis, amplitude, variância, desvio padrão, IQR e CV, com motivo para o que não se aplica, cálculo passo a passo, interpretações e fórmulas.
- "Onde está meu valor?" (`GET /api/datasets/{id}/colunas/{coluna}/posicao`).
- Gráficos por tipo de variável na análise (barras, bastões, histograma, boxplot, ogiva, acumulada e pizza), com título, resumo e "por que este gráfico".
- Mini relatório HTML (`GET /api/datasets/{id}/relatorio`): leitura, tipos, limpeza e análise por coluna, com gráficos, fórmulas e opção de funcionar sem internet.
- Base visual do frontend (M1.1, parte 1): fontes e ícones locais (@fontsource), tokens de espaço, raio e fontes, `color-scheme` por tema, estilos base com foco visível e movimento reduzido; tema claro/escuro salvo no navegador e aplicado antes do primeiro render.
- Componentes de `shared/ui`: Icone, Botao, Card, Banner, estados de carregando/vazio/erro, Toast, Tooltip, Select, CampoNumero, CaixaSelecao, Segmented, Abas, CardMetrica e Tabela.
- Sessão do dataset no navegador (`localStorage`), validada na leitura.
- Formatadores pt-BR (`shared/lib/formatar.ts`) com a mesma regra de casas do backend e tradução dos erros da API em textos de tela.
- Testes de componentes com Vitest + jsdom + Testing Library.
- Base visual do frontend (M1.1, parte 2): layout com barra de etapas (concluída, atual, disponível, bloqueada; recolhível), cabeçalho com arquivo atual, troca de arquivo e alternância de tema, e rotas das 8 etapas (5–7 bloqueadas até a versão em que entram); `PaginaEtapa` e páginas provisórias das etapas.
- Sessão expirada na API leva de volta para Importar com aviso.
- Wrapper Plotly com o tema dos tokens, carregado sob demanda.
- Telas do M1.6:
  - Tela Importar: envio por arrastar/soltar ou teclado, arquivo de exemplo, detecções com motivo e correção da leitura, prévia de 20 linhas e erros da API (1a–1c).
  - Tela Variáveis: tipos com chip, motivo, válidos/faltantes e exemplos; correção do tipo; editor de ordem dos ordinais com arrastar, botões e teclado (2a).
  - Tela Limpeza: cards de resumo, ação por problema, limites por coluna, aplicar e desfazer tudo, registro "O que fizemos" (3a).
  - Cabeçalho com linhas × colunas do dataset; sessão expirada avisa uma só vez, mesmo com várias consultas falhando juntas.
  - `ChipTipo`, `ConteudoConsulta`, `BarraAcoes`, `ExigeDataset`, `SemDataset` e convenção de chaves de query por dataset.
- Tela Análise univariada (etapa 4): seletor de coluna (na URL), abas Frequências, Tendência central, Separatrizes, Dispersão e Gráficos; abas e medidas que não se aplicam aparecem desabilitadas ou esmaecidas com o motivo; número de classes ajustável (3 a 30); "Onde está meu valor?" com régua das separatrizes; estados de carregando, vazio e erro.
- Utilitários do frontend: `urlDaApi`/`requisitarBlob`, colunas analisáveis compartilhadas, `baixarArquivo`, `formatarDecimal`.
- Tela Relatório (etapa 8): escolha de seções (leitura, tipos, limpeza, análises) e colunas, prévia em iframe sempre clara, "Baixar HTML" (com opção "Funciona sem internet") e "Imprimir / salvar PDF".

### Removido
- Página inicial com o status da API (as telas mostram a falta de conexão no próprio estado de erro).
