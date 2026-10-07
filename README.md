# Analisador e Gerador de Dados

Aplicação web para **análise estatística descritiva e inferencial básica**, **geração de dados artificiais** e **detecção de dados suspeitos de serem artificiais**.

Trabalho da disciplina de Estatística.

## Funcionalidades

**Análise**
- Leitura de TXT, CSV, TSV, XLSX e JSON (detecção automática de separador, decimal e codificação)
- Classificação automática de cada coluna: qualitativa nominal, qualitativa ordinal, quantitativa discreta, quantitativa contínua ou binária, com o motivo exibido e ajuste manual
- Limpeza: faltantes, duplicados e valores fora de faixa, com log das alterações
- Frequências absoluta, relativa e acumulada (com classes para dados contínuos)
- Média, mediana e moda
- Quartis, decis e percentis, além de consulta de "em qual região está meu valor"
- Amplitude, variância, desvio padrão, IQR (Q3 − Q1) e coeficiente de variação
- Ajuste de distribuição Normal e Binomial
- Assimetria e curtose
- Correlação de Pearson, regressão linear simples e previsão de Y por X
- Gráficos escolhidos automaticamente pelo tipo de variável

**Gerador**
- Univariado: gera X novos dados preservando as estatísticas originais ou seguindo novos parâmetros
- Bivariado: gera pares com médias, desvios e correlação alvo

**Detector**
- 11 regras de suspeita (blocos alinhados, correlação por blocos, formato numérico, valores redondos, duplicatas, comparação temporal, outliers, Lei de Benford, último dígito, normalidade perfeita demais e sequências), com explicações em linguagem simples

**Relatório** em HTML (imprimível em PDF), com tabelas, gráficos e fórmulas.

## Tecnologias
- **Backend:** Python 3.12, FastAPI, pandas, numpy, scipy, plotly
- **Frontend:** React, Vite, TypeScript, react-plotly.js

## Como rodar
Requisitos: Python 3.12+ e Node 22+.

**Backend** (terminal 1)
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows  (Linux/macOS: source .venv/bin/activate)
pip install -e ".[dev]"
uvicorn app.main:app --reload   # http://localhost:8000/docs
```

**Frontend** (terminal 2)
```bash
cd frontend
npm install
npm run dev                     # http://localhost:5173
```

**Qualidade** (os mesmos comandos do CI; no backend, com o venv ativo)
```bash
# em backend/
ruff check . && ruff format --check . && mypy app && complexipy app --max-complexity-allowed 15 && pytest

# em frontend/
npm run lint && npm run format && npm run test && npm run build

# na raiz
npx --yes jscpd@4 backend/app backend/tests frontend/src
```

**Tipos do frontend após mudar a API**
```bash
# em backend/ (venv ativo)
python scripts/exportar_openapi.py
# em frontend/
npm run gerar:tipos
```

## Documentação
- [Visão geral](docs/specs/00-visao-geral.md)
- [Decisões](docs/decisions.md) · [ADRs](docs/adr/)
- [Especificações por módulo](docs/specs/)
- [Roadmap](docs/roadmap.md) · [Changelog](CHANGELOG.md)

## Licença
[MIT](LICENSE)
