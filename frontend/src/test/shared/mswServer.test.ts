import { describe, it, expect } from 'vitest';
import { http, HttpResponse } from 'msw';
import { API_BASE, server } from '@/test/shared';

describe('Подключение MSW-сервера', () => {
  it('отдаёт обработчик, зарегистрированный для настроенного базового URL API', async () => {
    server.use(http.get(`${API_BASE}/health`, () => HttpResponse.json({ status: 'UP' })));

    const response = await fetch(`${API_BASE}/health`);

    expect(response.status).toBe(200);
    expect(await response.json()).toEqual({ status: 'UP' });
  });
});
