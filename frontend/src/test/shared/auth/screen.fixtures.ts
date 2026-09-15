import type { AuthScreenState, CodeScreenState, EmailScreenState } from '@/modules/auth/types';
import { CHALLENGE_ID, EMAIL, EMPTY_CELLS, EXPIRES_AT_EPOCH_MS, FULL_CELLS } from './auth.fixtures';

export function emailScreen(overrides: Partial<EmailScreenState> = {}): EmailScreenState {
  return { email: EMAIL, status: 'idle', cooldownSecondsLeft: null, pendingRequestId: null, ...overrides };
}

export function emailSendingScreen(): EmailScreenState {
  return emailScreen({ status: 'sending', pendingRequestId: 1 });
}

export function codeScreen(overrides: Partial<CodeScreenState> = {}): CodeScreenState {
  return {
    email: EMAIL,
    challengeId: CHALLENGE_ID,
    expiresAtEpochMs: EXPIRES_AT_EPOCH_MS,
    secondsLeft: 300,
    cells: EMPTY_CELLS,
    focusedCell: 0,
    status: 'waiting',
    resendCooldownSecondsLeft: null,
    pendingRequestId: null,
    ...overrides,
  };
}

export function codeFilledScreen(overrides: Partial<CodeScreenState> = {}): CodeScreenState {
  return codeScreen({ cells: FULL_CELLS, focusedCell: 5, secondsLeft: 280, ...overrides });
}

export function codeSubmittingScreen(): CodeScreenState {
  return codeFilledScreen({ status: 'submitting', pendingRequestId: 1 });
}

export function onEmailScreen(email: EmailScreenState): AuthScreenState {
  return { screen: 'email', email };
}

export function onCodeScreen(code: CodeScreenState): AuthScreenState {
  return { screen: 'code', code };
}
