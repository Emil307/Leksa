import { describe, expect, it } from 'vitest';
import {
  callTimedOutServer,
  captureRequest,
  createTestApiClient,
  errorEnvelope,
  respondWithJson,
  respondWithText,
  spyOnConsoleError,
} from '@/test/shared';
import { AuthChallengeApi, authChallengeApi } from '../main/challenge.api';
import type { ChallengeStartOutcome } from '../../types';

const START_PATH = '/api/v1/auth/challenge/start';
const EMAIL = 'anna@example.com';
const REQUEST = { email: EMAIL, challengeType: 'EMAIL_CODE' as const };
const STARTED_BODY = {
  challengeId: '2f9c3a1e-6b7d-4c8e-9f01-23456789abcd',
  challengeType: 'EMAIL_CODE',
  expiresAt: '2026-09-14T12:05:00Z',
};
const ENVELOPE_MESSAGE = 'Secret envelope text with anna@example.com';

const client = new AuthChallengeApi(createTestApiClient());
const consoleError = spyOnConsoleError();

function respondWith(status: number, body: Record<string, unknown>) {
  respondWithJson(START_PATH, status, body);
}

function failWith(status: number, code: string, payload: Record<string, unknown> = {}) {
  respondWithJson(START_PATH, status, errorEnvelope(code, ENVELOPE_MESSAGE, payload));
}

async function start(): Promise<ChallengeStartOutcome> {
  return client.startChallenge(REQUEST);
}

describe('API-клиент startChallenge', () => {
  it('отправляет почту с типом EMAIL_CODE и возвращает started', async () => {
    const received = captureRequest(START_PATH, 200, STARTED_BODY);

    const outcome = await authChallengeApi.startChallenge(REQUEST);

    expect(received.contentType).toBe('application/json');
    expect(received.body).toStrictEqual({ email: EMAIL, challengeType: 'EMAIL_CODE' });
    expect(outcome).toStrictEqual({ kind: 'started', challenge: STARTED_BODY });
    consoleError.expectSilent();
  });

  it('игнорирует лишние поля в ответе о запущенной проверке', async () => {
    respondWith(200, { ...STARTED_BODY, nonce: 'ignored', attemptsLeft: 5 });

    const outcome = await start();

    expect(outcome).toStrictEqual({ kind: 'started', challenge: STARTED_BODY });
    consoleError.expectSilent();
  });

  it('превращает 400 в validation-failed без текста конверта', async () => {
    failWith(400, 'VALIDATION_FAILED');

    const outcome = await start();

    expect(outcome).toStrictEqual({ kind: 'validation-failed' });
    consoleError.expectSilent();
  });

  it('превращает 409 CONFLICT в conflict с retryAfterSeconds', async () => {
    failWith(409, 'CONFLICT', { retryAfterSeconds: 42 });

    const outcome = await start();

    expect(outcome).toStrictEqual({ kind: 'conflict', retryAfterSeconds: 42 });
    consoleError.expectSilent();
  });

  it('превращает 409 CONFLICT без retryAfterSeconds в conflict без подсказки о повторе', async () => {
    failWith(409, 'CONFLICT');

    const outcome = await start();

    expect(outcome).toStrictEqual({ kind: 'conflict', retryAfterSeconds: null });
    consoleError.expectSilent();
  });

  it('превращает 503 в unavailable', async () => {
    failWith(503, 'UNAVAILABLE');

    const outcome = await start();

    expect(outcome).toStrictEqual({ kind: 'unavailable' });
    consoleError.expectSilent();
  });

  it('считает неизвестный статус неожиданным и логирует только путь и статус', async () => {
    failWith(500, 'UNAVAILABLE');

    const outcome = await start();

    expect(outcome).toStrictEqual({ kind: 'unexpected', status: 500 });
    consoleError.expectReportedOnce({ path: START_PATH, status: 500 });
    consoleError.expectNeverReported(EMAIL);
    consoleError.expectNeverReported(ENVELOPE_MESSAGE);
  });

  it('считает не-JSON тело 200 неожиданным ответом и не бросает исключение', async () => {
    respondWithText(START_PATH, 200, '<html>gateway</html>');

    const outcome = await start();

    expect(outcome).toStrictEqual({ kind: 'unexpected', status: 200 });
    consoleError.expectReportedOnce({ path: START_PATH, status: 200 });
  });

  it('считает тело 200 без expiresAt неожиданным ответом', async () => {
    respondWith(200, { challengeId: STARTED_BODY.challengeId, challengeType: 'EMAIL_CODE' });

    const outcome = await start();

    expect(outcome).toStrictEqual({ kind: 'unexpected', status: 200 });
    consoleError.expectReportedOnce({ path: START_PATH, status: 200 });
  });

  it('превращает таймаут запроса в unavailable', async () => {
    const outcome = await callTimedOutServer(START_PATH, start);

    expect(outcome).toStrictEqual({ kind: 'unavailable' });
    consoleError.expectSilent();
  });
});
