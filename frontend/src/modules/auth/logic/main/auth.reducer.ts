import type {
  AuthAction,
  AuthReducer,
  AuthScreenState,
  ChallengeStartOutcome,
  ChallengeStartResponse,
  ChallengeVerifyOutcome,
  CodeScreenRoute,
  CodeScreenState,
  CreateInitialAuthState,
  EmailScreenRoute,
  EmailScreenState,
  NextRequestId,
} from '../../types';
import { clearCellBackwards, createEmptyCells, enterCellDigit } from './code.logic';
import { computeSecondsLeft, parseExpiresAt } from './countdown.logic';

const emailRoute = (email: EmailScreenState): EmailScreenRoute => ({ screen: 'email', email });

const codeRoute = (code: CodeScreenState): CodeScreenRoute => ({ screen: 'code', code });

const idleEmail = (email: string): EmailScreenRoute =>
  emailRoute({ email, status: 'idle', cooldownSecondsLeft: null, pendingRequestId: null });

export const createInitialAuthState: CreateInitialAuthState = () => idleEmail('');

const pendingRequestId = (state: AuthScreenState): number | null => {
  if (state.screen === 'email') return state.email.pendingRequestId;
  if (state.screen === 'code') return state.code.pendingRequestId;
  return null;
};

export const nextRequestId: NextRequestId = (state) => (pendingRequestId(state) ?? 0) + 1;

const startedCode = (email: string, challenge: ChallengeStartResponse, nowEpochMs: number): CodeScreenState => {
  const expiresAtEpochMs = parseExpiresAt(challenge.expiresAt);
  return {
    email,
    challengeId: challenge.challengeId,
    expiresAtEpochMs,
    secondsLeft: computeSecondsLeft(expiresAtEpochMs, nowEpochMs),
    cells: createEmptyCells(),
    focusedCell: 0,
    status: 'waiting',
    resendCooldownSecondsLeft: null,
    pendingRequestId: null,
  };
};

const cooldownSeconds = (outcome: ChallengeStartOutcome): number | null =>
  outcome.kind === 'conflict' ? outcome.retryAfterSeconds : null;

const REJECTED_KINDS: ReadonlySet<ChallengeVerifyOutcome['kind']> = new Set(['unauthorized', 'validation-failed']);

const emailAfterFailedStart = (email: EmailScreenState, outcome: ChallengeStartOutcome): EmailScreenState => {
  const settled = { ...email, pendingRequestId: null };
  if (outcome.kind === 'validation-failed') return { ...settled, status: 'invalid' };
  const cooldown = cooldownSeconds(outcome);
  if (cooldown !== null) return { ...settled, status: 'cooldown', cooldownSecondsLeft: cooldown };
  return { ...settled, status: 'unavailable' };
};

const reduceEmailScreen = (state: EmailScreenRoute, action: AuthAction): AuthScreenState => {
  const email = state.email;
  switch (action.type) {
    case 'email-changed':
      return idleEmail(action.email);
    case 'request-code':
      if (email.pendingRequestId !== null) return state;
      return emailRoute({ ...email, status: 'sending', pendingRequestId: action.requestId });
    case 'code-requested':
      if (email.pendingRequestId !== action.requestId) return state;
      if (action.outcome.kind === 'started') {
        return codeRoute(startedCode(email.email, action.outcome.challenge, action.nowEpochMs));
      }
      return emailRoute(emailAfterFailedStart(email, action.outcome));
    default:
      return state;
  }
};

const codeAfterFailedVerify = (code: CodeScreenState, outcome: ChallengeVerifyOutcome): CodeScreenState => ({
  ...code,
  pendingRequestId: null,
  status: REJECTED_KINDS.has(outcome.kind) ? 'rejected' : 'unavailable',
});

const codeAfterResend = (
  code: CodeScreenState,
  outcome: ChallengeStartOutcome,
  nowEpochMs: number
): CodeScreenState => {
  if (outcome.kind === 'started') return startedCode(code.email, outcome.challenge, nowEpochMs);
  const settled = { ...code, pendingRequestId: null };
  const cooldown = cooldownSeconds(outcome);
  if (cooldown !== null) return { ...settled, resendCooldownSecondsLeft: cooldown };
  return { ...settled, status: 'unavailable' };
};

const tickCode = (code: CodeScreenState, nowEpochMs: number): CodeScreenState => {
  const secondsLeft = computeSecondsLeft(code.expiresAtEpochMs, nowEpochMs);
  const expired = secondsLeft === 0 && code.status !== 'submitting';
  return { ...code, secondsLeft, status: expired ? 'expired' : code.status };
};

const reduceCodeScreen = (state: CodeScreenRoute, action: AuthAction): AuthScreenState => {
  const code = state.code;
  switch (action.type) {
    case 'cell-input':
      return codeRoute({ ...code, ...enterCellDigit(code.cells, action.index, action.value) });
    case 'cell-backspace':
      return codeRoute({ ...code, ...clearCellBackwards(code.cells, action.index) });
    case 'confirm-code':
      if (code.pendingRequestId !== null) return state;
      return codeRoute({ ...code, status: 'submitting', pendingRequestId: action.requestId });
    case 'code-verified':
      if (code.pendingRequestId !== action.requestId) return state;
      if (action.outcome.kind === 'signed-in') return { screen: 'signed-in', session: action.outcome.session };
      return codeRoute(codeAfterFailedVerify(code, action.outcome));
    case 'resend-code':
      if (code.pendingRequestId !== null) return state;
      return codeRoute({ ...code, pendingRequestId: action.requestId });
    case 'code-resent':
      if (code.pendingRequestId !== action.requestId) return state;
      return codeRoute(codeAfterResend(code, action.outcome, action.nowEpochMs));
    case 'change-email':
      return idleEmail(code.email);
    case 'tick':
      return codeRoute(tickCode(code, action.nowEpochMs));
    default:
      return state;
  }
};

export const authReducer: AuthReducer = (state, action) => {
  if (state.screen === 'email') return reduceEmailScreen(state, action);
  if (state.screen === 'code') return reduceCodeScreen(state, action);
  return state;
};
