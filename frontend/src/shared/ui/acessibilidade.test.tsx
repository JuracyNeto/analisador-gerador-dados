import { render } from '@testing-library/react';
import type { ReactElement } from 'react';
import { describe, it, vi } from 'vitest';
import { esperarSemViolacoes } from '../../testes/acessibilidade';
import Accordion from './Accordion';
import BadgeSeveridade from './BadgeSeveridade';
import Banner from './Banner';
import Botao from './Botao';
import CaixaSelecao from './CaixaSelecao';
import CampoNumero from './CampoNumero';
import Card from './Card';
import CardMetrica from './CardMetrica';
import CartaoOpcao from './CartaoOpcao';
import ChipFiltro from './ChipFiltro';
import ChipTipo from './ChipTipo';
import EstadoCarregando from './EstadoCarregando';
import EstadoErro from './EstadoErro';
import EstadoVazio from './EstadoVazio';
import Segmented from './Segmented';
import Select from './Select';
import Slider from './Slider';
import Tabela from './Tabela';

/** Cada componente de `shared/ui` nos estados principais, sem violações do axe (D153). */
const CASOS: readonly (readonly [string, () => ReactElement])[] = [
  [
    'Botao (variantes, carregando, desabilitado)',
    () => (
      <div>
        <Botao>Continuar</Botao>
        <Botao variante="secundario" icone="refresh">
          Analisar de novo
        </Botao>
        <Botao carregando textoCarregando="Gerando…">
          Gerar dados
        </Botao>
        <Botao disabled>Aplicar limpeza</Botao>
      </div>
    ),
  ],
  [
    'CaixaSelecao (marcada e desabilitada)',
    () => (
      <div>
        <CaixaSelecao rotulo="Leitura" marcada aoMudar={vi.fn()} />
        <CaixaSelecao rotulo="Gerador" marcada={false} aoMudar={vi.fn()} desabilitada />
      </div>
    ),
  ],
  [
    'CampoNumero (com ajuda e com erro)',
    () => (
      <div>
        <CampoNumero rotulo="Semente" valor="42" aoMudar={vi.fn()} ajuda="Repete o resultado." />
        <CampoNumero
          rotulo="Quantidade de valores (X)"
          valor="0"
          aoMudar={vi.fn()}
          erro="Digite um número inteiro entre 1 e 1.000.000."
        />
      </div>
    ),
  ],
  [
    'CartaoOpcao (grupo de rádio)',
    () => (
      <fieldset>
        <legend>Modo</legend>
        <CartaoOpcao nome="modo" titulo="Preservar" selecionado aoSelecionar={vi.fn()} />
        <CartaoOpcao
          nome="modo"
          titulo="Novos parâmetros"
          selecionado={false}
          aoSelecionar={vi.fn()}
          desabilitado
        />
      </fieldset>
    ),
  ],
  [
    'ChipFiltro',
    () => (
      <div role="group" aria-label="Severidade">
        <ChipFiltro rotulo="Suspeita alta" marcado cor="--sev-alta" aoAlternar={vi.fn()} />
        <ChipFiltro rotulo="Atenção" marcado={false} cor="--sev-atencao" aoAlternar={vi.fn()} />
      </div>
    ),
  ],
  [
    'Segmented',
    () => (
      <Segmented
        rotulo="Agrupar por"
        valor="coluna"
        opcoes={[
          { valor: 'coluna', rotulo: 'Coluna' },
          { valor: 'regra', rotulo: 'Regra' },
        ]}
        aoMudar={vi.fn()}
      />
    ),
  ],
  [
    'Select (visível e com rótulo oculto)',
    () => (
      <div>
        <Select
          rotulo="Coluna"
          valor="peso_kg"
          opcoes={[
            { valor: 'peso_kg', rotulo: 'peso_kg' },
            { valor: 'id', rotulo: 'id', desabilitada: true },
          ]}
          aoMudar={vi.fn()}
          ajuda="Só colunas analisáveis."
        />
        <Select
          rotulo="Tipo de idade"
          rotuloOculto
          valor="discreta"
          opcoes={[{ valor: 'discreta', rotulo: 'Quantitativa discreta' }]}
          aoMudar={vi.fn()}
        />
      </div>
    ),
  ],
  [
    'Slider',
    () => (
      <Slider
        rotulo="Correlação alvo (ρ)"
        valor={0.7}
        min={-1}
        max={1}
        passo={0.01}
        aoMudar={vi.fn()}
      />
    ),
  ],
  [
    'Accordion (aberto e fechado)',
    () => (
      <div>
        <Accordion titulo="Detalhes técnicos" abertoInicial>
          <p>Teste binomial · p = 0,0003</p>
        </Accordion>
        <Accordion titulo="Regras não verificadas" complemento="2 regras" variante="secao">
          <p>Lei de Benford não verificada em idade.</p>
        </Accordion>
      </div>
    ),
  ],
  [
    'BadgeSeveridade e ChipTipo',
    () => (
      <div>
        <BadgeSeveridade severidade="alta" />
        <BadgeSeveridade severidade="info" tamanho="sm" />
        <ChipTipo tipo="continua" curto />
        <ChipTipo tipo="nominal" />
      </div>
    ),
  ],
  [
    'Banner, Card e CardMetrica (com fórmula e não aplicável)',
    () => (
      <div>
        <h2>Medidas</h2>
        <Banner variante="info" titulo="Média e mediana próximas">
          Os dados são quase simétricos.
        </Banner>
        <Card titulo="Prever Y para X =">
          <p>Digite um valor de X.</p>
        </Card>
        <CardMetrica
          rotulo="Média"
          valor="70,3"
          unidade="kg"
          interpretacao="O centro dos dados."
          formula={{ expressao: 'x̄ = Σxᵢ / n', calculo: '15.958 / 227' }}
        />
        <CardMetrica
          rotulo="Variância"
          valor="—"
          naoAplicavel={{ motivo: 'Variância não se aplica a qualitativas nominais.' }}
        />
      </div>
    ),
  ],
  [
    'Estados carregando, vazio e erro',
    () => (
      <div>
        <EstadoCarregando mensagem="Calculando…" forma={['cards', 'tabela']} />
        <EstadoVazio
          icone="dataset"
          titulo="Nenhum dado gerado ainda"
          descricao="Preencha o formulário."
          acao={<Botao>Gerar dados</Botao>}
        />
        <EstadoErro erro={new Error('falhou')} aoTentarDeNovo={vi.fn()} />
      </div>
    ),
  ],
  [
    'Tabela (com rolagem)',
    () => (
      <Tabela
        legenda="Prévia dos dados"
        alturaMaxima={200}
        colunas={[
          { id: 'linha', titulo: 'Linha', celula: (l: { n: number }) => l.n, cabecalhoLinha: true },
          {
            id: 'valor',
            titulo: 'Valor',
            celula: (l: { n: number }) => l.n * 2,
            alinhamento: 'direita',
          },
        ]}
        linhas={[{ n: 1 }, { n: 2 }]}
        chave={(l) => String(l.n)}
      />
    ),
  ],
];

describe('componentes de shared/ui', () => {
  it.each(CASOS)('%s não tem violações de acessibilidade', async (_nome, montar) => {
    const { container } = render(montar());

    await esperarSemViolacoes(container);
  });
});
