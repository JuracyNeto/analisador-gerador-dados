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
