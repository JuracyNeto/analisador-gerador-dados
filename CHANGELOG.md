# Changelog

Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/) e [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [Não lançado]

### Adicionado
- Linha do cabeçalho em qualquer posição: a leitura acha sozinha o cabeçalho abaixo de títulos e linhas vazias (TXT, CSV, TSV e XLSX), e a tela Importar deixa escolher a linha ("Linha 3") ou "Sem cabeçalho", com o card "Início do arquivo" mostrando as primeiras linhas e o que fica de fora.

### Alterado
- API: a opção de leitura `tem_cabecalho` virou `linha_cabecalho` (nº da linha; `0` = sem cabeçalho), e os metadados trazem `linhas_iniciais`.
- XLSX: colunas vazias em toda a aba são ignoradas.

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
