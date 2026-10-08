# Tokens de design

Fonte única: `frontend/src/shared/ui/tokens.css`. Tema por atributo `data-tema="claro"|"escuro"` em `<html>`. Nunca usar hex direto em componentes: sempre `var(--token)`.

## Interface
| Token | Claro | Escuro | Uso |
|---|---|---|---|
| `--cor-fundo` | #f5f6f8 | #0e1115 | Fundo da página |
| `--cor-superficie` | #ffffff | #161a20 | Cards, barra lateral, cabeçalho |
| `--cor-superficie-elevada` | #ffffff | #1d222a | Menus, toast, drawer |
| `--cor-superficie-2` | #f0f2f5 | #20262e | Cabeçalho de tabela, preenchimentos, skeleton |
| `--cor-zebra` | #f7f8fa | #1a1f26 | Linhas pares de tabela |
| `--cor-borda` | #dadee4 | #2f3640 | Divisórias, borda de card |
| `--cor-borda-forte` | #868f9c | #707a89 | Borda de campo/botão secundário (≥ 3:1) |
| `--cor-texto` | #161a20 | #e8ebef | Texto primário |
| `--cor-texto-2` | #4b5462 | #a9b2be | Texto secundário (≥ 4,5:1) |
| `--cor-texto-desab` | #8c94a1 | #636c79 | Desabilitado |
| `--cor-primaria` | #4338ca | #9196f8 | Ação, link, aba ativa |
| `--cor-primaria-hover` | #3730a3 | #a9adfa | Hover do primário |
| `--cor-primaria-ativa` | #312a8c | #bfc2fb | Pressionado |
| `--cor-primaria-suave` | #eef0fd | #25274a | Selecionado, etapa atual |
| `--cor-sobre-primaria` | #ffffff | #10121a | Texto sobre primário |
| `--cor-foco` | #1d4ed8 | #7fabff | Anel de foco |
| `--cor-sucesso` / `-suave` | #157a3c / #e7f5ec | #4fd187 / #15301f | Sucesso |
| `--cor-erro` / `-suave` | #b42318 / #fdeceb | #ff8278 / #3a1a18 | Erro, perigo |
| `--cor-destaque-linha` | #fff4d6 | #3a3014 | Linhas destacadas ("Ver na tabela") |
| `--cor-overlay` | rgba(16,20,26,.38) | rgba(0,0,0,.55) | Fundo de drawer |

## Tipos de variável (ícone + rótulo + cor)
| Token | Claro / suave | Escuro / suave | Ícone | Rótulo curto · completo |
|---|---|---|---|---|
| `--tipo-nominal` | #6d3fd6 / #f2edfd | #b79bff / #2a2240 | `sell` | Nominal · Qualitativa nominal |
| `--tipo-ordinal` | #a3207f / #fcebf6 | #f08ad0 / #3a1c32 | `stairs` | Ordinal · Qualitativa ordinal |
| `--tipo-discreta` | #0b62a3 / #e7f1fa | #6fb6f2 / #15283a | `pin` | Discreta · Quantitativa discreta |
| `--tipo-continua` | #0d7268 / #e3f4f1 | #4fd1c0 / #11302d | `straighten` | Contínua · Quantitativa contínua |
| `--tipo-binaria` | #a14a0b / #fcefe4 | #f5a565 / #362416 | `toggle_on` | Binária |
| `--tipo-data` | #5f6b00 / #f3f6dc | #c9d46a / #2b2f12 | `calendar_month` | Data · Data ou hora (ignorada) — borda tracejada como o identificador (D92) |
| `--tipo-identificador` | #5b6472 / #eef0f3 | #a9b2be / #252b33 | `fingerprint` | Identificador · Identificador (ignorada) |

Implementar como tabela `as const satisfies Record<TipoVariavel, ...>` em `shared/ui/tipos.ts` (padroes-codigo §5).

## Severidades do detector
| Token | Claro / suave | Escuro / suave | Ícone (preenchido) | Palavra |
|---|---|---|---|---|
| `--sev-info` | #1d5fd1 / #e8f0fd | #74abff / #172540 | `info` (círculo i) | Informativo |
| `--sev-atencao` | #995700 / #fff3df | #f3b54a / #332612 | `warning` (triângulo) | Atenção |
| `--sev-alta` | #b42318 / #fdeceb | #ff8278 / #3a1a18 | `report` (octógono) | Suspeita alta |
`--sev-atencao-borda`: #e0a03a / #a8792b (banners de aviso).

## Paleta de gráficos (Okabe-Ito ajustada, ≥ 3:1 no fundo)
| Token | Claro | Escuro |
|---|---|---|
| `--graf-1` | #0b6aa8 | #56b4e9 |
| `--graf-2` | #c4520a | #f08a3c |
| `--graf-3` | #0b7a5a | #2fbf8f |
| `--graf-4` | #b0548f | #e08fc0 |
| `--graf-5` | #8f6400 | #e6c84a |
| `--graf-6` | #5a4bb5 | #b29cf0 |
| `--graf-7` | #3f8fc4 | #8fd0f5 |
| `--graf-8` | #4b5563 | #a9b2be |
| `--graf-grade` | #e6e9ee | #29303a |
| `--graf-eixo` | #868f9c | #707a89 |
| `--graf-fundo` | #ffffff | #161a20 |

## Tipografia
Famílias: `Inter, system-ui, sans-serif` (texto) · `'JetBrains Mono', monospace` (números grandes, fórmulas, nomes de coluna, valores em tabela de detalhes). Tabelas: `font-variant-numeric: tabular-nums`.
| Nome | Tamanho / peso / altura de linha / tracking |
|---|---|
| display | 40 / 700 / 1,15 / −0,02em |
| titulo-1 (h1 da etapa) | 28 / 700 / 1,25 / −0,015em |
| titulo-2 | 20 / 600 / 1,3 / −0,01em |
| titulo-3 (título de card/seção) | 16–17 / 600 / 1,35 |
| corpo | 15 / 400 / 1,55 |
| corpo-p | 14 / 400 / 1,5 |
| legenda / rótulo | 12–13 / 500 / 1,4 |
| sobrelinha (rótulo de seção no alerta) | 12 / 600 / maiúsculas / +0,04em |
| numero-grande (mono) | 32–34 / 600 / 1,1 / −0,02em |
| formula (mono) | 15–16 / 500 / 1,5 |

## Espaço, raio, sombra
- Espaço (grade 4/8): `--esp-4 8 12 16 20 24 32 48 64`. Padding de main 32; gap entre cards 16; gap entre blocos 20–24; padding de card 18–24.
- Raio: `--raio-xs 4` (marcas pequenas) · `--raio-sm 6` (badge, segmento interno) · `--raio-md 8` (botão, campo) · `--raio-lg 12` (card) · `999px` (chip de tipo, filtros).
- Sombra: `--sombra-1` cards · `--sombra-2` menus/toast · `--sombra-3` drawer.

Os tokens `--esp-*` e `--raio-*` não estão no `tokens.css` atual; adicione-os no `:root` com esses valores ao implementar.
