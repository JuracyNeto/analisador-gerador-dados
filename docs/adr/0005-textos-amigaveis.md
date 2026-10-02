# 0005 — Textos amigáveis e divulgação progressiva
- **Status:** Aceito
- **Data:** 02/10/2026

## Contexto
O detector e as análises produzem resultados técnicos (p-valores, estatísticas de teste). O público (colegas, professor na apresentação) precisa entender *o que* foi visto e *por quê* sem ler fórmulas, mas os detalhes devem estar disponíveis.

## Decisão
- Todo aviso do detector segue a estrutura de 8 partes de `docs/specs/16-ux-writing.md`: título simples, severidade (ícone + palavra + cor), resumo, por que chama atenção, exemplo, "pode ser normal se…", o que fazer, detalhes técnicos recolhidos.
- Textos ficam em modelos centralizados (`detector/textos.py` e `app/compartilhado/textos.py`), com placeholders preenchidos pelas regras.
- Tom neutro: nunca "fraude", "falso", "manipulado"; usar "fora do esperado", "suspeita".
- Regras não aplicadas aparecem com o motivo.

## Consequências
- (+) Consistência e revisão de tom em um único lugar; ótimo para prints no relatório.
- (+) Acessível (não depende só de cor) e transparente.
- (−) Cada regra precisa preencher mais campos. Aceitável: o contrato `Aviso` obriga.
