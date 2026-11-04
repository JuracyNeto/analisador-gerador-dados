/**
 * Prints das telas para o relatório final (D168): percorre o fluxo com os arquivos de exemplo e
 * grava os PNG em docs/relatorio-final/prints/, com os nomes de docs/design/telas/prints/.
 *
 * Usa o Edge instalado (playwright-core, sem baixar navegador) e fica fora do CI. O backend e o
 * frontend precisam estar rodando. Uso (em frontend/): npm run prints [-- http://localhost:5173]
 */
import { mkdir } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium, type Browser, type Page } from 'playwright-core';

const URL_PADRAO = 'http://localhost:5173';
const PASTA = path.resolve(
  path.dirname(fileURLToPath(import.meta.url)),
  '../../docs/relatorio-final/prints',
);
const VIEWPORT = { width: 1440, height: 900 };
const ESPERA_MAXIMA = 90_000;
const INTERVALO = 250;
const PAUSA_FINAL = 500;
/** Mesma geração do exemplo do relatório HTML (backend/scripts/exportar_relatorio_exemplo.py). */
const SEMENTE = '42';
const ANALISE = '/analise?coluna=peso_kg&aba=';

interface OpcoesPrint {
  /** Só a janela (o drawer fica preso à janela); sem a opção, a página inteira. */
  soJanela?: boolean;
}

function avisar(texto: string): void {
  process.stdout.write(`${texto}\n`);
}

async function esperarAte(condicao: () => Promise<boolean>): Promise<void> {
  const limite = Date.now() + ESPERA_MAXIMA;
  while (!(await condicao())) {
    if (Date.now() > limite) throw new Error('A tela demorou demais para carregar.');
    await new Promise((resolver) => setTimeout(resolver, INTERVALO));
  }
}

/** Espera os pedidos à API, as fontes e o desenho de cada gráfico Plotly (também na prévia). */
async function esperarTela(pagina: Page): Promise<void> {
  await pagina.waitForLoadState('networkidle');
  await pagina.evaluate('document.fonts.ready.then(() => true)');
  const semDesenho = '.js-plotly-plot:not(:has(.main-svg))';
  const previa = pagina.frameLocator('iframe').locator(semDesenho);
  await esperarAte(
    async () => (await pagina.locator(semDesenho).count()) + (await previa.count()) === 0,
  );
  await pagina.waitForTimeout(PAUSA_FINAL);
}

/** Os avisos de sucesso ("Geramos 500 pares.") cobririam o topo da tela. */
async function fecharAvisos(pagina: Page): Promise<void> {
  const fechar = pagina.getByRole('button', { name: 'Fechar aviso' });
  while ((await fechar.count()) > 0) await fechar.first().click();
}

/** A barra lateral tem a altura da janela: para a página inteira, a janela cresce até o fim. */
async function esticarJanela(pagina: Page): Promise<void> {
  const altura = Number(await pagina.evaluate('document.documentElement.scrollHeight'));
  await pagina.setViewportSize({
    width: VIEWPORT.width,
    height: Math.max(altura, VIEWPORT.height),
  });
  await esperarTela(pagina);
}

async function print(pagina: Page, nome: string, opcoes: OpcoesPrint = {}): Promise<void> {
  await esperarTela(pagina);
  await fecharAvisos(pagina);
  if (opcoes.soJanela !== true) await esticarJanela(pagina);
  await pagina.screenshot({ path: path.join(PASTA, `${nome}.png`) });
  await pagina.setViewportSize(VIEWPORT);
  avisar(`Gravado ${nome}.png`);
}

async function abrir(pagina: Page, caminho: string): Promise<void> {
  await pagina.goto(caminho);
  await esperarTela(pagina);
}

async function novaPagina(navegador: Browser, base: string): Promise<Page> {
  const contexto = await navegador.newContext({
    baseURL: base,
    viewport: VIEWPORT,
    colorScheme: 'light',
    reducedMotion: 'reduce',
    locale: 'pt-BR',
  });
  const pagina = await contexto.newPage();
  pagina.setDefaultTimeout(ESPERA_MAXIMA);
  return pagina;
}

/** Abre um exemplo pela tela Importar ("Abrir pesquisa_saude.txt de exemplo" ou outro). */
async function importarExemplo(pagina: Page, botao: string): Promise<void> {
  await abrir(pagina, '/importar');
  await pagina.getByRole('button', { name: botao }).click();
  await pagina.getByText('O que detectamos').waitFor();
}

async function emEscuro(pagina: Page, passos: () => Promise<void>): Promise<void> {
  await pagina.emulateMedia({ colorScheme: 'dark' });
  await passos();
  await pagina.emulateMedia({ colorScheme: 'light' });
}

/** 1a a 3a; aplica a limpeza sugerida (a 1ª opção de cada linha), como o exemplo do HTML. */
async function importarELimpar(pagina: Page): Promise<void> {
  await importarExemplo(pagina, 'Abrir pesquisa_saude.txt de exemplo');
  await print(pagina, '1a-importar');
  await abrir(pagina, '/variaveis');
  await print(pagina, '2a-variaveis');
  await abrir(pagina, '/limpeza');
  const escolhas = pagina.locator('main select');
  for (const escolha of await escolhas.all()) await escolha.selectOption({ index: 0 });
  await print(pagina, '3a-limpeza');
  await pagina.getByRole('button', { name: 'Aplicar limpeza' }).click();
  await pagina.getByText('Resultado:').waitFor();
}

async function separatrizes(pagina: Page): Promise<void> {
  await abrir(pagina, `${ANALISE}separatrizes`);
  await pagina.getByLabel('Valor de peso_kg').fill('80');
}

/** 4a a 4g e 4i (separatrizes no tema escuro). */
async function analisar(pagina: Page): Promise<void> {
  await separatrizes(pagina);
  await print(pagina, '4a-univariada-separatrizes');
  const abas = [
    ['frequencias', '4b-univariada-frequencias'],
    ['tendencia', '4c-univariada-tendencia'],
    ['dispersao', '4d-univariada-dispersao'],
    ['forma', '4e-univariada-forma'],
    ['graficos', '4f-univariada-graficos'],
  ] as const;
  for (const [aba, nome] of abas) {
    await abrir(pagina, `${ANALISE}${aba}`);
    await print(pagina, nome);
  }
  await abrir(pagina, '/analise?coluna=cidade&aba=frequencias');
  await print(pagina, '4g-univariada-nominal');
  await emEscuro(pagina, async () => {
    await separatrizes(pagina);
    await print(pagina, '4i-univariada-escuro');
  });
}

async function preverNaBivariada(pagina: Page): Promise<void> {
  await abrir(pagina, '/bivariada');
  await pagina.getByLabel('altura_m', { exact: true }).fill('1,75');
  await pagina.getByRole('button', { name: 'Prever' }).click();
  await print(pagina, '5a-bivariada');
}

async function gerarDados(pagina: Page): Promise<void> {
  await pagina.getByLabel('Semente (repete o mesmo resultado)').fill(SEMENTE);
  await pagina.getByRole('button', { name: 'Gerar dados' }).click();
  await pagina.getByText('Original × Gerado').first().waitFor();
}

/** 6b e depois 6a: a última geração (univariada) é a que vai para o relatório (8a). */
async function gerar(pagina: Page): Promise<void> {
  await abrir(pagina, '/gerador?aba=bivariado');
  // A coluna escolhida num eixo fica desabilitada no outro: o Y sai de altura_m antes.
  await pagina.getByLabel('Y', { exact: true }).selectOption('peso_kg');
  await pagina.getByLabel('X', { exact: true }).selectOption('altura_m');
  await pagina.getByLabel('Correlação alvo (ρ)').fill('0.8');
  await gerarDados(pagina);
  await print(pagina, '6b-gerador-bivariado');
  await pagina.getByRole('tab', { name: 'Univariado' }).click();
  await pagina.getByLabel('Coluna', { exact: true }).selectOption('peso_kg');
  await pagina.getByLabel('Quantidade de valores (X)').fill('500');
  await gerarDados(pagina);
  await print(pagina, '6a-gerador-univariado');
}

async function relatorio(pagina: Page): Promise<void> {
  await abrir(pagina, '/relatorio');
  await pagina.frameLocator('iframe').locator('.js-plotly-plot').first().waitFor();
  await print(pagina, '8a-relatorio');
}

/** 7a, 7b (drawer da R4) e 7d (escuro) com os dados plantados; 7c com as alturas reais. */
async function detectar(navegador: Browser, base: string): Promise<void> {
  const plantadas = await novaPagina(navegador, base);
  await importarExemplo(plantadas, 'alturas_plantadas.txt');
  await abrir(plantadas, '/detector');
  await print(plantadas, '7a-detector');
  const cartao = plantadas.locator('article', { hasText: 'R4 · Valores redondos' });
  await cartao.getByRole('button', { name: 'Ver na tabela' }).click();
  await plantadas.getByRole('dialog').waitFor();
  await print(plantadas, '7b-detector-drawer', { soJanela: true });
  await plantadas.keyboard.press('Escape');
  await emEscuro(plantadas, async () => {
    await abrir(plantadas, '/detector');
    await print(plantadas, '7d-detector-escuro');
  });
  const reais = await novaPagina(navegador, base);
  await importarExemplo(reais, 'alturas_reais.txt');
  await abrir(reais, '/detector');
  await print(reais, '7c-detector-vazio');
}

async function tirarPrints(base: string): Promise<void> {
  await mkdir(PASTA, { recursive: true });
  const navegador = await chromium.launch({ channel: 'msedge' });
  try {
    const pagina = await novaPagina(navegador, base);
    await importarELimpar(pagina);
    await analisar(pagina);
    await preverNaBivariada(pagina);
    await gerar(pagina);
    await relatorio(pagina);
    await detectar(navegador, base);
  } finally {
    await navegador.close();
  }
}

const base = process.argv[2] ?? URL_PADRAO;
tirarPrints(base).catch((erro: unknown) => {
  const motivo = erro instanceof Error ? erro.message : String(erro);
  avisar(`Não conseguimos tirar os prints em ${base}: ${motivo}`);
  avisar('Confira se o backend e o frontend estão rodando e se o Microsoft Edge está instalado.');
  process.exitCode = 1;
});
