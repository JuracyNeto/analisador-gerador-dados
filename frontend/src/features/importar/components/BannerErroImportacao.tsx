import Banner from '../../../shared/ui/Banner';
import { descreverErroImportacao } from '../apresentacao';
import { TEXTOS_IMPORTAR as T } from '../textos';
import BotaoLink from './BotaoLink';

interface PropsBannerErroImportacao {
  erro: unknown;
  nomeArquivo: string;
  aoUsarExemplo: () => void;
}

/** Erro 1c: mensagem e sugestão vêm da API; o link "Como exportar para CSV" fica fora (sem destino). */
export default function BannerErroImportacao({
  erro,
  nomeArquivo,
  aoUsarExemplo,
}: Readonly<PropsBannerErroImportacao>) {
  const { titulo, texto } = descreverErroImportacao(erro, nomeArquivo);
  return (
    <Banner
      variante="erro"
      titulo={titulo}
      acoes={<BotaoLink onClick={aoUsarExemplo}>{T.erro.usarExemplo}</BotaoLink>}
    >
      {texto}
    </Banner>
  );
}
