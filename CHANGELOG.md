# Changelog

Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/) e [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [Não lançado]

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
- Base visual do frontend (M1.1, parte 1): fontes e ícones locais (@fontsource), tokens de espaço, raio e fontes, `color-scheme` por tema, estilos base com foco visível e movimento reduzido; tema claro/escuro salvo no navegador e aplicado antes do primeiro render.
- Componentes de `shared/ui`: Icone, Botao, Card, Banner, estados de carregando/vazio/erro, Toast, Tooltip, Select, CampoNumero, CaixaSelecao, Segmented, Abas, CardMetrica e Tabela.
- Sessão do dataset no navegador (`localStorage`), validada na leitura.
- Formatadores pt-BR (`shared/lib/formatar.ts`) com a mesma regra de casas do backend e tradução dos erros da API em textos de tela.
- Testes de componentes com Vitest + jsdom + Testing Library.
- Base visual do frontend (M1.1, parte 2): layout com barra de etapas (concluída, atual, disponível, bloqueada; recolhível), cabeçalho com arquivo atual, troca de arquivo e alternância de tema, e rotas das 8 etapas (5–7 bloqueadas até a versão em que entram); `PaginaEtapa` e páginas provisórias das etapas.
- Sessão expirada na API leva de volta para Importar com aviso.
- Wrapper Plotly com o tema dos tokens, carregado sob demanda.

### Removido
- Página inicial com o status da API (as telas mostram a falta de conexão no próprio estado de erro).
