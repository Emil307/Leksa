export type EmailValidity = 'empty' | 'malformed' | 'too-long' | 'valid';

export type EmailMaxOctets = 254;

export type EmailScreenStatus = 'idle' | 'sending' | 'invalid' | 'unavailable' | 'cooldown';

export interface EmailScreenState {
  email: string;
  status: EmailScreenStatus;
  cooldownSecondsLeft: number | null;
  pendingRequestId: number | null;
}

export type EmailScreenMessageKind = 'invalid-email' | 'unavailable' | 'email-cooldown';

export interface EmailScreenMessage {
  kind: EmailScreenMessageKind;
  secondsLeft: number | null;
}

export type RequestCodeButtonMode = 'request' | 'sending' | 'retry';

export interface EmailScreenView {
  email: string;
  inputEnabled: boolean;
  requestEnabled: boolean;
  requestButton: RequestCodeButtonMode;
  fieldTone: 'normal' | 'error' | 'disabled';
  message: EmailScreenMessage | null;
}
