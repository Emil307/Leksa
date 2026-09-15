import { ApiClient } from '@/shared/api';

export const API_BASE: string = import.meta.env.VITE_API_URL;

if (!API_BASE) throw new Error('VITE_API_URL is required for frontend API tests');

export const API_TIMEOUT_MS = 10000;

export function createTestApiClient(): ApiClient {
  return new ApiClient({ baseUrl: API_BASE, timeoutMs: API_TIMEOUT_MS });
}
