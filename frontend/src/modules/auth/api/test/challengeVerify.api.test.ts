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
import type { ChallengeVerifyOutcome } from '../../types';

const VERIFY_PATH = '/api/v1/auth/challenge/verify';
const CHALLENGE_ID = '2f9c3a1e-6b7d-4c8e-9f01-23456789abcd';
const REQUEST = { challengeId: CHALLENGE_ID, code: '012345' };
const SIGNED_IN_BODY = {
  user: { id: 'user-7c1d' },
  session: { id: 'session-9e2f', accessToken: 'access-token-value', refreshToken: 'refresh-token-value' },
};
const SESSION = {
  userId: 'user-7c1d',
  sessionId: 'session-9e2f',
  accessToken: 'access-token-value',
  refreshToken: 'refresh-token-value',
};
const ENVELOPE_MESSAGE = 'Secret envelope text about the code';

const client = new AuthChallengeApi(createTestApiClient());
const consoleError = spyOnConsoleError();

function respondWith(status: number, body: Record<string, unknown>) {
  respondWithJson(VERIFY_PATH, status, body);
}

function failWith(status: number, code: string) {
  respondWithJson(VERIFY_PATH, status, errorEnvelope(code, ENVELOPE_MESSAGE));
}

async function verify(): Promise<ChallengeVerifyOutcome> {
  return client.verifyChallenge(REQUEST);
}

describe('API-клиент verifyChallenge', () => {
  it('отправляет challengeId и код строкой в JSON и возвращает сессию входа', async () => {
    const received = captureRequest(VERIFY_PATH, 200, SIGNED_IN_BODY);

    const outcome = await authChallengeApi.verifyChallenge(REQUEST);

    expect(received.contentType).toBe('application/json');
    expect(received.body).toStrictEqual({ challengeId: CHALLENGE_ID, code: '012345' });
    expect(outcome).toStrictEqual({ kind: 'signed-in', session: SESSION });
    consoleError.expectSilent();
  });

  it('игнорирует лишние поля в ответе о входе', async () => {
    respondWith(200, { ...SIGNED_IN_BODY, user: { id: 'user-7c1d', email: 'anna@example.com' }, issuedAt: 'x' });

    const outcome = await verify();

    expect(outcome).toStrictEqual({ kind: 'signed-in', session: SESSION });
    consoleError.expectSilent();
  });

  it('превращает 401 в unauthorized без текста конверта', async () => {
    failWith(401, 'UNAUTHORIZED');

    const outcome = await verify();

    expect(outcome).toStrictEqual({ kind: 'unauthorized' });
    consoleError.expectSilent();
  });

  it('превращает 400 в validation-failed', async () => {
    failWith(400, 'VALIDATION_FAILED');

    const outcome = await verify();

    expect(outcome).toStrictEqual({ kind: 'validation-failed' });
    consoleError.expectSilent();
  });

  it('превращает 503 в unavailable', async () => {
    failWith(503, 'UNAVAILABLE');

    const outcome = await verify();

    expect(outcome).toStrictEqual({ kind: 'unavailable' });
    consoleError.expectSilent();
  });

  it('считает неизвестный статус неожиданным и логирует только путь и статус', async () => {
    failWith(500, 'UNAVAILABLE');

    const outcome = await verify();

    expect(outcome).toStrictEqual({ kind: 'unexpected', status: 500 });
    consoleError.expectReportedOnce({ path: VERIFY_PATH, status: 500 });
    consoleError.expectNeverReported(ENVELOPE_MESSAGE);
  });

  it('считает не-JSON тело 200 неожиданным и не сообщает о входе', async () => {
    respondWithText(VERIFY_PATH, 200, '<html>gateway</html>');

    const outcome = await verify();

    expect(outcome).toStrictEqual({ kind: 'unexpected', status: 200 });
    consoleError.expectReportedOnce({ path: VERIFY_PATH, status: 200 });
  });

  it('считает тело 200 без токенов сессии неожиданным и не сообщает о входе', async () => {
    respondWith(200, { user: { id: 'user-7c1d' }, session: { id: 'session-9e2f' } });

    const outcome = await verify();

    expect(outcome).toStrictEqual({ kind: 'unexpected', status: 200 });
    consoleError.expectReportedOnce({ path: VERIFY_PATH, status: 200 });
  });

  it('превращает таймаут запроса в unavailable', async () => {
    const outcome = await callTimedOutServer(VERIFY_PATH, verify);

    expect(outcome).toStrictEqual({ kind: 'unavailable' });
    consoleError.expectSilent();
  });
});
