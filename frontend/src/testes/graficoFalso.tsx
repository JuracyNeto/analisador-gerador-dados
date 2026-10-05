interface Props {
  titulo: string;
  resumo: string;
}

/** Uso: vi.mock('<caminho>/shared/graficos/Grafico', () => import('<caminho>/testes/graficoFalso')); */
export default function GraficoFalso({ titulo, resumo }: Readonly<Props>) {
  return (
    <figure aria-label={titulo} data-resumo={resumo}>
      <figcaption>{titulo}</figcaption>
    </figure>
  );
}
