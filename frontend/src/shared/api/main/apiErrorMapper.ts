import { isJsonObject, isPositiveNumber, isString } from '@/shared/utils';
import type { ApiError, ApiErrorCode, ApiErrorEnvelope, ApiErrorLocation } from './apiError.types';
import type { ReportUnexpectedResponse } from './apiClient.types';
import { reportUnexpectedResponse } from './unexpectedResponse';

const STATUS_CODES: Record<number, ApiErrorCode> = {
  400: 'VALIDATION_FAILED',
  401: 'UNAUTHORIZED',
  403: 'FORBIDDEN',
  404: 'NOT_FOUND',
  409: 'CONFLICT',
  503: 'UNAVAILABLE',
};

export class ApiErrorMapper {
  constructor(private readonly report: ReportUnexpectedResponse = reportUnexpectedResponse) {}

  static parseEnvelope(body: unknown): ApiErrorEnvelope | null {
    if (!isJsonObject(body) || !isString(body.code)) return null;
    return { code: body.code, payload: isJsonObject(body.payload) ? body.payload : {} };
  }

  timedOut(): ApiError {
    return { kind: 'unavailable' };
  }

  map(location: ApiErrorLocation, body: unknown): ApiError {
    const code = STATUS_CODES[location.status];
    if (code === undefined) return this.unexpected(location);
    const envelope = ApiErrorMapper.parseEnvelope(body);
    if (envelope !== null && envelope.code !== code) return this.unexpected(location);
    return this.byCode(code, envelope);
  }

  unexpected(location: ApiErrorLocation): ApiError {
    this.report(location);
    return { kind: 'unexpected', status: location.status };
  }

  private byCode(code: ApiErrorCode, envelope: ApiErrorEnvelope | null): ApiError {
    switch (code) {
      case 'VALIDATION_FAILED':
        return { kind: 'validation-failed' };
      case 'UNAUTHORIZED':
        return this.unauthorized();
      case 'FORBIDDEN':
        return { kind: 'forbidden' };
      case 'NOT_FOUND':
        return { kind: 'not-found' };
      case 'CONFLICT':
        return this.conflict(envelope);
      case 'UNAVAILABLE':
        return { kind: 'unavailable' };
    }
  }

  private unauthorized(): ApiError {
    return { kind: 'unauthorized' };
  }

  private conflict(envelope: ApiErrorEnvelope | null): ApiError {
    const retryAfterSeconds = envelope?.payload.retryAfterSeconds;
    return { kind: 'conflict', retryAfterSeconds: isPositiveNumber(retryAfterSeconds) ? retryAfterSeconds : null };
  }
}
