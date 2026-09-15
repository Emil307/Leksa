import { afterEach, beforeEach, expect, vi, type MockInstance } from 'vitest';
import type { UnexpectedResponseReport } from '@/shared/api';

export interface ConsoleErrorSpy {
  expectSilent(): void;
  expectReportedOnce(report: UnexpectedResponseReport): void;
  expectNeverReported(secret: string): void;
}

export function spyOnConsoleError(): ConsoleErrorSpy {
  let spy: MockInstance<typeof console.error>;

  beforeEach(() => {
    spy = vi.spyOn(console, 'error').mockImplementation(() => undefined);
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  return {
    expectSilent: () => expect(spy).not.toHaveBeenCalled(),
    expectReportedOnce: (report) => expect(spy).toHaveBeenCalledExactlyOnceWith(report),
    expectNeverReported: (secret) => expect(JSON.stringify(spy.mock.calls)).not.toContain(secret),
  };
}
