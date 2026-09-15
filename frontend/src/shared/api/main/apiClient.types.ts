export interface ApiReceived {
  kind: 'received';
  status: number;
  body: unknown;
}

export interface ApiTimedOut {
  kind: 'timed-out';
}

export type ApiResult = ApiReceived | ApiTimedOut;

export interface ApiClientOptions {
  baseUrl: string;
  timeoutMs: number;
}

export type ApiRequestTimeoutMs = 10000;

export interface UnexpectedResponseReport {
  path: string;
  status: number;
}

export type ReportUnexpectedResponse = (report: UnexpectedResponseReport) => void;
