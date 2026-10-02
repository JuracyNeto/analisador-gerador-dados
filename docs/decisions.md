# Registro de decisões

> Uma linha por decisão. Decisões estruturais têm ADR em `docs/adr/`. Nova decisão → adicionar ao final com o próximo número.

| # | Data | Decisão | Alternativas consideradas | Motivo | ADR |
|---|---|---|---|---|---|
| D1 | 02/10/2026 | Linguagem Python | JS puro, outras | Ecossistema estatístico maduro (pandas/scipy) | — |
| D2 | 02/10/2026 | Cálculos com bibliotecas prontas (numpy/scipy/pandas), fórmulas documentadas na interface e no relatório | Tudo à mão; híbrido | Rapidez e confiabilidade | — |
| D3 | 02/10/2026 | Classificação de tipos automática, com motivo exibido e ajuste manual | Só automático; só manual | Cumpre "o programa define" e corrige erros da heurística | [0006](adr/0006-classificacao-de-tipos.md) |
| D4 | 02/10/2026 | Limpeza = diagnóstico + escolha do usuário + log | Automática; só diagnóstico | Controle e rastreabilidade | — |
| D5 | 02/10/2026 | Relatório em HTML (imprimível em PDF) | PDF direto; MD; DOCX | Gráficos embutidos, simples de gerar | — |
| D6 | 02/10/2026 | Gerador univariado por tipo de variável + ajuste fino de média/desvio | Só Normal; bootstrap | Dados realistas e novos parâmetros | — |
| D7 | 02/10/2026 | Detector: 6 regras do professor + outliers + Benford, último dígito, normalidade perfeita demais, sequência/variância | Só as do professor | Cobertura dos 10% da nota | — |
| D8 | 02/10/2026 | Projeto em `C:\Users\gamer\Documents\Projetos`; repositório público no GitHub | — | Exigência | — |
| D9 | 02/10/2026 | Sem autoria/coautoria de IA; sem seção de IA no relatório | — | Exigência | — |
| D10 | 02/10/2026 | Documentação modular em .md (CLAUDE.md índice, specs, ADR, decisions, CHANGELOG) | Documento único | Carregar só o contexto necessário | — |
| D11 | 02/10/2026 | Arquitetura API FastAPI + frontend separado | Streamlit; script único | Liberdade de design, separação de responsabilidades | [0001](adr/0001-arquitetura-fastapi-react.md) |
| D12 | 02/10/2026 | Frontend React + Vite + TypeScript | Jinja2+HTMX; Vue; JS puro | Handoff direto do Claude Design, flexibilidade | [0001](adr/0001-arquitetura-fastapi-react.md) |
| D13 | 02/10/2026 | Figuras Plotly montadas no backend, enviadas como JSON; o frontend só renderiza | Gráficos montados no frontend | Fonte única para tela e relatório | [0003](adr/0003-figuras-plotly-no-backend.md) |
| D14 | 02/10/2026 | Estado em memória por `dataset_id` (versões original e limpa) | Banco de dados; arquivos | Uso local, 1 usuário (YAGNI) | [0004](adr/0004-estado-em-memoria.md) |
| D15 | 02/10/2026 | Código de domínio puro, sem dependência de FastAPI | Lógica nos routers | Testável, divisível entre membros | [0002](adr/0002-nucleo-puro.md) |
| D16 | 02/10/2026 | Resultado do gerador pode ser "adotado" como dataset | — | Fecha o ciclo gerador → detector para demonstração | — |
| D17 | 02/10/2026 | Tipo auxiliar "identificador" (excluído da análise) | Forçar em um dos 5 tipos | Evita estatísticas sem sentido em IDs/CEP | [0006](adr/0006-classificacao-de-tipos.md) |
| D18 | 02/10/2026 | Variância/DP amostrais (n−1) por padrão, populacional ao lado; separatrizes por interpolação linear | Populacional; outros métodos de quantil | Padrão usual e do numpy; documentado | — |
| D19 | 02/10/2026 | Limite de 30 valores distintos entre discreta e contínua para inteiros (ajustável) | Outros limiares | Heurística simples e explicável | [0006](adr/0006-classificacao-de-tipos.md) |
| D20 | 02/10/2026 | Cada regra do detector declara aplicabilidade (tipo, n mínimo) | Rodar todas sempre | Menos falsos positivos | — |
| D21 | 02/10/2026 | Gerador bivariado por Cholesky, com opção de ajuste exato do r | Só aleatório | Atende correlação alvo; ajuste exato serve à demonstração do detector | — |
| D22 | 02/10/2026 | Geradores aceitam semente (seed) | Sem seed | Reprodutibilidade | — |
| D23 | 02/10/2026 | Avisos do detector em 8 partes com divulgação progressiva | Mensagem única técnica | Compreensão por leigos e transparência | [0005](adr/0005-textos-amigaveis.md) |
| D24 | 02/10/2026 | Textos centralizados em modelos, tom neutro, sem acusação | Textos espalhados no código | Consistência e revisão fácil | [0005](adr/0005-textos-amigaveis.md) |
| D25 | 02/10/2026 | Regras não aplicadas são exibidas com o motivo | Omitir | Transparência | [0005](adr/0005-textos-amigaveis.md) |
| D26 | 02/10/2026 | Erros da API padronizados `{codigo, mensagem, sugestao}` | Exceções cruas | UX consistente | — |
| D27 | 02/10/2026 | CI no GitHub Actions (ruff + pytest + build) | Sem CI | Qualidade em repositório público | — |
| D28 | 02/10/2026 | Roadmap M0–M4 | — | Ver `roadmap.md` | — |
| D29 | 02/10/2026 | Licença MIT, Conventional Commits, tags por marco | — | Padrões de mercado | — |
| D30 | 02/10/2026 | Monólito em camadas com separação por domínio (`app/dominios/*` com router/schemas/servico/domínio/repositório) | Pacote plano; microsserviços | Fronteiras claras para trabalho em grupo | [0007](adr/0007-monolito-camadas-dominios.md) |
| D31 | 02/10/2026 | Limites: arquivo ≤ 500 linhas, ciclomática ≤ 10, cognitiva ≤ 15, aninhamento ≤ 3, zero duplicação — verificados no CI (ruff, complexipy, ESLint/sonarjs, jscpd) | Sem limites | Exigência; legibilidade | — |
| D32 | 02/10/2026 | Padrões de projeto: Fachada, Repositório, Strategy, Chain of Responsibility, Registro, Template Method, Fábrica, DI, Value Object | — | Ver `padroes-codigo.md` §3 | — |
| D33 | 02/10/2026 | Endpoints FastAPI síncronos (`def`) | `async def` | Trabalho CPU-bound (pandas/scipy) roda em threadpool | — |
| D34 | 02/10/2026 | Tipos TS gerados do OpenAPI (`openapi-typescript`) | Tipos escritos à mão | Fonte única, sem duplicação | — |
| D35 | 02/10/2026 | Frontend por feature (`app/`, `features/<etapa>/`, `shared/`), react-query, Plotly sob demanda | Por tipo de arquivo | Coesão por etapa; bundle menor | — |
| D36 | 02/10/2026 | Fluxo Git com `main` (estável, protegida, tags) + `develop` (integração, branch padrão); tarefas saem de e voltam para `develop` por PR | Só `main` + feature branches | Exigência; `main` sempre entregável | — |
| D37 | 02/10/2026 | Regra `N818` do ruff desligada no `pyproject.toml` | Sufixo inglês `Error` nas exceções; `noqa` por arquivo | Nomes em português (`ErroAplicacao`, `NaoEncontrado`) são regra do projeto; a regra exige sufixo em inglês | — |
