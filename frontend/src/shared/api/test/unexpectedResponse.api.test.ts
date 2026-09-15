import { afterEach, describe, expect, it, vi } from 'vitest';
import { reportUnexpectedResponse } from '../main/unexpectedResponse';

afterEach(() => {
  vi.restoreAllMocks();
});

describe('reportUnexpectedResponse', () => {
  it('логирует путь и статус единственным аргументом console.error', () => {
    const consoleError = vi.spyOn(console, 'error').mockImplementation(() => undefined);

    reportUnexpectedResponse({ path: '/api/v1/auth/challenge/start', status: 502 });

    expect(consoleError).toHaveBeenCalledExactlyOnceWith({ path: '/api/v1/auth/challenge/start', status: 502 });
  });
});
