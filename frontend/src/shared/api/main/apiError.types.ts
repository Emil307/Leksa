export interface ApiValidationFailed {
  kind: 'validation-failed';
}

export interface ApiUnauthorized {
  kind: 'unauthorized';
}

export interface ApiForbidden {
  kind: 'forbidden';
}

export interface ApiNotFound {
  kind: 'not-found';
}

export interface ApiConflict {
  kind: 'conflict';
  retryAfterSeconds: number | null;
}

export interface ApiUnavailable {
  kind: 'unavailable';
}

export interface ApiUnexpected {
  kind: 'unexpected';
  status: number;
}

export type ApiError =
  ApiValidationFailed | ApiUnauthorized | ApiForbidden | ApiNotFound | ApiConflict | ApiUnavailable | ApiUnexpected;

export type ApiErrorCode =
  'VALIDATION_FAILED' | 'UNAUTHORIZED' | 'FORBIDDEN' | 'NOT_FOUND' | 'CONFLICT' | 'UNAVAILABLE';

export interface ApiErrorEnvelope {
  code: string;
  payload: Record<string, unknown>;
}

export interface ApiErrorLocation {
  path: string;
  status: number;
}
