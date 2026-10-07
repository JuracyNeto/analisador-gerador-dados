/** Salva um Blob no computador do usuário com o nome escolhido. */
export function baixarArquivo(conteudo: Blob, nomeArquivo: string): void {
  const url = URL.createObjectURL(conteudo);
  const link = document.createElement('a');
  link.href = url;
  link.download = nomeArquivo;
  link.hidden = true;
  document.body.append(link);
  link.click();
  link.remove();
  // Liberar no próximo ciclo: alguns navegadores ainda leem a URL logo depois do clique.
  window.setTimeout(() => {
    URL.revokeObjectURL(url);
  }, 0);
}
