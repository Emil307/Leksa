import type { ApiClientOptions, ApiRequestTimeoutMs, ApiResult } from './apiClient.types';
import type { ApiEndpoint, ApiOutcome } from './apiEndpoint.types';
import { ApiErrorMapper } from './apiErrorMapper';

const BASE_URL = import.meta.env.VITE_API_URL;

if (!BASE_URL) throw new Error('VITE_API_URL is required');

const DEFAULT_TIMEOUT_MS: ApiRequestTimeoutMs = 10000;

async function readJsonBody(response: Response): Promise<unknown> {
  try {
    return await response.json();
  } catch {
    return undefined;
  }
}

async function postJson(url: string, payload: unknown, timeoutMs: number): Promise<ApiResult> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      signal: controller.signal,
    });
    return { kind: 'received', status: response.status, body: await readJsonBody(response) };
  } catch {
    return { kind: 'timed-out' };
  } finally {
    clearTimeout(timer);
  }
}

export class ApiClient {
  constructor(
    private readonly options: ApiClientOptions,
    private readonly errors: ApiErrorMapper = new ApiErrorMapper()
  ) {}

  call = async <Success>(endpoint: ApiEndpoint<Success>, payload: unknown): Promise<ApiOutcome<Success>> => {
    const result = await postJson(`${this.options.baseUrl}${endpoint.path}`, payload, this.options.timeoutMs);
    if (result.kind === 'timed-out') return this.errors.timedOut();
    const location = { path: endpoint.path, status: result.status };
    if (result.status !== 200) return this.errors.map(location, result.body);
    return endpoint.parse(result.body) ?? this.errors.unexpected(location);
  };
}

export const apiClient = new ApiClient({ baseUrl: BASE_URL, timeoutMs: DEFAULT_TIMEOUT_MS });
