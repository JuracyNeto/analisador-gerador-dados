import { renderHook } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { expect, it, vi } from 'vitest';
import { useTeclaEsc } from './useTeclaEsc';

it('chama o callback no Esc só quando está ativo', async () => {
  const aoPressionar = vi.fn();
  const { rerender } = renderHook(
    ({ ativo }) => {
      useTeclaEsc(ativo, aoPressionar);
    },
    {
      initialProps: { ativo: false },
    },
  );

  await userEvent.keyboard('{Escape}');
  expect(aoPressionar).not.toHaveBeenCalled();

  rerender({ ativo: true });
  await userEvent.keyboard('{Escape}');
  expect(aoPressionar).toHaveBeenCalledOnce();
});
