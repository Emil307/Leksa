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
import { apiClient, type ApiEndpoint } from '../index';
import { isJsonObject, isString } from '@/shared/utils';

const PATH = '/api/v1/echo';
const PAYLOAD = { value: 'hello' };
const ENVELOPE_MESSAGE = 'secret';

interface EchoSuccess {
  kind: 'echoed';
  value: string;
}

const endpoint: ApiEndpoint<EchoSuccess> = {
  path: PATH,
  parse: (body) => (isJsonObject(body) && isString(body.value) ? { kind: 'echoed', value: body.value } : null),
};

const client = createTestApiClient();
const consoleError = spyOnConsoleError();

function failWith(status: number, code: string, payload: Record<string, unknown> = {}) {
  respondWithJson(PATH, status, errorEnvelope(code, ENVELOPE_MESSAGE, payload));
}

async function echo() {
  return client.call(endpoint, PAYLOAD);
}

describe('Общий API-клиент', () => {
  it('отправляет JSON на базовый URL плюс путь эндпоинта и разбирает тело 200', async () => {
    const received = captureRequest(PATH, 200, { value: 'echo' });

    const outcome = await echo();

    expect(received.contentType).toBe('application/json');
    expect(received.body).toStrictEqual(PAYLOAD);
    expect(outcome).toStrictEqual({ kind: 'echoed', value: 'echo' });
    consoleError.expectSilent();
  });

  it('считает тело 200, отвергнутое эндпоинтом, неожиданным и логирует его', async () => {
    respondWithJson(PATH, 200, { other: 1 });

    expect(await echo()).toStrictEqual({ kind: 'unexpected', status: 200 });
    consoleError.expectReportedOnce({ path: PATH, status: 200 });
  });

  it.each([
    [400, 'VALIDATION_FAILED', { kind: 'validation-failed' }],
    [401, 'UNAUTHORIZED', { kind: 'unauthorized' }],
    [403, 'FORBIDDEN', { kind: 'forbidden' }],
    [404, 'NOT_FOUND', { kind: 'not-found' }],
    [503, 'UNAVAILABLE', { kind: 'unavailable' }],
  ])('превращает %i %s в общий вид ошибки', async (status, code, expected) => {
    failWith(status, code);

    expect(await echo()).toStrictEqual(expected);
    consoleError.expectSilent();
  });

  it('превращает 409 CONFLICT в conflict с retryAfterSeconds из payload', async () => {
    failWith(409, 'CONFLICT', { retryAfterSeconds: 42 });

    expect(await echo()).toStrictEqual({ kind: 'conflict', retryAfterSeconds: 42 });
  });

  it('превращает 409 CONFLICT без положительного retryAfterSeconds в conflict с null', async () => {
    failWith(409, 'CONFLICT', { retryAfterSeconds: 0 });

    expect(await echo()).toStrictEqual({ kind: 'conflict', retryAfterSeconds: null });
  });

  it('распознаёт известный статус без конверта по одному статусу', async () => {
    respondWithText(PATH, 503, '<html/>');

    expect(await echo()).toStrictEqual({ kind: 'unavailable' });
    consoleError.expectSilent();
  });

  it('считает код конверта, не совпадающий со статусом, неожиданным ответом', async () => {
    failWith(400, 'NOT_FOUND');

    expect(await echo()).toStrictEqual({ kind: 'unexpected', status: 400 });
    consoleError.expectReportedOnce({ path: PATH, status: 400 });
  });

  it('считает неизвестный статус неожиданным и логирует только путь и статус', async () => {
    failWith(418, 'TEAPOT');

    expect(await echo()).toStrictEqual({ kind: 'unexpected', status: 418 });
    consoleError.expectReportedOnce({ path: PATH, status: 418 });
    consoleError.expectNeverReported(ENVELOPE_MESSAGE);
  });

  it('превращает таймаут запроса в unavailable', async () => {
    const outcome = await callTimedOutServer(PATH, echo);

    expect(outcome).toStrictEqual({ kind: 'unavailable' });
    consoleError.expectSilent();
  });

  it('экспортирует клиент по умолчанию, привязанный к VITE_API_URL', async () => {
    respondWithJson(PATH, 200, { value: 'default' });

    expect(await apiClient.call(endpoint, PAYLOAD)).toStrictEqual({ kind: 'echoed', value: 'default' });
  });
});
