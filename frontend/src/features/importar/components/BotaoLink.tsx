import type { ButtonHTMLAttributes } from 'react';
import estilos from './BotaoLink.module.css';

type PropsBotaoLink = Omit<ButtonHTMLAttributes<HTMLButtonElement>, 'className' | 'type'>;

export default function BotaoLink(props: Readonly<PropsBotaoLink>) {
  return <button type="button" className={estilos.link} {...props} />;
}
