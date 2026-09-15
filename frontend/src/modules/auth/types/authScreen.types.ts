import type { ChallengeStartOutcome, ChallengeVerifyOutcome } from './challengeClient.types';
import type { CodeCellIndex, CodeScreenState } from './codeScreen.types';
import type { EmailScreenState } from './emailScreen.types';
import type { AuthSession } from './session.types';

export interface EmailScreenRoute {
  screen: 'email';
  email: EmailScreenState;
}

export interface CodeScreenRoute {
  screen: 'code';
  code: CodeScreenState;
}

export interface SignedInRoute {
  screen: 'signed-in';
  session: AuthSession;
}

export type AuthScreenState = EmailScreenRoute | CodeScreenRoute | SignedInRoute;

export type AuthScreenName = AuthScreenState['screen'];

export interface EmailChangedAction {
  type: 'email-changed';
  email: string;
}

export interface RequestCodeAction {
  type: 'request-code';
  requestId: number;
}

export interface CodeRequestedAction {
  type: 'code-requested';
  requestId: number;
  outcome: ChallengeStartOutcome;
  nowEpochMs: number;
}

export interface CellInputAction {
  type: 'cell-input';
  index: CodeCellIndex;
  value: string;
}

export interface CellBackspaceAction {
  type: 'cell-backspace';
  index: CodeCellIndex;
}

export interface ConfirmCodeAction {
  type: 'confirm-code';
  requestId: number;
}

export interface CodeVerifiedAction {
  type: 'code-verified';
  requestId: number;
  outcome: ChallengeVerifyOutcome;
}

export interface ResendCodeAction {
  type: 'resend-code';
  requestId: number;
}

export interface CodeResentAction {
  type: 'code-resent';
  requestId: number;
  outcome: ChallengeStartOutcome;
  nowEpochMs: number;
}

export interface ChangeEmailAction {
  type: 'change-email';
}

export interface TickAction {
  type: 'tick';
  nowEpochMs: number;
}

export type AuthAction =
  | EmailChangedAction
  | RequestCodeAction
  | CodeRequestedAction
  | CellInputAction
  | CellBackspaceAction
  | ConfirmCodeAction
  | CodeVerifiedAction
  | ResendCodeAction
  | CodeResentAction
  | ChangeEmailAction
  | TickAction;

export type AuthReducer = (state: AuthScreenState, action: AuthAction) => AuthScreenState;

export type CreateInitialAuthState = () => AuthScreenState;

export type NextRequestId = (state: AuthScreenState) => number;
