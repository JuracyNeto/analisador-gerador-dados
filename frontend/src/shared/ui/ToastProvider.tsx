import { type ReactNode, useCallback, useMemo, useRef, useState } from 'react';
import { ContextoToast, type PedidoToast, type ToastAtivo } from './contextoToast';
import ItemToast from './ItemToast';
import estilos from './Toast.module.css';

interface PropsToastProvider {
  children: ReactNode;
}

export default function ToastProvider({ children }: Readonly<PropsToastProvider>) {
  const [toasts, setToasts] = useState<readonly ToastAtivo[]>([]);
  const proximoId = useRef(0);

  const mostrar = useCallback((pedido: PedidoToast) => {
    proximoId.current += 1;
    const id = proximoId.current;
    setToasts((atuais) => [...atuais, { ...pedido, id }]);
  }, []);
  const remover = useCallback((id: number) => {
    setToasts((atuais) => atuais.filter((toast) => toast.id !== id));
  }, []);
  const valor = useMemo(() => ({ mostrar }), [mostrar]);

  return (
    <ContextoToast value={valor}>
      {children}
      <div className={estilos.regiao} aria-live="polite">
        {toasts.map((toast) => (
          <ItemToast key={toast.id} toast={toast} aoRemover={remover} />
        ))}
      </div>
    </ContextoToast>
  );
}
