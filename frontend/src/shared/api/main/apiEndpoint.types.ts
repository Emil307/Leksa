import type { ApiError } from './apiError.types';

export type ApiOutcome<Success> = Success | ApiError;

export type ParseSuccessBody<Success> = (body: unknown) => Success | null;

export interface ApiEndpoint<Success> {
  path: string;
  parse: ParseSuccessBody<Success>;
}

export type CallEndpoint = <Success>(endpoint: ApiEndpoint<Success>, payload: unknown) => Promise<ApiOutcome<Success>>;

export interface ApiClient {
  call: CallEndpoint;
}
