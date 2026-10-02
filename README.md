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
> Em construção. Ver [`docs/roadmap.md`](docs/roadmap.md).

```bash
# backend
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -e ".[dev]"
uvicorn app.main:app --reload

# frontend (outro terminal)
cd frontend
npm install
npm run dev
```

## Documentação
- [Visão geral](docs/specs/00-visao-geral.md)
- [Decisões](docs/decisions.md) · [ADRs](docs/adr/)
- [Especificações por módulo](docs/specs/)
- [Roadmap](docs/roadmap.md) · [Changelog](CHANGELOG.md)

## Licença
[MIT](LICENSE)
