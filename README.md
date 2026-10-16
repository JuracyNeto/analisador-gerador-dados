# Analisador e Gerador de Dados

Aplicação web para **análise estatística descritiva e inferencial básica**, **geração de dados artificiais** e **detecção de dados suspeitos de serem artificiais**.

Trabalho da disciplina de Estatística.

## Funcionalidades

**Análise**
- Leitura de TXT, CSV, TSV, XLSX e JSON (detecção automática de separador, decimal e codificação)
- Classificação automática de cada coluna: qualitativa nominal, qualitativa ordinal, quantitativa discreta, quantitativa contínua ou binária, com o motivo exibido e ajuste manual; colunas de data e hora são reconhecidas e ficam fora das análises
- Limpeza: faltantes, duplicados e valores fora de faixa, com log das alterações
- Frequências absoluta, relativa e acumulada (com classes para dados contínuos)
- Média, mediana e moda
- Quartis, decis e percentis, além de consulta de "em qual região está meu valor"
- Amplitude, variância, desvio padrão, IQR (Q3 − Q1) e coeficiente de variação
- Ajuste de distribuição Normal, Binomial e Bernoulli, com testes de aderência
- Assimetria e curtose (Fisher, Pearson e percentílica), com histograma e curva Normal e QQ-plot
- Correlação de Pearson (com teste de significância) e Spearman, regressão linear simples, resíduos, previsão de Y por X e matriz de correlação
- Gráficos escolhidos automaticamente pelo tipo de variável

**Gerador**
- Univariado: gera X novos dados a partir de uma coluna (preservando a média e o desvio exatos, ou com novos parâmetros) ou só com parâmetros; o método segue o tipo da coluna (Normal ou KDE com reescala, Poisson, empírica, Bernoulli, sorteio pelas frequências)
- Bivariado: gera pares com médias, desvios e correlação alvo (Cholesky; com ajuste exato, r = ρ)
- Semente para repetir o resultado, tabela Original × Gerado, gráfico, explicação do método em linguagem simples, Baixar CSV, Anexar ao dataset atual e Usar como novo dataset

**Detector**
- 11 regras de suspeita (bloco alinhado, correlação por blocos, formato numérico, valores redondos, duplicatas, comparação temporal, valores distantes, Lei de Benford, último dígito, Normal perfeita demais e sequência), cada uma comparada com o que o acaso produziria
- Resumo por severidade, alertas explicados em linguagem simples (por que chama atenção, quando pode ser normal, o que fazer), detalhes técnicos com gráfico, as linhas de cada alerta numa tabela lateral (com exportação em CSV) e as regras não verificadas com o motivo

**Relatório** em HTML (imprimível em PDF, funciona sem internet), com tabelas, gráficos e fórmulas: leitura, tipos, limpeza, análise e forma de cada coluna, bivariada, a última geração do Gerador e os alertas do Detector.

## Dados de exemplo
Em `dados-exemplo/`; os quatro primeiros abrem direto na tela Importar:
- `pesquisa_saude.txt` — exemplo principal: pesquisa de saúde com tipos variados, valores fora de faixa e duplicados
- `alturas_reais.txt` — alturas e pesos sem manipulação (nenhum alerta de atenção ou alta)
- `alturas_plantadas.txt` — o mesmo conjunto com dados plantados (bloco alinhado, inteiros no meio de decimais, valores redondos, linhas copiadas, Normal perfeita demais)
- `vendas_correlacao_puxada.txt` — vendas semanais com a correlação puxada no fim e semanas copiadas
- `notas_turma.csv` — notas de uma turma em CSV com vírgula e ponto decimal (correlação e regressão); envie pela tela Importar

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
