import { vi } from 'vitest';
import { delay, http, HttpResponse, type JsonBodyType } from 'msw';
import { server } from './mswServer';
import { API_BASE, API_TIMEOUT_MS } from './apiTestClient';

export interface CapturedRequest {
  contentType: string | null;
  body: unknown;
}

export interface ErrorEnvelope {
  code: string;
  message: string;
  payload: Record<string, unknown>;
}

export function errorEnvelope(code: string, message: string, payload: Record<string, unknown> = {}): ErrorEnvelope {
  return { code, message, payload };
}

export function respondWithJson(path: string, status: number, body: JsonBodyType): void {
  server.use(http.post(`${API_BASE}${path}`, () => HttpResponse.json(body, { status })));
}

export function respondWithText(path: string, status: number, text: string): void {
  server.use(http.post(`${API_BASE}${path}`, () => HttpResponse.text(text, { status })));
}

export function captureRequest(path: string, status: number, body: JsonBodyType): CapturedRequest {
  const captured: CapturedRequest = { contentType: null, body: null };
  server.use(
    http.post(`${API_BASE}${path}`, async ({ request }) => {
      captured.contentType = request.headers.get('content-type');
      captured.body = await request.json();
      return HttpResponse.json(body, { status });
    })
  );
  return captured;
}

export async function callTimedOutServer<T>(path: string, call: () => Promise<T>): Promise<T> {
  vi.useFakeTimers();
  server.use(http.post(`${API_BASE}${path}`, async () => await delay('infinite')));
  try {
    const [outcome] = await Promise.all([call(), vi.advanceTimersByTimeAsync(API_TIMEOUT_MS)]);
    return outcome;
  } finally {
    vi.useRealTimers();
  }
}
