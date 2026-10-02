import { useQuery } from '@tanstack/react-query';
import { requisitar } from '../../shared/api/cliente';
import type { components } from '../../shared/api/schema';

export type Saude = components['schemas']['Saude'];

export const chavesSistema = {
  saude: ['sistema', 'saude'] as const,
};

export function useSaude() {
  return useQuery({
    queryKey: chavesSistema.saude,
    queryFn: () => requisitar<Saude>('/saude'),
  });
}
