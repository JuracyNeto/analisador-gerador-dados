import { expect, it } from 'vitest';
import { juntarClasses } from './classes';

it('junta só as classes preenchidas', () => {
  expect(juntarClasses('a', false, undefined, null, '', 'b')).toBe('a b');
});
