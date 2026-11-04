# Relatório final do trabalho

Material do relatório final pedido pelo professor (objetivo 7 da versão final: "prints das telas e gráficos, fórmulas, explicação do gerador e do detector, documentação do trabalho"). Decisões: D168 (prints) e D169 (relatório em Markdown e fórmulas do catálogo).

## O que tem aqui

| Arquivo | O que é | Como refazer |
|---|---|---|
| [`relatorio-final.md`](relatorio-final.md) | O relatório do grupo: introdução, arquitetura, uso, cada etapa com prints e fórmulas, gerador, detector, qualidade, conclusão e referências. Rascunho para revisar; os campos **[preencher]** (nomes, matrículas, professor, turma) ficam com o grupo | Texto escrito à mão; os números vêm de `pesquisa_saude.txt` com a limpeza sugerida e dos outros exemplos |
| [`formulas.md`](formulas.md) | Todas as fórmulas do programa (análise, gerador e detector), com a forma matemática e o texto de reserva | `python scripts/exportar_formulas.py` em `backend/` (venv ativo) |
| [`exemplo-relatorio.html`](exemplo-relatorio.html) | O relatório HTML do programa para `pesquisa_saude.txt`, com as 9 seções; abra no navegador (gráficos e fórmulas vêm da internet) | `python scripts/exportar_relatorio_exemplo.py --data "08/12/2026 10:00"` em `backend/` |
| [`prints/`](prints/) | As 19 telas da versão final, com os nomes de `docs/design/telas/prints/` | `npm run prints` em `frontend/` (abaixo) |
| [`roteiro-apresentacao.md`](roteiro-apresentacao.md) | A demonstração de ~10 minutos, quem fala o quê e as perguntas prováveis | — |

Os scripts de fórmulas e do exemplo não precisam do servidor: chamam a API por dentro (`TestClient`). Um teste confere que `formulas.md` é exatamente o que o script gera; se uma fórmula mudar no programa, o teste falha até o arquivo ser refeito.

## Como refazer os prints

1. Abra o backend (`uvicorn app.main:app` em `backend/`) e o frontend (`npm run dev` em `frontend/`).
2. Em `frontend/`: `npm run prints` (ou `npm run prints -- http://localhost:5174` para outro endereço).

O script usa o Microsoft Edge instalado (nada a baixar), janela de 1440 px de largura, tema claro (4i e 7d no escuro) e percorre o fluxo como um usuário: abre `pesquisa_saude.txt`, aplica a limpeza sugerida (a primeira opção de cada linha), passa pelas abas da análise com `peso_kg` (e `cidade` no 4g), prevê o peso para 1,75 m, gera 500 pares com ρ = 0,8 e 500 valores de `peso_kg` (semente 42) e abre o relatório; depois abre `alturas_plantadas.txt` (detector, "Ver na tabela" da R4 e tema escuro) e `alturas_reais.txt` (detector sem alertas). Leva alguns minutos. Os PNG saem iguais a cada execução, menos o 8a, que mostra a data e a hora do relatório, e os do tema escuro, em que as bordas podem variar em 1 ou 2 tons (invisível).

## Como gerar o PDF

O relatório usa Markdown com as fórmulas em blocos ` ```math `, que o GitHub desenha (com `$$…$$`, o Markdown do GitHub tiraria a barra de `\#`, `\,` e `\%` e estragaria algumas fórmulas):

- **Pelo GitHub:** abra `relatorio-final.md` no repositório e use "Imprimir" do navegador (Ctrl+P) → "Salvar como PDF".
- **Pelo VS Code:** a prévia do Markdown (Ctrl+Shift+V) serve para revisar o texto e as figuras; as fórmulas aparecem como código LaTeX, a menos que uma extensão de prévia desenhe os blocos `math`. Para o PDF, imprima pelo GitHub.

Confira as fórmulas e as figuras na prévia antes de imprimir. Para entregar o exemplo do relatório HTML junto, abra `exemplo-relatorio.html` no navegador e imprima (Ctrl+P → "Salvar como PDF"); o arquivo já vem com o estilo de impressão (uma seção por página).
