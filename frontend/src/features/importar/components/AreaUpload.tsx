import { type ChangeEvent, type DragEvent, useId, useRef, useState } from 'react';
import Botao from '../../../shared/ui/Botao';
import Icone from '../../../shared/ui/Icone';
import { TEXTOS_IMPORTAR as T } from '../textos';
import estilos from './AreaUpload.module.css';

interface PropsAreaUpload {
  enviando: boolean;
  nomeEnviando: string;
  comErro: boolean;
  aoEscolher: (arquivo: File) => void;
}

type EstadoArea = 'normal' | 'arrastando' | 'enviando' | 'erro';

function estadoDaArea(situacao: {
  arrastando: boolean;
  enviando: boolean;
  comErro: boolean;
}): EstadoArea {
  if (situacao.enviando) return 'enviando';
  if (situacao.arrastando) return 'arrastando';
  return situacao.comErro ? 'erro' : 'normal';
}

const FORMATOS = T.formatosAceitos.map((formato) => (
  <li key={formato} className={estilos.formato}>
    {formato}
  </li>
));

/** Arrastar e soltar um arquivo na área (ignora o que é solto enquanto envia). */
function useArrasteArquivo(enviando: boolean, aoEscolher: (arquivo: File) => void) {
  const [arrastando, setArrastando] = useState(false);
  return {
    arrastando,
    onDragOver: (evento: DragEvent<HTMLDivElement>): void => {
      evento.preventDefault();
      setArrastando(true);
    },
    onDragLeave: (evento: DragEvent<HTMLDivElement>): void => {
      const destino = evento.relatedTarget;
      if (destino instanceof Node && evento.currentTarget.contains(destino)) return;
      setArrastando(false);
    },
    onDrop: (evento: DragEvent<HTMLDivElement>): void => {
      evento.preventDefault();
      setArrastando(false);
      const arquivo = evento.dataTransfer.files[0];
      if (arquivo !== undefined && !enviando) aoEscolher(arquivo);
    },
  };
}

interface PropsSeletorArquivo {
  enviando: boolean;
  nomeEnviando: string;
  idApoio: string;
  aoEscolher: (arquivo: File) => void;
}

/** Botão "Escolher arquivo" + `<input type="file">` escondido (o foco fica no botão). */
function SeletorArquivo({
  enviando,
  nomeEnviando,
  idApoio,
  aoEscolher,
}: Readonly<PropsSeletorArquivo>) {
  const entrada = useRef<HTMLInputElement>(null);

  function aoMudarEntrada(evento: ChangeEvent<HTMLInputElement>): void {
    const arquivo = evento.target.files?.[0];
    evento.target.value = ''; // permite escolher o mesmo arquivo de novo
    if (arquivo !== undefined) aoEscolher(arquivo);
  }

  return (
    <>
      <Botao
        tamanho="lg"
        icone="folder_open"
        carregando={enviando}
        textoCarregando={T.area.enviando(nomeEnviando)}
        aria-describedby={idApoio}
        onClick={() => {
          entrada.current?.click();
        }}
      >
        {T.area.botao}
      </Botao>
      <input
        ref={entrada}
        className={estilos.entrada}
        type="file"
        accept={T.formatosAceitos.join(',')}
        aria-label={T.area.rotuloEntrada}
        tabIndex={-1}
        onChange={aoMudarEntrada}
      />
    </>
  );
}

export default function AreaUpload({
  enviando,
  nomeEnviando,
  comErro,
  aoEscolher,
}: Readonly<PropsAreaUpload>) {
  const idApoio = useId();
  const { arrastando, ...eventosArraste } = useArrasteArquivo(enviando, aoEscolher);

  return (
    <div
      className={estilos.area}
      data-estado={estadoDaArea({ arrastando, enviando, comErro })}
      {...eventosArraste}
    >
      <span className={estilos.circulo}>
        <Icone nome="upload_file" tamanho={36} />
      </span>
      <div className={estilos.textos}>
        <p className={estilos.titulo}>{arrastando ? T.area.soltar : T.area.titulo}</p>
        <p className={estilos.apoio} id={idApoio}>
          {T.area.apoio}
        </p>
      </div>
      {enviando ? (
        <div role="progressbar" aria-label={T.area.rotuloProgresso} className={estilos.progresso} />
      ) : null}
      <SeletorArquivo
        enviando={enviando}
        nomeEnviando={nomeEnviando}
        idApoio={idApoio}
        aoEscolher={aoEscolher}
      />
      <ul className={estilos.formatos} aria-label={T.area.rotuloFormatos}>
        {FORMATOS}
      </ul>
    </div>
  );
}
