import { formatarInteiro, formatarNumero } from '../../shared/lib/formatar';
import { formatarCelula } from '../../shared/lib/formatarCelula';
import {
  descreverLinhas,
  descreverOcorrencias,
  listarComE,
  listarNumeros,
  primeiraMaiuscula,
  soma,
} from './descricoes';
import { TEXTOS_LIMPEZA as T } from './textos';
import type {
  Diagnostico,
  EscolhasLimpeza,
  ForaDeFaixaColuna,
  InconsistenciaColuna,
  LinhaProblema,
  OpcaoAcao,
  PedidoLimpeza,
  Problema,
  SecaoDiagnostico,
  ValoresSugeridos,
} from './tipos';

type BaseAcao = LinhaProblema['acaoBase'];

interface TextosSecao {
  titulo: string;
  cabecalhos: readonly [string, string];
}

const MANTER: OpcaoAcao = { valor: 'manter', rotulo: T.acoes.manter };
const OPCOES_DUPLICADOS: readonly OpcaoAcao[] = [
  { valor: 'remover', rotulo: T.acoes.remover },
  MANTER,
];
const OPCOES_TIPO_MISTO: readonly OpcaoAcao[] = [
  { valor: 'marcar_faltante', rotulo: T.acoes.removerValor },
  MANTER,
];
const MAX_COPIAS_ROTULO = 3;

function baseAcao(problema: Problema, extras: Partial<Omit<BaseAcao, 'problema'>> = {}): BaseAcao {
  return { problema, coluna: null, valor: null, limites: null, grupo: null, ...extras };
}

function secao(
  id: Problema,
  textos: TextosSecao,
  subtitulo: string,
  linhas: LinhaProblema[],
): SecaoDiagnostico {
  return { id, titulo: textos.titulo, subtitulo, cabecalhos: textos.cabecalhos, linhas };
}

function opcoesFaltantes({ media, mediana, moda }: ValoresSugeridos): OpcaoAcao[] {
  const opcoes: OpcaoAcao[] = [];
  if (mediana !== null)
    opcoes.push({
      valor: 'preencher_mediana',
      rotulo: T.acoes.preencherMediana(formatarNumero(mediana)),
    });
  if (media !== null)
    opcoes.push({
      valor: 'preencher_media',
      rotulo: T.acoes.preencherMedia(formatarNumero(media)),
    });
  if (moda !== null)
    opcoes.push({ valor: 'preencher_moda', rotulo: T.acoes.preencherModa(formatarCelula(moda)) });
  opcoes.push(
    { valor: 'remover_linhas', rotulo: T.acoes.removerLinha },
    { valor: 'manter', rotulo: T.acoes.manterNaoInformado },
  );
  return opcoes;
}

function secaoFaltantes(itens: Diagnostico['faltantes']): SecaoDiagnostico {
  const linhas = itens.map((item) => ({
    chave: `faltantes:${item.coluna}`,
    rotulo: item.coluna,
    descricao: `${formatarInteiro(item.n)} · ${descreverLinhas(item.linhas)}`,
    detalhe: null,
    opcoes: opcoesFaltantes(item.sugeridos),
    acaoBase: baseAcao('faltantes', { coluna: item.coluna }),
  }));
  const textos = T.secoes.faltantes;
  return secao('faltantes', textos, textos.subtitulo(soma(itens.map((i) => i.n))), linhas);
}

/** A API aplica "remover duplicados" a todos os grupos de uma vez: uma linha, um Select. */
function secaoDuplicados(grupos: Diagnostico['duplicados']): SecaoDiagnostico {
  const copias = grupos.flatMap((g) => g.copias);
  const originais = descreverLinhas(grupos.map((g) => g.linha_original));
  const textos = T.secoes.duplicados;
  const linhas: LinhaProblema[] =
    grupos.length === 0
      ? []
      : [
          {
            chave: 'duplicados',
            rotulo: listarNumeros(copias, MAX_COPIAS_ROTULO),
            descricao: textos.igualA(primeiraMaiuscula(originais)),
            detalhe: null,
            opcoes: OPCOES_DUPLICADOS,
            acaoBase: baseAcao('duplicados'),
          },
        ];
  return secao('duplicados', textos, textos.subtitulo(copias.length), linhas);
}

function opcoesForaDeFaixa(item: ForaDeFaixaColuna): OpcaoAcao[] {
  const limites = T.acoes.limitar(
    formatarNumero(item.limite_inferior),
    formatarNumero(item.limite_superior),
  );
  return [
    { valor: 'marcar_faltante', rotulo: T.acoes.removerValor },
    { valor: 'limitar', rotulo: limites },
    { valor: 'remover_linhas', rotulo: T.acoes.removerLinha },
    MANTER,
  ];
}

function secaoForaDeFaixa(itens: Diagnostico['fora_de_faixa']): SecaoDiagnostico {
  const textos = T.secoes.foraDeFaixa;
  const linhas = itens.map((item) => ({
    chave: `fora_de_faixa:${item.coluna}`,
    rotulo: item.coluna,
    descricao: descreverOcorrencias(item.ocorrencias),
    detalhe: textos.faixa(
      formatarNumero(item.limite_inferior),
      formatarNumero(item.limite_superior),
      textos.origem[item.origem],
    ),
    opcoes: opcoesForaDeFaixa(item),
    acaoBase: baseAcao('fora_de_faixa', {
      coluna: item.coluna,
      limites: { min: item.limite_inferior, max: item.limite_superior },
    }),
  }));
  return secao(
    'fora_de_faixa',
    textos,
    textos.subtitulo(soma(itens.map((i) => i.ocorrencias.length))),
    linhas,
  );
}

function linhasGrafias(item: InconsistenciaColuna): LinhaProblema[] {
  return item.grupos.map((grupo) => {
    const variacoes = grupo.variacoes.filter((v) => v.texto !== grupo.forma_preferida);
    const unificar = T.acoes.unificar(
      variacoes.map((v) => `'${v.texto}'`).join(', '),
      grupo.forma_preferida,
    );
    return {
      chave: `inconsistencia:${item.coluna}:${grupo.forma_preferida}`,
      rotulo: grupo.forma_preferida,
      descricao: variacoes.map((v) => `"${v.texto}" (${formatarInteiro(v.n)})`).join(', '),
      detalhe: T.secoes.grafias.naColuna(item.coluna),
      opcoes: [{ valor: 'unificar', rotulo: unificar }, MANTER],
      acaoBase: baseAcao('inconsistencia', { coluna: item.coluna, grupo: grupo.forma_preferida }),
    };
  });
}

function secaoGrafias(itens: Diagnostico['inconsistencias']): SecaoDiagnostico {
  const linhas = itens.flatMap(linhasGrafias);
  const textos = T.secoes.grafias;
  return secao(
    'inconsistencia',
    textos,
    textos.subtitulo(linhas.length, listarComE(itens.map((i) => i.coluna))),
    linhas,
  );
}

function secaoTipoMisto(itens: Diagnostico['tipo_misto']): SecaoDiagnostico {
  const linhas = itens.map((item) => ({
    chave: `tipo_misto:${item.coluna}`,
    rotulo: item.coluna,
    descricao: descreverOcorrencias(item.ocorrencias),
    detalhe: null,
    opcoes: OPCOES_TIPO_MISTO,
    acaoBase: baseAcao('tipo_misto', { coluna: item.coluna }),
  }));
  const textos = T.secoes.tipoMisto;
  return secao(
    'tipo_misto',
    textos,
    textos.subtitulo(soma(itens.map((i) => i.ocorrencias.length))),
    linhas,
  );
}

/** Seções com pelo menos uma linha, na ordem do design 3a (tipo misto só aparece se houver). */
export function montarSecoes(diagnostico: Diagnostico): SecaoDiagnostico[] {
  return [
    secaoFaltantes(diagnostico.faltantes),
    secaoDuplicados(diagnostico.duplicados),
    secaoForaDeFaixa(diagnostico.fora_de_faixa),
    secaoGrafias(diagnostico.inconsistencias),
    secaoTipoMisto(diagnostico.tipo_misto),
  ].filter((s) => s.linhas.length > 0);
}

/** D75: só vão para a API as linhas cuja escolha é diferente de "manter". */
export function montarPedido(
  secoes: readonly SecaoDiagnostico[],
  escolhas: EscolhasLimpeza,
): PedidoLimpeza {
  const acoes = secoes
    .flatMap((s) => s.linhas)
    .flatMap((linha) => {
      const acao = escolhas[linha.chave] ?? 'manter';
      return acao === 'manter' ? [] : [{ ...linha.acaoBase, acao }];
    });
  return { acoes };
}
